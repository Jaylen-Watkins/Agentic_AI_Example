from google.genai import types # type: ignore
from config import WORKING_DIR
from functions.get_file_content import get_file_content, schema_get_file_content
from functions.get_files_info import get_files_info, schema_get_files_info
from functions.run_python_file import run_python_file, schema_run_python_file
from functions.write_files import write_file, schema_write_file

function_map = {
    "get_files_info": get_files_info,
    "get_file_content": get_file_content,
    "run_python_file": run_python_file,
    "write_file": write_file,
}

available_functions = types.Tool(
    function_declarations=[schema_get_files_info,
                           schema_write_file,
                           schema_get_file_content,
                           schema_run_python_file],
    
)


def call_function(function_call, verbose=False):
    function_name = function_call.name or ""
    args = dict(function_call.args) if function_call.args else {}
    args["working_directory"] = WORKING_DIR

    if verbose:
        print(f"Calling function: {function_name}({function_call.args})")
    else:
        print(f" - Calling function: {function_name}")
    func = function_map.get(function_name)
    if func is None:
        return types.Content(
                role="tool",
                parts=[
                    types.Part.from_function_response(
                        name=function_name,
                        response={"error": f"Unknown function: {function_name}"}
                    )
                ],
            )
    function_result = func(**args)

    return types.Content(
            role="tool",
            parts=[
                types.Part.from_function_response(
                    name=function_name,
                    response={"result": function_result}
                )
            ],
        )