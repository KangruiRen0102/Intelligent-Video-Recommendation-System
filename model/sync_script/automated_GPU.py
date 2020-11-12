# # 848084185210-q6g400ans0ddc451tlak117dr7icvt8l.apps.googleusercontent.com
# # E2k0Khce2aMFmo7144jZ7gES

### Calling this function means the developer has decided
### to use a new model instead of the old one

import os
import shutil
from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive

gauth = GoogleAuth()
gauth.LoadCredentialsFile("mycreds.txt")
if gauth.credentials is None:
    # Authenticate if they're not there
    gauth.LocalWebserverAuth()
elif gauth.access_token_expired:
    # Refresh them if expired
    gauth.Refresh()
else:
    # Initialize the saved creds
    gauth.Authorize()
# Save the current credentials to a file
gauth.SaveCredentialsFile("mycreds.txt")


drive = GoogleDrive(gauth)

## New model is trained automatically

## Delete last version
file_list = drive.ListFile({'q': "'root' in parents and trashed=false"}).GetList()
for file1 in file_list:
    print('title: %s, id: %s' % (file1['title'], file1['id']))
    if file1['title'] == 'model.zip':
        file1.Trash()


## Delete 
shutil.make_archive("model", 'zip', "../checkpoint/model")
file = drive.CreateFile()
file.SetContentFile("model.zip")
file.Upload()
print(file['id'])


