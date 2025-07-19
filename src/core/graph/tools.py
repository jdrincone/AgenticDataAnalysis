from langchain_core.tools import tool
from langchain_experimental.utilities import PythonREPL

from langchain_core.messages import AIMessage
from typing import Annotated, Tuple
from langgraph.prebuilt import InjectedState
import sys
from io import StringIO
import os
import plotly
import plotly.graph_objects as go
import plotly.io as pio
import plotly.express as px
import pandas as pd
import sklearn
import pickle
import uuid
from src.config.settings import config

# Initialize PythonREPL with persistent variables
repl = PythonREPL()

# Global persistent variables for maintaining state across executions
persistent_vars = {}

# Plotly saving code template
plotly_saving_code = """import pickle
import uuid
import plotly
import os
from src.config.settings import config

for figure in plotly_figures:
    pickle_filename = os.path.join(config.PLOTLY_FIGURES_DIR, f"{uuid.uuid4()}.pickle")
    with open(pickle_filename, 'wb') as f:
        pickle.dump(figure, f)
"""

@tool(parse_docstring=True)
def complete_python_task(
        graph_state: Annotated[dict, InjectedState], thought: str, python_code: str
) -> Tuple[str, dict]:
    """Completes a python task using PythonREPL for better isolation and error handling

    Args:
        thought: Internal thought about the next action to be taken, and the reasoning behind it. This should be formatted in MARKDOWN and be high quality.
        python_code: Python code to be executed to perform analyses, create a new dataset or create a visualization.
    """
    # Initialize variables from graph state
    current_variables = graph_state.get("current_variables", {})
    
    # Load input datasets if not already loaded
    for input_dataset in graph_state.get("input_data", []):
        if input_dataset.variable_name not in current_variables:
            try:
                current_variables[input_dataset.variable_name] = pd.read_csv(input_dataset.data_path)
            except Exception as e:
                return f"Error loading dataset {input_dataset.variable_name}: {str(e)}", {
                    "intermediate_outputs": [{"thought": thought, "code": python_code, "output": f"Error loading dataset: {str(e)}"}]
                }
    
    # Ensure plotly figures directory exists
    plotly_dir = config.PLOTLY_FIGURES_DIR
    if not os.path.exists(plotly_dir):
        os.makedirs(plotly_dir, exist_ok=True)

    current_image_pickle_files = os.listdir(plotly_dir)
    
    try:
        # Prepare execution environment
        exec_globals = {
            'pd': pd,
            'plotly': plotly,
            'go': go,
            'px': px,
            'pio': pio,
            'sklearn': sklearn,
            'plotly_figures': [],
            **persistent_vars,
            **current_variables
        }
        
        # Execute code using PythonREPL for better isolation
        result = repl.run(python_code, globals=exec_globals)
        
        # Update persistent variables (excluding built-ins and modules)
        persistent_vars.update({
            k: v for k, v in exec_globals.items() 
            if k not in globals() and not k.startswith('_') and k not in ['pd', 'plotly', 'go', 'px', 'pio', 'sklearn']
        })
        
        # Handle plotly figures if any were created
        updated_state = {
            "intermediate_outputs": [{"thought": thought, "code": python_code, "output": result}],
            "current_variables": persistent_vars
        }

        if 'plotly_figures' in exec_globals and exec_globals['plotly_figures']:
            # Save plotly figures
            exec(plotly_saving_code, exec_globals)
            
            # Check for new image files
            new_image_folder_contents = os.listdir(plotly_dir)
            new_image_files = [file for file in new_image_folder_contents if file not in current_image_pickle_files]
            
            if new_image_files:
                updated_state["output_image_paths"] = new_image_files
            
            # Reset plotly_figures for next execution
            persistent_vars["plotly_figures"] = []

        return result, updated_state
        
    except Exception as e:
        error_msg = f"Error executing Python code: {str(e)}"
        return error_msg, {
            "intermediate_outputs": [{"thought": thought, "code": python_code, "output": error_msg}]
        }

class PythonAnalysisTool:
    """Tool for executing Python code analysis."""
    
    def __init__(self):
        """Initialize the Python analysis tool."""
        self.repl = PythonREPL()
        self.persistent_vars = {}
        self.latest_images = []
        
        # Ensure plotly figures directory exists
        if not os.path.exists(config.PLOTLY_FIGURES_DIR):
            os.makedirs(config.PLOTLY_FIGURES_DIR, exist_ok=True)
    
    def run(self, response_content: str, input_data: list) -> str:
        """Run Python code extracted from response content."""
        try:
            # Extract Python code from markdown blocks
            import re
            code_blocks = re.findall(r'```python\n(.*?)\n```', response_content, re.DOTALL)
            
            if not code_blocks:
                return "No se encontró código Python para ejecutar."
            
            # Load input datasets
            current_variables = {}
            for data in input_data:
                try:
                    current_variables[data.variable_name] = pd.read_csv(data.data_path)
                except Exception as e:
                    return f"Error cargando dataset {data.variable_name}: {str(e)}"
            
            # Track current images
            current_image_files = set(os.listdir(config.PLOTLY_FIGURES_DIR))
            
            # Initialize REPL with necessary variables
            init_code = f"""
import pandas as pd
import plotly
import plotly.graph_objects as go
import plotly.io as pio
import plotly.express as px
import sklearn
import pickle
import uuid
import os

# Load datasets
{chr(10).join([f'{var_name} = pd.read_csv("{data.data_path}")' for var_name, data in zip(current_variables.keys(), input_data)])}

# Initialize plotly_figures list
plotly_figures = []

# Set plotly template with corporate colors
pio.templates.default = "plotly_white"

# Define corporate color palette from config
corporate_colors = {config.CORPORATE_COLORS}

# Set default color sequence for plotly
import plotly.colors as pc
pc.DEFAULT_PLOTLY_COLORS = corporate_colors
"""
            
            # Execute initialization code
            self.repl.run(init_code)
            
            # Execute each code block
            results = []
            for i, code in enumerate(code_blocks):
                try:
                    # Execute code using PythonREPL
                    result = self.repl.run(code)
                    results.append(f"Bloque {i+1}:\n{result}")
                    
                    # Update persistent variables from the REPL's namespace
                    repl_vars = self.repl.locals
                    self.persistent_vars.update({
                        k: v for k, v in repl_vars.items() 
                        if k not in globals() and not k.startswith('_') and k not in ['pd', 'plotly', 'go', 'px', 'pio', 'sklearn', 'pickle', 'uuid', 'os']
                    })
                    
                    # Handle plotly figures if they exist in the REPL
                    if 'plotly_figures' in repl_vars and repl_vars['plotly_figures']:
                        print(f"Found {len(repl_vars['plotly_figures'])} plotly figures to save")
                        # Save plotly figures
                        for figure in repl_vars['plotly_figures']:
                            pickle_filename = os.path.join(config.PLOTLY_FIGURES_DIR, f"{uuid.uuid4()}.pickle")
                            with open(pickle_filename, 'wb') as f:
                                pickle.dump(figure, f)
                            print(f"Saved figure to {pickle_filename}")
                        
                        # Check for new image files
                        new_image_files = set(os.listdir(config.PLOTLY_FIGURES_DIR)) - current_image_files
                        self.latest_images.extend(list(new_image_files))
                        print(f"New images detected: {list(new_image_files)}")
                        
                        # Reset plotly_figures
                        if 'plotly_figures' in self.persistent_vars:
                            self.persistent_vars["plotly_figures"] = []
                    else:
                        print("No plotly_figures found in REPL")
                
                except Exception as e:
                    results.append(f"Error en bloque {i+1}: {str(e)}")
            
            return "\n\n".join(results)
            
        except Exception as e:
            return f"Error ejecutando código Python: {str(e)}"
    
    def get_latest_images(self) -> list:
        """Get the latest images created."""
        images = self.latest_images.copy()
        self.latest_images.clear()
        return images