from os.path import dirname, abspath, join

import pandas as pd
import numpy as np
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers
import sys


ROOT = dirname(dirname(abspath(__file__)))
DATA = join(ROOT, 'dataset', 'final_csv')
MODEL = join(ROOT, 'checkpoint', 'explicit_model')


class RecommenderNet(keras.Model):
    def __init__(self, num_users, num_movies, embedding_size, **kwargs):
        super(RecommenderNet, self).__init__(**kwargs)
        self.num_users = num_users
        self.num_movies = num_movies
        self.embedding_size = embedding_size
        self.user_embedding = layers.Embedding(
            num_users,
            embedding_size,
            embeddings_initializer="he_normal",
            embeddings_regularizer=keras.regularizers.l2(1e-6),
        )
        self.user_bias = layers.Embedding(num_users, 1)
        self.movie_embedding = layers.Embedding(
            num_movies,
            embedding_size,
            embeddings_initializer="he_normal",
            embeddings_regularizer=keras.regularizers.l2(1e-6),
        )
        self.movie_bias = layers.Embedding(num_movies, 1)

    def call(self, inputs):
        user_vector = self.user_embedding(inputs[:, 0])
        user_bias = self.user_bias(inputs[:, 0])
        movie_vector = self.movie_embedding(inputs[:, 1])
        movie_bias = self.movie_bias(inputs[:, 1])
        dot_user_movie = tf.tensordot(user_vector, movie_vector, 2)
        # Add all the components (including bias)
        x = dot_user_movie + user_bias + movie_bias
        # The sigmoid activation forces the rating to between 0 and 1
        return tf.nn.sigmoid(x)


def inference_service(user_id):
    movie_df = pd.read_csv(join(DATA, 'movies.csv'))
    rating_df = pd.read_csv(join(DATA, 'explicit_fb.csv'))
    df = pd.merge(rating_df, movie_df, on="web_id").dropna(axis = 0, subset=['movie_id'])

    user_ids = df["user_id"].unique().tolist()
    user2user_encoded = {x: i for i, x in enumerate(user_ids)}
    userencoded2user = {i: x for i, x in enumerate(user_ids)}
    movie_ids = df["web_id"].unique().tolist()
    movie2movie_encoded = {x: i for i, x in enumerate(movie_ids)}
    movie_encoded2movie = {i: x for i, x in enumerate(movie_ids)}
    df["user"] = df["user_id"].map(user2user_encoded)
    df["movie"] = df["web_id"].map(movie2movie_encoded)
    df = df.sample(frac=1, random_state=42)

    num_users = len(user2user_encoded)
    num_movies = len(movie_encoded2movie)
    df["rating"] = df["rating"].values.astype(np.float32)

    EMBEDDING_SIZE = 50

    model = RecommenderNet(num_users, num_movies, EMBEDDING_SIZE)
    model.load_weights(MODEL) 

    movies_watched_by_user = df[df.user_id == user_id]
    movies_not_watched = movie_df[
    ~movie_df["web_id"].isin(movies_watched_by_user.web_id.values)
    ]["web_id"]
    movies_not_watched = list(
        set(movies_not_watched).intersection(set(movie2movie_encoded.keys()))
    )
    movies_not_watched = [[movie2movie_encoded.get(x)] for x in movies_not_watched]
    user_encoder = user2user_encoded.get(user_id)
    user_movie_array = np.hstack(
        ([[user_encoder]] * len(movies_not_watched), movies_not_watched)
    )
    
    ratings = model.predict(user_movie_array).flatten()
    top_ratings_indices = ratings.argsort()[-20:][::-1]

    return top_ratings_indices
