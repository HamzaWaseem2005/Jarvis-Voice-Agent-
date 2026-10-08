from langchain_core.tools import tool
import sys
import io

@tool
def run_python_code(code: str) -> str:
    """Executes a short Python code snippet safely and returns the output or result."""
    old_stdout = sys.stdout
    redirected_output = io.StringIO()
    sys.stdout = redirected_output
    
    try:
        exec(code, {})
        sys.stdout = old_stdout
        output = redirected_output.getvalue()
        return output if output.strip() else "Code executed successfully with no output."
    except Exception as e:
        sys.stdout = old_stdout
        return f"Error executing code: {str(e)}"