# 🛠️ Guía de Desarrollo - Okuo IA DataLab

## 🎯 Descripción General

Esta guía está diseñada para desarrolladores que quieren contribuir al proyecto **Okuo IA DataLab**. Incluye información sobre la arquitectura, estándares de código, procesos de desarrollo y las nuevas funcionalidades de storytelling ejecutivo.

---

## 🏗️ Arquitectura del Proyecto

### Estructura de Directorios

```
AgenticDataAnalysis/
├── main_app.py                    # Punto de entrada principal
├── setup.py                      # Script de instalación
├── requirements.txt              # Dependencias del proyecto
├── pyproject.toml               # Configuración moderna del proyecto
├── src/                         # Código fuente principal
│   ├── config/                 # Configuración de la aplicación
│   │   ├── settings.py         # Configuración centralizada
│   │   └── environments/       # Configuraciones por entorno
│   ├── core/                   # Lógica de negocio central
│   │   ├── agents/            # Agentes de IA
│   │   │   ├── python_agent.py       # Agente principal de análisis
│   │   │   └── storytelling_agent.py # Agente de storytelling ejecutivo 🆕
│   │   ├── graph/             # Grafo de flujo de trabajo
│   │   │   ├── state.py       # Estado del agente
│   │   │   ├── nodes.py       # Nodos del grafo
│   │   │   └── tools.py       # Herramientas de Python
│   │   └── prompts/           # Prompts para la IA
│   │       ├── main_prompt.md        # Prompt principal
│   │       └── storytelling_prompt.md # Prompt de storytelling 🆕
│   ├── models/                 # Modelos de datos
│   │   └── data_models.py     # Clases de datos principales
│   ├── ui/                     # Componentes de interfaz
│   │   └── components/        # Componentes de UI
│   │       ├── chat_interface.py    # Interfaz de chat
│   │       ├── file_upload.py       # Carga de archivos
│   │       ├── header.py            # Header de la aplicación
│   │       └── pdf_export.py        # Exportación PDF 🆕
│   └── utils/                  # Utilidades
│       └── file_utils.py      # Gestión de archivos
├── assets/                     # Recursos estáticos
│   ├── css/                   # Estilos CSS
│   ├── images/                # Imágenes y visualizaciones
│   └── uploads/               # Archivos subidos por usuarios
├── logs/                      # Archivos de log
└── uploads/                   # Archivos temporales
```

### Flujo de Datos

```mermaid
graph TD
    A[Usuario] --> B[Streamlit UI]
    B --> C[File Manager]
    C --> D[Data Dictionary]
    D --> E[Chat Interface]
    E --> F[Python Agent]
    F --> G[LangGraph Workflow]
    G --> H[Python Tools]
    H --> I[Plotly Figures]
    I --> J[Storytelling Agent] 🆕
    J --> K[PDF Export]
    K --> L[Download]
```

---

## 🧠 Componentes Principales

### 1. **PythonAnalysisAgent** (`src/core/agents/python_agent.py`)

**Responsabilidades**:
- Coordinar el análisis de datos
- Gestionar el estado de la conversación
- Ejecutar el grafo de trabajo LangGraph
- Manejar visualizaciones Plotly

**Métodos Clave**:
```python
def process_query(self, user_query: str, input_data: List[InputData]) -> AnalysisResult
def get_chat_history(self) -> List[ChatMessage]
def load_plotly_figure(self, image_path: str) -> plotly.Figure
```

### 2. **StorytellingAgent** (`src/core/agents/storytelling_agent.py`) 🆕

**Responsabilidades**:
- Analizar conversaciones completas
- Extraer insights relevantes para el negocio
- Generar recomendaciones accionables
- Crear narrativas ejecutivas coherentes
- Integrar visualizaciones en reportes

**Métodos Clave**:
```python
def analyze_conversation(self, chat_history: List[ChatMessage], analysis_results: List[AnalysisResult]) -> List[ConversationInsight]
def generate_storytelling_pdf(self, chat_history: List[ChatMessage], analysis_results: List[AnalysisResult], filename: str = None) -> str
def _extract_key_findings_with_prompt(self, answer: str) -> List[str]
def _generate_recommendations_with_prompt(self, question: str, answer: str) -> List[str]
```

**Estructura de Datos**:
```python
@dataclass
class ConversationInsight:
    question: str                    # Pregunta del usuario
    answer: str                      # Respuesta del agente
    key_findings: List[str]          # Hallazgos principales
    data_insights: List[str]         # Insights de datos
    recommendations: List[str]       # Recomendaciones
    visualizations: List[str]        # Visualizaciones asociadas
    confidence_score: float          # Puntuación de confianza
```

### 3. **Prompts Especializados** (`src/core/prompts/`)

#### **Main Prompt** (`main_prompt.md`)
- **Propósito**: Guiar el comportamiento del agente principal
- **Enfoque**: Análisis técnico y ejecución de código Python
- **Características**: Instrucciones para visualizaciones y estadísticas

#### **Storytelling Prompt** (`storytelling_prompt.md`) 🆕
- **Propósito**: Guiar el análisis narrativo y generación de reportes
- **Enfoque**: Storytelling de datos y comunicación ejecutiva
- **Características**:
  - Metodología de análisis de conversaciones
  - Extracción de insights de negocio
  - Generación de recomendaciones accionables
  - Estructura de reportes ejecutivos

### 4. **LangGraph Workflow** (`src/core/graph/`)

**Componentes**:
- **`state.py`**: Define el estado del agente
- **`nodes.py`**: Nodos del grafo (modelo, herramientas)
- **`tools.py`**: Herramientas de ejecución de Python

**Flujo de Trabajo**:
1. **Agente** recibe consulta del usuario
2. **Router** decide si usar herramientas
3. **Tools** ejecuta código Python
4. **Modelo** genera respuesta
5. **Ciclo** hasta completar la tarea

### 5. **Modelos de Datos** (`src/models/data_models.py`)

**Clases Principales**:

#### `InputData`
```python
@dataclass
class InputData:
    variable_name: str          # Nombre de la variable
    data_path: Path            # Ruta al archivo
    data_description: str      # Descripción del dataset
    data_frame: Optional[pd.DataFrame]  # DataFrame cargado
```

#### `ChatMessage`
```python
@dataclass
class ChatMessage:
    content: str               # Contenido del mensaje
    sender: str               # "user" o "assistant"
    timestamp: Optional[str]  # Marca de tiempo
```

#### `AnalysisResult`
```python
@dataclass
class AnalysisResult:
    query: str                # Consulta original
    response: str             # Respuesta de la IA
    visualizations: List[str] # Rutas a visualizaciones
    intermediate_outputs: List[Dict]  # Salidas intermedias
```

### 6. **Configuración** (`src/config/settings.py`)

**Configuraciones Principales**:
```python
@dataclass
class AppConfig:
    APP_NAME: str = "Okuo IA DataLab"
    BASE_DIR: Path = Path(__file__).parent.parent.parent
    UPLOADS_DIR: Path = ASSETS_DIR / "uploads"
    PLOTLY_FIGURES_DIR: Path = IMAGES_DIR / "plotly_figures" / "pickle"
    OPENAI_API_KEY: Optional[str] = os.getenv("OPENAI_API_KEY")
    
    # Colores corporativos
    PRIMARY_COLOR: str = "#1C8074"      # Verde primario
    SECONDARY_COLOR: str = "#666666"    # Gris
    ACCENT_COLOR: str = "#1A494C"       # Verde oscuro
```

---

## 🎨 Componentes de UI

### 1. **Interfaz Principal** (`main_app.py`)

**Estructura**:
- **Header**: Título y navegación
- **Tabs**: Gestión de Datos, Chat, Depuración
- **Session State**: Manejo de estado de Streamlit

**Funciones Principales**:
```python
def render_data_management_tab()    # Gestión de archivos CSV
def render_chat_tab()              # Interfaz de chat
def render_debug_tab()             # Herramientas de depuración
```

### 2. **Chat Interface** (`src/ui/components/chat_interface.py`)

**Características**:
- ✅ Historial de conversación
- ✅ Visualización de gráficos Plotly
- ✅ Exportación a PDF con storytelling
- ✅ Depuración de salidas intermedias

### 3. **PDF Export** (`src/ui/components/pdf_export.py`) 🆕

**Funcionalidades**:
- ✅ Generación de reportes ejecutivos con storytelling
- ✅ Análisis automático de conversaciones
- ✅ Inclusión de visualizaciones con explicaciones
- ✅ Estilos profesionales con colores corporativos
- ✅ Limpieza automática de archivos temporales

**Proceso de Generación**:
1. **Análisis de Conversación**: El StorytellingAgent analiza toda la conversación
2. **Extracción de Insights**: Identifica hallazgos clave y patrones
3. **Generación de Recomendaciones**: Crea recomendaciones accionables
4. **Creación de PDF**: Genera reporte ejecutivo profesional
5. **Limpieza**: Elimina archivos temporales

---

## 🎭 Storytelling de Datos - Guía de Desarrollo

### Metodología de Análisis

#### **1. Análisis de Conversación**
El StorytellingAgent analiza las conversaciones siguiendo estos pasos:

```python
def analyze_conversation(self, chat_history: List[ChatMessage], analysis_results: List[AnalysisResult]) -> List[ConversationInsight]:
    """
    Analiza una conversación completa y extrae insights relevantes.
    
    Args:
        chat_history: Lista de mensajes de la conversación
        analysis_results: Resultados de análisis previos
        
    Returns:
        Lista de insights extraídos de la conversación
    """
```

**Proceso**:
1. **Agrupación**: Agrupa preguntas y respuestas por temas
2. **Extracción**: Identifica hallazgos clave en cada respuesta
3. **Análisis**: Genera insights de negocio
4. **Recomendaciones**: Crea sugerencias accionables

#### **2. Extracción de Insights**
Para cada respuesta del agente, identifica:

- **Hallazgos estadísticos importantes** (medias, correlaciones, distribuciones)
- **Patrones y tendencias** detectados en los datos
- **Anomalías o valores atípicos** significativos
- **Relaciones entre variables** relevantes para el negocio
- **Insights de negocio** derivados de los análisis

#### **3. Generación de Storytelling**
- **Crea una narrativa coherente** que conecte todos los hallazgos
- **Desarrolla un hilo conductor** que guíe al lector
- **Presenta los datos como una historia** de descubrimiento
- **Conecta los insights** con implicaciones de negocio

### Criterios de Calidad

#### **Relevancia**
- **Enfócate en insights** que impacten el negocio
- **Prioriza hallazgos** por importancia estratégica
- **Elimina detalles técnicos** innecesarios
- **Mantén el foco** en las implicaciones de negocio

#### **Claridad**
- **Explica conceptos técnicos** de manera accesible
- **Usa ejemplos concretos** cuando sea posible
- **Proporciona contexto** para cada hallazgo
- **Estructura la información** de manera lógica

#### **Accionabilidad**
- **Cada insight** debe llevar a una recomendación
- **Las recomendaciones** deben ser específicas y medibles
- **Incluye pasos concretos** para implementación
- **Define métricas** para monitorear el progreso

### Estructura del Reporte Ejecutivo

```python
def generate_storytelling_pdf(self, chat_history: List[ChatMessage], analysis_results: List[AnalysisResult], filename: str = None) -> str:
    """
    Genera un reporte ejecutivo PDF con storytelling.
    
    Args:
        chat_history: Historial de conversación
        analysis_results: Resultados de análisis
        filename: Nombre del archivo PDF (opcional)
        
    Returns:
        Ruta al archivo PDF generado
    """
```

**Estructura del Reporte**:
1. **Portada**: Título, fecha y contexto
2. **Resumen Ejecutivo**: Insights clave y recomendaciones principales
3. **Análisis Detallado**: Análisis por temas identificados
4. **Insights Estratégicos**: Patrones y tendencias detectados
5. **Recomendaciones**: Acciones específicas y medibles
6. **Anexos**: Visualizaciones y detalles técnicos

---

## 🔧 Herramientas y Utilidades

### 1. **File Manager** (`src/utils/file_utils.py`)

**Responsabilidades**:
- ✅ Carga y guardado de archivos CSV
- ✅ Gestión del diccionario de datos
- ✅ Validación de extensiones
- ✅ Manejo de rutas absolutas

### 2. **Python Tools** (`src/core/graph/tools.py`)

**Funcionalidad**:
- ✅ Ejecución segura de código Python
- ✅ Captura de salida estándar
- ✅ Persistencia de variables
- ✅ Guardado automático de figuras Plotly

### 3. **PDF Generation** (`src/ui/components/pdf_export.py`)

**Tecnologías**:
- **ReportLab**: Generación de PDFs profesionales
- **Plotly**: Conversión de gráficos a imágenes
- **PIL**: Procesamiento de imágenes
- **Tempfile**: Manejo de archivos temporales

**Características**:
- **Estilos profesionales** con colores corporativos
- **Tipografía Inter** para mejor legibilidad
- **Estructura ejecutiva** con secciones claras
- **Visualizaciones integradas** con explicaciones
- **Limpieza automática** de archivos temporales

---

## 🎨 Diseño y UX

### Colores Corporativos

```css
:root {
    --primary-color: #1C8074;    /* Verde primario - PANTONE 3295 U */
    --secondary-color: #666666;  /* Gris - PANTONE 426 U */
    --accent-color: #1A494C;     /* Verde oscuro - PANTONE 175-16 U */
    --light-green: #94AF92;      /* Verde claro - PANTONE 7494 U */
    --very-light-green: #E6ECD8; /* Verde muy claro - PANTONE 152-2 U */
    --light-gray: #C9C9C9;       /* Gris claro - PANTONE COLOR GRAY 2 U */
}
```

### Tipografía

- **Fuente Principal**: Inter (Google Fonts)
- **Peso**: 400 (normal), 600 (semi-bold), 700 (bold)
- **Tamaños**: 11px (cuerpo), 14px (subtítulos), 18px (títulos), 28px (título principal)

### Componentes UI

#### **Botones**
- **Primario**: Verde corporativo con hover effects
- **Secundario**: Gris con bordes
- **Exportación**: Iconos descriptivos y estados de carga

#### **Tarjetas**
- **Bordes suaves** con sombras sutiles
- **Espaciado consistente** entre elementos
- **Colores corporativos** para acentos

#### **Formularios**
- **Validación en tiempo real** con feedback visual
- **Estados de error** claramente marcados
- **Autocompletado** cuando es apropiado

---

## 🔍 Depuración y Monitoreo

### 1. **Debug Tab**

**Funcionalidades**:
- ✅ Visualización del estado de la aplicación
- ✅ Historial de conversaciones
- ✅ Resultados de análisis
- ✅ Rutas de archivos y configuraciones

### 2. **Logging**

**Niveles**:
- **INFO**: Operaciones normales
- **WARNING**: Situaciones que requieren atención
- **ERROR**: Errores que afectan la funcionalidad
- **DEBUG**: Información detallada para desarrollo

**Ubicación**: `logs/app.log`

### 3. **Manejo de Errores**

**Estrategias**:
- **Try-catch** en operaciones críticas
- **Fallbacks** para funcionalidades opcionales
- **Mensajes de error** claros para el usuario
- **Logging detallado** para debugging

---

## 🚀 Optimización y Rendimiento

### 1. **Gestión de Memoria**

**Estrategias**:
- **Limpieza automática** de archivos temporales
- **Persistencia selectiva** de datos importantes
- **Carga lazy** de visualizaciones grandes
- **Compresión** de archivos pickle

### 2. **Optimización de UI**

**Técnicas**:
- **Renderizado condicional** de componentes pesados
- **Caché** de resultados de análisis
- **Debouncing** en inputs de usuario
- **Lazy loading** de imágenes

### 3. **Manejo de Archivos**

**Mejoras**:
- **Rutas absolutas** para mayor robustez
- **Validación** de tipos de archivo
- **Límites** de tamaño de archivo
- **Compresión** automática de datos

---

## 🔒 Seguridad

### 1. **Ejecución de Código**

**Medidas**:
- **PythonREPL** de LangChain para ejecución segura
- **Sandboxing** de operaciones críticas
- **Validación** de código antes de ejecución
- **Límites** de tiempo de ejecución

### 2. **Manejo de Datos**

**Protecciones**:
- **Validación** de tipos de archivo
- **Sanitización** de nombres de archivo
- **Límites** de tamaño de archivo
- **Encriptación** de datos sensibles

### 3. **API Keys**

**Seguridad**:
- **Variables de entorno** para claves API
- **Validación** de claves antes del uso
- **Rotación** automática de claves
- **Logging** de uso de API

---

## 📊 Métricas y Analytics

### 1. **Métricas de Uso**

**Datos Recopilados**:
- **Número de consultas** por sesión
- **Tipos de análisis** más populares
- **Tiempo de respuesta** promedio
- **Tasa de éxito** de consultas

### 2. **Métricas de Rendimiento**

**Indicadores**:
- **Tiempo de carga** de la aplicación
- **Uso de memoria** por operación
- **Tiempo de generación** de PDFs
- **Tasa de errores** por funcionalidad

### 3. **Métricas de Calidad**

**Medidas**:
- **Satisfacción del usuario** con resultados
- **Calidad de visualizaciones** generadas
- **Relevancia de insights** extraídos
- **Accionabilidad de recomendaciones**

---

## 🔮 Roadmap y Futuras Mejoras

### Próximas Características

#### **Análisis Avanzado**
- [ ] **Machine Learning automático** para detección de patrones
- [ ] **Análisis de series temporales** con predicciones
- [ ] **Análisis de sentimientos** en datos textuales
- [ ] **Detección de anomalías** automática

#### **Integración de Datos**
- [ ] **Conexión a bases de datos** (PostgreSQL, MySQL)
- [ ] **APIs externas** para enriquecimiento de datos
- [ ] **Sincronización en la nube** de archivos
- [ ] **Colaboración en tiempo real** entre usuarios

#### **Storytelling Avanzado**
- [ ] **Múltiples formatos** de exportación (PowerPoint, Word)
- [ ] **Templates personalizables** para reportes
- [ ] **Análisis comparativo** entre datasets
- [ ] **Recomendaciones automáticas** de visualizaciones

#### **UI/UX Mejoras**
- [ ] **Modo oscuro** para la interfaz
- [ ] **Responsive design** para móviles
- [ ] **Accesibilidad** mejorada (WCAG 2.1)
- [ ] **Internacionalización** (múltiples idiomas)

### En Desarrollo

#### **Optimización de Rendimiento**
- [ ] **Caché distribuido** con Redis
- [ ] **Procesamiento asíncrono** de tareas pesadas
- [ ] **Compresión inteligente** de datos
- [ ] **CDN** para assets estáticos

#### **Inteligencia Artificial**
- [ ] **Fine-tuning** de modelos para casos específicos
- [ ] **Aprendizaje continuo** basado en feedback
- [ ] **Personalización** de respuestas por usuario
- [ ] **Detección de contexto** automática

---

## 🤝 Contribución

### Guías de Contribución

#### **Estándares de Código**
- **Python**: PEP 8, type hints, docstrings en español
- **JavaScript/HTML**: ESLint, Prettier
- **CSS**: BEM methodology, variables CSS
- **Commits**: Conventional Commits

#### **Proceso de Desarrollo**
1. **Fork** el repositorio
2. **Crea** una rama para tu feature
3. **Desarrolla** con tests incluidos
4. **Documenta** tus cambios
5. **Abre** un Pull Request

#### **Áreas de Contribución**
- **Nuevas funcionalidades** de análisis
- **Mejoras en UI/UX**
- **Optimización de rendimiento**
- **Documentación y ejemplos**
- **Tests y calidad de código**

### Estándares de Código

#### **Python**
```python
# Ejemplo de función bien documentada
def analyze_data_with_storytelling(data: pd.DataFrame, 
                                  analysis_type: str = "exploratory") -> AnalysisResult:
    """
    Analiza datos y genera insights con storytelling.
    
    Args:
        data: DataFrame con los datos a analizar
        analysis_type: Tipo de análisis a realizar
        
    Returns:
        AnalysisResult con resultados y visualizaciones
        
    Raises:
        ValueError: Si el tipo de análisis no es válido
    """
    if analysis_type not in ["exploratory", "statistical", "predictive"]:
        raise ValueError(f"Tipo de análisis '{analysis_type}' no válido")
    
    # Implementación...
    return result
```

#### **Type Hints**
```python
from typing import List, Dict, Optional, Union
from pathlib import Path
import pandas as pd

def process_file(file_path: Path, 
                options: Optional[Dict[str, Union[str, int]]] = None) -> pd.DataFrame:
    """Procesa un archivo y retorna un DataFrame."""
    pass
```

#### **Docstrings**
```python
def generate_report(insights: List[str], 
                   visualizations: List[str], 
                   format: str = "pdf") -> str:
    """
    Genera un reporte ejecutivo con insights y visualizaciones.
    
    Args:
        insights: Lista de insights extraídos del análisis
        visualizations: Lista de rutas a visualizaciones
        format: Formato de salida ("pdf", "html", "docx")
        
    Returns:
        Ruta al archivo generado
        
    Example:
        >>> insights = ["Correlación fuerte entre X e Y", "Tendencia creciente"]
        >>> viz = ["plot1.png", "plot2.png"]
        >>> path = generate_report(insights, viz, "pdf")
        >>> print(f"Reporte generado en: {path}")
    """
    pass
```

---

## 📞 Soporte y Contacto

### Canales de Soporte

- **Issues de GitHub**: Para reportar bugs y solicitar features
- **Discussions**: Para preguntas y discusiones generales
- **Wiki**: Documentación adicional y ejemplos

### Recursos Adicionales

- **Tutoriales**: Guías paso a paso para usuarios
- **Ejemplos**: Casos de uso reales con datasets
- **API Reference**: Documentación técnica completa
- **Changelog**: Historial detallado de cambios

---

## 📄 Licencia

Este proyecto está bajo la **Licencia MIT**. Ver el archivo [LICENSE](LICENSE) para detalles completos.

### Términos de Uso

- **Uso comercial** permitido
- **Modificación** permitida
- **Distribución** permitida
- **Atribución** requerida

---

*Guía de desarrollo actualizada el 19 de julio de 2025* 