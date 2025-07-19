# 🤖 Okuo IA DataLab

> **Laboratorio de Análisis Inteligente de Datos** - Una aplicación web que combina IA conversacional con análisis de datos avanzado.

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://python.org)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.28+-red.svg)](https://streamlit.io)
[![LangChain](https://img.shields.io/badge/LangChain-0.1+-green.svg)](https://langchain.com)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

## 🎯 ¿Qué es Okuo IA DataLab?

Okuo IA DataLab es una aplicación web inteligente que permite a usuarios no técnicos realizar análisis complejos de datos a través de una interfaz conversacional natural. Combina la potencia de la inteligencia artificial con herramientas de visualización avanzadas.

### ✨ Características Principales

- 🤖 **IA Conversacional**: Análisis de datos mediante lenguaje natural
- 📊 **Visualizaciones Automáticas**: Gráficos interactivos con Plotly
- 📁 **Gestión Inteligente de Datos**: Carga y organización de archivos CSV
- 📄 **Reportes Profesionales**: Exportación automática a PDF
- 🔍 **Depuración Avanzada**: Herramientas para entender el proceso de análisis
- 🎨 **UI Moderna**: Interfaz intuitiva con Streamlit

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

### 3. Exportación de Resultados
1. Usa el botón **"📊 Exportar a PDF"**
2. Descarga el reporte ejecutivo profesional
3. Revisa el proceso en **"🔍 Depuración"**

## 🏗️ Arquitectura

```
┌─────────────────────────────────────┐
│           Streamlit UI              │
├─────────────────────────────────────┤
│         Python Agent                │
├─────────────────────────────────────┤
│        LangGraph Workflow           │
├─────────────────────────────────────┤
│         OpenAI API                  │
└─────────────────────────────────────┘
```

### Componentes Principales

- **`main_app.py`**: Punto de entrada de la aplicación
- **`PythonAnalysisAgent`**: Agente principal de análisis
- **`LangGraph Workflow`**: Flujo de trabajo de IA
- **`PDF Exporter`**: Generación de reportes
- **`File Manager`**: Gestión de archivos

## 🔧 Tecnologías Utilizadas

### Frontend
- **Streamlit**: Framework web para aplicaciones de datos
- **Plotly**: Visualizaciones interactivas
- **ReportLab**: Generación de PDFs

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

### Análisis Estadístico
```
Usuario: "Calcula estadísticas descriptivas"
IA: "Estadísticas descriptivas del dataset:
     
     Ventas:
     - Media: $1,234
     - Mediana: $987
     - Desviación estándar: $456
     - Mínimo: $100
     - Máximo: $5,000
     
     ¿Te gustaría ver un histograma de la distribución?"
```

## 🐛 Solución de Problemas

### Error: "No such file or directory: temp_pdf_images/"
**Solución**: ✅ **CORREGIDO** - El problema de rutas relativas ha sido solucionado.

### Error: "Missing ScriptRunContext"
**Solución**: Usar `streamlit run main_app.py` en lugar de `python main_app.py`

### Error: "OPENAI_API_KEY not found"
**Solución**: Configurar la variable de entorno en el archivo `.env`

## 📚 Documentación

- **[Documentación Completa](DOCUMENTATION.md)**: Guía detallada del proyecto
- **[Diagrama de Arquitectura](ARCHITECTURE_DIAGRAM.md)**: Estructura técnica
- **[Guía de Desarrollo](DEVELOPER_GUIDE.md)**: Para contribuidores

## 🤝 Contribución

¡Las contribuciones son bienvenidas! Por favor:

1. **Fork** el repositorio
2. **Crea** una rama para tu funcionalidad (`git checkout -b feature/nueva-funcionalidad`)
3. **Commit** tus cambios (`git commit -m 'feat: agregar nueva funcionalidad'`)
4. **Push** a la rama (`git push origin feature/nueva-funcionalidad`)
5. **Abre** un Pull Request

### Estándares de Contribución

- **Código**: Seguir PEP 8 y usar type hints
- **Documentación**: Docstrings en español
- **Tests**: Agregar tests para nuevas funcionalidades
- **Commits**: Usar [Conventional Commits](https://conventionalcommits.org/)

## 📄 Licencia

Este proyecto está bajo la Licencia MIT. Ver el archivo [LICENSE](LICENSE) para más detalles.

## 🙏 Agradecimientos

- **OpenAI** por proporcionar acceso a GPT-4o
- **Streamlit** por el framework web
- **LangChain** por las herramientas de IA
- **Plotly** por las visualizaciones interactivas

## 📞 Contacto

- **Desarrollador**: [Tu Nombre]
- **Email**: [tu-email@ejemplo.com]
- **Proyecto**: [https://github.com/tu-usuario/AgenticDataAnalysis](https://github.com/tu-usuario/AgenticDataAnalysis)

## 🔮 Roadmap

### Próximas Características
- [ ] Conexión a bases de datos
- [ ] Análisis de series temporales
- [ ] Machine Learning automático
- [ ] Exportación a múltiples formatos
- [ ] Colaboración en tiempo real

### En Desarrollo
- [ ] Optimización de rendimiento
- [ ] Más tipos de visualizaciones
- [ ] Integración con APIs externas

---

<div align="center">

**¿Te gustó el proyecto? ¡Dale una ⭐!**

*Construido con ❤️ para democratizar el análisis de datos*

</div> 