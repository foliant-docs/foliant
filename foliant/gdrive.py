import pydrive.auth

def upload(document, secret):
    auth = pydrive.auth.GoogleAuth()
    auth.LocalWebserverAuth()

    return "link"