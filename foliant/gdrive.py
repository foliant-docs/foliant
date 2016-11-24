import os.path
import webbrowser
import pydrive.auth, pydrive.drive

def upload(document):
    """Upload .docx file to Google Drive and return a web view link to it."""

    auth = pydrive.auth.GoogleAuth()
    auth.LocalWebserverAuth()

    gdrive = pydrive.drive.GoogleDrive(auth)

    gdoc = gdrive.CreateFile({
        "title": os.path.splitext(os.path.basename(document))[0]
    })
    gdoc.SetContentFile(document)
    gdoc.Upload({"convert": True})

    webbrowser.open(gdoc["alternateLink"])

    return gdoc["alternateLink"]
