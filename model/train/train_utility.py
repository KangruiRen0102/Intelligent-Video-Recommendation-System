import pandas as pd
import numpy as np
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers
from sklearn.metrics import mean_absolute_error, roc_auc_score
import os
from recommender import RecommenderNet
import matplotlib.pyplot as plt

def preprocess_data(val_ratio=0.1):
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
    df = df.sample(frac=1, random_state=42)

    num_users = len(user2user_encoded)
    num_movies = len(movie_encoded2movie)
    df["rating"] = df["rating"].values.astype(np.float32)
    min_rating = min(df["rating"])
    max_rating = max(df["rating"])


    df = df.sample(frac=1, random_state=42)
    x = df[["user", "movie"]].values
    # Normalize the targets between 0 and 1. Makes it easy to train.
    y = df["rating"].apply(lambda x: (x - min_rating) / (max_rating - min_rating)).values
    # Assuming training on 90% of the data and validating on 10%.
    train_indices = int((1.-val_ratio)* df.shape[0])
    x_train, x_val, y_train, y_val = (
        x[:train_indices],
        x[train_indices:],
        y[:train_indices],
        y[train_indices:],
    )

    return (x_train, x_val, y_train, y_val, num_users, num_movies)

def offline_eval(model_path, val_ratio=0.1, EMBEDDING_SIZE=50):
    x_train, x_val, y_train, y_val, num_users, num_movies = preprocess_data(val_ratio)
    model = RecommenderNet(num_users, num_movies, EMBEDDING_SIZE)
    model.load_weights(model_path) 
    predictions = model.predict(x = x_val)
    MAE = mean_absolute_error(y_val , predictions)
    # AUC = roc_auc_score(y_val, predictions)
    AUC = 0.

    return (MAE, AUC)


def data_distribution(val_ratio=0.1):
    x_train, x_val, y_train, y_val, num_users, num_movies = preprocess_data(val_ratio)
    plt.hist(y_train, bins=5, facecolor="blue", edgecolor="black", alpha=0.7)
    plt.show()


def train_model(model_path, val_ratio=0.1, EMBEDDING_SIZE=50, batch_size=256, epochs=10):
    x_train, x_val, y_train, y_val, num_users, num_movies = preprocess_data(val_ratio)

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

    model.save_weights(model_path)

def report_model(model_path, val_ratio=0.1, EMBEDDING_SIZE=50):
    my_path = os.path.abspath(os.path.dirname(__file__))
    if not os.path.isdir(os.path.join(my_path, '../report')):
        os.makedirs(os.path.join(my_path, '../report'))
    (MAE, AUC) = offline_eval(model_path, val_ratio, EMBEDDING_SIZE)
    print(MAE, AUC)
    data_distribution()


