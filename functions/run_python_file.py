import os
import subprocess
import sys
from google.genai import types # type: ignore
from config import MAX_OUTPUT_CHARS

def run_python_file(working_directory, file_path, args=None):
    working_dir_abs = os.path.abspath(working_directory)
    target_file = os.path.realpath(os.path.join(working_dir_abs, file_path))

    # Will be True or False
    valid_target_file = os.path.commonpath([working_dir_abs, target_file]) == working_dir_abs

    if not valid_target_file:
        return f'Error: Cannot execute "{file_path}" as it is outside the permitted working directory'

    if not os.path.isfile(target_file):
        return f'Error: "{file_path}" does not exist or is not a regular file'
    
    if not target_file.endswith('.py'):
        return f'Error: "{file_path}" is not a Python file'
    try:
        
        result = subprocess.run(
            [sys.executable,
                target_file] + (args or []),
                capture_output=True,
                text=True,
                timeout=30)
        stdout = result.stdout
        stderr = result.stderr

        # 3. Truncate output to protect context window/RAM
        if len(stdout) > MAX_OUTPUT_CHARS:
            stdout = stdout[:MAX_OUTPUT_CHARS] + "\n[...STDOUT Truncated...]"
        if len(stderr) > MAX_OUTPUT_CHARS:
            stderr = stderr[:MAX_OUTPUT_CHARS] + "\n[...STDERR Truncated...]"

        if result.returncode != 0:
            return f'Error: Process exited with code {result.returncode}\nStderr:\n{stderr}'
        if not stdout.strip() and not stderr.strip():
            return 'No output produced'
        return f'STDOUT:\n{stdout}\nSTDERR:\n{stderr}'
    except subprocess.TimeoutExpired:
        return f'Error: Execution of "{file_path}" timed out after 30 seconds'
    except Exception as e:
        return f'Error: executing Python file: "{file_path}": {str(e)}'
    

schema_run_python_file = types.FunctionDeclaration(
    name="run_python_file",
    description="Executes a Python file relative to the working directory",
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={
            "file_path": types.Schema(
                type=types.Type.STRING,
                description="Path to the file to execute, relative to the working directory",
            ),
            "args": types.Schema(
                type=types.Type.ARRAY,
                items=types.Schema(
                   type=types.Type.STRING,
                ),
                description="Optional list of arguments to pass to the Python script",
            ),
        },
        required=["file_path"],
    )
)