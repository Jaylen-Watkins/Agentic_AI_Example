import os

def write_file(working_directory, file_path, content):
    working_dir_abs = os.path.abspath(working_directory)
    target_file = os.path.normpath(os.path.join(working_dir_abs, file_path))

    # Will be True or False
    valid_target_file = os.path.commonpath([working_dir_abs, target_file]) == working_dir_abs

    if not valid_target_file:
        return f'Error: Cannot write to "{file_path}" as it is outside the permitted working directory'
    if os.path.isdir(target_file):
        return f'Error: Cannot write to "{file_path}" as it is a directory'
    try:
        with open(target_file, 'w', encoding='utf-8') as f:
            f.write(content)
        return f'Successfully wrote to "{file_path}" ({len(content)} characters written)'
    except PermissionError:
        return f'Error: Permission denied to write to "{file_path}"'
    except Exception as e:
        return f'Error: An error occurred while writing to "{file_path}": {str(e)}'