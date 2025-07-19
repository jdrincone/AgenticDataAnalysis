"""
Configuration settings for the Agentic Data Analysis application.
"""
import os
from pathlib import Path
from typing import List, Optional
from dataclasses import dataclass
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

@dataclass
class AppConfig:
    """Application configuration settings."""
    
    # App metadata
    APP_NAME: str = "Okuo IA DataLab"
    APP_VERSION: str = "1.0.0"
    APP_DESCRIPTION: str = "Laboratorio de Análisis Inteligente de Datos"
    
    # Paths
    BASE_DIR: Path = Path(__file__).parent.parent.parent
    ASSETS_DIR: Path = BASE_DIR / "assets"
    UPLOADS_DIR: Path = ASSETS_DIR / "uploads"
    IMAGES_DIR: Path = ASSETS_DIR / "images"
    PLOTLY_FIGURES_DIR: Path = IMAGES_DIR / "plotly_figures" / "pickle"
    
    # Data files
    DATA_DICTIONARY_FILE: Path = BASE_DIR / "data_dictionary.json"
    
    # API Configuration
    OPENAI_API_KEY: Optional[str] = os.getenv("OPENAI_API_KEY")
    OPENAI_MODEL: str = os.getenv("OPENAI_MODEL", "gpt-4o")
    
    # Streamlit Configuration
    STREAMLIT_PORT: int = int(os.getenv("STREAMLIT_PORT", "8501"))
    STREAMLIT_HOST: str = os.getenv("STREAMLIT_HOST", "localhost")
    MAX_UPLOAD_SIZE: int = int(os.getenv("MAX_UPLOAD_SIZE", "2000"))
    
    # UI Configuration
    PRIMARY_COLOR: str = "#1C8074"
    SECONDARY_COLOR: str = "#1A494C"
    SUCCESS_COLOR: str = "#1C8074"
    ERROR_COLOR: str = "#D32F2F"
    
    # File upload settings
    ALLOWED_EXTENSIONS: List[str] = None
    
    def __post_init__(self):
        """Initialize derived settings."""
        if self.ALLOWED_EXTENSIONS is None:
            self.ALLOWED_EXTENSIONS = [".csv", ".xlsx", ".xls"]
        
        # Create necessary directories
        self.UPLOADS_DIR.mkdir(parents=True, exist_ok=True)
        self.PLOTLY_FIGURES_DIR.mkdir(parents=True, exist_ok=True)
    
    def validate_config(self) -> bool:
        """Validate the configuration."""
        if not self.OPENAI_API_KEY:
            raise ValueError("OPENAI_API_KEY is required. Please set it in your .env file.")
        return True

# Global configuration instance
config = AppConfig() 