# Import necessary libraries
import streamlit as st
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from transformers import pipeline

# Set up Spotify API credentials
def initialize_spotify_client(client_id, client_secret):
    """
    Initialize the Spotify client with provided credentials.

    Args:
    - client_id (str): Your Spotify API client ID.
    - client_secret (str): Your Spotify API client secret.

    Returns:
    - sp (spotipy.Spotify): Authenticated Spotify client.
    """
    auth_manager = SpotifyClientCredentials(client_id=client_id, client_secret=client_secret)
    return spotipy.Spotify(auth_manager=auth_manager)

# Function to fetch mood-based recommendations from Spotify
def get_mood_recommendations(sp, mood, genre):
    """
    Fetch song recommendations based on the specified mood and genre.

    Args:
    - sp (spotipy.Spotify): Authenticated Spotify client.
    - mood (str): User's mood, such as 'happy' or 'chill'.
    - genre (str): User's preferred genre, such as 'pop' or 'rock'.

    Returns:
    - list: A list of tuples containing song name and Spotify URL.
    """
    # Prioritize Hindi songs
    if genre == "hindi":
        # Search specifically for Hindi songs
        results = sp.search(q='genre:hindi', limit=20)
    else:
        # Search for tracks based on the selected genre
        results = sp.search(q=f'genre:{genre}', limit=20)

    mood_tracks = []

    # Analyze the audio features of each track to match mood requirements
    for track in results['tracks']['items']:
        features = sp.audio_features(track['id'])[0]

        # Mood filtering using Spotify's 'valence' (happiness) and 'energy' attributes
        if features:
            if mood == "happy" and features['valence'] > 0.7:
                mood_tracks.append((track['name'], track['external_urls']['spotify']))
            elif mood == "chill" and features['energy'] < 0.5:
                mood_tracks.append((track['name'], track['external_urls']['spotify']))
            # You can add more mood-specific filters here if needed

    return mood_tracks

# Main function for Streamlit app
def main():
    st.title("🎶 Mood-Based Music Recommendation Bot 🎶")
    st.write("Tell me your mood and preferred genre, and I'll recommend songs just for you!")

    # User input for mood and genre
    user_input = st.text_input("Type your mood and genre (e.g., 'I feel happy, maybe some hindi')")

    # Initialize Spotify client with your credentials
    client_id = "44f923f287084e9ab7cd8403d150e404"  # Your client ID
    client_secret = "c0cea3085bfe488e90564388f260f4cd"  # Your client secret
    sp = initialize_spotify_client(client_id, client_secret)

    # Load a pre-trained sentiment analysis model from Hugging Face
    classifier = pipeline("sentiment-analysis")

    # Process the input only if the user has entered something
    if user_input:
        # Perform basic NLP analysis on user input to determine mood
        mood_analysis = classifier(user_input)[0]  # Analyze the sentiment of the input
        
        # Basic mapping of sentiment to mood (e.g., POSITIVE = "happy")
        mood = "happy" if mood_analysis['label'] == "POSITIVE" else "chill"

        # Attempt to extract genre from user input
        genre = "pop"  # Default genre
        genres = ["pop", "rock", "jazz", "hip hop", "classical", "electronic", "hindi"]
        
        # Check if a specific genre is mentioned in user input
        for g in genres:
            if g in user_input.lower():
                genre = g
                break

        # Get song recommendations based on mood and genre
        recommendations = get_mood_recommendations(sp, mood, genre)

        # Display recommendations
        if recommendations:
            st.write(f"**Here are some {mood} {genre} songs for you:**")
            for name, link in recommendations:
                st.markdown(f"- [{name}]({link})")
        else:
            st.write("Sorry, I couldn't find any recommendations. Try another mood or genre.")

if __name__ == "__main__":
    main()



#to run the app , write in terminal
#streamlit run music_chatbot.py
