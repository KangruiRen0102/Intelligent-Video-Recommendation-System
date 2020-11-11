import numpy
import csv
import json
import pandas as pd
from io import StringIO

movies = []

def clear_movie():
    global movies
    with open('raw_data/movies_data') as f:
        movies = json.load(f)

    with open("final_csv/movies.csv", 'w', newline='') as file:
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
    with open('raw_data/movie_ratings.csv', 'r') as f:
        explicit_fb = csv.DictReader(f)
        
        with open("final_csv/explicit_fb.csv", "w", newline='') as file:
            writer = csv.writer(file)
            writer.writerow(["web_id", "user_id", "rating"])

            iter = 0
            for record in explicit_fb:
                
                if iter % 10000 == 0:
                    print(iter)
                iter += 1
                
                web_id = find_web_id(record['movie_id'])
                if web_id != -1:
                    writer.writerow([web_id, record['user_id'], float(record['rating'])])
                else:
                    continue


if __name__ == "__main__":
    clear_movie()
    # clear_user()
    clean_explicit()