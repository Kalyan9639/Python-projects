import requests
import random

YOUTUBE_API_KEY = "YOUR API KEY"  # Replace this with your YouTube Data API Key

def search_youtube_video(query, api_key):
    """Searches YouTube for a list of videos based on a query and returns a random one."""
    url = "https://www.googleapis.com/youtube/v3/search"
    params = {
        "part": "snippet",
        "q": query,
        "type": "video",
        "order": "viewCount",
        "maxResults": 10,  # Get up to 10 results for variety
        "key": api_key
    }
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()  # Raise an exception for HTTP errors
        data = response.json()

        if "items" in data and data["items"]:
            # Choose a random video from the results
            video = random.choice(data["items"])
            video_id = video["id"]["videoId"]
            video_title = video["snippet"]["title"]
            video_url = f"https://www.youtube.com/watch?v={video_id}"
            return video_title, video_url
        else:
            print("No videos found for the query.")
            return None, None
    except requests.exceptions.RequestException as e:
        print(f"Error fetching data from YouTube API: {e}")
        return None, None

def get_user_mood_and_genre():
    """Asks the user for their mood and desired genre."""
    mood = input("What is your current mood? (e.g., happy, sad, energetic): ")
    genre = input("What genre of music would you like to listen to? (e.g., pop, rock, jazz): ")
    return mood, genre

def main():
    """Main function to execute the music recommendation system."""
    # Step 1: Ask the user for their mood and genre
    mood, genre = get_user_mood_and_genre()

    # Step 2: Ask for a specific artist (optional)
    artist_name = input("Enter a specific artist you like (or press Enter to skip): ")

    # Step 3: Formulate the search query
    if artist_name:
        query = f"{mood} {genre} {artist_name}"
    else:
        query = f"{mood} {genre}"

    # Step 4: Search YouTube for a random music video
    print(f"Searching for a video for: {query}")
    video_title, video_url = search_youtube_video(query, YOUTUBE_API_KEY)

    # Step 5: Display the result
    if video_title and video_url:
        print(f"We recommend you listen to: {video_title}")
        print(f"YouTube Link: {video_url}")
    else:
        print("Sorry, we couldn't find a video for your request.")

if __name__ == "__main__":
    main()
