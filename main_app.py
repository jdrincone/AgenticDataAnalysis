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
from src.models.data_models import InputData, DatasetInfo, AppState, ChatMessage, AnalysisResult
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
    """Initialize Streamlit session state with AppState."""
    if 'app_state' not in st.session_state:
        st.session_state.app_state = AppState()
    
    if 'agent' not in st.session_state:
        st.session_state.agent = PythonAnalysisAgent()
    
    # Load data dictionary into app state if not already loaded
    if not st.session_state.app_state.data_dictionary:
        st.session_state.app_state.data_dictionary = file_manager.load_data_dictionary()

def handle_chat_submit(user_query: str):
    """Handle chat submission using AppState."""
    print(f"handle_chat_submit called with: {user_query}")
    
    if not user_query.strip():
        print("Empty query, returning")
        return
    
    try:
        app_state = st.session_state.app_state
        print(f"App state initialized, selected files: {len(app_state.selected_files)}")
        
        if not app_state.has_selected_files():
            print("No files selected")
            st.error("No hay archivos seleccionados para analizar.")
            return
        
        # Add user message to chat history
        app_state.add_chat_message(ChatMessage(
            role="user",
            content=user_query
        ))
        print("User message added to chat history")
        
        # Prepare input data using AppState
        input_data_list = app_state.get_input_data_list(file_manager.uploads_dir)
        print(f"Input data list prepared: {len(input_data_list)} items")
        
        # Process query
        print("Calling agent.process_query...")
        result = st.session_state.agent.process_query(user_query, input_data_list)
        print(f"Agent returned result: {result}")
        
        # Add assistant response to chat history
        assistant_response = result.get('response', 'No se pudo procesar la consulta.')
        print(f"Adding assistant response to chat history: {len(assistant_response)} characters")
        
        app_state.add_chat_message(ChatMessage(
            role="assistant",
            content=assistant_response
        ))
        print(f"Chat history after adding assistant message: {len(app_state.chat_history)} messages")
        
        # Add analysis result
        analysis_result = AnalysisResult(
            query=user_query,
            response=result.get('response', ''),
            code_executed=result.get('code', ''),
            output_image_paths=result.get('output_image_paths', [])
        )
        app_state.add_analysis_result(analysis_result)
        
    except Exception as e:
        error_msg = f"Error processing query: {str(e)}"
        st.error(error_msg)
        
        # Add error message to chat history
        st.session_state.app_state.add_chat_message(ChatMessage(
            role="assistant",
            content=f"❌ {error_msg}"
        ))

def render_data_management_tab():
    """Render the data management tab using AppState."""
    st.header("📊 Gestión de Datos")
    
    app_state = st.session_state.app_state
    
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
        
        # Update app state with selected files
        if selected_files:
            app_state.selected_files = selected_files
            
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
                        
                        # Get current description from app state
                        current_description = app_state.get_dataset_description(filename)
                        
                        # Description input
                        new_descriptions[filename] = st.text_area(
                            "Descripción del dataset",
                            value=current_description,
                            key=f"description_{filename}",
                            help="Proporciona una descripción de este dataset"
                        )
                        
                        # Display existing info from data dictionary
                        if filename in app_state.data_dictionary:
                            info = app_state.data_dictionary[filename]
                            
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
                        app_state.update_dataset_description(filename, description)
                
                if file_manager.save_data_dictionary(app_state.data_dictionary):
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
    """Render the chat interface tab using AppState."""
    st.header("💬 Interfaz de Chat")
    
    app_state = st.session_state.app_state
    
    if not app_state.has_selected_files():
        st.info("Por favor, selecciona archivos para analizar en la pestaña de Gestión de Datos primero.")
        return
    
    render_chat_interface(
        agent=st.session_state.agent,
        on_submit=handle_chat_submit,
        selected_files=app_state.selected_files
    )

def render_debug_tab():
    """Render the debug tab using AppState."""
    st.header("🔍 Depuración")
    
    app_state = st.session_state.app_state
    
    # Debug controls
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("🗑️ Limpiar historial"):
            app_state.clear_chat_history()
            st.success("Historial limpiado")
    
    with col2:
        if st.button("🗑️ Limpiar resultados"):
            app_state.clear_analysis_results()
            st.success("Resultados limpiados")
    
    with col3:
        if st.button("🔄 Reiniciar estado"):
            app_state.reset()
            st.success("Estado reiniciado")
    
    # Debug information
    st.subheader("Estado de la aplicación")
    st.write(f"**Archivos seleccionados:** {len(app_state.selected_files)}")
    st.write(f"**Mensajes en historial:** {len(app_state.chat_history)}")
    st.write(f"**Resultados de análisis:** {len(app_state.analysis_results)}")
    st.write(f"**Modo debug:** {app_state.debug_mode}")
    
    # Render debug section
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
    
    # Render header
    render_header()
    
    # Main tabs
    tab1, tab2, tab3 = st.tabs(["📊 Gestión de Datos", "💬 Chat", "🔍 Debug"])
    
    with tab1:
        render_data_management_tab()
    
    with tab2:
        render_chat_tab()
    
    with tab3:
        render_debug_tab()

if __name__ == "__main__":
    main() 