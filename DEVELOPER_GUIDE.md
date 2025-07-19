# 👨‍💻 Guía de Desarrollo - Okuo IA DataLab

## 🎯 Introducción

Esta guía está diseñada para desarrolladores que quieran contribuir, extender o mantener el proyecto Okuo IA DataLab. Incluye estándares de código, patrones de diseño, y mejores prácticas.

---

## 🏗️ Arquitectura de Desarrollo

### Patrones de Diseño Utilizados

#### 1. **Arquitectura en Capas**
```
┌─────────────────────────────────────┐
│           Presentation Layer        │  ← Streamlit UI
├─────────────────────────────────────┤
│           Business Logic Layer      │  ← Python Agent
├─────────────────────────────────────┤
│           Data Access Layer         │  ← File Manager
├─────────────────────────────────────┤
│           Infrastructure Layer      │  ← LangGraph, OpenAI
└─────────────────────────────────────┘
```

#### 2. **Patrón Observer (Event-Driven)**
- **LangGraph Workflow**: Maneja eventos de estado
- **Streamlit Session State**: Notifica cambios de UI
- **Agent State Management**: Propaga cambios de estado

#### 3. **Factory Pattern**
```python
# Ejemplo: Creación de agentes
class AgentFactory:
    @staticmethod
    def create_agent(agent_type: str) -> BaseAgent:
        if agent_type == "python":
            return PythonAnalysisAgent()
        # Extensible para futuros tipos
```

---

## 📝 Estándares de Código

### 1. **Convenciones de Nomenclatura**

#### Archivos y Directorios
```python
# ✅ Correcto
src/core/agents/python_agent.py
src/ui/components/chat_interface.py
src/utils/file_utils.py

# ❌ Incorrecto
src/core/agents/PythonAgent.py
src/ui/components/ChatInterface.py
```

#### Clases
```python
# ✅ Correcto - PascalCase
class PythonAnalysisAgent:
class FileManager:
class ChatMessage:

# ❌ Incorrecto
class python_analysis_agent:
class fileManager:
```

#### Funciones y Variables
```python
# ✅ Correcto - snake_case
def process_query():
def load_plotly_figure():
def render_chat_interface():

# ❌ Incorrecto
def ProcessQuery():
def loadPlotlyFigure():
```

#### Constantes
```python
# ✅ Correcto - UPPER_SNAKE_CASE
APP_NAME = "Okuo IA DataLab"
MAX_UPLOAD_SIZE = 2000
PRIMARY_COLOR = "#1C8074"
```

### 2. **Type Hints (Obligatorios)**

```python
from typing import List, Dict, Any, Optional, Union
from pathlib import Path
import pandas as pd

def process_data(
    file_path: Path,
    options: Optional[Dict[str, Any]] = None
) -> pd.DataFrame:
    """Procesa datos desde un archivo."""
    pass

def create_visualization(
    data: pd.DataFrame,
    chart_type: str = "scatter"
) -> "plotly.graph_objects.Figure":
    """Crea una visualización."""
    pass
```

### 3. **Docstrings (Estilo Google)**

```python
def analyze_dataset(
    data: pd.DataFrame,
    analysis_type: str,
    parameters: Optional[Dict[str, Any]] = None
) -> AnalysisResult:
    """Realiza análisis estadístico en un dataset.
    
    Args:
        data: DataFrame con los datos a analizar.
        analysis_type: Tipo de análisis ('descriptive', 'correlation', etc.).
        parameters: Parámetros adicionales para el análisis.
        
    Returns:
        AnalysisResult con los resultados del análisis.
        
    Raises:
        ValueError: Si el tipo de análisis no es válido.
        DataError: Si los datos no son compatibles.
        
    Example:
        >>> result = analyze_dataset(df, 'descriptive')
        >>> print(result.summary)
    """
    pass
```

### 4. **Manejo de Errores**

```python
# ✅ Correcto - Manejo específico de errores
try:
    result = process_data(file_path)
except FileNotFoundError:
    logger.error(f"Archivo no encontrado: {file_path}")
    raise
except pd.errors.EmptyDataError:
    logger.warning(f"Archivo vacío: {file_path}")
    return pd.DataFrame()
except Exception as e:
    logger.error(f"Error inesperado: {e}")
    raise

# ❌ Incorrecto - Captura genérica
try:
    result = process_data(file_path)
except:
    pass  # Silenciar errores
```

---

## 🔧 Configuración del Entorno de Desarrollo

### 1. **Setup del Entorno**

```bash
# Clonar repositorio
git clone <repository-url>
cd AgenticDataAnalysis

# Crear entorno virtual
python3.12 -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate  # Windows

# Instalar dependencias de desarrollo
pip install -r requirements.txt
pip install -r requirements-dev.txt  # Si existe
```

### 2. **Pre-commit Hooks**

```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.4.0
    hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer
      - id: check-yaml
      - id: check-added-large-files

  - repo: https://github.com/psf/black
    rev: 23.3.0
    hooks:
      - id: black

  - repo: https://github.com/pycqa/isort
    rev: 5.12.0
    hooks:
      - id: isort

  - repo: https://github.com/pycqa/flake8
    rev: 6.0.0
    hooks:
      - id: flake8
```

### 3. **Configuración de IDE (VS Code)**

```json
// .vscode/settings.json
{
    "python.defaultInterpreterPath": "./venv/bin/python",
    "python.linting.enabled": true,
    "python.linting.flake8Enabled": true,
    "python.formatting.provider": "black",
    "python.sortImports.args": ["--profile", "black"],
    "editor.formatOnSave": true,
    "editor.codeActionsOnSave": {
        "source.organizeImports": true
    }
}
```

---

## 🧪 Testing

### 1. **Estructura de Tests**

```
tests/
├── unit/
│   ├── test_agents.py
│   ├── test_models.py
│   └── test_utils.py
├── integration/
│   ├── test_workflow.py
│   └── test_pdf_export.py
├── fixtures/
│   ├── sample_data.csv
│   └── test_config.json
└── conftest.py
```

### 2. **Ejemplo de Test Unitario**

```python
# tests/unit/test_agents.py
import pytest
from unittest.mock import Mock, patch
from src.core.agents.python_agent import PythonAnalysisAgent
from src.models.data_models import InputData

class TestPythonAnalysisAgent:
    """Tests para PythonAnalysisAgent."""
    
    @pytest.fixture
    def agent(self):
        """Fixture para crear un agente de prueba."""
        return PythonAnalysisAgent()
    
    @pytest.fixture
    def sample_data(self):
        """Fixture para datos de prueba."""
        return [
            InputData(
                variable_name="test_data",
                data_path="tests/fixtures/sample_data.csv",
                data_description="Datos de prueba"
            )
        ]
    
    def test_agent_initialization(self, agent):
        """Test de inicialización del agente."""
        assert agent.chat_history == []
        assert agent.intermediate_outputs == []
        assert agent.output_image_paths == {}
    
    def test_process_query_success(self, agent, sample_data):
        """Test de procesamiento exitoso de consulta."""
        with patch('src.core.agents.python_agent.StateGraph') as mock_graph:
            mock_graph.return_value.invoke.return_value = {
                "messages": [Mock(content="Respuesta de prueba")],
                "output_image_paths": []
            }
            
            result = agent.process_query("Consulta de prueba", sample_data)
            
            assert result.query == "Consulta de prueba"
            assert result.response == "Respuesta de prueba"
    
    def test_process_query_empty_input(self, agent):
        """Test de consulta vacía."""
        with pytest.raises(ValueError):
            agent.process_query("", [])
```

### 3. **Ejemplo de Test de Integración**

```python
# tests/integration/test_workflow.py
import pytest
import pandas as pd
from pathlib import Path
from src.core.agents.python_agent import PythonAnalysisAgent

class TestWorkflowIntegration:
    """Tests de integración para el flujo de trabajo."""
    
    def test_complete_analysis_workflow(self, tmp_path):
        """Test del flujo completo de análisis."""
        # Crear datos de prueba
        test_data = pd.DataFrame({
            'x': [1, 2, 3, 4, 5],
            'y': [2, 4, 1, 3, 5]
        })
        test_file = tmp_path / "test_data.csv"
        test_data.to_csv(test_file, index=False)
        
        # Crear agente
        agent = PythonAnalysisAgent()
        
        # Procesar consulta
        input_data = [InputData(
            variable_name="test_data",
            data_path=test_file,
            data_description="Datos de prueba"
        )]
        
        result = agent.process_query(
            "Crea un gráfico de dispersión de x vs y",
            input_data
        )
        
        # Verificar resultados
        assert result.query == "Crea un gráfico de dispersión de x vs y"
        assert len(agent.get_chat_history()) > 0
        assert len(agent.get_output_images(0)) > 0
```

---

## 🔄 Flujo de Desarrollo

### 1. **Git Workflow**

```bash
# 1. Crear branch para nueva funcionalidad
git checkout -b feature/nueva-funcionalidad

# 2. Hacer cambios y commits
git add .
git commit -m "feat: agregar nueva funcionalidad de análisis"

# 3. Ejecutar tests
pytest tests/

# 4. Verificar calidad de código
flake8 src/
black --check src/
isort --check-only src/

# 5. Push y crear Pull Request
git push origin feature/nueva-funcionalidad
```

### 2. **Conventional Commits**

```bash
# Tipos de commits
feat: nueva funcionalidad
fix: corrección de bug
docs: cambios en documentación
style: cambios de formato
refactor: refactorización de código
test: agregar o modificar tests
chore: tareas de mantenimiento

# Ejemplos
git commit -m "feat: agregar soporte para análisis de series temporales"
git commit -m "fix: corregir error en exportación PDF"
git commit -m "docs: actualizar guía de instalación"
```

### 3. **Pull Request Template**

```markdown
## Descripción
Breve descripción de los cambios realizados.

## Tipo de Cambio
- [ ] Bug fix
- [ ] Nueva funcionalidad
- [ ] Breaking change
- [ ] Documentación

## Cambios Realizados
- Lista de cambios específicos

## Tests
- [ ] Tests unitarios pasan
- [ ] Tests de integración pasan
- [ ] Tests manuales realizados

## Checklist
- [ ] Código sigue estándares del proyecto
- [ ] Documentación actualizada
- [ ] No hay warnings de linting
- [ ] Tests agregados para nueva funcionalidad
```

---

## 🚀 Deployment

### 1. **Configuración de Producción**

```python
# src/config/production.py
import os
from src.config.settings import AppConfig

class ProductionConfig(AppConfig):
    """Configuración para producción."""
    
    # Configuraciones de seguridad
    DEBUG = False
    SECRET_KEY = os.getenv("SECRET_KEY")
    
    # Configuraciones de base de datos
    DATABASE_URL = os.getenv("DATABASE_URL")
    
    # Configuraciones de logging
    LOG_LEVEL = "INFO"
    LOG_FILE = "/var/log/okuo_datalab.log"
    
    # Configuraciones de cache
    CACHE_TYPE = "redis"
    CACHE_REDIS_URL = os.getenv("REDIS_URL")
```

### 2. **Docker Configuration**

```dockerfile
# Dockerfile
FROM python:3.9-slim

WORKDIR /app

# Instalar dependencias del sistema
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copiar requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar código
COPY . .

# Exponer puerto
EXPOSE 8501

# Comando de inicio
CMD ["streamlit", "run", "main_app.py", "--server.port=8501", "--server.address=0.0.0.0"]
```

### 3. **Docker Compose**

```yaml
# docker-compose.yml
version: '3.8'

services:
  app:
    build: .
    ports:
      - "8501:8501"
    environment:
      - OPENAI_API_KEY=${OPENAI_API_KEY}
      - DATABASE_URL=${DATABASE_URL}
    volumes:
      - ./uploads:/app/uploads
      - ./assets:/app/assets
    depends_on:
      - redis
      - postgres

  redis:
    image: redis:alpine
    ports:
      - "6379:6379"

  postgres:
    image: postgres:13
    environment:
      - POSTGRES_DB=okuo_datalab
      - POSTGRES_USER=postgres
      - POSTGRES_PASSWORD=${DB_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data

volumes:
  postgres_data:
```

---

## 🔍 Debugging

### 1. **Logging Configuration**

```python
# src/utils/logger.py
import logging
import sys
from pathlib import Path
from src.config.settings import config

def setup_logger(name: str, level: str = "INFO") -> logging.Logger:
    """Configura un logger personalizado."""
    
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, level.upper()))
    
    # Handler para consola
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_format = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    console_handler.setFormatter(console_format)
    
    # Handler para archivo
    log_file = config.BASE_DIR / "logs" / f"{name}.log"
    log_file.parent.mkdir(exist_ok=True)
    file_handler = logging.FileHandler(log_file)
    file_handler.setLevel(logging.DEBUG)
    file_format = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s'
    )
    file_handler.setFormatter(file_format)
    
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)
    
    return logger
```

### 2. **Debug Tools**

```python
# src/utils/debug.py
import traceback
import sys
from typing import Any, Dict
from functools import wraps

def debug_function(func):
    """Decorator para debugging de funciones."""
    @wraps(func)
    def wrapper(*args, **kwargs):
        print(f"🔍 DEBUG: Llamando {func.__name__}")
        print(f"   Args: {args}")
        print(f"   Kwargs: {kwargs}")
        
        try:
            result = func(*args, **kwargs)
            print(f"✅ DEBUG: {func.__name__} completado exitosamente")
            return result
        except Exception as e:
            print(f"❌ DEBUG: Error en {func.__name__}: {e}")
            traceback.print_exc()
            raise
    
    return wrapper

def inspect_object(obj: Any, name: str = "object") -> None:
    """Inspecciona un objeto y muestra su información."""
    print(f"🔍 INSPECT: {name}")
    print(f"   Type: {type(obj)}")
    print(f"   Dir: {dir(obj)}")
    if hasattr(obj, '__dict__'):
        print(f"   Dict: {obj.__dict__}")
```

---

## 📚 Recursos Adicionales

### 1. **Documentación de Referencia**
- [Streamlit Documentation](https://docs.streamlit.io/)
- [LangChain Documentation](https://python.langchain.com/)
- [LangGraph Documentation](https://langchain-ai.github.io/langgraph/)
- [Plotly Documentation](https://plotly.com/python/)

### 2. **Herramientas de Desarrollo**
- **Linting**: flake8, pylint
- **Formatting**: black, isort
- **Testing**: pytest, coverage
- **Type Checking**: mypy
- **Documentation**: Sphinx, MkDocs

### 3. **Mejores Prácticas**
- **SOLID Principles**: Aplicar principios de diseño
- **DRY**: Don't Repeat Yourself
- **KISS**: Keep It Simple, Stupid
- **YAGNI**: You Aren't Gonna Need It

---

*Guía de Desarrollo - Okuo IA DataLab v1.0.0* 