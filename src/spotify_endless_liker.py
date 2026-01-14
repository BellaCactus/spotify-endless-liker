import os
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import time
import random

# --- 1. SET UP YOUR CREDENTIALS ---
CLIENT_ID = "811e4e5457634663840762c6d327b6de"
CLIENT_SECRET = "16301f8ead6a4c60b3a23d65d22668c3"
# FINAL, CORRECT URI based on Spotify's new documentation
REDIRECT_URI = "http://127.0.0.1:8000/callback"

# --- 2. CONFIGURE YOUR BOT ---
SEED_ARTISTS = [
    '3TVXtAsR1Inumwj472S9r4',  # Drake
    '06HL4z0CvFAxyc27GXpf02',  # Taylor Swift
    '1Xyo4uXC1ZmMpatF05PJ',  # The Weeknd
    '4r63FhuTkUYltbVAg5TQnk',  # Daft Punk
    '0Y5tJX1ZmMpatF05PJ'  # Kendrick Lamar
]
SONGS_TO_LIKE_GOAL = 100000
DELAY_BETWEEN_LIKES = 0.5

# --- 3. SCRIPT LOGS ---
LIKED_LOG_FILE = "liked_songs_log.txt"
ARTIST_LOG_FILE = "discovered_artists_log.txt"


# --- 4. THE MAIN SCRIPT ---
def load_ids_from_log(filename):
    if not os.path.exists(filename):
        return set()
    with open(filename, 'r') as f:
        return {line.strip() for line in f}


def save_id_to_log(filename, item_id):
    with open(filename, 'a') as f:
        f.write(item_id + '\n')


def main():
    """Main function to authenticate manually and run the song liker bot."""
    # --- Manual Authentication Flow ---
    scope = "user-library-modify user-library-read"
    auth_manager = SpotifyOAuth(
        client_id=CLIENT_ID,
        client_secret=CLIENT_SECRET,
        redirect_uri=REDIRECT_URI,
        scope=scope,
        open_browser=True
    )

    # 1. Generate and print the authorization URL
    auth_url = auth_manager.get_authorize_url()
    print("-" * 80)
    print("Please open this URL in an Incognito Browser window to authorize:")
    print(auth_url)
    print("-" * 80)

    # 2. Ask the user to paste the redirect URL
    redirect_url = input(
        "After authorizing, paste the full URL from your browser's address bar here and press Enter:\n")

    # 3. Use the redirect URL to fetch the token
    try:
        code = auth_manager.parse_response_code(redirect_url)
        auth_manager.get_access_token(code, as_dict=False)
        print("\n✅ Authentication successful!")
    except Exception as e:
        print(f"\n--- ❌ AUTHENTICATION FAILED ---")
        print(f"The URL you pasted was: '{redirect_url}'")
        print(f"Error: {e}")
        print(
            "\n>>> Please try again. Make sure you are pasting the FULL URL from the browser after you click 'Agree'.")
        print(f">>> It must start with '{REDIRECT_URI}?code=...'")
        return

    # 4. Create the authenticated Spotify object
    sp = spotipy.Spotify(auth_manager=auth_manager)

    # --- Liking Loop Starts Here ---
    already_liked_ids = load_ids_from_log(LIKED_LOG_FILE)
    discovered_artist_ids = load_ids_from_log(ARTIST_LOG_FILE)

    for artist_uri in SEED_ARTISTS:
        artist_id = artist_uri.split(':')[-1]
        discovered_artist_ids.add(artist_id)

    print(f"Goal is to like {SONGS_TO_LIKE_GOAL} new songs.")
    print(f"Already liked {len(already_liked_ids)} songs in previous sessions.")

    while len(already_liked_ids) < SONGS_TO_LIKE_GOAL:
        try:
            current_seeds = random.sample(
                list(discovered_artist_ids),
                min(len(discovered_artist_ids), 5)
            )
            recommendations = sp.recommendations(seed_artists=current_seeds, limit=100)

            if not recommendations['tracks']:
                print("Could not find any new recommendations. Trying again...")
                time.sleep(10)
                continue

            track_ids_to_check = [track['id'] for track in recommendations['tracks']]
            new_track_ids = [tid for tid in track_ids_to_check if tid not in already_liked_ids]

            if not new_track_ids:
                print("Found recommendations, but all have been processed before. Discovering...")
                time.sleep(5)
                continue

            already_in_library_results = sp.current_user_saved_tracks_contains(tracks=new_track_ids)

            truly_new_tracks = []
            for i, is_in_library in enumerate(already_in_library_results):
                if not is_in_library:
                    truly_new_tracks.append(new_track_ids[i])

            if not truly_new_tracks:
                print("Found recommendations, but all are already in your Liked Songs. Discovering...")
                for tid in new_track_ids:
                    save_id_to_log(LIKED_LOG_FILE, tid)
                    already_liked_ids.add(tid)
                continue

            for track_id in truly_new_tracks:
                if len(already_liked_ids) >= SONGS_TO_LIKE_GOAL:
                    break
                sp.current_user_saved_tracks_add(tracks=[track_id])
                save_id_to_log(LIKED_LOG_FILE, track_id)
                already_liked_ids.add(track_id)

                track_info = next((t for t in recommendations['tracks'] if t['id'] == track_id), None)
                if track_info:
                    track_name = track_info['name']
                    artist_name = track_info['artists'][0]['name']
                    print(f"({len(already_liked_ids)}/{SONGS_TO_LIKE_GOAL}) Liked: '{track_name}' by {artist_name}")

                    new_artist_id = track_info['artists'][0]['id']
                    if new_artist_id not in discovered_artist_ids:
                        discovered_artist_ids.add(new_artist_id)
                        save_id_to_log(ARTIST_LOG_FILE, new_artist_id)
                        print(f"  > Discovered new artist: {artist_name}")
                time.sleep(DELAY_BETWEEN_LIKES)
        except spotipy.exceptions.SpotifyException as e:
            if e.http_status == 429:
                print("Rate limit exceeded. Waiting for 30 seconds...")
                time.sleep(30)
            else:
                print(f"A Spotify error occurred: {e}")
                break
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
            break

    print(f"\nGoal of {SONGS_TO_LIKE_GOAL} reached! Total songs liked by this script: {len(already_liked_ids)}.")


if __name__ == "__main__":
    main()

