import json
import requests
from multiprocessing import cpu_count, Pool, Manager
from functools import partial
from tqdm import tqdm


""" A script to scrape the movies and users from the api

Check that you are connected to the McGill VPN before running.
"""


BASE_URL = "http://fall2020-comp598.cs.mcgill.ca:8080"


def get_object(responses, url):
    response = requests.get(url)
    if response.status_code != "404":
        responses.append(json.loads(response.content.decode("utf-8")))
    else:
        raise Exception(f"Server unreachable")


def get_all_objects(category, upper_limit):
    workers = max(cpu_count() - 1, 1)
    urls = [f"{BASE_URL}/{category}/{obj_id}" for obj_id in range(1, upper_limit + 1)]
    with Manager() as manager, Pool(workers) as pool:
        responses = manager.list()
        p = partial(get_object, responses)
        for _ in tqdm(pool.imap_unordered(p, urls), total=len(urls)):
            pass
        return list(responses)


if __name__ == "__main__":
    with open("movies_data", "w") as f:
        """
        Sparse results after 10000
        """
        movie_data = get_all_objects('movie', 10000)
        json.dump(movie_data, f)

    with open("users_data", "w") as f:
        """
        Sparse results after 1100000
        """
        user_data = get_all_objects('user', 50000)
        json.dump(user_data, f)
