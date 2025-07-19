"""
Python analysis agent for data processing and visualization.
"""
from typing import List, Dict, Any, Optional
from pathlib import Path
import pickle
from langchain_core.messages import HumanMessage, AIMessage
from langgraph.graph import StateGraph
from src.config.settings import config
from src.models.data_models import InputData, AnalysisResult, ChatMessage
from src.core.graph.state import AgentState
from src.core.graph.nodes import call_model, call_tools, route_to_tools
from src.utils.file_utils import file_manager

class PythonAnalysisAgent:
    """Main agent for Python-based data analysis."""
    
    def __init__(self):
        """Initialize the analysis agent."""
        self.reset_state()
        self.graph = self._create_graph()
    
    def _create_graph(self) -> StateGraph:
        """Create the LangGraph workflow."""
        workflow = StateGraph(AgentState)
        
        # Add nodes
        workflow.add_node('agent', call_model)
        workflow.add_node('tools', call_tools)
        
        # Add edges
        workflow.add_conditional_edges('agent', route_to_tools)
        workflow.add_edge('tools', 'agent')
        
        # Set entry point
        workflow.set_entry_point('agent')
        
        return workflow.compile()
    
    def reset_state(self):
        """Reset the agent state."""
        self.chat_history: List[ChatMessage] = []
        self.intermediate_outputs: List[Dict[str, Any]] = []
        self.output_image_paths: Dict[int, List[str]] = {}
        self.analysis_results: List[AnalysisResult] = []
    
    def process_query(self, user_query: str, input_data: List[InputData]) -> AnalysisResult:
        """Process a user query and return analysis results."""
        # Convert to LangChain messages
        messages = [HumanMessage(content=user_query)]
        
        # Prepare input state
        starting_image_paths = set(sum(self.output_image_paths.values(), []))
        input_state = {
            "messages": messages,
            "output_image_paths": list(starting_image_paths),
            "input_data": input_data,
        }
        
        # Execute the graph
        result = self.graph.invoke(input_state, {"recursion_limit": 25})
        
        # Update state
        from datetime import datetime
        current_time = datetime.now().strftime("%H:%M:%S")
        
        self.chat_history.extend([
            ChatMessage(
                content=msg.content, 
                sender="user" if isinstance(msg, HumanMessage) else "assistant",
                timestamp=current_time
            )
            for msg in result["messages"]
        ])
        
        # Track new images
        new_image_paths = set(result["output_image_paths"]) - starting_image_paths
        if new_image_paths:
            self.output_image_paths[len(self.chat_history) - 1] = list(new_image_paths)
        
        # Store intermediate outputs
        if "intermediate_outputs" in result:
            self.intermediate_outputs.extend(result["intermediate_outputs"])
        
        # Create analysis result
        analysis_result = AnalysisResult(
            query=user_query,
            response=result["messages"][-1].content if result["messages"] else "",
            intermediate_outputs=result.get("intermediate_outputs", [])
        )
        
        self.analysis_results.append(analysis_result)
        return analysis_result
    
    def get_chat_history(self) -> List[ChatMessage]:
        """Get the chat history."""
        return self.chat_history
    
    def get_intermediate_outputs(self) -> List[Dict[str, Any]]:
        """Get intermediate outputs from the last analysis."""
        return self.intermediate_outputs
    
    def get_output_images(self, message_index: int) -> List[str]:
        """Get output images for a specific message."""
        return self.output_image_paths.get(message_index, [])
    
    def load_plotly_figure(self, image_path: str):
        """Load a plotly figure from file."""
        try:
            # Use absolute path from config
            figure_path = config.PLOTLY_FIGURES_DIR / image_path
            with open(figure_path, "rb") as f:
                return pickle.load(f)
        except Exception as e:
            print(f"Error loading plotly figure {image_path}: {e}")
            return None 