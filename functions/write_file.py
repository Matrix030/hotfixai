import os
from google.genai import types

def write_file(working_directory, file_path, content):
    abs_working_dir = os.path.abspath(working_directory)
    abs_file_path = os.path.abspath(os.path.join(working_directory, file_path))
    if not abs_file_path.startswith(abs_working_dir):
        return f'Error: Cannot write to "{file_path}" as it is outside the permitted working directory'
    if not os.path.exists(abs_file_path):
        try:
            os.makedirs(os.path.dirname(abs_file_path), exist_ok=True)
        except Exception as e:
            return f"Error: creating directory: {e}"
    if os.path.exists(abs_file_path) and os.path.isdir(abs_file_path):
        return f'Error: "{file_path}" is a directory, not a file'
    try:
        with open(abs_file_path, "w") as f:
            f.write(content)
        return (
            f'Successfully wrote to "{file_path}" ({len(content)} characters written)'
        )
    except Exception as e:
        return f"Error: writing to file: {e}"
   
schema_write_file = types.FunctionDeclaration(
    name="write_file",
    description=(
        "Writes text content to a file within the working directory. "
        "Creates parent directories if they do not exist. Overwrites the file if it already exists. "
        "Rejects paths outside the working directory and attempts to write to a directory."
    ),
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={
            "file_path": types.Schema(
                type=types.Type.STRING,
                description="Path to the target file, relative to the working directory (parent folders will be created as needed).",
            ),
            "content": types.Schema(
                type=types.Type.STRING,
                description="The textual content to write into the file.",
            ),
        },
        required=["file_path", "content"],
    ),
)
