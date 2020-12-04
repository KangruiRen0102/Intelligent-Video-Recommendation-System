from os.path import join, dirname, abspath

import pandas as pd
import numpy as np
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers
from tensorflow.python.keras.backend import set_session


EMBEDDING_SIZE = 50

ROOT = abspath(join(dirname(__file__), ".."))
DATA = join(ROOT, "dataset", "final_csv")
MODEL_WEIGHTS = join(ROOT, "checkpoint", "explicit_model") + "/"

DF = None
GRAPH = None
MODEL = None
MOVIE2MOVIE_ENCODED = None
MOVIE_DF = None
MOVIE_ENCODED2MOVIE = None
SESSION = None
USER2USER_ENCODED = None


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


def prepare_model():
    """
    Prepare the model for predictions.
    To improve performance, this method performs all preliminary computations once, when the API starts.
    The computations include loading the model weights and generating the user and movie encodings.
    """
    global DF, MOVIE_DF, MODEL, SESSION, USER2USER_ENCODED, MOVIE2MOVIE_ENCODED, MOVIE_ENCODED2MOVIE, GRAPH
    MOVIE_DF = pd.read_csv(join(DATA, "movies.csv"))
    rating_df = pd.read_csv(join(DATA, "explicit_fb.csv"))
    DF = pd.merge(rating_df, MOVIE_DF, on="web_id").dropna(axis=0, subset=["movie_id"])

    user_ids = DF["user_id"].unique().tolist()
    USER2USER_ENCODED = {x: i for i, x in enumerate(user_ids)}
    movie_ids = DF["web_id"].unique().tolist()
    MOVIE2MOVIE_ENCODED = {x: i for i, x in enumerate(movie_ids)}
    MOVIE_ENCODED2MOVIE = {i: x for i, x in enumerate(movie_ids)}
    DF["user"] = DF["user_id"].map(USER2USER_ENCODED)
    DF["movie"] = DF["web_id"].map(MOVIE2MOVIE_ENCODED)
    DF = DF.sample(frac=1, random_state=42)

    num_users = len(USER2USER_ENCODED)
    num_movies = len(MOVIE_ENCODED2MOVIE)
    DF["rating"] = DF["rating"].values.astype(np.float32)

    SESSION = tf.Session()
    set_session(SESSION)
    MODEL = RecommenderNet(num_users, num_movies, EMBEDDING_SIZE)
    MODEL.load_weights(MODEL_WEIGHTS)
    GRAPH = tf.get_default_graph()


def infer(user_id):
    """
    Return top 20 movies for user with given id to watch.

    Parameters:
        user_id (int): The id of the user seeking recommendations

    Returns:
        top20_movies (list): Listing containing ids of top 20 movies
    """
    movies_watched_by_user = DF[DF.user_id == user_id]
    movies_not_watched = MOVIE_DF[
        ~MOVIE_DF["web_id"].isin(movies_watched_by_user.web_id.values)
    ]["web_id"]
    movies_not_watched = list(
        set(movies_not_watched).intersection(set(MOVIE2MOVIE_ENCODED.keys()))
    )
    movies_not_watched = [[MOVIE2MOVIE_ENCODED.get(x)] for x in movies_not_watched]
    user_encoder = USER2USER_ENCODED.get(user_id)
    user_movie_array = np.hstack(
        ([[user_encoder]] * len(movies_not_watched), movies_not_watched)
    )

    with SESSION.as_default():
        with GRAPH.as_default():
            ratings = MODEL.predict(user_movie_array).flatten()
            top20_movies = ratings.argsort()[-20:][::-1]
    return top20_movies
