import os

def run_python_file(working_directory, file_path, args=[]):
    try:
        base_path = os.path.abspath(working_directory)
        full_path = os.path.abspath(os.path.join(working_directory, file_path))

        
        if not full_path.startswith(base_path):
            return f'Error: Cannot execute "{file_path}" as it is outside the permitted working directory'
        
        if not os.path.isfile(full_path):
            return f'File "{file_path}" not found.'
        
        if ".py" not in full_path:
            return f'Error: "{file_path}" is not a Python file.'
    
        #TODO  - subprocess work
