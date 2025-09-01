import streamlit as st
import pickle
import pandas as pd
import os
import gdown


def download_file_gdrive(url, filename):
    st.info(f"Downloading {filename} from Google Drive ...")
    try:
        gdown.download(url, filename, quiet=False)
        st.success(f"{filename} downloaded.")
    except Exception as e:
        st.error(f"Failed to download {filename}: {e}")
        st.stop()


def show_file_head(filename):
    with open(filename, "rb") as f:
        head = f.read(200)
    st.warning(f"First 200 bytes of {filename}: {head}")


def is_valid_pickle(filename):
    with open(filename, "rb") as f:
        start = f.read(1)
        # Pickle files start with b'\x80', HTML files start with b'<'
        return start == b"\x80"


def recommend(movie):
    index = movies[movies["title"] == movie].index[0]
    distances = sorted(
        list(enumerate(similarity[index])), reverse=True, key=lambda x: x[1]
    )
    recommended_movies = []
    for i in distances[1:6]:
        recommended_movies.append(movies.iloc[i[0]].title)

    return recommended_movies


MOVIE_LIST_PATH = "movie_list.pkl"
MOVIE_LIST_URL = (
    "https://drive.google.com/uc?export=download&id=16443lzrLofq2PowRbBWEahIEJCCoOpmZ"
)

SIMILARITY_PATH = "similarity.pkl"
SIMILARITY_URL = (
    "https://drive.google.com/uc?export=download&id=1ehXOlYlvz-_gUEmNzfT3Mf2zcv4mQ6Sy"
)

if not os.path.exists(MOVIE_LIST_PATH):
    download_file_gdrive(MOVIE_LIST_URL, MOVIE_LIST_PATH)

if not os.path.exists(SIMILARITY_PATH):
    download_file_gdrive(SIMILARITY_URL, SIMILARITY_PATH)

if not is_valid_pickle(MOVIE_LIST_PATH):
    st.error(
        "Downloaded movie_list.pkl is not a valid pickle file. Check your link and sharing settings."
    )
    show_file_head(MOVIE_LIST_PATH)
    st.stop()

if not is_valid_pickle(SIMILARITY_PATH):
    st.error(
        "Downloaded similarity.pkl is not a valid pickle file. "
        "Please check your Google Drive link and ensure the file is shared with 'Anyone with the link'. "
        "Try opening the link in an incognito window to verify direct download access."
    )
    show_file_head(SIMILARITY_PATH)
    st.stop()

movies_dict = pickle.load(open(MOVIE_LIST_PATH, "rb"))
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
    recommendations = recommend(selected_movie_name)
    st.write("Recommendations for:", selected_movie_name)
    for movie in recommendations:
        st.write(movie)
