import os
from google.genai import types # type: ignore

def safe_path(filename, base_dir):
    """Resolves the real path and ensures it is within the base_dir sandbox."""
    # We use realpath to resolve symlinks that might point outside the box
    joined = os.path.join(base_dir, filename)
    normalized = os.path.realpath(joined)
    
    if not normalized.startswith(os.path.abspath(base_dir)):
        raise PermissionError(f"Security Alert: Access to {filename} is outside the sandbox.")
    return normalized

def write_file(working_directory, file_path, content):
    working_dir_abs = os.path.abspath(working_directory)
    
    try:
        target_file = safe_path(file_path, working_dir_abs)

        # Prevent the AI from overwriting the agent's own source code
        protected_files = ["main.py", "config.py", ".env", "call_function.py"]
        if os.path.basename(target_file) in protected_files:
            return f"Error: '{file_path}' is a protected system file and cannot be modified."


        target_dir = os.path.dirname(target_file)
        if not os.path.exists(target_dir):
            os.makedirs(target_dir, exist_ok=True)


        with open(target_file, 'w', encoding='utf-8') as f:
            f.write(content)
            
        return f"Successfully wrote {len(content)} characters to {file_path}"

    except PermissionError as e:
        return f"Error: {str(e)}"
    except Exception as e:
        return f"Error writing to '{file_path}': {str(e)}"

# Schema for the Gemini API
schema_write_file = types.FunctionDeclaration(
    name="write_file",
    description="Writes or overwrites a file within the working directory.",
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={
            "file_path": types.Schema(
                type=types.Type.STRING,
                description="The relative path where the file should be saved.",
            ),
            "content": types.Schema(
                type=types.Type.STRING,
                description="The full string content to write to the file.",
            ),
        },
        required=["file_path", "content"],
    ),
)