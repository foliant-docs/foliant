# Requires PyDrive: https://github.com/googledrive/PyDrive

from pydrive.drive import GoogleDrive
from pydrive.auth import GoogleAuth
import sys
import os

current_path = sys.argv[1]

gauth = GoogleAuth()
drive = GoogleDrive(gauth)

# TODO: Set ID with settings
file = drive.CreateFile({'id': "3F2AC8BC-66F7-4C80-8A0A-FBB969057760"})
file.SetContentFile(os.path.join(current_path,'output.docx'))
file.Upload({'convert': True})

