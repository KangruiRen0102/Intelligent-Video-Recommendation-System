from datetime import datetime

"""Helper module to parse important information from raw Kafka lines."""


def parse_recommendation_request(line):
    """
    Return the time, user id, and recommended movies from the raw Kafka line.

        Parameters:
            line (str): A line from the Kafka logs that corresponds to a recommend request

        Returns:
            time (str): Timestamp of the request
            user_id (str): ID of user who made the request
            recommendations (list): Containing recommended movies
    """
    time, user_id, _, _ = line[: line.find(", result:")].split(",")
    recommendations = line[line.rfind("result:") + 7: line.rfind(", ")]
    latency = line[line.rfind(", ") + 1: line.rfind("ms")].strip()
    return time, user_id, recommendations.replace(" ", "").split(","), latency


def parse_watch_request(line):
    """
    Return the time, user id, movie id, and minute from the raw Kafka line.

        Parameters:
            line (str): A line from the Kafka logs that corresponds to a watch request

        Returns:
            time (str): Timestamp of the request
            user_id (str): ID of user who made the request
            movie_id (str): ID of movie the user requests to watch
            minutes (str): The minute of the movie the user requests to watch
    """
    time, user_id, _ = line.split(",")
    movie_id, minutes = line[line.find("/m/") + 3: line.rfind(".mpg")].split("/")
    return time, user_id, movie_id, minutes


def parse_rating_request(line):
    """
    Return the time, user id, movie id, and rating from the raw Kafka line.

        Parameters:
            line (str): A line from the Kafka logs that corresponds to a rate request

        Returns:
            time (str): Timestamp of the request
            user_id (str): ID of user who made the request
            movie_id (str): ID of movie the user requests to watch
            rating (str): The rating the user assigns the movie
    """
    time, user_id, _ = line.split(",")
    rating_part = line[line.rfind("/") + 1:]
    movie_id, rating = rating_part.split("=")
    return time, user_id, movie_id, rating


def time_to_date(time):
    """
    Return the date from the provided time.

        Parameters:
            time (str): Representing a timestamp in the format '%Y-%m-%dT%H:%M:%S.%f'

        Returns:
            date (str): The date from the timestamp in the format '%Y-%m-%d'
    """
    try:
        time_parsed = datetime.strptime(time, "%Y-%m-%dT%H:%M:%S.%f")
    except ValueError:
        try:
            time_parsed = datetime.strptime(time, "%Y-%m-%dT%H:%M:%S")
        except ValueError:
            return None

    return str(time_parsed.date())  # Transform time to date
