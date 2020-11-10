# from pydrive.auth import GoogleAuth

# # 848084185210-q6g400ans0ddc451tlak117dr7icvt8l.apps.googleusercontent.com
# # E2k0Khce2aMFmo7144jZ7gES

# gauth = GoogleAuth()
# gauth.LocalWebserverAuth(8080) # Creates local webserver and auto handles authentication.

import os
import shutil
from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive

gauth = GoogleAuth()
gauth.LocalWebserverAuth()

drive = GoogleDrive(gauth)

## Call train func

# shutil.make_archive("model", 'zip', "model/checkpoint/explicit_model")

# file = drive.CreateFile()
# file.SetContentFile("model.zip")
# file.Upload()

# print(file['id'])

file_list = drive.ListFile({'q': "'root' in parents and trashed=false"}).GetList()
for file1 in file_list:
    print('title: %s, id: %s' % (file1['title'], file1['id']))


# new_file = drive.CreateFile({'id': file['id']})
# new_file.GetContentFile('new_model.zip')


# with open("model/checkpoint/explicit_model/checkpoint","r") as file:
#     #do something here with file
#     file_drive = drive.CreateFile({'title':os.path.basename(file.name) })  
#     file_drive.SetContentString(file.read()) 
#     file_drive.Upload()

# file1 = drive.CreateFile({'title': 'Hello.txt'})  # Create GoogleDriveFile instance with title 'Hello.txt'.
# file1.SetContentString('Hello World!') # Set content of the file from given string.
# file1.Upload()