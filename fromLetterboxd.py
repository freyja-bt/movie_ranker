# import re
import sys
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

if len(sys.argv) < 3:
    raise Exception("Missing a zipfile or csv")

letterboxd_zipfilename = sys.argv[1]
existing_csv = sys.argv[2]

if len(sys.argv) > 3:
    new_csvfilename = sys.argv[3]
    print("Using", existing_csv, "and will export as", new_csvfilename)
else:
    new_csvfilename = existing_csv

# unzip_loc = tempfile.tempdir
unzip_loc = "."
print(unzip_loc)
with ZipFile(letterboxd_zipfilename, "r") as zObject:
    zObject.extract(
        member= "watched.csv",
        path= unzip_loc
    )
print(pd.io.common.file_exists(unzip_loc+'\\'+"watched.csv"))
letterboxd_watched = pd.read_csv(filepath_or_buffer = path.join(unzip_loc, "watched.csv"))
letterboxd_watched = letterboxd_watched.rename(columns={"Letterboxd URI":"Letterboxd_URI"})

letterboxd_watched["genres"] = letterboxd_watched["Letterboxd_URI"].map(movie_genres)

letterboxdList = pd.read_csv(existing_csv)

if len(letterboxdList.index) == 0:
    letterboxdList['title'] = letterboxd_watched['Name']
    letterboxdList['genre'] = letterboxd_watched["genres"]
    letterboxdList['year'] = letterboxd_watched["Year"]
    letterboxdList['elo'] = 0
    letterboxdList['W'] = 0
    letterboxdList['L'] = 0
    letterboxdList['uri'] = letterboxd_watched["Letterboxd_URI"]
else:
    # Identify what values are in TableB and not in TableA
    key_diff = set(letterboxd_watched.Letterboxd_URI).difference(letterboxdList.uri)
    where_diff = letterboxd_watched.Letterboxd_URI.isin(key_diff)
    # Slice TableB accordingly and append to TableA
    letterboxd_watched_temp = letterboxd_watched.rename(columns={'Name':'title','Letterboxd_URI':'uri','genres':'genre','Year':'year'})
    letterboxd_watched_temp = letterboxd_watched_temp.drop(columns = ['Date'])
    letterboxd_watched_temp['elo'] = 0
    letterboxd_watched_temp['W'] = 0
    letterboxd_watched_temp['L'] = 0
    letterboxdList = pd.concat([letterboxdList, letterboxd_watched_temp[where_diff]], ignore_index=True)


letterboxdList.to_csv(new_csvfilename, index = False)
