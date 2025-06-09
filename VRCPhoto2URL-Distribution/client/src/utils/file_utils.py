def read_file(filepath):
    """Read the contents of a file."""
    with open(filepath, 'r') as file:
        return file.read()

def write_file(filepath, content):
    """Write content to a file."""
    with open(filepath, 'w') as file:
        file.write(content)

def delete_file(filepath):
    """Delete a file."""
    if os.path.exists(filepath):
        os.remove(filepath)
        return True
    return False

def get_file_extension(filepath):
    """Get the file extension."""
    return os.path.splitext(filepath)[1]

def is_image_file(filepath):
    """Check if the file is an image based on its extension."""
    image_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp', '.tiff', '.tif'}
    return get_file_extension(filepath).lower() in image_extensions

def copy_file(src, dst):
    """Copy a file from src to dst."""
    if os.path.exists(src):
        shutil.copy(src, dst)
        return True
    return False

def move_file(src, dst):
    """Move a file from src to dst."""
    if os.path.exists(src):
        shutil.move(src, dst)
        return True
    return False