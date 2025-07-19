import streamlit as st
import pandas as pd
import os
import json
from dotenv import load_dotenv
load_dotenv()
from langchain_core.messages import HumanMessage, AIMessage
from modules.backend import PythonChatbot, InputData
import pickle

# Create uploads directory if it doesn't exist
if not os.path.exists("uploads"):
    os.makedirs("uploads")

# Header profesional con emoji de IA y subtítulo
st.markdown("""
    <div style='display: flex; flex-direction: column; align-items: center; justify-content: center; margin-bottom: 2rem;'>
        <h1 style='font-size: 3rem; font-weight: 800; color: #1C8074; margin-bottom: 0.2em;'>🤖 Okuo IA DataLab</h1>
        <p style='font-size: 1.3rem; color: #444; margin-top: 0;'>Laboratorio de Análisis Inteligente de Datos</p>
    </div>
""", unsafe_allow_html=True)

with open('data_dictionary.json', 'r') as f:
    data_dictionary = json.load(f)

tab1, tab2, tab3 = st.tabs(["Gestión de Datos", "Interfaz de Chat", "Depuración"])

with tab1:
    # Selector de fuente de datos
    data_source = st.radio(
        "¿Qué tipo de datos deseas analizar?",
        ["Archivos CSV", "Base de datos"],
        horizontal=True
    )

    if data_source == "Archivos CSV":
        # Sección de carga de archivos CSV (igual que antes)
        uploaded_files = st.file_uploader("Sube archivos CSV", type="csv", accept_multiple_files=True)

        if uploaded_files:
            for file in uploaded_files:
                with open(os.path.join("uploads", file.name), "wb") as f:
                    f.write(file.getbuffer())
            st.success("¡Archivos subidos exitosamente!")

        available_files = [f for f in os.listdir("uploads") if f.endswith('.csv')]

        if available_files:
            selected_files = st.multiselect(
                "Selecciona los archivos a analizar",
                available_files,
                key="selected_files"
            )
            new_descriptions = {}
            if selected_files:
                file_tabs = st.tabs(selected_files)
                for tab, filename in zip(file_tabs, selected_files):
                    with tab:
                        try:
                            df = pd.read_csv(os.path.join("uploads", filename))
                            st.write(f"Vista previa de {filename}:")
                            st.dataframe(df.head())
                            st.subheader("Información del dataset")
                            if filename in data_dictionary:
                                info = data_dictionary[filename]
                                current_description = info.get('description', '')
                            else:
                                current_description = ''
                            new_descriptions[filename] = st.text_area(
                                "Descripción del dataset",
                                value=current_description,
                                key=f"description_{filename}",
                                help="Proporciona una descripción de este dataset"
                            )
                            if filename in data_dictionary:
                                info = data_dictionary[filename]
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
                if st.button("Guardar descripciones"):
                    for filename, description in new_descriptions.items():
                        if description:
                            if filename not in data_dictionary:
                                data_dictionary[filename] = {}
                            data_dictionary[filename]['description'] = description
                    with open('data_dictionary.json', 'w') as f:
                        json.dump(data_dictionary, f, indent=4)
                    st.success("¡Descripciones guardadas exitosamente!")
        else:
            st.info("No hay archivos CSV disponibles. Por favor, sube archivos primero.")

    elif data_source == "Base de datos":
        st.subheader("Conexión a base de datos")
        
        # Centrar el botón con CSS personalizado
        st.markdown("""
            <div style='display: flex; justify-content: center; align-items: center; margin: 2rem 0;'>
        """, unsafe_allow_html=True)
        
        # Botón grande y centrado
        if st.button("🔗 Conectar a BD", type="primary", use_container_width=True):
            st.info("Funcionalidad próximamente disponible")
        
        st.markdown("</div>", unsafe_allow_html=True)

with tab2:
    def on_submit_user_query():
        user_query = st.session_state['user_input']
        input_data_list = [
            InputData(
                variable_name=f"{file.split('.')[0]}", 
                data_path=os.path.abspath(os.path.join("uploads", file)), 
                data_description=data_dictionary.get(file, {}).get('description', '')
            ) 
            for file in selected_files
        ]
        st.session_state.visualisation_chatbot.user_sent_message(user_query, input_data=input_data_list)

    if 'selected_files' in st.session_state and st.session_state['selected_files']:
        if 'visualisation_chatbot' not in st.session_state:
            st.session_state.visualisation_chatbot = PythonChatbot()
        chat_container = st.container(height=500)
        with chat_container:
            # Mostrar historial de chat con imágenes asociadas
            for msg_index, msg in enumerate(st.session_state.visualisation_chatbot.chat_history):
                msg_col, img_col = st.columns([2, 1])
                
                with msg_col:
                    if isinstance(msg, HumanMessage):
                        st.chat_message("Tú").markdown(msg.content)
                    elif isinstance(msg, AIMessage):
                        with st.chat_message("IA"):
                            st.markdown(msg.content)

                    if isinstance(msg, AIMessage) and msg_index in st.session_state.visualisation_chatbot.output_image_paths:
                        image_paths = st.session_state.visualisation_chatbot.output_image_paths[msg_index]
                        for image_path in image_paths:
                            with open(os.path.join("images/plotly_figures/pickle", image_path), "rb") as f:
                                fig = pickle.load(f)
                            st.plotly_chart(fig, use_container_width=True)
        # Entrada de chat
        st.chat_input(placeholder="Hazme cualquier pregunta sobre tus datos", on_submit=on_submit_user_query, key='user_input')
    else:
        st.info("Por favor, selecciona archivos para analizar en la pestaña de Gestión de Datos primero.")

with tab3:
    if 'visualisation_chatbot' in st.session_state:
        st.subheader("Salidas intermedias")
        for i, output in enumerate(st.session_state.visualisation_chatbot.intermediate_outputs):
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
        st.info("Aún no hay información de depuración. Inicia una conversación para ver salidas intermedias.")