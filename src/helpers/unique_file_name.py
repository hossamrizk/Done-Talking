import uuid

def unique_file_name(file_extension: str):
    return f"output_{uuid.uuid4().hex}.{file_extension}"