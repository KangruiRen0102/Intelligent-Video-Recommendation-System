from pathlib import Path
import os
from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive


# path = os.path.join(os.path.abspath(os.path.dirname(__file__)), "../dataset/final_csv/movies.csv")
# print(path)

# import pandas as pd
# movie_df = pd.read_csv(path)
# print(movie_df)

my_path = os.path.abspath(os.path.dirname(__file__))


gauth = GoogleAuth(settings_file = os.path.join(my_path, "settings.yaml"))
gauth.LoadCredentialsFile(os.path.join(my_path, "mycreds.txt"))
if gauth.credentials is None:
    # Authenticate if they're not there
    gauth.LocalWebserverAuth()
    # gauth.CommandLineAuth()
elif gauth.access_token_expired:
    # Refresh them if expired
    gauth.Refresh()
else:
    # Initialize the saved creds
    gauth.Authorize()
# Save the current credentials to a file
gauth.SaveCredentialsFile(os.path.join(my_path,"mycreds.txt"))

drive = GoogleDrive(gauth)

file_list = drive.ListFile({'q': "'root' in parents and trashed=false"}).GetList()
for file1 in file_list:
    print('title: %s, id: %s' % (file1['title'], file1['id']))
    if file1['title'] == 'model.zip':
        model_id = file1['id']
    elif file1['title'] == 'movies.csv':
    	movie_id = file1['id']
    elif file1['title'] == 'explicit_fb.csv':
    	fb_id = file1['id']
