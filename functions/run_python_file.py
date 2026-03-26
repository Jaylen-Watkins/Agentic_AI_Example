import os
import subprocess
def run_python_file(working_directory, file_path, args=None):
    working_dir_abs = os.path.abspath(working_directory)
    target_file = os.path.normpath(os.path.join(working_dir_abs, file_path))

    # Will be True or False
    valid_target_file = os.path.commonpath([working_dir_abs, target_file]) == working_dir_abs

    if not valid_target_file:
        return f'Error: Cannot execute "{file_path}" as it is outside the permitted working directory'

    if not os.path.isfile(target_file):
        return f'Error: "{file_path}" does not exist or is not a regular file'
    
    if not target_file.endswith('.py'):
        return f'Error: "{file_path}" is not a Python file'
    try:
        
        result = subprocess.run(['python', target_file] + (args or []), capture_output=True, text=True)
        if result.returncode != 0:
            return f'Error: Process exited with code {result.returncode}\nStderr:\n{result.stderr}'
        if not result.stdout.strip() and not result.stderr.strip():
            return 'No output produced'
        return f'STDOUT:\n{result.stdout}\nSTDERR:\n{result.stderr}'
    except Exception as e:
        return f'Error: executing Python file: "{file_path}": {str(e)}'