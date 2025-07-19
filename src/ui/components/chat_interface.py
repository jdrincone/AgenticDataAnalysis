"""
Chat interface component for the application.
"""
import streamlit as st
from typing import List, Callable
from src.models.data_models import ChatMessage
from src.core.agents.python_agent import PythonAnalysisAgent
from src.ui.components.pdf_export import render_pdf_export_button

def render_chat_interface(
    agent: PythonAnalysisAgent,
    on_submit: Callable[[str], None],
    selected_files: List[str]
):
    """Render the chat interface."""
    st.subheader("💬 Interfaz de Chat")
    
    if not selected_files:
        st.info("Por favor, selecciona archivos para analizar en la pestaña de Gestión de Datos primero.")
        return
    
    # Chat container
    chat_container = st.container(height=500)
    
    with chat_container:
        # Display chat history from app state
        chat_history = st.session_state.app_state.chat_history
        print(f"Chat interface - History length: {len(chat_history)}")
        
        # Debug: Show available analysis results
        analysis_results = st.session_state.app_state.analysis_results
        print(f"Available analysis results: {len(analysis_results)}")
        for i, result in enumerate(analysis_results):
            print(f"Analysis {i}: {len(result.output_image_paths)} images")
        
        for msg_index, msg in enumerate(chat_history):
            print(f"Message {msg_index}: role={msg.role}, content_length={len(msg.content)}")
            if msg.role == "user":
                st.chat_message("Tú").markdown(msg.content)
            else:
                with st.chat_message("IA"):
                    st.markdown(msg.content)
                
                # Display associated images from analysis results
                # Find the corresponding analysis result for this assistant message
                analysis_index = (msg_index - 1) // 2  # Each analysis corresponds to a user-assistant pair
                if analysis_index >= 0 and analysis_index < len(st.session_state.app_state.analysis_results):
                    analysis_result = st.session_state.app_state.analysis_results[analysis_index]
                    # Display images for this analysis
                    if analysis_result.output_image_paths:
                        print(f"Found {len(analysis_result.output_image_paths)} images for analysis {msg_index}")
                        
                        # Use a counter to ensure unique keys
                        image_counter = 0
                        displayed_images = set()  # Track displayed images to avoid duplicates
                        
                        for image_path in analysis_result.output_image_paths:
                            # Skip if already displayed
                            if image_path in displayed_images:
                                continue
                                
                            try:
                                # Load and display the plotly figure
                                import pickle
                                from src.config.settings import config
                                figure_path = config.PLOTLY_FIGURES_DIR / image_path
                                print(f"Loading figure from: {figure_path}")
                                
                                with open(figure_path, "rb") as f:
                                    fig = pickle.load(f)
                                
                                # Create unique key with counter
                                unique_key = f"chart_{msg_index}_{image_counter}_{image_path.replace('.pickle', '')}"
                                st.plotly_chart(fig, use_container_width=True, key=unique_key)
                                
                                print(f"Displayed figure: {image_path}")
                                displayed_images.add(image_path)
                                image_counter += 1
                                
                            except Exception as e:
                                print(f"Error loading figure {image_path}: {e}")
                                # Don't show error in frontend, just log it
                                continue
                    else:
                        print(f"No images found for analysis {analysis_index}")
                else:
                    print(f"No analysis result found for message {msg_index}")
    
    # Chat input
    st.chat_input(
        placeholder="Hazme cualquier pregunta sobre tus datos",
        on_submit=lambda: on_submit(st.session_state.get('user_input', '')),
        key='user_input'
    )
    
    # PDF Export section
    if chat_history:
        st.markdown("---")
        render_pdf_export_button()

def render_debug_section(agent: PythonAnalysisAgent):
    """Render the debug section with intermediate outputs."""
    st.subheader("🔍 Salidas Intermedias")
    
    intermediate_outputs = agent.get_intermediate_outputs()
    
    if not intermediate_outputs:
        st.info("Aún no hay información de depuración. Inicia una conversación para ver salidas intermedias.")
        return
    
    for i, output in enumerate(intermediate_outputs):
        with st.expander(f"Paso {i+1}"):
            if 'thought' in output:
                st.markdown("### Proceso de razonamiento")
                st.markdown(output['thought'])
            
            if 'code' in output:
                st.markdown("### Código")
                st.code(output['code'], language="python")
            
            if 'output' in output:
                st.markdown("### Salida")
                st.text(output['output'])
            else:
                st.markdown("### Salida")
                st.text(output) 