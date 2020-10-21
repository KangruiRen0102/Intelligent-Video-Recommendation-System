import pandas as pd


def get_watch_events(filename: str):
    """Return pandas Dataframe containing all watch events in given file"""
    header_list = ["date", "user_id", "movie_id", "minute"]
    return pd.read_csv(filename, names=header_list)


def get_watch_history(df):
    """Transform watch events into CSV containing one row for each user and one column for each movie 
       where value is 1 if user watched movie, 0 otherwise."""
    df = df.drop(columns=['date', 'minute'])  # We just want to know whether or not user X watched movie Y
    df = df.drop_duplicates()  # Dataframe containing one row for each movie each user watched
    df = df.groupby("user_id")['movie_id'].apply(list).to_frame("movie_ids").reset_index()
    data = dict(zip(df.user_id.values, df.movie_ids.values))
    df2 = pd.DataFrame.from_dict(data, orient='index')
    df2 = df2.stack().reset_index()
    df2.level_1 = 1
    table = df2.pivot(index='level_0', columns=0, values='level_1').fillna(0)
    flattened = pd.DataFrame(table.to_records())
    flattened = flattened.rename(columns={'level_0': 'user_id'})
    flattened.to_csv("watch_history.csv", index=False)
    return flattened


if __name__ == '__main__':
    df = get_watch_events("watch_events.csv")
    watch_history = get_watch_history(df)
    
