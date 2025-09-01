import streamlit as st
import pickle
import pandas as pd
import os
import gdown

# --- Configuration ---
# Store file paths and their corresponding Google Drive file IDs in a dictionary
# This makes it easier to manage and add more files in the future.
FILES_TO_DOWNLOAD = {
    "movie_list.pkl": "16443lzrLofq2PowRbBWEahIEJCCoOpmZ",
    "similarity.pkl": "1ehXOlYlvz-_gUEmNzfT3Mf2zcv4mQ6Sy"
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
            st.info(f"Downloading {filename} from Google Drive...")
            try:
                # Use gdown's recommended method: passing the file ID directly
                gdown.download(id=file_id, output=filename, quiet=False)
                st.success(f"{filename} downloaded successfully.")
            except Exception as e:
                st.error(f"Failed to download {filename}: {e}")
                # Show the first 200 bytes for debugging if the file was partially created
                if os.path.exists(filename):
                    with open(filename, "rb") as f:
                        st.warning(f"First 200 bytes of failed download: {f.read(200)}")
                st.stop() # Stop the app if a critical file fails to download

        # Validate that the downloaded file is a real pickle file, not an HTML error page
        with open(filename, 'rb') as f:
            # Pickle files start with a protocol byte, typically b'\x80'. HTML starts with b'<'
            if f.read(1) != b'\x80':
                st.error(
                    f"Validation Error: {filename} is not a valid pickle file. "
                    "This often happens if the Google Drive link is not shared correctly "
                    "('Anyone with the link'). Please verify your link and sharing settings."
                )
                with open(filename, "rb") as f_debug:
                     st.warning(f"First 200 bytes of {filename}: {f_debug.read(200)}")
                st.stop()

    # If all files are present and valid, load them
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
        # Get the index of the selected movie
        movie_index = movies_df[movies_df["title"] == movie_title].index[0]

        # Get the similarity scores for that movie and enumerate them with their index
        distances = list(enumerate(similarity_matrix[movie_index]))

        # Sort the movies based on the similarity scores in descending order
        distances_sorted = sorted(distances, reverse=True, key=lambda x: x[1])

        # Get the titles of the top 5 recommended movies (from index 1 to 6 to exclude the movie itself)
        recommended_movies = [movies_df.iloc[i[0]].title for i in distances_sorted[1:6]]
        return recommended_movies
    except IndexError:
        return ["Movie not found in the dataset."]
    except Exception as e:
        return [f"An error occurred: {e}"]


# --- Streamlit UI ---

st.title("🎬 Movie Recommendation System")
st.write("Select a movie you like, and we'll suggest 5 similar ones!")

# Load the data using the cached function
movies, similarity = load_data()

# Create the dropdown for movie selection
selected_movie_name = st.selectbox(
    "Type or select a movie from the dropdown:",
    movies["title"].values
)

# Create the recommendation button
if st.button("Recommend Me Movies"):
    with st.spinner(f"Finding recommendations for '{selected_movie_name}'..."):
        recommendations = recommend(selected_movie_name, movies, similarity)
        st.subheader("Here are your recommendations:")
        for movie in recommendations:
            st.success(movie)
