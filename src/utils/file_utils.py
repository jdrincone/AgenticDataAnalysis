"""
File utility functions for the Agentic Data Analysis application.
"""
import json
import pandas as pd
from pathlib import Path
from typing import List, Dict, Any, Optional
from src.config.settings import config
from src.models.data_models import DatasetInfo

class FileManager:
    """Manages file operations for the application."""
    
    def __init__(self):
        self.uploads_dir = config.UPLOADS_DIR
        self.data_dict_file = config.DATA_DICTIONARY_FILE
        self.plotly_dir = config.PLOTLY_FIGURES_DIR
    
    def save_uploaded_file(self, file_content: bytes, filename: str) -> Path:
        """Save an uploaded file to the uploads directory."""
        file_path = self.uploads_dir / filename
        with open(file_path, 'wb') as f:
            f.write(file_content)
        return file_path
    
    def get_available_files(self, extension: str = ".csv") -> List[str]:
        """Get list of available files with specified extension."""
        return [f.name for f in self.uploads_dir.glob(f"*{extension}")]
    
    def load_dataframe(self, filename: str) -> pd.DataFrame:
        """Load a dataframe from a file."""
        file_path = self.uploads_dir / filename
        if not file_path.exists():
            raise FileNotFoundError(f"File {filename} not found")
        
        if filename.endswith('.csv'):
            return pd.read_csv(file_path)
        elif filename.endswith(('.xlsx', '.xls')):
            return pd.read_excel(file_path)
        else:
            raise ValueError(f"Unsupported file format: {filename}")
    
    def load_data_dictionary(self) -> Dict[str, Any]:
        """Load the data dictionary from JSON file."""
        if not self.data_dict_file.exists():
            return {}
        
        try:
            with open(self.data_dict_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading data dictionary: {e}")
            return {}
    
    def save_data_dictionary(self, data_dict: Dict[str, Any]) -> bool:
        """Save the data dictionary to JSON file."""
        try:
            with open(self.data_dict_file, 'w', encoding='utf-8') as f:
                json.dump(data_dict, f, indent=4, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"Error saving data dictionary: {e}")
            return False
    
    def update_dataset_info(self, filename: str, info: DatasetInfo) -> bool:
        """Update dataset information in the data dictionary."""
        data_dict = self.load_data_dictionary()
        data_dict[filename] = info.to_dict()
        return self.save_data_dictionary(data_dict)
    
    def save_plotly_figure(self, figure, filename: str) -> Path:
        """Save a plotly figure to the plotly figures directory."""
        file_path = self.plotly_dir / filename
        figure.write_image(str(file_path))
        return file_path
    
    def get_plotly_figure_path(self, filename: str) -> Path:
        """Get the path to a plotly figure file."""
        return self.plotly_dir / filename
    
    def validate_file_extension(self, filename: str) -> bool:
        """Validate if file extension is allowed."""
        return any(filename.endswith(ext) for ext in config.ALLOWED_EXTENSIONS)

# Global file manager instance
file_manager = FileManager() 