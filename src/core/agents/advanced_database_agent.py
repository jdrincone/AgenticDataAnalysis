"""
Advanced Database Analysis Agent for PostgreSQL.
This agent can connect directly to databases and perform sophisticated analysis.
"""
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import seaborn as sns
import matplotlib.pyplot as plt
from typing import Dict, Any, List, Optional, Tuple
import psycopg2
from psycopg2 import sql
from psycopg2.extras import RealDictCursor
from sqlalchemy import create_engine, text
import pickle
from pathlib import Path
import sys
import os

# Add src to path for imports
sys.path.append(str(Path(__file__).parent.parent.parent))

from src.config.settings import DB_CONFIG, config
# Load the expert data analyst prompt
def load_expert_prompt():
    """Load the expert data analyst prompt."""
    prompt_path = Path(__file__).parent.parent / "prompts" / "data_analyst_prompt.md"
    try:
        with open(prompt_path, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        print(f"Error loading expert prompt: {str(e)}")
        return "Eres un analista de datos experto."


class AdvancedDatabaseAgent:
    """Advanced agent for PostgreSQL database analysis with sophisticated visualizations."""
    
    def __init__(self):
        self.connection = None
        self.cursor = None
        self.engine = None
        self.is_connected = False
        self.expert_prompt = load_expert_prompt()
        
        # Try to connect automatically
        self.connect()
        
    def connect(self) -> bool:
        """Establish connection to PostgreSQL database."""
        try:
            print(f"Attempting to connect to database...")
            print(f"Host: {DB_CONFIG['host']}")
            print(f"Port: {DB_CONFIG['port']}")
            print(f"Database: {DB_CONFIG['dbname']}")
            print(f"User: {DB_CONFIG['user']}")
            
            # Create psycopg2 connection for metadata queries
            self.connection = psycopg2.connect(
                dbname=DB_CONFIG["dbname"],
                user=DB_CONFIG["user"],
                password=DB_CONFIG["password"],
                host=DB_CONFIG["host"],
                port=DB_CONFIG["port"],
                connect_timeout=10
            )
            print("✅ psycopg2 connection established")
            
            self.cursor = self.connection.cursor(cursor_factory=RealDictCursor)
            print("✅ Cursor created")
            
            # Create SQLAlchemy engine for pandas operations
            connection_string = f"postgresql://{DB_CONFIG['user']}:{DB_CONFIG['password']}@{DB_CONFIG['host']}:{DB_CONFIG['port']}/{DB_CONFIG['dbname']}"
            print(f"Creating SQLAlchemy engine with: {connection_string.replace(DB_CONFIG['password'], '***')}")
            
            self.engine = create_engine(connection_string, connect_args={"connect_timeout": 10})
            print("✅ SQLAlchemy engine created")
            
            # Test the connection
            with self.engine.connect() as conn:
                result = conn.execute(text("SELECT 1"))
                print("✅ Connection test successful")
            
            self.is_connected = True
            print("✅ Database connection successful")
            return True
            
        except Exception as e:
            print(f"❌ Error connecting to database: {str(e)}")
            print(f"Error type: {type(e).__name__}")
            import traceback
            traceback.print_exc()
            self.is_connected = False
            return False
    
    def disconnect(self):
        """Close database connection."""
        if self.cursor:
            self.cursor.close()
        if self.connection:
            self.connection.close()
        if self.engine:
            self.engine.dispose()
        self.is_connected = False
    
    def get_connection_status(self) -> Dict[str, Any]:
        """Get detailed connection status information."""
        status = {
            'is_connected': self.is_connected,
            'connection_details': {},
            'available_tables': [],
            'error_message': None
        }
        
        # If not connected, try to connect
        if not self.is_connected:
            print("🔄 Attempting to reconnect to database...")
            if self.connect():
                print("✅ Reconnection successful")
            else:
                status['error_message'] = 'No se pudo conectar a la base de datos'
                return status
        
        try:
            # Test connection by getting tables
            tables = self.get_tables()
            status['available_tables'] = tables
            
            # Get connection details
            if self.connection:
                status['connection_details'] = {
                    'database': self.connection.info.dbname,
                    'host': self.connection.info.host,
                    'port': self.connection.info.port,
                    'user': self.connection.info.user
                }
            
            return status
            
        except Exception as e:
            status['is_connected'] = False
            status['error_message'] = str(e)
            return status
    
    def get_tables(self) -> List[str]:
        """Get list of available tables in the database."""
        if not self.is_connected:
            return []
        
        try:
            query = """
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_type = 'BASE TABLE'
                ORDER BY table_name
            """
            self.cursor.execute(query)
            tables = [row['table_name'] for row in self.cursor.fetchall()]
            return tables
        except Exception as e:
            print(f"Error getting tables: {str(e)}")
            return []
    
    def get_table_info(self, table_name: str) -> Dict[str, Any]:
        """Get detailed information about a specific table."""
        if not self.is_connected:
            return {}
        
        try:
            # Get column information
            column_query = """
                SELECT 
                    column_name,
                    data_type,
                    is_nullable,
                    column_default
                FROM information_schema.columns 
                WHERE table_name = %s 
                AND table_schema = 'public'
                ORDER BY ordinal_position
            """
            self.cursor.execute(column_query, (table_name,))
            columns = [dict(row) for row in self.cursor.fetchall()]
            
            # Get row count
            count_query = sql.SQL("SELECT COUNT(*) as count FROM {}").format(
                sql.Identifier(table_name)
            )
            self.cursor.execute(count_query)
            row_count = self.cursor.fetchone()['count']
            
            return {
                'table_name': table_name,
                'columns': columns,
                'row_count': row_count,
                'column_count': len(columns)
            }
        except Exception as e:
            print(f"Error getting table info for {table_name}: {str(e)}")
            return {}
    
    def execute_query(self, query: str) -> Optional[pd.DataFrame]:
        """Execute a SQL query and return results as DataFrame."""
        if not self.is_connected:
            return None
        
        try:
            df = pd.read_sql_query(text(query), self.engine)
            return df
        except Exception as e:
            print(f"Error executing query: {str(e)}")
            return None
    
    def create_advanced_visualization(self, df: pd.DataFrame, viz_type: str, **kwargs) -> Optional[go.Figure]:
        """Create advanced visualizations based on data and type."""
        try:
            if viz_type == "correlation_heatmap":
                return self._create_correlation_heatmap(df)
            elif viz_type == "distribution_analysis":
                return self._create_distribution_analysis(df, **kwargs)
            elif viz_type == "time_series_analysis":
                return self._create_time_series_analysis(df, **kwargs)
            elif viz_type == "multi_metric_dashboard":
                return self._create_multi_metric_dashboard(df, **kwargs)
            elif viz_type == "trend_analysis":
                return self._create_trend_analysis(df, **kwargs)
            elif viz_type == "comparative_analysis":
                return self._create_comparative_analysis(df, **kwargs)
            else:
                return self._create_default_visualization(df, viz_type, **kwargs)
        except Exception as e:
            print(f"Error creating visualization {viz_type}: {str(e)}")
            return None
    
    def _create_correlation_heatmap(self, df: pd.DataFrame) -> go.Figure:
        """Create correlation heatmap for numerical columns with corporate colors."""
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        if len(numeric_cols) < 2:
            return None
        
        corr_matrix = df[numeric_cols].corr()
        
        fig = go.Figure(data=go.Heatmap(
            z=corr_matrix.values,
            x=corr_matrix.columns,
            y=corr_matrix.columns,
            colorscale=[
                [0, '#d32f2f'],    # Rojo para correlaciones negativas
                [0.5, '#fafafa'],  # Blanco para correlación cero
                [1, '#2e7d32']     # Verde para correlaciones positivas
            ],
            zmid=0,
            text=np.round(corr_matrix.values, 2),
            texttemplate="%{text}",
            textfont={"size": 10, "color": "#1f4e79"},
            hoverongaps=False
        ))
        
        fig.update_layout(
            title={
                'text': "Matriz de Correlación - Análisis de Variables",
                'font': {'size': 18, 'color': '#1f4e79'}
            },
            xaxis_title="Variables",
            yaxis_title="Variables",
            height=600,
            plot_bgcolor='white',
            paper_bgcolor='white',
            font={'color': '#1f4e79'}
        )
        
        return fig
    
    def _create_distribution_analysis(self, df: pd.DataFrame, column: str = None) -> go.Figure:
        """Create distribution analysis for a column."""
        if column is None:
            numeric_cols = df.select_dtypes(include=[np.number]).columns
            if len(numeric_cols) == 0:
                return None
            column = numeric_cols[0]
        
        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=('Histogram', 'Box Plot', 'Q-Q Plot', 'Statistics'),
            specs=[[{"secondary_y": False}, {"secondary_y": False}],
                   [{"secondary_y": False}, {"secondary_y": False}]]
        )
        
        # Histogram
        fig.add_trace(
            go.Histogram(x=df[column], nbinsx=30, name="Histogram"),
            row=1, col=1
        )
        
        # Box plot
        fig.add_trace(
            go.Box(y=df[column], name="Box Plot"),
            row=1, col=2
        )
        
        # Q-Q plot (simplified)
        sorted_data = np.sort(df[column].dropna())
        theoretical_quantiles = np.quantile(sorted_data, np.linspace(0, 1, len(sorted_data)))
        
        fig.add_trace(
            go.Scatter(x=theoretical_quantiles, y=sorted_data, mode='markers', name="Q-Q Plot"),
            row=2, col=1
        )
        
        # Statistics table
        stats_text = f"""
        Mean: {df[column].mean():.2f}<br>
        Median: {df[column].median():.2f}<br>
        Std: {df[column].std():.2f}<br>
        Min: {df[column].min():.2f}<br>
        Max: {df[column].max():.2f}<br>
        Skewness: {df[column].skew():.2f}<br>
        Kurtosis: {df[column].kurtosis():.2f}
        """
        
        fig.add_trace(
            go.Scatter(x=[0], y=[0], mode='text', text=[stats_text], textposition='middle center'),
            row=2, col=2
        )
        
        fig.update_layout(
            title={
                'text': f"Análisis de Distribución: {column}",
                'font': {'size': 18, 'color': '#1f4e79'}
            },
            height=800,
            showlegend=False,
            plot_bgcolor='white',
            paper_bgcolor='white',
            font={'color': '#1f4e79'}
        )
        
        return fig
    
    def _create_time_series_analysis(self, df: pd.DataFrame, date_column: str = None, value_column: str = None) -> go.Figure:
        """Create time series analysis."""
        if date_column is None or value_column is None:
            return None
        
        # Convert to datetime if needed
        df[date_column] = pd.to_datetime(df[date_column])
        df_sorted = df.sort_values(date_column)
        
        fig = make_subplots(
            rows=3, cols=1,
            subplot_titles=('Time Series', 'Moving Average', 'Seasonal Decomposition'),
            vertical_spacing=0.1
        )
        
        # Time series
        fig.add_trace(
            go.Scatter(x=df_sorted[date_column], y=df_sorted[value_column], mode='lines', name="Original"),
            row=1, col=1
        )
        
        # Moving average
        window = min(30, len(df_sorted) // 4)
        if window > 1:
            ma = df_sorted[value_column].rolling(window=window).mean()
            fig.add_trace(
                go.Scatter(x=df_sorted[date_column], y=ma, mode='lines', name=f"MA({window})"),
                row=2, col=1
            )
        
        # Seasonal decomposition (simplified)
        # Calculate trend using moving average
        trend = df_sorted[value_column].rolling(window=window).mean()
        detrended = df_sorted[value_column] - trend
        
        fig.add_trace(
            go.Scatter(x=df_sorted[date_column], y=detrended, mode='lines', name="Detrended"),
            row=3, col=1
        )
        
        fig.update_layout(
            title={
                'text': f"Análisis de Series Temporales: {value_column} vs {date_column}",
                'font': {'size': 18, 'color': '#1f4e79'}
            },
            height=900,
            showlegend=True,
            plot_bgcolor='white',
            paper_bgcolor='white',
            font={'color': '#1f4e79'}
        )
        
        return fig
    
    def _create_multi_metric_dashboard(self, df: pd.DataFrame, metrics: List[str] = None) -> go.Figure:
        """Create multi-metric dashboard."""
        if metrics is None:
            numeric_cols = df.select_dtypes(include=[np.number]).columns[:4]
        else:
            numeric_cols = [col for col in metrics if col in df.columns]
        
        if len(numeric_cols) == 0:
            return None
        
        n_metrics = len(numeric_cols)
        cols = min(2, n_metrics)
        rows = (n_metrics + cols - 1) // cols
        
        fig = make_subplots(
            rows=rows, cols=cols,
            subplot_titles=numeric_cols,
            specs=[[{"type": "indicator"} for _ in range(cols)] for _ in range(rows)]
        )
        
        for i, col in enumerate(numeric_cols):
            row = i // cols + 1
            col_idx = i % cols + 1
            
            fig.add_trace(
                go.Indicator(
                    mode="gauge+number+delta",
                    value=df[col].mean(),
                    title={'text': f"Avg {col}"},
                    delta={'reference': df[col].median()},
                    gauge={'axis': {'range': [df[col].min(), df[col].max()]},
                           'bar': {'color': "darkblue"},
                           'steps': [{'range': [df[col].min(), df[col].quantile(0.25)], 'color': "lightgray"},
                                    {'range': [df[col].quantile(0.25), df[col].quantile(0.75)], 'color': "gray"}],
                           'threshold': {'line': {'color': "red", 'width': 4},
                                        'thickness': 0.75,
                                        'value': df[col].quantile(0.9)}}),
                row=row, col=col_idx
            )
        
        fig.update_layout(
            title={
                'text': "Dashboard de Métricas Clave",
                'font': {'size': 18, 'color': '#1f4e79'}
            },
            height=300 * rows,
            plot_bgcolor='white',
            paper_bgcolor='white',
            font={'color': '#1f4e79'}
        )
        
        return fig
    
    def _create_trend_analysis(self, df: pd.DataFrame, date_column: str = None, value_column: str = None) -> go.Figure:
        """Create simple line chart for time series analysis."""
        if date_column is None or value_column is None:
            return None
        
        try:
            # Convert date column to datetime
            df_copy = df.copy()
            df_copy[date_column] = pd.to_datetime(df_copy[date_column])
            df_sorted = df_copy.sort_values(date_column)
            
            # Remove any NaN values
            df_clean = df_sorted.dropna(subset=[date_column, value_column])
            
            if len(df_clean) == 0:
                return None
            
            fig = go.Figure()
            
            # Create line chart with corporate colors
            fig.add_trace(go.Scatter(
                x=df_clean[date_column], 
                y=df_clean[value_column], 
                mode='lines+markers', 
                name=value_column,
                line=dict(color='#1C8074', width=3),
                marker=dict(color='#1C8074', size=6),
                hovertemplate='<b>Fecha:</b> %{x}<br><b>Valor:</b> %{y:.2f}<extra></extra>'
            ))
            
            # Add trend line if enough data points
            if len(df_clean) > 5:
                x_numeric = np.arange(len(df_clean))
                z = np.polyfit(x_numeric, df_clean[value_column], 1)
                p = np.poly1d(z)
                trend_values = p(x_numeric)
                
                fig.add_trace(go.Scatter(
                    x=df_clean[date_column], 
                    y=trend_values, 
                    mode='lines', 
                    name='Tendencia',
                    line=dict(color='#D32F2F', width=2, dash='dash'),
                    hovertemplate='<b>Tendencia:</b> %{y:.2f}<extra></extra>'
                ))
            
            fig.update_layout(
                title={
                    'text': f"Evolución Temporal: {value_column}",
                    'font': {'size': 18, 'color': '#1f4e79'}
                },
                xaxis_title="Fecha",
                yaxis_title=value_column,
                height=500,
                plot_bgcolor='white',
                paper_bgcolor='white',
                font={'color': '#1f4e79'},
                hovermode='x unified',
                legend=dict(
                    orientation="h",
                    yanchor="bottom",
                    y=1.02,
                    xanchor="right",
                    x=1
                )
            )
            
            return fig
            
        except Exception as e:
            print(f"Error creating trend analysis: {str(e)}")
            return None
    
    def _create_comparative_analysis(self, df: pd.DataFrame, group_column: str = None, value_column: str = None) -> go.Figure:
        """Create comparative analysis between groups."""
        if group_column is None or value_column is None:
            return None
        
        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=('Box Plot by Group', 'Violin Plot', 'Bar Chart', 'Statistics by Group'),
            specs=[[{"secondary_y": False}, {"secondary_y": False}],
                   [{"secondary_y": False}, {"secondary_y": False}]]
        )
        
        groups = df[group_column].unique()
        
        # Box plot
        for group in groups:
            group_data = df[df[group_column] == group][value_column]
            fig.add_trace(
                go.Box(y=group_data, name=str(group)),
                row=1, col=1
            )
        
        # Violin plot
        for group in groups:
            group_data = df[df[group_column] == group][value_column]
            fig.add_trace(
                go.Violin(y=group_data, name=str(group)),
                row=1, col=2
            )
        
        # Bar chart (mean by group)
        group_means = df.groupby(group_column)[value_column].mean()
        fig.add_trace(
            go.Bar(x=group_means.index, y=group_means.values, name="Mean"),
            row=2, col=1
        )
        
        # Statistics table
        stats_text = ""
        for group in groups:
            group_data = df[df[group_column] == group][value_column]
            stats_text += f"<b>{group}:</b><br>"
            stats_text += f"Count: {len(group_data)}<br>"
            stats_text += f"Mean: {group_data.mean():.2f}<br>"
            stats_text += f"Std: {group_data.std():.2f}<br><br>"
        
        fig.add_trace(
            go.Scatter(x=[0], y=[0], mode='text', text=[stats_text], textposition='middle center'),
            row=2, col=2
        )
        
        fig.update_layout(
            title={
                'text': f"Análisis Comparativo: {value_column} por {group_column}",
                'font': {'size': 18, 'color': '#1f4e79'}
            },
            height=800,
            showlegend=True,
            plot_bgcolor='white',
            paper_bgcolor='white',
            font={'color': '#1f4e79'}
        )
        
        return fig
    
    def _create_default_visualization(self, df: pd.DataFrame, viz_type: str, **kwargs) -> go.Figure:
        """Create default visualization based on data types."""
        try:
            if viz_type == "scatter" and len(df.columns) >= 2:
                return px.scatter(df, x=df.columns[0], y=df.columns[1], title="Scatter Plot")
            elif viz_type == "histogram" and len(df.columns) >= 1:
                return px.histogram(df, x=df.columns[0], title="Histogram")
            elif viz_type == "bar" and len(df.columns) >= 1:
                return px.bar(df, x=df.columns[0], title="Bar Chart")
            elif viz_type == "line" and len(df.columns) >= 2:
                return px.line(df, x=df.columns[0], y=df.columns[1], title="Line Chart")
            else:
                # Default to correlation heatmap for numerical data
                return self._create_correlation_heatmap(df)
        except Exception as e:
            print(f"Error in default visualization: {str(e)}")
            return None
    
    def save_visualization(self, fig: go.Figure, filename: str) -> str:
        """Save visualization to file and return path."""
        try:
            # Ensure directory exists
            config.PLOTLY_FIGURES_DIR.mkdir(parents=True, exist_ok=True)
            
            filepath = config.PLOTLY_FIGURES_DIR / filename
            
            # Save as pickle for later loading
            with open(filepath, 'wb') as f:
                pickle.dump(fig, f)
            
            return filename
        except Exception as e:
            print(f"Error saving visualization: {str(e)}")
            return ""
    
    def process_query(self, query: str) -> Dict[str, Any]:
        """Process a natural language query and return analysis results."""
        try:
            # Connect to database if not connected
            if not self.is_connected:
                if not self.connect():
                    return {
                        'response': '❌ Error: No se pudo conectar a la base de datos. Verifica la configuración.',
                        'code': '',
                        'output_image_paths': []
                    }
            
            # Parse query to determine action
            query_lower = query.lower()
            
            # Get available tables
            tables = self.get_tables()
            
            if 'tablas' in query_lower or 'tables' in query_lower:
                return self._handle_tables_query(tables)
            
            # Check if query mentions specific table
            mentioned_table = None
            for table in tables:
                if table.lower() in query_lower:
                    mentioned_table = table
                    break
            
            if mentioned_table:
                return self._handle_expert_table_analysis(query, mentioned_table)
            
            # Check if it's a SQL query
            if 'select' in query_lower or 'sql' in query_lower:
                return self._handle_sql_query(query)
            
            # Default: try to analyze all tables
            return self._handle_general_analysis(query, tables)
            
        except Exception as e:
            return {
                'response': f'❌ Error procesando la consulta: {str(e)}',
                'code': '',
                'output_image_paths': []
            }
    
    def _handle_tables_query(self, tables: List[str]) -> Dict[str, Any]:
        """Handle query about available tables."""
        if not tables:
            response = "❌ No se encontraron tablas en la base de datos."
        else:
            response = f"📋 **Tablas disponibles en la base de datos:**\n\n"
            for table in tables:
                info = self.get_table_info(table)
                if info:
                    response += f"• **{table}**: {info['row_count']:,} filas, {info['column_count']} columnas\n"
                else:
                    response += f"• **{table}**\n"
        
        return {
            'response': response,
            'code': '',
            'output_image_paths': []
        }
    
    def _handle_expert_table_analysis(self, query: str, table_name: str) -> Dict[str, Any]:
        """Handle expert analysis of a specific table with professional insights."""
        try:
            print(f"🔍 Debug - Starting expert analysis for table: {table_name}")
            print(f"🔍 Debug - Query: {query}")
            
            # Get table info
            table_info = self.get_table_info(table_name)
            if not table_info:
                print(f"❌ Debug - No table info found for {table_name}")
                return {
                    'response': f'❌ No se pudo obtener información de la tabla {table_name}',
                    'code': '',
                    'output_image_paths': []
                }
            
            # Load data for analysis (more data for better analysis)
            sample_query = f"SELECT * FROM {table_name} ORDER BY 1 LIMIT 2000"
            print(f"🔍 Debug - Executing query: {sample_query}")
            df = self.execute_query(sample_query)
            
            if df is None or df.empty:
                print(f"❌ Debug - No data loaded for {table_name}")
                return {
                    'response': f'❌ No se pudo cargar datos de la tabla {table_name}',
                    'code': '',
                    'output_image_paths': []
                }
            
            print(f"🔍 Debug - Data loaded successfully: {df.shape}")
            print(f"🔍 Debug - Columns: {list(df.columns)}")
            
            # Analyze query intent and create comprehensive analysis
            query_lower = query.lower()
            output_images = []
            
            print(f"🔍 Debug - Query lower: {query_lower}")
            print(f"🔍 Debug - Looking for fines keywords: {any(word in query_lower for word in ['fino', 'finos', 'fines'])}")
            print(f"🔍 Debug - Looking for time keywords: {any(word in query_lower for word in ['tiempo', 'time', 'tendencia', 'trend', 'línea', 'linea', 'line', 'gráfico', 'grafico'])}")
            
            # Start with expert prompt context only for comprehensive analysis
            if not any(word in query_lower for word in ['cuantos', 'cuántos', 'datos', 'registros', 'filas', 'columnas']):
                response = f"🔬 **Análisis Experto de Datos - {table_name}**\n\n"
                response += f"Como **Analista Científico de Datos Senior**, he analizado la tabla **{table_name}** con {table_info['row_count']:,} registros y {table_info['column_count']} variables.\n\n"
            else:
                response = ""
            
            # Comprehensive analysis based on table type
            print(f"🔍 Debug - Table type: {table_name}")
            if table_name == 'production_orders':
                print(f"🔍 Debug - Calling production_orders analysis")
                analysis_result = self._analyze_production_orders(df, query_lower, output_images)
                print(f"🔍 Debug - Analysis result length: {len(analysis_result)}")
                print(f"🔍 Debug - Output images: {output_images}")
                response += analysis_result
            elif table_name == 'production_stops':
                response += self._analyze_production_stops(df, query_lower, output_images)
            else:
                response += self._analyze_generic_table(df, table_name, query_lower, output_images)
            
            # Add expert recommendations only for comprehensive analysis
            if not any(word in query_lower for word in ['fino', 'finos', 'fines', 'tiempo', 'time', 'tendencia', 'trend', 'correlación', 'correlacion', 'cuantos', 'cuántos', 'datos', 'registros']):
                response += "\n\n💡 **Recomendaciones del Analista:**\n"
                response += "• Considera implementar alertas automáticas para valores fuera de rango\n"
                response += "• Establece monitoreo continuo de las métricas clave identificadas\n"
                response += "• Programa análisis periódicos para detectar tendencias tempranas\n"
                
                response += "\n🔍 **Próximos Pasos Sugeridos:**\n"
                response += "• ¿Te gustaría profundizar en algún aspecto específico?\n"
                response += "• ¿Quieres que analice la correlación con otras variables?\n"
                response += "• ¿Necesitas un dashboard de monitoreo en tiempo real?\n"
            
            return {
                'response': response,
                'code': sample_query,
                'output_image_paths': output_images
            }
            
        except Exception as e:
            return {
                'response': f'❌ Error en análisis experto de la tabla {table_name}: {str(e)}',
                'code': '',
                'output_image_paths': []
            }
    
    def _analyze_production_orders(self, df: pd.DataFrame, query_lower: str, output_images: List[str]) -> str:
        """Expert analysis for production_orders table based on user query intent."""
        print(f"🔍 Debug - Starting production_orders analysis")
        print(f"🔍 Debug - Query lower: {query_lower}")
        print(f"🔍 Debug - DataFrame shape: {df.shape}")
        print(f"🔍 Debug - DataFrame columns: {list(df.columns)}")
        
        analysis = ""
        
        # Analyze user query intent
        fines_detected = any(word in query_lower for word in ['fino', 'finos', 'fines'])
        time_detected = any(word in query_lower for word in ['tiempo', 'time', 'tendencia', 'trend', 'línea', 'linea', 'line', 'gráfico', 'grafico'])
        
        print(f"🔍 Debug - Fines detected: {fines_detected}")
        print(f"🔍 Debug - Time detected: {time_detected}")
        
        if fines_detected:
            # User is asking about fines specifically
            if 'fines_content' in df.columns:
                fines_stats = df['fines_content'].describe()
                analysis += f"**Análisis Específico de Finos (Fines Content):**\n"
                analysis += f"• Media: {fines_stats['mean']:.2f}%\n"
                analysis += f"• Mediana: {fines_stats['50%']:.2f}%\n"
                analysis += f"• Desviación estándar: {fines_stats['std']:.2f}%\n"
                analysis += f"• Rango: {fines_stats['min']:.2f}% - {fines_stats['max']:.2f}%\n\n"
                
                # Check if user wants time series analysis
                if any(word in query_lower for word in ['tiempo', 'time', 'tendencia', 'trend', 'línea', 'linea', 'line', 'gráfico', 'grafico']):
                    if 'production_date' in df.columns:
                        fig = self._create_trend_analysis(df, 'production_date', 'fines_content')
                        if fig:
                            filename = f"fines_trend_{hash(query_lower) % 10000}.pickle"
                            saved_path = self.save_visualization(fig, filename)
                            if saved_path:
                                output_images.append(saved_path)
                                analysis += "📈 **Gráfico de Línea: Tendencia de Finos en el Tiempo**\n\n"
                                analysis += "**Interpretación:**\n"
                                analysis += "• La línea muestra la evolución de los finos a lo largo del tiempo\n"
                                analysis += "• Picos altos pueden indicar problemas en el proceso\n"
                                analysis += "• Tendencias descendentes sugieren mejoras en la calidad\n\n"
                
                # Check if user wants distribution analysis
                elif any(word in query_lower for word in ['distribución', 'distribucion', 'histograma', 'histogram']):
                    fig = self._create_distribution_analysis(df, 'fines_content')
                    if fig:
                        filename = f"fines_distribution_{hash(query_lower) % 10000}.pickle"
                        saved_path = self.save_visualization(fig, filename)
                        if saved_path:
                            output_images.append(saved_path)
                            analysis += "📊 **Distribución de Finos**\n\n"
                            analysis += "**Interpretación:**\n"
                            analysis += "• El histograma muestra la frecuencia de diferentes niveles de finos\n"
                            analysis += "• Una distribución normal sugiere un proceso estable\n"
                            analysis += "• Sesgos pueden indicar problemas sistemáticos\n\n"
                
                # Default fines analysis
                else:
                    analysis += "**Análisis General de Finos:**\n"
                    high_fines = df[df['fines_content'] > df['fines_content'].quantile(0.9)]
                    analysis += f"• {len(high_fines)} registros ({(len(high_fines)/len(df)*100):.1f}%) tienen finos superiores al percentil 90\n"
                    analysis += "• Esto podría indicar problemas en el proceso de molienda\n\n"
                    
                    # Create a simple bar chart of fines distribution
                    fig = self._create_distribution_analysis(df, 'fines_content')
                    if fig:
                        filename = f"fines_overview_{hash(query_lower) % 10000}.pickle"
                        saved_path = self.save_visualization(fig, filename)
                        if saved_path:
                            output_images.append(saved_path)
                            analysis += "📊 **Vista General de la Distribución de Finos**\n\n"
        
        elif any(word in query_lower for word in ['correlación', 'correlacion', 'correlation']):
            # User specifically wants correlation analysis
            numeric_cols = df.select_dtypes(include=[np.number]).columns
            if len(numeric_cols) >= 2:
                fig = self._create_correlation_heatmap(df)
                if fig:
                    filename = f"production_correlation_{hash(query_lower) % 10000}.pickle"
                    saved_path = self.save_visualization(fig, filename)
                    if saved_path:
                        output_images.append(saved_path)
                        analysis += "🔗 **Matriz de Correlación entre Variables de Producción**\n\n"
                        analysis += "**Interpretación:**\n"
                        analysis += "• Verde: Correlación positiva fuerte\n"
                        analysis += "• Rojo: Correlación negativa fuerte\n"
                        analysis += "• Blanco: Poca o ninguna correlación\n\n"
        
        elif any(word in query_lower for word in ['tendencia', 'trend', 'tiempo', 'time', 'evolución', 'evolucion']):
            # User wants time series analysis
            if 'production_date' in df.columns:
                # Find a numeric column for time series
                numeric_cols = df.select_dtypes(include=[np.number]).columns
                if len(numeric_cols) > 0:
                    value_col = numeric_cols[0]  # Use first numeric column
                    fig = self._create_trend_analysis(df, 'production_date', value_col)
                    if fig:
                        filename = f"time_series_{hash(query_lower) % 10000}.pickle"
                        saved_path = self.save_visualization(fig, filename)
                        if saved_path:
                            output_images.append(saved_path)
                            analysis += f"📈 **Análisis de Tendencia Temporal - {value_col}**\n\n"
                            analysis += "**Interpretación:**\n"
                            analysis += "• La línea muestra la evolución temporal de la variable\n"
                            analysis += "• Patrones cíclicos pueden indicar estacionalidad\n"
                            analysis += "• Tendencias ayudan a identificar mejoras o deterioros\n\n"
        
        elif any(word in query_lower for word in ['cuantos', 'cuántos', 'datos', 'registros', 'filas', 'columnas']):
            # User is asking about data count/size
            analysis = f"📊 **Información de la Tabla production_orders:**\n\n"
            analysis += f"• **Total de registros**: {len(df):,} filas\n"
            analysis += f"• **Total de columnas**: {len(df.columns)} variables\n"
            analysis += f"• **Período de datos**: {df['production_date'].min()} a {df['production_date'].max()}\n\n"
            
            # Show column names
            analysis += "**Columnas disponibles:**\n"
            for i, col in enumerate(df.columns, 1):
                analysis += f"{i}. {col}\n"
            
        else:
            # Default comprehensive analysis
            analysis += "**Análisis General de Producción:**\n"
            
            # Basic statistics for key metrics
            if 'fines_at_die_exit' in df.columns:
                fines_stats = df['fines_at_die_exit'].describe()
                analysis += f"• **Finos**: Media {fines_stats['mean']:.2f}%, Rango {fines_stats['min']:.2f}%-{fines_stats['max']:.2f}%\n"
            
            # Create a dashboard view
            fig = self._create_multi_metric_dashboard(df)
            if fig:
                filename = f"production_dashboard_{hash(query_lower) % 10000}.pickle"
                saved_path = self.save_visualization(fig, filename)
                if saved_path:
                    output_images.append(saved_path)
                    analysis += "📊 **Dashboard de Métricas de Producción**\n\n"
        
        return analysis
    
    def _analyze_production_stops(self, df: pd.DataFrame, query_lower: str, output_images: List[str]) -> str:
        """Expert analysis for production_stops table."""
        analysis = "🛑 **Análisis de Paradas de Producción**\n\n"
        
        # Stop frequency analysis
        if 'stop_type' in df.columns:
            stop_counts = df['stop_type'].value_counts()
            analysis += f"**Frecuencia de Paradas por Tipo:**\n"
            for stop_type, count in stop_counts.head(5).items():
                analysis += f"• {stop_type}: {count} paradas ({(count/len(df)*100):.1f}%)\n"
            analysis += "\n"
        
        # Duration analysis
        if 'duration_minutes' in df.columns:
            duration_stats = df['duration_minutes'].describe()
            analysis += f"**Análisis de Duración de Paradas:**\n"
            analysis += f"• Duración promedio: {duration_stats['mean']:.1f} minutos\n"
            analysis += f"• Duración máxima: {duration_stats['max']:.1f} minutos\n"
            analysis += f"• Total de tiempo perdido: {(df['duration_minutes'].sum()/60):.1f} horas\n\n"
        
        # Time series analysis
        if 'start_datetime' in df.columns and 'duration_minutes' in df.columns:
            fig = self._create_time_series_analysis(df, 'start_datetime', 'duration_minutes')
            if fig:
                filename = f"stops_timeseries_{hash(query_lower) % 10000}.pickle"
                saved_path = self.save_visualization(fig, filename)
                if saved_path:
                    output_images.append(saved_path)
                    analysis += "⏰ **Análisis Temporal de Paradas** generado.\n\n"
        
        return analysis
    
    def _analyze_generic_table(self, df: pd.DataFrame, table_name: str, query_lower: str, output_images: List[str]) -> str:
        """Generic expert analysis for any table."""
        analysis = f"📊 **Análisis General de {table_name}**\n\n"
        
        # Basic statistics
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        if len(numeric_cols) > 0:
            analysis += f"**Estadísticas Descriptivas:**\n"
            for col in numeric_cols[:3]:  # Show first 3 numeric columns
                stats = df[col].describe()
                analysis += f"• **{col}**: Media={stats['mean']:.2f}, Std={stats['std']:.2f}, Min={stats['min']:.2f}, Max={stats['max']:.2f}\n"
            analysis += "\n"
        
        # Correlation analysis
        if len(numeric_cols) >= 2:
            fig = self._create_correlation_heatmap(df)
            if fig:
                filename = f"generic_correlation_{table_name}_{hash(query_lower) % 10000}.pickle"
                saved_path = self.save_visualization(fig, filename)
                if saved_path:
                    output_images.append(saved_path)
                    analysis += "🔗 **Análisis de Correlaciones** entre variables numéricas.\n\n"
        
        # Distribution analysis
        if len(numeric_cols) > 0:
            fig = self._create_distribution_analysis(df, numeric_cols[0])
            if fig:
                filename = f"generic_distribution_{table_name}_{hash(query_lower) % 10000}.pickle"
                saved_path = self.save_visualization(fig, filename)
                if saved_path:
                    output_images.append(saved_path)
                    analysis += "📊 **Análisis de Distribución** de la variable principal.\n\n"
        
        return analysis
    
    def _handle_sql_query(self, query: str) -> Dict[str, Any]:
        """Handle direct SQL query."""
        try:
            # Extract SQL from query (simple approach)
            sql_query = query
            if 'sql:' in query.lower():
                sql_query = query.split('sql:')[1].strip()
            elif 'consulta:' in query.lower():
                sql_query = query.split('consulta:')[1].strip()
            
            # Execute query
            df = self.execute_query(sql_query)
            
            if df is None:
                return {
                    'response': '❌ Error ejecutando la consulta SQL.',
                    'code': sql_query,
                    'output_image_paths': []
                }
            
            response = f"✅ **Consulta SQL ejecutada exitosamente**\n\n"
            response += f"• **Resultados**: {len(df)} filas, {len(df.columns)} columnas\n\n"
            
            # Show first few rows
            response += "**Primeras filas:**\n"
            response += df.head().to_string()
            
            # Create visualization if data is suitable
            output_images = []
            if len(df) > 0 and len(df.columns) >= 2:
                numeric_cols = df.select_dtypes(include=[np.number]).columns
                if len(numeric_cols) >= 2:
                    fig = self._create_correlation_heatmap(df)
                    if fig:
                        filename = f"sql_result_{hash(sql_query) % 10000}.pickle"
                        saved_path = self.save_visualization(fig, filename)
                        if saved_path:
                            output_images.append(saved_path)
                            response += "\n\n📊 **Visualización** generada automáticamente."
            
            return {
                'response': response,
                'code': sql_query,
                'output_image_paths': output_images
            }
            
        except Exception as e:
            return {
                'response': f'❌ Error ejecutando consulta SQL: {str(e)}',
                'code': query,
                'output_image_paths': []
            }
    
    def _handle_general_analysis(self, query: str, tables: List[str]) -> Dict[str, Any]:
        """Handle general analysis query."""
        if not tables:
            return {
                'response': '❌ No hay tablas disponibles para analizar.',
                'code': '',
                'output_image_paths': []
            }
        
        response = f"🔍 **Análisis general de la base de datos**\n\n"
        response += f"Se encontraron {len(tables)} tablas disponibles:\n\n"
        
        # Analyze each table
        output_images = []
        for table in tables[:3]:  # Limit to first 3 tables
            table_info = self.get_table_info(table)
            if table_info:
                response += f"📋 **{table}**: {table_info['row_count']:,} filas, {table_info['column_count']} columnas\n"
                
                # Load sample data for visualization
                sample_query = f"SELECT * FROM {table} LIMIT 500"
                df = self.execute_query(sample_query)
                
                if df is not None and not df.empty:
                    numeric_cols = df.select_dtypes(include=[np.number]).columns
                    if len(numeric_cols) >= 2:
                        fig = self._create_correlation_heatmap(df)
                        if fig:
                            filename = f"general_{table}.pickle"
                            saved_path = self.save_visualization(fig, filename)
                            if saved_path:
                                output_images.append(saved_path)
                                response += f"  📊 Visualización generada\n"
        
        response += "\n💡 **Sugerencias:**\n"
        response += "• Pregunta por una tabla específica para análisis detallado\n"
        response += "• Solicita análisis de correlación, distribución o tendencias\n"
        response += "• Ejecuta consultas SQL personalizadas\n"
        
        return {
            'response': response,
            'code': '',
            'output_image_paths': output_images
        } 