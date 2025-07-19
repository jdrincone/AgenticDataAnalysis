# 🏗️ Diagrama de Arquitectura - Okuo IA DataLab

## 🔄 Flujo de Datos Completo

```mermaid
graph TB
    subgraph "Frontend (Streamlit)"
        A[Usuario] --> B[main_app.py]
        B --> C[Session State]
        C --> D[UI Components]
    end
    
    subgraph "Data Layer"
        D --> E[File Upload]
        E --> F[File Manager]
        F --> G[Data Dictionary]
        F --> H[CSV Files]
    end
    
    subgraph "Core Logic"
        D --> I[Chat Interface]
        I --> J[Python Agent]
        J --> K[LangGraph Workflow]
        K --> L[State Management]
    end
    
    subgraph "AI Processing"
        K --> M[Model Node]
        K --> N[Tools Node]
        N --> O[Python Execution]
        O --> P[Plotly Figures]
        P --> Q[Pickle Storage]
    end
    
    subgraph "Output Generation"
        Q --> R[PDF Export]
        R --> S[ReportLab]
        S --> T[PDF Download]
        P --> U[Streamlit Display]
    end
    
    style A fill:#e1f5fe
    style B fill:#f3e5f5
    style J fill:#e8f5e8
    style K fill:#fff3e0
    style O fill:#fce4ec
    style R fill:#f1f8e9
```

## 🧩 Componentes Detallados

### 1. **Frontend Layer**

```mermaid
graph LR
    subgraph "Streamlit UI"
        A[main_app.py] --> B[Header Component]
        A --> C[File Upload Component]
        A --> D[Chat Interface Component]
        A --> E[PDF Export Component]
        A --> F[Debug Component]
    end
    
    subgraph "State Management"
        G[Session State] --> H[Agent Instance]
        G --> I[Data Dictionary]
        G --> J[Selected Files]
        G --> K[Chat History]
    end
```

### 2. **Core Agent Architecture**

```mermaid
graph TD
    subgraph "PythonAnalysisAgent"
        A[process_query] --> B[Create Messages]
        B --> C[Prepare Input State]
        C --> D[Execute Graph]
        D --> E[Update State]
        E --> F[Return Result]
    end
    
    subgraph "LangGraph Workflow"
        G[Agent Node] --> H[Router]
        H --> I[Tools Node]
        H --> J[Model Node]
        I --> K[Python Execution]
        J --> L[Response Generation]
        K --> M[State Update]
        L --> M
    end
```

### 3. **Data Flow Architecture**

```mermaid
graph LR
    subgraph "Input Processing"
        A[CSV Upload] --> B[File Validation]
        B --> C[Data Loading]
        C --> D[Data Dictionary Update]
    end
    
    subgraph "Analysis Pipeline"
        D --> E[Query Processing]
        E --> F[Python Code Execution]
        F --> G[Data Analysis]
        G --> H[Visualization Generation]
    end
    
    subgraph "Output Generation"
        H --> I[Plotly Figures]
        I --> J[Pickle Storage]
        J --> K[PDF Generation]
        K --> L[File Download]
    end
```

## 🔧 Herramientas y Dependencias

### Stack Tecnológico

```mermaid
graph TB
    subgraph "Frontend"
        A[Streamlit] --> B[Plotly]
        A --> C[ReportLab]
    end
    
    subgraph "Backend"
        D[Python 3.8+] --> E[LangChain]
        D --> F[LangGraph]
        D --> G[OpenAI API]
    end
    
    subgraph "Data Processing"
        H[Pandas] --> I[NumPy]
        H --> J[Scikit-learn]
        H --> K[Plotly]
    end
    
    subgraph "File Management"
        L[Pathlib] --> M[Pickle]
        L --> N[CSV]
        L --> O[PDF]
    end
```

## 📊 Estados del Sistema

### 1. **Estado de la Aplicación**

```mermaid
stateDiagram-v2
    [*] --> Initialized
    Initialized --> FileUploaded: Upload CSV
    FileUploaded --> FilesSelected: Select Files
    FilesSelected --> ChatReady: Navigate to Chat
    ChatReady --> Processing: Send Query
    Processing --> ResultsReady: Analysis Complete
    ResultsReady --> ChatReady: New Query
    ResultsReady --> PDFExport: Export Request
    PDFExport --> ResultsReady: Export Complete
    ChatReady --> FilesSelected: Change Files
```

### 2. **Estado del Agente**

```mermaid
stateDiagram-v2
    [*] --> Idle
    Idle --> Processing: Query Received
    Processing --> Executing: Graph Invoked
    Executing --> Analyzing: Python Code Running
    Analyzing --> Visualizing: Creating Plots
    Visualizing --> Complete: Results Ready
    Complete --> Idle: State Reset
    Executing --> Error: Exception
    Error --> Idle: Error Handled
```

## 🔐 Seguridad y Validación

### Capas de Seguridad

```mermaid
graph TD
    subgraph "Input Validation"
        A[File Upload] --> B[Extension Check]
        B --> C[Size Validation]
        C --> D[Content Validation]
    end
    
    subgraph "Code Execution"
        D --> E[Sandboxed Environment]
        E --> F[Library Restrictions]
        F --> G[Output Capture]
    end
    
    subgraph "File Management"
        G --> H[Path Sanitization]
        H --> I[Directory Isolation]
        I --> J[Cleanup Procedures]
    end
```

## 📈 Escalabilidad

### Arquitectura Escalable

```mermaid
graph TB
    subgraph "Current Architecture"
        A[Single Instance] --> B[Local Storage]
        B --> C[File-based State]
    end
    
    subgraph "Future Scalability"
        D[Multiple Instances] --> E[Database Storage]
        E --> F[Session Management]
        F --> G[Load Balancing]
        G --> H[Microservices]
    end
```

## 🔄 Ciclo de Vida de una Consulta

```mermaid
sequenceDiagram
    participant U as Usuario
    participant UI as Streamlit UI
    participant A as Python Agent
    participant G as LangGraph
    participant T as Tools
    participant M as Model
    participant S as Storage
    
    U->>UI: Subir CSV
    UI->>S: Guardar archivo
    U->>UI: Seleccionar archivos
    U->>UI: Enviar consulta
    UI->>A: process_query()
    A->>G: invoke()
    G->>M: call_model()
    M->>G: response
    G->>T: call_tools()
    T->>T: execute_python()
    T->>S: save_plotly_figure()
    T->>G: result
    G->>A: final_result
    A->>UI: update_state()
    UI->>U: mostrar resultados
    U->>UI: exportar PDF
    UI->>S: generate_pdf()
    S->>U: download_pdf()
```

## 🎯 Puntos de Integración

### APIs y Extensiones

```mermaid
graph LR
    subgraph "Current Integrations"
        A[OpenAI API] --> B[GPT-4o]
        C[Plotly] --> D[Interactive Charts]
        E[ReportLab] --> F[PDF Generation]
    end
    
    subgraph "Future Integrations"
        G[Database APIs] --> H[PostgreSQL/MySQL]
        I[ML APIs] --> J[AutoML Services]
        K[Cloud Storage] --> L[AWS S3/GCP]
        M[Collaboration] --> N[Real-time Sharing]
    end
```

---

*Diagramas generados con Mermaid - Okuo IA DataLab Architecture v1.0.0* 