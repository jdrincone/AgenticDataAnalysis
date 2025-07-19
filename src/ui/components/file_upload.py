"""
File upload component for the application.
"""
import streamlit as st
from typing import List, Optional
from src.utils.file_utils import file_manager
from src.config.settings import config

def render_file_upload() -> Optional[List[str]]:
    """Render the file upload section."""
    st.subheader("📁 Carga de Archivos")
    
    # File uploader
    uploaded_files = st.file_uploader(
        "Sube archivos CSV",
        type=["csv"],
        accept_multiple_files=True,
        help="Selecciona uno o más archivos CSV para analizar"
    )
    
    if uploaded_files:
        # Save uploaded files
        saved_files = []
        for file in uploaded_files:
            if file_manager.validate_file_extension(file.name):
                try:
                    file_manager.save_uploaded_file(file.getbuffer(), file.name)
                    saved_files.append(file.name)
                except Exception as e:
                    st.error(f"Error al guardar {file.name}: {str(e)}")
            else:
                st.warning(f"Formato no soportado: {file.name}")
        
        if saved_files:
            st.success(f"¡{len(saved_files)} archivo(s) subido(s) exitosamente!")
            return saved_files
    
    return None

def render_file_selector() -> Optional[List[str]]:
    """Render the file selection section."""
    available_files = file_manager.get_available_files(".csv")
    
    if not available_files:
        st.info("No hay archivos CSV disponibles. Por favor, sube archivos primero.")
        return None
    
    st.subheader("📋 Selección de Archivos")
    selected_files = st.multiselect(
        "Selecciona los archivos a analizar",
        available_files,
        key="file_selector_multiselect",
        help="Elige los archivos que quieres incluir en el análisis"
    )
    
    return selected_files if selected_files else None 