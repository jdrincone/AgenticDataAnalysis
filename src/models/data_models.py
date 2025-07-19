"""
Data models for the Agentic Data Analysis application.
"""
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from pathlib import Path
import pandas as pd

@dataclass
class InputData:
    """Represents input data for analysis."""
    name: str
    data: pd.DataFrame
    description: str = ""
    source: str = "file"  # Only "file" now

@dataclass
class ChatMessage:
    """Represents a chat message."""
    role: str  # 'user' or 'assistant'
    content: str
    timestamp: Optional[str] = None

@dataclass
class AnalysisResult:
    """Represents the result of an analysis."""
    query: str
    response: str
    code_executed: Optional[str] = None
    output_image_paths: List[str] = field(default_factory=list)
    error: Optional[str] = None

@dataclass
class DatasetInfo:
    """Represents information about a dataset."""
    filename: str
    description: str
    coverage: Optional[str] = None
    features: List[str] = field(default_factory=list)
    usage: Optional[str] = None
    linkage: Optional[str] = None

class AppState:
    """Centralized state management for the Streamlit application."""
    
    def __init__(self):
        self._selected_files: List[str] = []
        self._data_dictionary: Dict[str, Any] = {}
        self._chat_history: List[ChatMessage] = []
        self._analysis_results: List[AnalysisResult] = []
        self._debug_mode: bool = False
        
    @property
    def selected_files(self) -> List[str]:
        """Get selected files."""
        return self._selected_files.copy()
    
    @selected_files.setter
    def selected_files(self, files: List[str]):
        """Set selected files."""
        self._selected_files = files.copy() if files else []
    
    @property
    def data_dictionary(self) -> Dict[str, Any]:
        """Get data dictionary."""
        return self._data_dictionary.copy()
    
    @data_dictionary.setter
    def data_dictionary(self, dictionary: Dict[str, Any]):
        """Set data dictionary."""
        self._data_dictionary = dictionary.copy() if dictionary else {}
    
    @property
    def chat_history(self) -> List[ChatMessage]:
        """Get chat history."""
        return self._chat_history.copy()
    
    def add_chat_message(self, message: ChatMessage):
        """Add a chat message to history."""
        self._chat_history.append(message)
    
    def clear_chat_history(self):
        """Clear chat history."""
        self._chat_history.clear()
    
    @property
    def analysis_results(self) -> List[AnalysisResult]:
        """Get analysis results."""
        return self._analysis_results.copy()
    
    def add_analysis_result(self, result: AnalysisResult):
        """Add an analysis result."""
        self._analysis_results.append(result)
    
    def clear_analysis_results(self):
        """Clear analysis results."""
        self._analysis_results.clear()
    
    @property
    def debug_mode(self) -> bool:
        """Get debug mode status."""
        return self._debug_mode
    
    @debug_mode.setter
    def debug_mode(self, enabled: bool):
        """Set debug mode."""
        self._debug_mode = enabled
    

    
    def get_dataset_description(self, filename: str) -> str:
        """Get description for a specific dataset."""
        return self._data_dictionary.get(filename, {}).get('description', '')
    
    def update_dataset_description(self, filename: str, description: str):
        """Update description for a specific dataset."""
        if filename not in self._data_dictionary:
            self._data_dictionary[filename] = {}
        self._data_dictionary[filename]['description'] = description
    
    def has_selected_files(self) -> bool:
        """Check if there are selected files."""
        return len(self._selected_files) > 0
    
    def get_input_data_list(self, uploads_dir: Path) -> List[InputData]:
        """Get list of InputData objects for selected files."""
        input_data_list = []
        
        # Add file-based data
        for file in self._selected_files:
            try:
                import pandas as pd
                df = pd.read_csv(uploads_dir / file)
                input_data_list.append(
                    InputData(
                        name=file,
                        data=df,
                        description=self.get_dataset_description(file),
                        source="file"
                    )
                )
            except Exception as e:
                print(f"Error loading file {file}: {str(e)}")
        
        return input_data_list
    
    def reset(self):
        """Reset all state to initial values."""
        self._selected_files.clear()
        self._chat_history.clear()
        self._analysis_results.clear()
        self._debug_mode = False 