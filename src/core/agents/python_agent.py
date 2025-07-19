"""
Python analysis agent for data processing and visualization.
"""
import logging
import re
from typing import List, Dict, Any, Optional
from pathlib import Path
import pickle
from langchain_core.messages import HumanMessage, AIMessage
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from src.config.settings import config
from src.models.data_models import InputData, AnalysisResult, ChatMessage
from src.core.graph.tools import PythonAnalysisTool
from src.utils.file_utils import file_manager

from src.config.logging_config import get_logger

# Configure logging
logger = get_logger(__name__)

class PythonAnalysisAgent:
    """Main agent for Python-based data analysis."""
    
    def __init__(self):
        """Initialize the analysis agent."""
        self.reset_state()
        self.llm = ChatOpenAI(
            model=config.OPENAI_MODEL,
            temperature=0.1,
            api_key=config.OPENAI_API_KEY
        )
        self.python_tool = PythonAnalysisTool()
        
        # Load the main prompt
        with open(config.MAIN_PROMPT_PATH, 'r', encoding='utf-8') as f:
            self.main_prompt = f.read()
    
    def reset_state(self):
        """Reset the agent state."""
        self.chat_history: List[ChatMessage] = []
        self.intermediate_outputs: List[Dict[str, Any]] = []
        self.output_image_paths: Dict[int, List[str]] = {}
        self.analysis_results: List[AnalysisResult] = []
    
    def process_query(self, user_query: str, input_data: List[InputData], chat_history: List[ChatMessage] = None) -> Dict[str, Any]:
        """Process a user query and return analysis results."""
        try:
            logger.info(f"Processing query: {user_query}")
            logger.info(f"Input data: {len(input_data)} datasets")
            
            # Prepare the prompt with context
            context = self._prepare_context(input_data)
            logger.info(f"Context prepared, length: {len(context)}")
            
            # Prepare chat history context
            chat_history_context = ""
            if chat_history and len(chat_history) > 0:
                chat_history_context = "\n\n**Historial de la conversación anterior:**\n"
                for message in chat_history[-10:]:  # Last 10 messages
                    role = "Usuario" if message.role == "user" else "Asistente"
                    chat_history_context += f"{role}: {message.content}\n"
                logger.info(f"Chat history context added: {len(chat_history)} messages")
            
            # Create the full prompt
            full_prompt = f"""
{self.main_prompt}

Contexto de los datos:
{context}

{chat_history_context}

Consulta actual del usuario: {user_query}

**INSTRUCCIONES IMPORTANTES:**
- Si el usuario pide crear gráficas, visualizaciones, análisis estadísticos o cualquier procesamiento de datos, DEBES incluir código Python en tu respuesta.
- El código debe estar en bloques markdown con ```python al inicio y ``` al final.
- Para gráficas, usa plotly y almacena las figuras en la lista `plotly_figures`.
- Para análisis estadísticos, usa print() para mostrar los resultados.
- **IMPORTANTE**: Usa el historial de la conversación para mantener contexto y recordar preguntas anteriores.

Por favor, analiza los datos y responde a la consulta del usuario. Si necesitas ejecutar código Python, inclúyelo en tu respuesta.
"""
            logger.info("Sending request to LLM...")
            
            # Get response from LLM
            response = self.llm.invoke(full_prompt)
            logger.info(f"LLM response received: {len(response.content)} characters")
            
            # Check if response contains code that needs to be executed
            if "```python" in response.content:
                logger.info("Python code detected, executing...")
                # Extract and execute Python code
                code_result = self.python_tool.run(response.content, input_data)
                logger.info(f"Code execution result: {len(code_result)} characters")
                
                # Get updated response with execution results (without showing code to user)
                # Remove code blocks from response for user display
                clean_response = re.sub(r'```python.*?```', '', response.content, flags=re.DOTALL).strip()
                final_response = f"{clean_response}\n\n**Resultado de la ejecución:**\n{code_result}"
            else:
                logger.info("No Python code detected")
                # Check if user is asking for visualizations or analysis
                visualization_keywords = [
                    'gráfica', 'grafica', 'gráfico', 'grafico', 'histograma', 
                    'dispersión', 'dispersion', 'correlación', 'correlacion', 
                    'análisis', 'analisis', 'estadística', 'estadistica', 
                    'distribución', 'distribucion'
                ]
                if any(keyword in user_query.lower() for keyword in visualization_keywords):
                    logger.info("Visualization requested but no code generated, prompting for code...")
                    # Ask the LLM to generate code for visualization
                    code_prompt = f"""
El usuario pidió: "{user_query}"

Necesitas generar código Python para crear la visualización solicitada. Responde SOLO con el código Python necesario, sin explicaciones adicionales.

```python
# Código para {user_query}
"""
                    code_response = self.llm.invoke(code_prompt)
                    if "```python" in code_response.content:
                        logger.info("Generated code for visualization, executing...")
                        code_result = self.python_tool.run(code_response.content, input_data)
                        final_response = f"{response.content}\n\n**Resultado de la ejecución:**\n{code_result}"
                    else:
                        final_response = response.content
                else:
                    final_response = response.content
            
            # Track any new images created
            new_images = self.python_tool.get_latest_images()
            logger.info(f"New images created: {len(new_images)}")
            logger.debug(f"Image paths: {new_images}")
            
            result = {
                'response': final_response,
                'code': code_result if "```python" in response.content else None,
                'output_image_paths': new_images
            }
            
            logger.info("Query processing completed successfully")
            return result
            
        except Exception as e:
            logger.error(f"Error in process_query: {str(e)}")
            logger.exception("Full traceback:")
            return {
                'response': f"Error procesando la consulta: {str(e)}",
                'code': None,
                'output_image_paths': []
            }
    
    def _prepare_context(self, input_data: List[InputData]) -> str:
        """Prepare context information from input data."""
        context_parts = []
        
        for data in input_data:
            try:
                # Load and analyze the dataset
                df = file_manager.load_dataframe(data.data_path.name)
                
                context_parts.append(f"""
Dataset: {data.variable_name}
Archivo: {data.data_path.name}
Descripción: {data.data_description}
Forma: {df.shape}
Columnas: {list(df.columns)}
Tipos de datos: {df.dtypes.to_dict()}
Primeras filas:
{df.head().to_string()}

**IMPORTANTE**: Usa '{data.variable_name}' como nombre de la variable para acceder a este dataset en tu código Python.
""")
            except Exception as e:
                context_parts.append(f"""
Dataset: {data.variable_name}
Archivo: {data.data_path.name}
Error al cargar: {str(e)}
""")
        
        return "\n".join(context_parts)
    
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
            logger.error(f"Error loading plotly figure {image_path}: {e}")
            return None 