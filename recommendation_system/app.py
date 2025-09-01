import streamlit as st
import pickle
import pandas as pd
import os
import requests


def download_similarity(url, filename):
    st.info(f"Downloading {filename} from {url} ...")
    response = requests.get(url)
    with open(filename, "wb") as f:
        f.write(response.content)
    st.success(f"{filename} downloaded.")


def recommend(movie):
    index = movies[movies["title"] == movie].index[0]
    distances = sorted(
        list(enumerate(similarity[index])), reverse=True, key=lambda x: x[1]
    )
    recommended_movies = []
    for i in distances[1:6]:
        recommended_movies.append(movies.iloc[i[0]].title)

    return recommended_movies


SIMILARITY_PATH = "similarity.pkl"
SIMILARITY_URL = (
    "https://drive.google.com/uc?export=download&id=1ehXOlYlvz-_gUEmNzfT3Mf2zcv4mQ6Sy"
)

if not os.path.exists(SIMILARITY_PATH):
    download_similarity(SIMILARITY_URL, SIMILARITY_PATH)

movies_dict = pickle.load(open("movie_list.pkl", "rb"))
movies = pd.DataFrame(movies_dict)
similarity = pickle.load(open(SIMILARITY_PATH, "rb"))

# movies.head()['title']
st.title("Movie Recommendation System")

selected_movie_name = st.selectbox("Enter the movie you like:", movies["title"].values)

if st.button("Recommend"):
    recommendations = recommend(selected_movie_name)
    st.write("Recommendations for:", selected_movie_name)
    for movie in recommendations:
        st.write(movie)
