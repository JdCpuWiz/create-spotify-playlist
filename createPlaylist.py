import spotipy
from spotipy.oauth2 import SpotifyOAuth

def read_config(secrets_file_path):
    config = {}
    with open(secrets_file_path, 'r') as file:
        for line in file:
            key, value = line.strip().split('=', 1)
            config[key] = value
    return config

def read_song_list(song_file_path):
    songs = []
    with open(song_file_path, 'r') as file:
        for line in file:
            track, artist = line.strip().split(',', 1)
            songs.append("track:" + track + " artist:" + artist)
    return songs

config = read_config("./secrets.cfg")
# Set your Spotify API config
client_id = config.get('client_id')
client_secret = config.get('client_secret')
redirect_uri = config.get('redirect_uri')
scope = [config.get('scope')]
# Authenticate with the Spotify API
auth_manager = SpotifyOAuth(client_id=client_id,client_secret=client_secret,redirect_uri=redirect_uri,scope=scope)
sp = spotipy.Spotify(auth_manager=auth_manager)

# playlist setup 
playlist_id = ""
user_id = config.get('user_id')
playlist_name = config.get('playlist_name')
playlist_description = config.get('playlist_description')
#search to see if playlist is already created
playlists = sp.user_playlists(user=user_id)
for playlist in playlists['items']:
    if playlist['name'] == playlist_name:
        print(f"Playlist found: " + playlist['name'] + " ID: " + playlist['id'])
        playlist_id = playlist['id']
if playlist_id == "":
    # Create the playlist on your Spotify account
    playlist = sp.user_playlist_create(user=user_id, name=playlist_name, description=playlist_description)
    playlist_id = playlist["id"]
    print(f"Playlist created: " + playlist['name'] + " ID: " + playlist['id'])

# search for song id and add songs to the track list
songs_to_add = read_song_list("./song_list.csv")
track_list = []
track_count = 0
for song in songs_to_add:
    try:
        results = sp.search(q=song, type='track', market='US', limit=1)
        for idx, track in enumerate(results['tracks']['items']):
            if track_count < 100:
                track_list.append(track['uri'])        
                print(f"ADDED -->{idx + 1}: {track['uri']} {track['name']} by {track['artists'][0]['name']}")
                track_count = track_count + 1
            else:
                sp.playlist_add_items(playlist_id=playlist_id, items=track_list)
                print("99 songs added... reading next batch")
                track_list = []
                track_list.append(track['uri'])        
                print(f"ADDED -->{idx + 1}: {track['uri']} {track['name']} by {track['artists'][0]['name']}")
                track_count = 1
    except Exception as e:
        print(f"error {e}")

sp.playlist_add_items(playlist_id=playlist_id, items=track_list)

print("Playlist created and populated!")

