import pandas as pd
import numpy as np
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers
import os
from recommender import RecommenderNet

def train(val_ratio=0.1, EMBEDDING_SIZE=50, batch_size=256, epochs=10):
    my_path = os.path.abspath(os.path.dirname(__file__))
    movie_df = pd.read_csv(os.path.join(my_path, '../dataset/final_csv/movies.csv'))
    rating_df = pd.read_csv(os.path.join(my_path, '../dataset/final_csv/explicit_fb.csv'))

    df = pd.merge(rating_df, movie_df, on="web_id").dropna(axis = 0, subset=['movie_id'])

    user_ids = df["user_id"].unique().tolist()
    user2user_encoded = {x: i for i, x in enumerate(user_ids)}
    userencoded2user = {i: x for i, x in enumerate(user_ids)}
    movie_ids = df["web_id"].unique().tolist()
    movie2movie_encoded = {x: i for i, x in enumerate(movie_ids)}
    movie_encoded2movie = {i: x for i, x in enumerate(movie_ids)}
    df["user"] = df["user_id"].map(user2user_encoded)
    df["movie"] = df["web_id"].map(movie2movie_encoded)

    num_users = len(user2user_encoded)
    num_movies = len(movie_encoded2movie)
    df["rating"] = df["rating"].values.astype(np.float32)
    # min and max ratings will be used to normalize the ratings later
    min_rating = min(df["rating"])
    max_rating = max(df["rating"])

    print(
        "Number of users: {}, Number of Movies: {}, Min rating: {}, Max rating: {}".format(
            num_users, num_movies, min_rating, max_rating
        )
    )


    df = df.sample(frac=1, random_state=42)
    x = df[["user", "movie"]].values
    # Normalize the targets between 0 and 1. Makes it easy to train.
    y = df["rating"].apply(lambda x: (x - min_rating) / (max_rating - min_rating)).values
    # Assuming training on 90% of the data and validating on 10%.
    train_indices = int((1 - val_ratio) * df.shape[0])
    x_train, x_val, y_train, y_val = (
        x[:train_indices],
        x[train_indices:],
        y[:train_indices],
        y[train_indices:],
    )

    model = RecommenderNet(num_users, num_movies, EMBEDDING_SIZE)
    model.compile(
        loss=tf.keras.losses.BinaryCrossentropy(), optimizer=keras.optimizers.Adam(lr=0.001)
    )

    history = model.fit(
        x=x_train,
        y=y_train,
        batch_size=batch_size,
        epochs=epochs,
        verbose=1,
        validation_data=(x_val, y_val),
    )

    model.save_weights(os.path.join(my_path, "model/"))
    # model.load_weights("explicit_model/")

    # user_id = df.web_id.sample(1).iloc[0]
    # movies_watched_by_user = df[df.user_id == user_id]
    # movies_not_watched = movie_df[
    #     ~movie_df["web_id"].isin(movies_watched_by_user.movie_id.values)
    # ]["web_id"]
    # movies_not_watched = list(
    #     set(movies_not_watched).intersection(set(movie2movie_encoded.keys()))
    # )
    # movies_not_watched = [[movie2movie_encoded.get(x)] for x in movies_not_watched]
    # user_encoder = user2user_encoded.get(user_id)
    # user_movie_array = np.hstack(
    #     ([[user_encoder]] * len(movies_not_watched), movies_not_watched)
    # )
    # ratings = model.predict(user_movie_array).flatten()
    # top_ratings_indices = ratings.argsort()[-20:][::-1]

    # recommended_movie_ids = [
    #     movie_encoded2movie.get(movies_not_watched[x][0]) for x in top_ratings_indices
    # ]

    # print("Showing recommendations for user: {}".format(user_id))
    # print("====" * 9)
    # print(top_ratings_indices)


