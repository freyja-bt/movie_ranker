import re
import tempfile
from os import path
from zipfile import ZipFile

import pandas as pd
import requests
from letterboxdpy import movie


def get_real_url_from_shortlink(url):
    resp = requests.get(url)
    return resp.url

def movie_genres(URI):
    # title = title.replace("'", "")
    # title_words = re.findall(r'\w+', title.casefold())
    # lbtitle = "-".join(title_words)
    lbtitle = get_real_url_from_shortlink(URI).replace("https://letterboxd.com/film/", "").replace("/", "")

    movie_instance = movie.Movie(lbtitle)
    instance_genres = []
    for x in movie_instance.genres:
        if (x['type'] == "genre"):
            instance_genres.append(x['name'])
    genre_string = "/".join(instance_genres)
    return genre_string

unzip_loc = tempfile.tempdir

with ZipFile("letterboxd-seabrightener-2026-08-05-17-18-utc.zip", "r") as zObject:
    zObject.extract(
        member= "watched.csv",
        path= unzip_loc
    )

letterboxd_watched = pd.read_csv(filepath_or_buffer = path.join(unzip_loc, "watched.csv"))

letterboxd_watched["genres"] = letterboxd_watched["Letterboxd URI"].map(movie_genres)

letterboxdList = pd.read_csv('templateList.csv')

letterboxdList['title'] = letterboxd_watched['Name']
letterboxdList['genre'] = letterboxd_watched["genres"]
letterboxdList['year'] = letterboxd_watched["Year"]

letterboxdList.to_csv("letterboxdList.csv")
