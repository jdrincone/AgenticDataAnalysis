# 🤖 Okuo IA DataLab

> **Laboratorio de Análisis Inteligente de Datos** - Una aplicación web que combina IA conversacional con análisis de datos avanzado y storytelling ejecutivo.

[![Python](https://img.shields.io/badge/Python-3.12+-blue.svg)](https://python.org)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.28+-red.svg)](https://streamlit.io)
[![LangChain](https://img.shields.io/badge/LangChain-0.1+-green.svg)](https://langchain.com)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

## 🎯 ¿Qué es Okuo IA DataLab?

Okuo IA DataLab es una aplicación web inteligente que permite a usuarios no técnicos realizar análisis complejos de datos a través de una interfaz conversacional natural. Combina la potencia de la inteligencia artificial con herramientas de visualización avanzadas y **storytelling ejecutivo profesional**.

### ✨ Características Principales

- 🤖 **IA Conversacional**: Análisis de datos mediante lenguaje natural
- 📊 **Visualizaciones Automáticas**: Gráficos interactivos con Plotly
- 📁 **Gestión Inteligente de Datos**: Carga y organización de archivos CSV
- 📄 **Reportes Ejecutivos Profesionales**: Exportación automática a PDF con storytelling
- 🎭 **Storytelling de Datos**: Análisis narrativo que transforma datos en insights ejecutivos
- 🔍 **Depuración Avanzada**: Herramientas para entender el proceso de análisis
- 🎨 **UI Moderna**: Interfaz intuitiva con Streamlit y colores corporativos

## 🚀 Instalación Rápida

### Prerrequisitos

- Python 3.12 o superior
- pip (gestor de paquetes de Python)
- Acceso a internet

### Instalación

```bash
# 1. Clonar el repositorio
git clone https://github.com/tu-usuario/AgenticDataAnalysis.git
cd AgenticDataAnalysis

# 2. Ejecutar el script de instalación automática
python3 setup.py

# 3. Configurar variables de entorno
cp .env.example .env
# Editar .env y agregar tu OPENAI_API_KEY

# 4. Ejecutar la aplicación
streamlit run main_app.py
```

**Alternativa usando pip:**
```bash
# Instalar directamente con pip (requiere Python 3.12+)
pip install -e .
streamlit run main_app.py
```

### Configuración

1. **Obtener API Key de OpenAI**:
   - Ve a [OpenAI Platform](https://platform.openai.com/)
   - Crea una cuenta y obtén tu API key
   - Agrega la key al archivo `.env`

2. **Configurar el archivo `.env`**:
```env
OPENAI_API_KEY=tu_api_key_aqui
OPENAI_MODEL=gpt-4o
STREAMLIT_PORT=8501
STREAMLIT_HOST=localhost
MAX_UPLOAD_SIZE=2000
```

## 📖 Uso

### 1. Carga de Datos
1. Navega a la pestaña **"📊 Gestión de Datos"**
2. Sube tus archivos CSV
3. Selecciona los archivos que quieres analizar
4. Agrega descripciones opcionales

### 2. Análisis Conversacional
1. Ve a la pestaña **"💬 Interfaz de Chat"**
2. Haz preguntas en lenguaje natural como:
   - "Muestra un gráfico de dispersión de ventas vs tiempo"
   - "Calcula la correlación entre edad e ingresos"
   - "Crea un histograma de la distribución de precios"
   - "Analiza las tendencias en los datos"

### 3. Exportación de Reportes Ejecutivos
1. **Después de una conversación**, usa el botón **"🚀 Generar Reporte Profesional"**
2. El sistema analizará toda la conversación automáticamente
3. Generará un **reporte ejecutivo con storytelling** que incluye:
   - **Resumen ejecutivo** con insights clave
   - **Análisis detallado** por temas identificados
   - **Insights estratégicos** y patrones detectados
   - **Recomendaciones accionables** basadas en datos
   - **Visualizaciones relevantes** con explicaciones
4. Descarga el PDF profesional listo para presentación

## 🏗️ Arquitectura

```
┌─────────────────────────────────────┐
│           Streamlit UI              │
├─────────────────────────────────────┤
│         Python Agent                │
├─────────────────────────────────────┤
│      Storytelling Agent             │
├─────────────────────────────────────┤
│        LangGraph Workflow           │
├─────────────────────────────────────┤
│         OpenAI API                  │
└─────────────────────────────────────┘
```

### Componentes Principales

- **`main_app.py`**: Punto de entrada de la aplicación
- **`PythonAnalysisAgent`**: Agente principal de análisis
- **`StorytellingAgent`**: Agente especializado en storytelling ejecutivo
- **`LangGraph Workflow`**: Flujo de trabajo de IA
- **`PDF Exporter`**: Generación de reportes profesionales
- **`File Manager`**: Gestión de archivos

## 🔧 Tecnologías Utilizadas

### Frontend
- **Streamlit**: Framework web para aplicaciones de datos
- **Plotly**: Visualizaciones interactivas
- **ReportLab**: Generación de PDFs profesionales

### Backend
- **Python 3.12+**: Lenguaje principal
- **LangChain**: Framework para aplicaciones de IA
- **LangGraph**: Orquestación de flujos de trabajo
- **OpenAI GPT-4o**: Modelo de lenguaje

### Data Processing
- **Pandas**: Manipulación de datos
- **NumPy**: Computación numérica
- **Scikit-learn**: Machine Learning

## 📊 Ejemplos de Uso

### Análisis Exploratorio
```
Usuario: "Analiza este dataset de ventas"
IA: "He analizado tu dataset. Encontré:
     - 1,234 registros de ventas
     - Rango de fechas: 2023-01-01 a 2024-01-01
     - Ventas totales: $2,345,678
     
     Aquí tienes un gráfico de tendencias..."
```

### Visualización Automática
```
Usuario: "Crea un gráfico de correlación"
IA: "He creado una matriz de correlación que muestra:
     - Correlación fuerte entre precio y calidad (0.85)
     - Correlación moderada entre edad y satisfacción (0.62)
     
     El gráfico está listo para revisar."
```

### Reporte Ejecutivo con Storytelling
```
Usuario: [Después de varias preguntas] "Genera un reporte ejecutivo"
IA: "He analizado toda nuestra conversación y generado un reporte que incluye:
     
     📋 RESUMEN EJECUTIVO:
     - 5 insights clave identificados
     - 3 patrones de negocio detectados
     - 4 recomendaciones estratégicas
     
     📊 ANÁLISIS DETALLADO:
     - Distribución de ventas por región
     - Correlación entre marketing y conversiones
     - Tendencias temporales identificadas
     
     🎯 RECOMENDACIONES:
     - Optimizar presupuesto de marketing en Q4
     - Expandir operaciones en región Norte
     - Implementar programa de fidelización
     
     El PDF está listo para descargar."
```

## 🎭 Storytelling de Datos

### ¿Qué es el Storytelling de Datos?

El **Storytelling de Datos** es una técnica que transforma análisis técnicos en narrativas ejecutivas que:
- **Conectan insights** con implicaciones de negocio
- **Presentan datos** como una historia coherente
- **Generan recomendaciones** accionables y específicas
- **Facilitan la toma de decisiones** ejecutiva

### Características del Storytelling en Okuo IA DataLab

#### 📋 **Análisis Inteligente de Conversaciones**
- **Agrupación automática** de preguntas y respuestas por temas
- **Identificación de patrones** y tendencias en los datos
- **Extracción de insights** relevantes para el negocio
- **Generación de recomendaciones** basadas en evidencia

#### 📊 **Reportes Ejecutivos Profesionales**
- **Resumen ejecutivo** con puntos clave
- **Análisis detallado** por temas identificados
- **Insights estratégicos** con implicaciones de negocio
- **Recomendaciones accionables** priorizadas
- **Visualizaciones integradas** con explicaciones claras

#### 🎨 **Diseño Corporativo**
- **Colores corporativos** consistentes
- **Tipografía profesional** (Inter font)
- **Estructura clara** y fácil de leer
- **Formato ejecutivo** listo para presentación

## 🐛 Solución de Problemas

### Error: "No such file or directory: temp_pdf_images/"
**Solución**: ✅ **CORREGIDO** - El problema de rutas relativas ha sido solucionado.

### Error: "Missing ScriptRunContext"
**Solución**: Usar `streamlit run main_app.py` en lugar de `python main_app.py`

### Error: "OPENAI_API_KEY not found"
**Solución**: Configurar la variable de entorno en el archivo `.env`

### Error: "StreamlitDuplicateElementKey"
**Solución**: ✅ **CORREGIDO** - Implementado sistema de claves únicas para elementos UI.

## 📚 Documentación

- **[Documentación Completa](DOCUMENTATION.md)**: Guía detallada del proyecto
- **[Diagrama de Arquitectura](ARCHITECTURE_DIAGRAM.md)**: Estructura técnica
- **[Guía de Desarrollo](DEVELOPER_GUIDE.md)**: Para contribuidores
- **[Changelog](CHANGELOG.md)**: Historial de cambios

## 🤝 Contribución

¡Las contribuciones son bienvenidas! Por favor:

1. **Fork** el repositorio
2. **Crea** una rama para tu funcionalidad (`git checkout -b feature/nueva-funcionalidad`)
3. **Commit** tus cambios (`git commit -m 'feat: agregar nueva funcionalidad'`)
4. **Push** a la rama (`git push origin feature/nueva-funcionalidad`)
5. **Abre** un Pull Request

### Estándares de Contribución

- **Código**: Seguir PEP 8 y usar type hints
- **Documentación**: Actualizar README y documentación relevante
- **Testing**: Agregar tests para nuevas funcionalidades
- **Commits**: Usar mensajes descriptivos y convencionales

## 📄 Licencia

Este proyecto está bajo la Licencia MIT - ver el archivo [LICENSE](LICENSE) para detalles.

## 🙏 Agradecimientos

- **OpenAI** por proporcionar acceso a modelos de lenguaje avanzados
- **Streamlit** por el framework de interfaz web
- **LangChain** por las herramientas de IA
- **Plotly** por las visualizaciones interactivas
- **ReportLab** por la generación de PDFs profesionales

---

**¿Listo para transformar tus datos en insights ejecutivos?** 🚀

[Empezar ahora](https://github.com/tu-usuario/AgenticDataAnalysis) | [Ver documentación](DOCUMENTATION.md) | [Reportar un problema](https://github.com/tu-usuario/AgenticDataAnalysis/issues) 