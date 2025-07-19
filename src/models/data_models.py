"""
Data models for the Agentic Data Analysis application.
"""
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from pathlib import Path
import pandas as pd

@dataclass
class InputData:
    """Model for input data files."""
    variable_name: str
    data_path: Path
    data_description: str = ""
    data_frame: Optional[pd.DataFrame] = None
    
    def __post_init__(self):
        """Load the data frame if path exists."""
        if self.data_path.exists() and self.data_frame is None:
            try:
                self.data_frame = pd.read_csv(self.data_path)
            except Exception as e:
                raise ValueError(f"Error loading data from {self.data_path}: {e}")

@dataclass
class DatasetInfo:
    """Model for dataset information."""
    filename: str
    description: str = ""
    coverage: str = ""
    features: List[str] = field(default_factory=list)
    usage: List[str] = field(default_factory=list)
    linkage: str = ""
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "description": self.description,
            "coverage": self.coverage,
            "features": self.features,
            "usage": self.usage,
            "linkage": self.linkage
        }

@dataclass
class ChatMessage:
    """Model for chat messages."""
    content: str
    sender: str  # "user" or "assistant"
    timestamp: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class AnalysisResult:
    """Model for analysis results."""
    query: str
    response: str
    code: Optional[str] = None
    visualizations: List[str] = field(default_factory=list)
    intermediate_outputs: List[Dict[str, Any]] = field(default_factory=list)
    timestamp: Optional[str] = None

@dataclass
class AppState:
    """Model for application state."""
    selected_files: List[str] = field(default_factory=list)
    chat_history: List[ChatMessage] = field(default_factory=list)
    analysis_results: List[AnalysisResult] = field(default_factory=list)
    current_dataset_info: Dict[str, DatasetInfo] = field(default_factory=dict) 