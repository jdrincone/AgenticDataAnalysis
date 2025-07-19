#!/usr/bin/env python3
"""
Setup script for Okuo IA DataLab
"""
import os
import sys
from pathlib import Path
import subprocess

def check_python_version():
    """Check if Python version is compatible."""
    if sys.version_info < (3, 12):
        print("❌ Error: Python 3.12 or higher is required")
        print(f"Current version: {sys.version_info.major}.{sys.version_info.minor}")
        sys.exit(1)
    print(f"✅ Python {sys.version_info.major}.{sys.version_info.minor} detected")

def install_requirements():
    """Install required packages."""
    print("📦 Installing requirements...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✅ Requirements installed successfully")
    except subprocess.CalledProcessError:
        print("❌ Error installing requirements")
        sys.exit(1)

def create_env_file():
    """Create .env file if it doesn't exist."""
    env_file = Path(".env")
    if not env_file.exists():
        print("🔧 Creating .env file...")
        env_content = """# Okuo IA DataLab Configuration
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_MODEL=gpt-4o
STREAMLIT_PORT=8501
STREAMLIT_HOST=localhost
MAX_UPLOAD_SIZE=2000
"""
        with open(env_file, 'w') as f:
            f.write(env_content)
        print("✅ .env file created")
        print("⚠️  Please update OPENAI_API_KEY in .env file")
    else:
        print("✅ .env file already exists")

def create_directories():
    """Create necessary directories."""
    print("📁 Creating directories...")
    directories = [
        "assets/uploads",
        "assets/images/plotly_figures/pickle",
        "temp_pdf_images",
        "logs"
    ]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
    
    print("✅ Directories created")

def validate_setup():
    """Validate the setup."""
    print("🔍 Validating setup...")
    
    # Check if .env exists
    if not Path(".env").exists():
        print("❌ .env file not found")
        return False
    
    # Check if requirements are installed
    try:
        import streamlit
        import pandas
        import plotly
        print("✅ All required packages are available")
    except ImportError as e:
        print(f"❌ Missing package: {e}")
        return False
    
    return True

def main():
    """Main setup function."""
    print("🚀 Setting up Okuo IA DataLab...")
    print("=" * 50)
    
    # Check Python version
    check_python_version()
    
    # Create directories
    create_directories()
    
    # Install requirements
    install_requirements()
    
    # Create .env file
    create_env_file()
    
    # Validate setup
    if validate_setup():
        print("=" * 50)
        print("🎉 Setup completed successfully!")
        print("\n📋 Next steps:")
        print("1. Update OPENAI_API_KEY in .env file")
        print("2. Run: streamlit run main_app.py")
        print("3. Open http://localhost:8501 in your browser")
    else:
        print("❌ Setup failed. Please check the errors above.")

if __name__ == "__main__":
    main() 