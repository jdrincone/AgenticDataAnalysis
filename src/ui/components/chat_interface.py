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
        # Display chat history
        chat_history = agent.get_chat_history()
        
        for msg_index, msg in enumerate(chat_history):
            if msg.sender == "user":
                st.chat_message("Tú").markdown(msg.content)
            else:
                with st.chat_message("IA"):
                    st.markdown(msg.content)
                
                # Display associated images
                image_paths = agent.get_output_images(msg_index)
                for image_path in image_paths:
                    fig = agent.load_plotly_figure(image_path)
                    if fig:
                        st.plotly_chart(fig, use_container_width=True)
    
    # Chat input
    st.chat_input(
        placeholder="Hazme cualquier pregunta sobre tus datos",
        on_submit=lambda: on_submit(st.session_state.get('user_input', '')),
        key='user_input'
    )
    
    # PDF Export section
    if chat_history:
        st.markdown("---")
        render_pdf_export_button(agent)

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