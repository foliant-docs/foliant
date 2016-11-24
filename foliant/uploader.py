"""Document uploader for foliant. Implements "upload" subcommand."""

from . import gdrive

def upload(document_path):
    """Upload .docx file to Google Drive."""

    return gdrive.upload(document_path)
