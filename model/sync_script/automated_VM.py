# # 848084185210-q6g400ans0ddc451tlak117dr7icvt8l.apps.googleusercontent.com
# # E2k0Khce2aMFmo7144jZ7gES

import os
import shutil
from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive
import sys

my_path = os.path.abspath(os.path.dirname(__file__))

# gauth = GoogleAuth()
# gauth.LoadCredentialsFile("mycreds.txt")
gauth = GoogleAuth(settings_file = os.path.join(my_path, "settings.yaml"))
gauth.LoadCredentialsFile(os.path.join(my_path, "mycreds.txt"))
if gauth.credentials is None:
    # Authenticate if they're not there
    # gauth.LocalWebserverAuth()
    gauth.CommandLineAuth()
elif gauth.access_token_expired:
    # Refresh them if expired
    gauth.Refresh()
else:
    # Initialize the saved creds
    gauth.Authorize()
# Save the current credentials to a file
gauth.SaveCredentialsFile(os.path.join(my_path,"mycreds.txt"))

drive = GoogleDrive(gauth)

# Get last model
file_list = drive.ListFile({'q': "'root' in parents and trashed=false"}).GetList()
for file1 in file_list:
    print('title: %s, id: %s' % (file1['title'], file1['id']))
    if file1['title'] == 'model.zip':
        model_id = file1['id']
    elif file1['title'] == 'movies.csv':
    	movie_id = file1['id']
    elif file1['title'] == 'explicit_fb.csv':
    	fb_id = file1['id']


new_file = drive.CreateFile({'id': movie_id})
new_file.GetContentFile(os.path.join(my_path,'../dataset/final_csv/movies.csv'))
new_file = drive.CreateFile({'id': fb_id})
new_file.GetContentFile(os.path.join(my_path,'../dataset/final_csv/explicit_fb.csv'))
new_file = drive.CreateFile({'id': model_id})
new_file.GetContentFile(os.path.join(my_path, '../checkpoint/model.zip'))

shutil.unpack_archive(os.path.join(my_path,'../checkpoint/model.zip'),
	extract_dir=os.path.join(my_path,'../checkpoint/model/'))
os.remove(os.path.join(my_path, '../checkpoint/model.zip'))