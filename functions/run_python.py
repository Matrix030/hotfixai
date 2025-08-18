import os
import subprocess

def run_python_file(working_directory, file_path, args=[]):
    abs_working_dir = os.path.abspath(working_directory)
    abs_file_path = os.path.abspath(os.path.join(working_directory, file_path))
    if not abs_file_path.startswith(abs_working_dir):
        return f'Error: Cannot write to "{file_path}" as it is outside the permitted working directory'
    
    if not os.path.exists(abs_file_path):
        return f'Error: File "{file_path}" not found.'
        
    if not file_path.endswith(".py"):
        return f'Error: "{file_path}" is not a Python file.'

    try:
        completed = subprocess.run(
        ["python3", abs_file_path] + args,
        cwd = abs_working_dir,
        capture_output = True,
        text = True,
        timeout = 30
    )

        stdout = completed.stdout.strip()
        stderr = completed.stderr.strip() 
        output_parts = []

        if stdout:
            output_parts.append("STDOUT:\n" + stdout)
        if stderr:
            output_parts.append("STDERR:\n" + stderr)
        if completed.returncode != 0:
            output_parts.append(f"Process exited with code {completed.returncode}")
        
        if not output_parts:
            return "No output produced."
   
    except Exception as e:
        return f'Error: executing Python file: {e}'
    
