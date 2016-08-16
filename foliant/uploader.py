from . import gdrive

def upload(document_path, secret_path):
    return gdrive.upload(document_path, secret_path)
