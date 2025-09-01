import streamlit as st
import pickle
import pandas as pd
import os
import gdown


FILES_TO_DOWNLOAD = {
    "movie_list.pkl": "16443lzrLofq2PowRbBWEahIEJCCoOpmZ",
    "similarity.pkl": "1ehXOlYlvz-_gUEmNzfT3Mf2zcv4mQ6Sy",
}

# --- Caching and Data Loading ---


@st.cache_data
def load_data():
    """
    Downloads, validates, and loads the movie data and similarity matrix.
    The @st.cache_data decorator ensures this function runs only once,
    caching the result for subsequent runs. This makes the app much faster.
    """
    for filename, file_id in FILES_TO_DOWNLOAD.items():
        # Check if the file exists
        if not os.path.exists(filename):
            try:
                gdown.download(id=file_id, output=filename, quiet=False)
            except Exception as e:
                st.error(f"Failed to download {filename}: {e}")
                if os.path.exists(filename):
                    with open(filename, "rb") as f:
                        st.warning(f"First 200 bytes of failed download: {f.read(200)}")
                st.stop()

        with open(filename, "rb") as f:
            if f.read(1) != b"\x80":
                st.error(
                    f"Validation Error: {filename} is not a valid pickle file. "
                    "This often happens if the Google Drive link is not shared correctly "
                    "('Anyone with the link'). Please verify your link and sharing settings."
                )
                with open(filename, "rb") as f_debug:
                    st.warning(f"First 200 bytes of {filename}: {f_debug.read(200)}")
                st.stop()

    with open("movie_list.pkl", "rb") as f:
        movies_dict = pickle.load(f)
    movies_df = pd.DataFrame(movies_dict)

    with open("similarity.pkl", "rb") as f:
        similarity_matrix = pickle.load(f)

    return movies_df, similarity_matrix


# --- Recommendation Logic ---


def recommend(movie_title, movies_df, similarity_matrix):
    """
    Finds and returns the top 5 most similar movies.
    """
    try:
        movie_index = movies_df[movies_df["title"] == movie_title].index[0]

        distances = list(enumerate(similarity_matrix[movie_index]))

        distances_sorted = sorted(distances, reverse=True, key=lambda x: x[1])

        recommended_movies = [movies_df.iloc[i[0]].title for i in distances_sorted[1:6]]
        return recommended_movies
    except IndexError:
        return ["Movie not found in the dataset."]
    except Exception as e:
        return [f"An error occurred: {e}"]


# --- Streamlit UI ---

st.title("🎬 Movie Recommendation System")
st.write("Select a movie you like, and we'll suggest 5 similar ones!")


movies, similarity = load_data()


selected_movie_name = st.selectbox(
    "Type or select a movie from the dropdown:", movies["title"].values
)


if st.button("Recommend"):
    with st.spinner(f"Finding recommendations for '{selected_movie_name}'..."):
        recommendations = recommend(selected_movie_name, movies, similarity)
        st.subheader("Here are your recommendations:")
        for movie in recommendations:
            st.success(movie)
