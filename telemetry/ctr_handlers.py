import parsers as p

"""
This script helps compute the global daily CTR and the daily CTR per model. 
"""


def watch_request(line, movies, recommendations_coll, ctr_per_model, ctr_global):
    """
    Determines if the inputted watch request result in a click.
    If so, updates the model's CTR and the global CTR.
    """
    time, user_id, movie_id, _ = p.parse_watch_request(
        line
    )  # Parse the watch event from the line
    date = p.time_to_date(time)

    web_id = get_web_id(movie_id, movies)  # Convert movie id into web id

    if web_id and date:
        start, end = p.five_min_interval(time)
        query = {
            "user_id": int(user_id),
            "timestamp": {"$gte": start, "$lte": end},
            "recommendations": {"$regex": f".*{web_id}.*"},
        }

        # Check if the user was recommended the movie within the past 5 mins
        results = [r for r in recommendations_coll.find(query)]
        for r in results:
            ctr_per_model.update_one(
                {"model_version": r["model_version"], "date": date},
                {"$inc": {"num_clicks": 1}},
                upsert=True,
            )  # Update the CTR per model
        if results:
            ctr_global.update_one(
                {"date": date},
                {"$inc": {"num_clicks": 1}},  # Increment the num_recommends by 1
                upsert=True,
            )  # Update the global CTR


def get_web_id(movie_id, movies):
    """
    Return the web id corresponding to the inputted movie_id.
        parameters:
            movie_id (str): The string movie id (e.g., willow+1988).
            movies (mongo.Collections): The collection in the prod MongoDB containing the movie id - web id mapping.
        returns:
            web_id (str): The web id of the inputted movie (e.g., 2193).
    """
    result = movies.find_one({"movie_id": movie_id})
    if result:
        return result["web_id"]
    return None


"""Example Usage
if __name__ == "__main__":
    client = MongoClient("fall2020-comp598-1.cs.mcgill.ca", 27017)
    db = client["prod_db"]
    line = "2020-12-03T08:27:32.42,29, GET /data/m/willow+1988/20.mpg"
    if "/data/" in line:
        watch_request(line, db.movies, db.recommendations, db.ctr_per_model, db.ctr_global)
"""
