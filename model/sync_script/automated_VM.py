# # 848084185210-q6g400ans0ddc451tlak117dr7icvt8l.apps.googleusercontent.com
# # E2k0Khce2aMFmo7144jZ7gES

import os
import shutil
from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive

gauth = GoogleAuth()
gauth.LocalWebserverAuth()

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

new_file = drive.CreateFile({'id': model_id})
new_file.GetContentFile('../checkpoint/model.zip')
new_file = drive.CreateFile({'id': movie_id})
new_file.GetContentFile('../dataset/final_csv/movies.csv')
new_file = drive.CreateFile({'id': fb_id})
new_file.GetContentFile('../dataset/final_csv/explicit_fb.csv')


shutil.unpack_archive('../checkpoint/model.zip', extract_dir='../checkpoint/model/')
os.remove('../checkpoint/model.zip')