import os

def get_resource_path(relative_path):
    # Base directory is the project root
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    return os.path.join(base_dir, relative_path)

def load_text_resource(path):
    full_path = get_resource_path(path)
    if os.path.exists(full_path):
        with open(full_path, 'r', encoding='utf-8') as f:
            return f.read()
    return f"Resource not found: {path}"
