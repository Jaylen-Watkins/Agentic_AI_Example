
import os
from google.genai import types # type: ignore
from config import CHARACTER_LIMIT


def safe_path(filename, base_dir):
    # Joins the directory and filename, then resolves '..' and '.'
    joined = os.path.join(base_dir, filename)
    normalized = os.path.normpath(joined)
    
    # Check if the resulting path still starts with our allowed directory
    if not normalized.startswith(os.path.abspath(base_dir)):
        raise PermissionError(f"Security Alert: Access to {filename} is outside the sandbox.")
    return normalized

def get_file_content(working_directory, file_path):

    working_dir_abs = os.path.abspath(working_directory)
    target_file = os.path.normpath(os.path.join(working_dir_abs, file_path))

    # Will be True or False
    valid_target_file = os.path.commonpath([working_dir_abs, target_file]) == working_dir_abs

    if not valid_target_file:
        return f'Error: Cannot read "{file_path}" as it is outside the permitted working directory'

    if not os.path.isfile(target_file):
        return f'Error: File not found or is not a regular file: "{file_path}"'
    
    try:
        if safe_path(file_path, working_dir_abs) != target_file:
            return f'Error: Invalid file path: "{file_path}"'
        with open(target_file, 'r', encoding='utf-8') as f:
            content = f.read(CHARACTER_LIMIT)
            # After reading the first MAX_CHARS...
            if f.read(1):
                content += f'[...File "{file_path}" truncated at {CHARACTER_LIMIT} characters]'
        return content
    except UnicodeDecodeError:
        return f'Error: "{file_path}" appears to be a binary file and cannot be read as text.'
    except PermissionError:
        return f'Error: Permission denied to read "{file_path}"'
    except Exception as e:
        return f'Error: An error occurred while reading "{file_path}": {str(e)}'
    


schema_get_file_content = types.FunctionDeclaration(
    name="get_file_content",
    description="...",
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={
            "file_path": types.Schema(
                type=types.Type.STRING,
                description="...",
            ),
        },
        required=["file_path"],
    ),
)