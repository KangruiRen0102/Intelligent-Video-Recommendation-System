import numpy
import csv
import json
import pandas as pd
from io import StringIO
import sys
sys.path.insert(0,'../..')
from data.scripts.extract_mongo_data import mongo_db, get_users

movies = []

def clear_movie():
    global movies
    with open('../dataset/raw_data/movies_data') as f:
        movies = json.load(f)

    with open("../dataset/final_csv/movies.csv", 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["web_id", "movie_id", "genres"]) 

        for index, movie in enumerate(movies):
            if 'message' in movie and movie['message'] == 'movie not found':
                continue
            else:
                try:
                    writer.writerow([int(movie['web_id']), movie['id'], movie['genres']])
                except:
                    print(movie)

def clean_user():
    return

def find_web_id(movie_id):
    global movies
    for movie in movies:
        if 'id' in movie:
            if movie['id'] == movie_id:
                return int(movie['web_id'])
    return -1



def clean_explicit():
    # explicit_fb = pd.read_csv('raw_data/movie_ratings.csv')
    with open('../dataset/raw_data/movie_ratings.csv', 'r') as f:
        explicit_fb = csv.DictReader(f)
        
        with open("../dataset/final_csv/explicit_fb.csv", "w", newline='') as file:
            writer = csv.writer(file)
            writer.writerow(["web_id", "user_id", "rating"])

            myiter = 0
            for record in explicit_fb:
                
                if myiter % 10000 == 0:
                    print(myiter)
                myiter += 1
                
                web_id = find_web_id(record['movie_id'])
                if web_id != -1:
                    writer.writerow([web_id, record['user_id'], float(record['rating'])])
                else:
                    continue


def clean_explicit_db():
    users = get_users()
    print(len(users))

    print(users[0]['user_id'])
    for key in users[0]:
        if key != 'user_id' and key != '_id':
            print(find_web_id(key), end='\t')
            print(users[0][key])

    with open("../dataset/final_csv/explicit_fb_db.csv", 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["web_id", "user_id", "rating"])

        myiter = 0
        for myiter in range(len(users)):
            this_user_id = int(users[myiter]['user_id'])
            for key in users[myiter]:
                if key != 'user_id' and key != '_id':
                    this_web_id = find_web_id(key)
                    if this_web_id != -1 and 'rating' in users[myiter][key]:
                        if users[myiter][key]['rating'] <= 5 and users[myiter][key]['rating'] >= 0:
                            writer.writerow([this_web_id, this_user_id, float(users[myiter][key]['rating'])])




if __name__ == "__main__":
    clear_movie()
    # clear_user()
    clean_explicit()
    clean_explicit_db()