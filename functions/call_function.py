import os
from google.genai import types

# assuming these are already imported at the top of main.py:
from functions.get_files_info import get_files_info
from functions.get_file_contents import get_file_content
from functions.write_file import write_file
from functions.run_python import run_python_file

def call_function(function_call_part, verbose=False):
    """
    function_call_part: types.FunctionCall (.name: str, .args: dict-like)
    returns: types.Content (role="tool") with a Part.from_function_response(...)
    """
    function_name = function_call_part.name
    args = dict(function_call_part.args or {})

    if verbose:
        print(f"Calling function: {function_name}({args})")
    else:
        print(f" - Calling function: {function_name}")

    # required working directory for this assignment
    working_dir = os.path.abspath("./calculator")
    args["working_directory"] = working_dir

    # map function names -> callables
    dispatch = {
        "get_files_info": get_files_info,
        "get_file_content": get_file_content,
        "write_file": write_file,
        "run_python_file": run_python_file,
    }

    if function_name not in dispatch:
        # Return a tool turn with an error payload
        return types.Content(
            role="tool",
            parts=[
                types.Part.from_function_response(
                    name=function_name,
                    response={"error": f"Unknown function: {function_name}"},
                )
            ],
        )

    # call the function with kwargs
    try:
        result_str = dispatch[function_name](**args)
    except Exception as e:
        result_str = f"Error while executing '{function_name}': {e}"

    # Return a tool turn with the result payload
    return types.Content(
        role="tool",
        parts=[
            types.Part.from_function_response(
                name=function_name,
                response={"result": result_str},
            )
        ],
    )

