"""
Main application entry point for Okuo IA DataLab.
"""
import streamlit as st
import os
import sys
from pathlib import Path

# Add src to path for imports
sys.path.append(str(Path(__file__).parent / "src"))

from src.config.settings import config
from src.utils.file_utils import file_manager
from src.core.agents.python_agent import PythonAnalysisAgent
from src.models.data_models import InputData, DatasetInfo
from src.ui.components.header import render_header
from src.ui.components.file_upload import render_file_upload, render_file_selector
from src.ui.components.chat_interface import render_chat_interface, render_debug_section

def load_css():
    """Load custom CSS styles."""
    css_file = Path(__file__).parent / "assets" / "css" / "styles.css"
    if css_file.exists():
        with open(css_file, 'r') as f:
            st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

def initialize_session_state():
    """Initialize Streamlit session state."""
    if 'agent' not in st.session_state:
        st.session_state.agent = PythonAnalysisAgent()
    
    if 'data_dictionary' not in st.session_state:
        st.session_state.data_dictionary = file_manager.load_data_dictionary()

def handle_chat_submit(user_query: str):
    """Handle chat submission."""
    if not user_query.strip():
        return
    
    try:
        # Get selected files from the widget's session state
        selected_files = st.session_state.get('selected_files', [])
        
        if not selected_files:
            st.error("No hay archivos seleccionados para analizar.")
            return
        
        # Prepare input data
        input_data_list = [
            InputData(
                variable_name=f"{file.split('.')[0]}", 
                data_path=file_manager.uploads_dir / file, 
                data_description=st.session_state.data_dictionary.get(file, {}).get('description', '')
            ) 
            for file in selected_files
        ]
        
        # Process query
        result = st.session_state.agent.process_query(user_query, input_data_list)
        
        # Note: st.rerun() is not needed here as Streamlit will automatically
        # update the UI when the session state changes
        
    except Exception as e:
        st.error(f"Error processing query: {str(e)}")

def render_data_management_tab():
    """Render the data management tab."""
    st.header("📊 Gestión de Datos")
    
    # Data source selector
    data_source = st.radio(
        "¿Qué tipo de datos deseas analizar?",
        ["Archivos CSV", "Base de datos"],
        horizontal=True
    )
    
    if data_source == "Archivos CSV":
        # File upload section
        uploaded_files = render_file_upload()
        
        # File selection section
        selected_files = render_file_selector()
        
        # Use selected_files directly from the widget
        if selected_files:
            # File preview tabs
            file_tabs = st.tabs(selected_files)
            new_descriptions = {}
            
            for tab, filename in zip(file_tabs, selected_files):
                with tab:
                    try:
                        # Load and display dataframe
                        df = file_manager.load_dataframe(filename)
                        st.write(f"Vista previa de {filename}:")
                        st.dataframe(df.head())
                        
                        # Dataset information
                        st.subheader("Información del dataset")
                        
                        # Get current description
                        current_description = st.session_state.data_dictionary.get(filename, {}).get('description', '')
                        
                        # Description input
                        new_descriptions[filename] = st.text_area(
                            "Descripción del dataset",
                            value=current_description,
                            key=f"description_{filename}",
                            help="Proporciona una descripción de este dataset"
                        )
                        
                        # Display existing info
                        if filename in st.session_state.data_dictionary:
                            info = st.session_state.data_dictionary[filename]
                            
                            if 'coverage' in info:
                                st.write(f"**Cobertura:** {info['coverage']}")
                            
                            if 'features' in info:
                                st.write("**Características:**")
                                for feature in info['features']:
                                    st.write(f"- {feature}")
                            
                            if 'usage' in info:
                                st.write("**Uso:**")
                                if isinstance(info['usage'], list):
                                    for use in info['usage']:
                                        st.write(f"- {use}")
                                else:
                                    st.write(f"- {info['usage']}")
                            
                            if 'linkage' in info:
                                st.write(f"**Vinculación:** {info['linkage']}")
                    
                    except Exception as e:
                        st.error(f"Error al cargar {filename}: {str(e)}")
            
            # Save descriptions button
            if st.button("💾 Guardar descripciones"):
                for filename, description in new_descriptions.items():
                    if description:
                        if filename not in st.session_state.data_dictionary:
                            st.session_state.data_dictionary[filename] = {}
                        st.session_state.data_dictionary[filename]['description'] = description
                
                if file_manager.save_data_dictionary(st.session_state.data_dictionary):
                    st.success("¡Descripciones guardadas exitosamente!")
                else:
                    st.error("Error al guardar las descripciones")
    
    elif data_source == "Base de datos":
        st.subheader("Conexión a base de datos")
        st.markdown("""
            <div style='display: flex; justify-content: center; align-items: center; margin: 2rem 0;'>
        """, unsafe_allow_html=True)
        
        if st.button("🔗 Conectar a BD", type="primary", use_container_width=True):
            st.info("Funcionalidad próximamente disponible")
        
        st.markdown("</div>", unsafe_allow_html=True)

def render_chat_tab():
    """Render the chat interface tab."""
    st.header("💬 Interfaz de Chat")
    
    # Get selected files from the widget's session state
    selected_files = st.session_state.get('selected_files', [])
    
    if not selected_files:
        st.info("Por favor, selecciona archivos para analizar en la pestaña de Gestión de Datos primero.")
        return
    
    render_chat_interface(
        agent=st.session_state.agent,
        on_submit=handle_chat_submit,
        selected_files=selected_files
    )

def render_debug_tab():
    """Render the debug tab."""
    st.header("🔍 Depuración")
    render_debug_section(st.session_state.agent)

def main():
    """Main application function."""
    # Page configuration
    st.set_page_config(
        page_title=config.APP_NAME,
        page_icon="🤖",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Load CSS
    load_css()
    
    # Initialize session state
    initialize_session_state()
    
    # Validate configuration
    try:
        config.validate_config()
    except ValueError as e:
        st.error(f"Configuration Error: {e}")
        st.info("Please set your OPENAI_API_KEY in the .env file")
        st.stop()
    
    # Render header
    render_header()
    
    # Main tabs
    tab1, tab2, tab3 = st.tabs(["📊 Gestión de Datos", "💬 Interfaz de Chat", "🔍 Depuración"])
    
    with tab1:
        render_data_management_tab()
    
    with tab2:
        render_chat_tab()
    
    with tab3:
        render_debug_tab()

if __name__ == "__main__":
    main() 