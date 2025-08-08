import os

def write_file(working_directory, file_path, content):
    try:
        base_path = os.path.abspath(working_directory)
        target_path = os.path.abspath(os.path.join(working_directory, file_path))

        
        if not target_path.startswith(base_path):
            return f'Error: Cannot read "{file_path}" as it is outside the permitted working directory'
        
        os.makedirs(os.path.dirname(target_path), exist_ok=True) 

        with open(target_path, "w", encoding="utf-8") as f:
            content = f.write(content)
       
        return f'Successfully wrote to "{file_path}" ({content} characters written)'
        
        
    except Exception as e:
        return f"Error: {str(e)}"
    
