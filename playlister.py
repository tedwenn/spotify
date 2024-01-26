import spotipy
from spotipy.oauth2 import SpotifyOAuth
from utils import client_id, client_secret

# Set up authentication
sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=client_id,
                                               client_secret=client_secret,
                                               redirect_uri='https://example.com/callback/',
                                               scope='playlist-modify-public playlist-modify-private'))

# Function to add songs to a playlist
def add_tracks_to_playlist(playlist_uri, track_uris):
    sp.playlist_add_items(playlist_uri, track_uris)
    
def album_tracks(album_uri):
    return [track['uri'] for track in sp.album_tracks(album_uri)['items']]

def splice_albums(album_uri_1, album_uri_2):
    tracks_1, tracks_2 = [album_tracks(album_uri) for album_uri in (album_uri_1, album_uri_2)]
    short = tracks_1 if len(tracks_1) < len(tracks_2) else tracks_2
    long = tracks_2 if short == tracks_1 else tracks_1
    result = []
    while short:
        n = len(long) // (len(short) + 1)
        for _ in range(n):
            result.append(long.pop(0))
        result.append(short.pop(0))
    while long:
        result.append(long.pop(0))
    return result

def search_album_uri(album_str):
    """Search for an album URI based on a string input of the form 'artist_name - album_name'."""
    artist_name, album_name = album_str.split(' - ')
    album_name = album_name.replace("'", '')
    results = sp.search(q=f'artist:{artist_name} album:{album_name}', type='album')
    albums = results['albums']['items']
    if albums:
        # Return the URI of the first album found
        return albums[0]['uri']
    else:
        raise Exception(f'No album found for the given artist ({artist_name}) and album ({album_name}) name.')

def reset_playlist(playlist_uri):

    # get tracks on playlist
    track_uris = []
    results = sp.playlist_tracks(playlist_uri)
    track_uris.extend([item['track']['uri'] for item in results['items']])
    # Continue fetching tracks until all are retrieved
    while results['next']:
        results = sp.next(results)
        track_uris.extend([track['track']['uri'] for track in results['items']])

    print(f'found {len(track_uris)} tracks on playlist')

    # Remove tracks in batches if necessary
    for i in range(0, len(track_uris), 100):
        batch = track_uris[i:i + 100]
        print(f'deleting {len(batch)} tracks from playlist')
        sp.playlist_remove_all_occurrences_of_items(playlist_uri, batch)
