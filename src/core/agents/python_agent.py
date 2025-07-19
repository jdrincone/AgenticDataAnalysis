"""
Python analysis agent for data processing and visualization.
"""
from typing import List, Dict, Any, Optional
from pathlib import Path
import pickle
from langchain_core.messages import HumanMessage, AIMessage
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from src.config.settings import config
from src.models.data_models import InputData, AnalysisResult, ChatMessage
from src.core.graph.tools import PythonAnalysisTool
from src.utils.file_utils import file_manager

class PythonAnalysisAgent:
    """Main agent for Python-based data analysis."""
    
    def __init__(self):
        """Initialize the analysis agent."""
        self.reset_state()
        self.llm = ChatOpenAI(
            model=config.OPENAI_MODEL,
            temperature=0.1,
            api_key=config.OPENAI_API_KEY
        )
        self.python_tool = PythonAnalysisTool()
        
        # Load the main prompt
        with open(config.MAIN_PROMPT_PATH, 'r', encoding='utf-8') as f:
            self.main_prompt = f.read()
    
    def reset_state(self):
        """Reset the agent state."""
        self.chat_history: List[ChatMessage] = []
        self.intermediate_outputs: List[Dict[str, Any]] = []
        self.output_image_paths: Dict[int, List[str]] = {}
        self.analysis_results: List[AnalysisResult] = []
    
    def process_query(self, user_query: str, input_data: List[InputData], chat_history: List[ChatMessage] = None) -> Dict[str, Any]:
        """Process a user query and return analysis results."""
        try:
            print(f"Processing query: {user_query}")
            print(f"Input data: {len(input_data)} datasets")
            
            # Check if query mentions database
            database_keywords = ['base de datos', 'database', 'sql', 'tabla', 'table', 'postgresql', 'postgres']
            has_database_keywords = any(keyword in user_query.lower() for keyword in database_keywords)
            
            # Check if a table is selected in session state
            selected_table = None
            try:
                from src.ui.components.table_selector import get_selected_table
                selected_table = get_selected_table()
            except:
                pass
            
            # Decision logic: prioritize database if table is selected, otherwise use file data
            use_database = selected_table is not None or has_database_keywords
            use_files = len(input_data) > 0 and not use_database
            
            # If both files and table are selected, prioritize based on user intent
            if len(input_data) > 0 and selected_table is not None:
                if has_database_keywords:
                    use_database = True
                    use_files = False
                else:
                    # Default to files if no specific database keywords
                    use_database = False
                    use_files = True
            
            print(f"🔍 Debug - Selected table: {selected_table}")
            print(f"🔍 Debug - Has database keywords: {has_database_keywords}")
            print(f"🔍 Debug - Input data count: {len(input_data)}")
            print(f"🔍 Debug - Use database: {use_database}")
            print(f"🔍 Debug - Use files: {use_files}")
            
            if use_database:
                # Redirect to database agent
                if len(input_data) > 0:
                    print(f"🔍 Debug - Switching from files to database analysis")
                
                # Redirect to database agent
                from src.core.agents.advanced_database_agent import AdvancedDatabaseAgent
                from src.ui.components.table_selector import get_db_agent
                
                # Try to get existing agent from session state, or create new one
                db_agent = get_db_agent()
                if db_agent is None:
                    db_agent = AdvancedDatabaseAgent()
                
                # If user is asking about connection status, show it first
                if 'conectado' in user_query.lower() or 'conexión' in user_query.lower() or 'connection' in user_query.lower():
                    status = db_agent.get_connection_status()
                    if status['is_connected']:
                        response = f"✅ **Conectado a la base de datos**\n\n"
                        response += f"• **Base de datos**: {status['connection_details'].get('database', 'N/A')}\n"
                        response += f"• **Host**: {status['connection_details'].get('host', 'N/A')}\n"
                        response += f"• **Puerto**: {status['connection_details'].get('port', 'N/A')}\n"
                        response += f"• **Usuario**: {status['connection_details'].get('user', 'N/A')}\n"
                        response += f"• **Tablas disponibles**: {len(status['available_tables'])}\n\n"
                        
                        if status['available_tables']:
                            response += "**Tablas encontradas:**\n"
                            for table in status['available_tables']:
                                response += f"• {table}\n"
                        
                        return {
                            'response': response,
                            'code': '',
                            'output_image_paths': []
                        }
                    else:
                        return {
                            'response': f"❌ **No conectado a la base de datos**\n\nError: {status['error_message']}\n\nEl agente intentará conectarse automáticamente cuando hagas una pregunta sobre la base de datos.",
                            'code': '',
                            'output_image_paths': []
                        }
                
                # If a table is selected, modify the query to include the table name
                if selected_table and not any(table.lower() in user_query.lower() for table in ['production_orders', 'production_stops']):
                    user_query = f"Analiza la tabla {selected_table}: {user_query}"
                
                print(f"🔍 Debug - Selected table: {selected_table}")
                print(f"🔍 Debug - Modified query: {user_query}")
                print(f"🔍 Debug - Redirecting to database agent")
                
                result = db_agent.process_query(user_query)
                print(f"🔍 Debug - Database agent result: {result}")
                return result
            
            # Use file-based analysis
            if selected_table is not None:
                print(f"🔍 Debug - Switching from database to file analysis")
            
            # Prepare the prompt with context
            context = self._prepare_context(input_data)
            print(f"Context prepared, length: {len(context)}")
            
            # Prepare chat history context
            chat_history_context = ""
            history_to_use = chat_history if chat_history is not None else self.chat_history
            if history_to_use:
                chat_history_context = "\n**Historial de Conversación:**\n"
                for i, message in enumerate(history_to_use[-5:], 1):  # Last 5 messages
                    role = "Usuario" if message.role == "user" else "Asistente"
                    chat_history_context += f"{i}. {role}: {message.content[:200]}...\n"
                chat_history_context += "\n"
            
            # Create the full prompt
            full_prompt = f"""
{self.main_prompt}

Contexto de los datos:
{context}

{chat_history_context}

Consulta del usuario: {user_query}

**INSTRUCCIONES IMPORTANTES:**
- Si el usuario pide crear gráficas, visualizaciones, análisis estadísticos o cualquier procesamiento de datos, DEBES incluir código Python en tu respuesta.
- El código debe estar en bloques markdown con ```python al inicio y ``` al final.
- Para gráficas, usa plotly y almacena las figuras en la lista `plotly_figures`.
- Para análisis estadísticos, usa print() para mostrar los resultados.
- Si el usuario pregunta sobre preguntas anteriores, consulta el historial de conversación.
- Mantén contexto de las preguntas y respuestas anteriores.

Por favor, analiza los datos y responde a la consulta del usuario. Si necesitas ejecutar código Python, inclúyelo en tu respuesta.
"""
            print("Sending request to LLM...")
            
            # Get response from LLM
            response = self.llm.invoke(full_prompt)
            print(f"LLM response received: {len(response.content)} characters")
            
            # Check if response contains code that needs to be executed
            if "```python" in response.content:
                print("Python code detected, executing...")
                # Extract and execute Python code
                code_result = self.python_tool.run(response.content, input_data)
                print(f"Code execution result: {len(code_result)} characters")
                
                # Get updated response with execution results (without showing code to user)
                # Remove code blocks from response for user display
                import re
                clean_response = re.sub(r'```python.*?```', '', response.content, flags=re.DOTALL).strip()
                final_response = f"{clean_response}\n\n**Resultado de la ejecución:**\n{code_result}"
            else:
                print("No Python code detected")
                # Check if user is asking for visualizations or analysis
                visualization_keywords = ['gráfica', 'grafica', 'gráfico', 'grafico', 'histograma', 'dispersión', 'dispersion', 'correlación', 'correlacion', 'análisis', 'analisis', 'estadística', 'estadistica', 'distribución', 'distribucion']
                if any(keyword in user_query.lower() for keyword in visualization_keywords):
                    print("Visualization requested but no code generated, prompting for code...")
                    # Ask the LLM to generate code for visualization
                    code_prompt = f"""
El usuario pidió: "{user_query}"

Necesitas generar código Python para crear la visualización solicitada. Responde SOLO con el código Python necesario, sin explicaciones adicionales.

```python
# Código para {user_query}
"""
                    code_response = self.llm.invoke(code_prompt)
                    if "```python" in code_response.content:
                        print("Generated code for visualization, executing...")
                        code_result = self.python_tool.run(code_response.content, input_data)
                        final_response = f"{response.content}\n\n**Resultado de la ejecución:**\n{code_result}"
                    else:
                        final_response = response.content
                else:
                    final_response = response.content
            
            # Track any new images created
            new_images = self.python_tool.get_latest_images()
            print(f"New images created: {len(new_images)}")
            print(f"Image paths: {new_images}")
            
            result = {
                'response': final_response,
                'code': code_result if "```python" in response.content else None,
                'output_image_paths': new_images
            }
            
            print("Query processing completed successfully")
            return result
            
        except Exception as e:
            print(f"Error in process_query: {str(e)}")
            import traceback
            traceback.print_exc()
            return {
                'response': f"Error procesando la consulta: {str(e)}",
                'code': None,
                'output_image_paths': []
            }
    
    def _prepare_context(self, input_data: List[InputData]) -> str:
        """Prepare context information from input data."""
        context_parts = []
        
        for data in input_data:
            try:
                # Handle both file-based and database data
                if data.source == "database":
                    # Database data is already loaded as DataFrame
                    df = data.data
                    source_info = f"Base de datos: {data.name}"
                else:
                    # File-based data needs to be loaded
                    df = file_manager.load_dataframe(data.name)
                    source_info = f"Archivo: {data.name}"
                
                context_parts.append(f"""
Dataset: {data.name}
Origen: {source_info}
Descripción: {data.description}
Forma: {df.shape}
Columnas: {list(df.columns)}
Tipos de datos: {df.dtypes.to_dict()}
Primeras filas:
{df.head().to_string()}

**IMPORTANTE**: Usa '{data.name}' como nombre de la variable para acceder a este dataset en tu código Python.
""")
            except Exception as e:
                context_parts.append(f"""
Dataset: {data.name}
Origen: {data.source}
Error al cargar: {str(e)}
""")
        
        return "\n".join(context_parts)
    
    def get_chat_history(self) -> List[ChatMessage]:
        """Get the chat history."""
        return self.chat_history
    
    def get_intermediate_outputs(self) -> List[Dict[str, Any]]:
        """Get intermediate outputs from the last analysis."""
        return self.intermediate_outputs
    
    def get_output_images(self, message_index: int) -> List[str]:
        """Get output images for a specific message."""
        return self.output_image_paths.get(message_index, [])
    
    def load_plotly_figure(self, image_path: str):
        """Load a plotly figure from file."""
        try:
            # Use absolute path from config
            figure_path = config.PLOTLY_FIGURES_DIR / image_path
            with open(figure_path, "rb") as f:
                return pickle.load(f)
        except Exception as e:
            print(f"Error loading plotly figure {image_path}: {e}")
            return None 