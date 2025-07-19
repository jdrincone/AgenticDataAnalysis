"""
Table selector component for database analysis.
"""
import streamlit as st
from typing import List, Optional
from src.core.agents.advanced_database_agent import AdvancedDatabaseAgent
from src.config.settings import DB_CONFIG


def render_table_selector() -> Optional[str]:
    """Render table selector and return selected table name."""
    st.subheader("🗄️ Selección de Tabla para Análisis")
    
    # Get or create database agent from session state
    if 'db_agent' not in st.session_state:
        st.session_state.db_agent = AdvancedDatabaseAgent()
    
    db_agent = st.session_state.db_agent
    
    # Get connection status
    with st.spinner("Conectando a la base de datos..."):
        status = db_agent.get_connection_status()
    
    if not status['is_connected']:
        st.error("❌ No se pudo conectar a la base de datos")
        
        # Show detailed error information
        if status.get('error_message'):
            with st.expander("🔍 Detalles del Error", expanded=False):
                st.error(f"Error: {status['error_message']}")
                st.info("**Posibles causas:**")
                st.info("• La base de datos no está disponible")
                st.info("• Credenciales incorrectas")
                st.info("• Problemas de red")
                st.info("• Firewall bloqueando la conexión")
        
        st.info("💡 **Solución:** El agente intentará conectarse automáticamente cuando hagas preguntas sobre la base de datos.")
        
        # Show connection details for debugging
        with st.expander("⚙️ Configuración de Conexión", expanded=False):
            st.write("**Parámetros de conexión:**")
            st.write(f"• Host: {DB_CONFIG['host']}")
            st.write(f"• Puerto: {DB_CONFIG['port']}")
            st.write(f"• Base de datos: {DB_CONFIG['dbname']}")
            st.write(f"• Usuario: {DB_CONFIG['user']}")
        
        return None
    
    # Show connection info
    with st.expander("ℹ️ Información de Conexión", expanded=False):
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Base de Datos", status['connection_details'].get('database', 'N/A'))
        with col2:
            st.metric("Host", status['connection_details'].get('host', 'N/A'))
        with col3:
            st.metric("Puerto", status['connection_details'].get('port', 'N/A'))
        with col4:
            st.metric("Usuario", status['connection_details'].get('user', 'N/A'))
    
    # Get available tables
    tables = status['available_tables']
    
    if not tables:
        st.warning("⚠️ No se encontraron tablas en la base de datos")
        return None
    
    # Table selection
    st.write("**Selecciona la tabla que deseas analizar:**")
    
    # Create table info for selection
    table_options = []
    for table in tables:
        table_info = db_agent.get_table_info(table)
        if table_info:
            description = f"{table} ({table_info['row_count']:,} filas, {table_info['column_count']} columnas)"
            table_options.append((table, description))
        else:
            table_options.append((table, table))
    
    # Create selection box
    selected_table = st.selectbox(
        "Tabla para análisis:",
        options=[opt[0] for opt in table_options],
        format_func=lambda x: next(opt[1] for opt in table_options if opt[0] == x),
        key="table_selector"
    )
    
    if selected_table:
        # Show detailed table info
        table_info = db_agent.get_table_info(selected_table)
        if table_info:
            st.success(f"✅ Tabla seleccionada: **{selected_table}**")
            
            # Show table details
            with st.expander(f"📋 Detalles de la tabla {selected_table}", expanded=False):
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Filas", f"{table_info['row_count']:,}")
                with col2:
                    st.metric("Columnas", table_info['column_count'])
                with col3:
                    st.metric("Tabla", selected_table)
                
                # Show columns
                st.write("**Columnas disponibles:**")
                for col in table_info['columns']:
                    st.write(f"• **{col['column_name']}** ({col['data_type']}) - {'NULL' if col['is_nullable'] == 'YES' else 'NOT NULL'}")
        
        # Store selected table in session state
        st.session_state.selected_table = selected_table
        
        return selected_table
    
    return None


def get_selected_table() -> Optional[str]:
    """Get the currently selected table from session state."""
    return st.session_state.get('selected_table', None)


def get_db_agent() -> Optional[AdvancedDatabaseAgent]:
    """Get the database agent from session state."""
    return st.session_state.get('db_agent', None) 