import os

def get_files_info(working_directory, directory="."):
    try:
        base_path = os.path.abspath(working_directory)
        target_path = os.path.abspath(os.path.join(working_directory, directory))


        if not target_path.startswith(base_path):
            return f'Error: Cannot list "{directory}" as it is outside the the permitted working directory'

        if not os.path.isdir(target_path):
            return f'Error: "{directory}" is not a directory'

        result_lines = [] 
        for entry in os.listdir(target_path):
            entry_path = os.path.join(target_path, entry)
            try:
                size = os.path.join(target_path, entry)
                is_dir = os.path.isdir(entry_path)
                result_lines.append(f"- {entry}: file_size={size} bytes, is_dir={is_dir}")
            except Exception as e:
                result_lines.append(f"- {entry}: Error retrieving info: {e}")
     
        return "\n".join(result_lines)

    except Exception as e:
            return f"Error: {str(e)}"

