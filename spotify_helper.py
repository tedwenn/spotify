import spotipy
from spotipy.oauth2 import SpotifyOAuth
from utils import client_id, client_secret, username
import requests
import time

class Spotify():

    def __init__(self) -> None:
        self.sp = spotipy.Spotify(auth_manager=SpotifyOAuth(username=username,
                                               scope='user-follow-read playlist-modify-public',
                                               client_id=client_id,
                                               client_secret=client_secret,
                                               redirect_uri='https://example.com/callback/'))
        self.headers = self.sp._auth_headers()

    def api_call_helper(self, get_response, parse_response=None, parse_item=None, kwargs={}):
        # TODO: handle requests.exceptions.ConnectionError: ('Connection aborted.', RemoteDisconnected('Remote end closed connection without response'))
        def get_response_helper(get_response, limit, **kwargs):
            n = 0
            while n < 5:
                try:
                    return get_response(limit=limit, **kwargs)
                except spotipy.exceptions.SpotifyException as spot_err:
                    if spot_err.http_status == 403:
                        print(f'403 error {n}')
                    else:
                        raise spot_err
                    n += 1
                    time.sleep(2)
            return get_response(limit=limit, **kwargs)
        def parse_response_helper(response):
            if parse_response:
                return parse_response(response)
            return response
        def parse_item_helper(item):
            if parse_item:
                return parse_item(item)
            return item
        limit = 50 # this is the most it allows
        response = parse_response_helper(get_response_helper(get_response, limit, **kwargs))
        while True:
            # TODO: KeyError: 'items'
            items = response['items']
            for item in items:
                item = parse_item_helper(item)
                yield item['id'], item
            if not response['next']:
                break

            response = parse_response_helper(get_response_helper(lambda limit, **kwargs: self.sp.next(response), limit, **kwargs))

    def get_followed_artists_helper(self, limit, offset):
        response = self.current_user_followed_artists(limit=limit, after=offset)
        return response['artists']

    def get_followed_artists(self):
        for result in self.api_call_helper(self.sp.current_user_followed_artists, parse_response=lambda response: response['artists']):
            yield result

    def get_artist_albums(self, artist_id, start_window, end_window):
        print(artist_id, start_window, end_window)
        # for album_id, album in self.api_call_helper(self.sp.artist_albums, kwargs={'artist_id': artist_id, 'include_groups': 'album', 'country': 'US'}):
        for album_id, album in self.api_call_helper(self._get_artist_albums, kwargs={'artist_id': artist_id}):
            if album['release_date'] >= start_window and album['release_date'] <= end_window:
                yield album_id, album

    def _get_artist_albums(self, artist_id, limit):
        return self.sp._get(
                "artists/" + artist_id + "/albums",
                include_groups='album',
                country='US',
                limit=limit,
            )

    def get_album_tracks(self, album_id):
        track_ids = [
            track_id for track_id, _ in self.api_call_helper(
                self.album_tracks,
                kwargs={'album_id': album_id}
            )
        ]
        return track_ids

    def get_playlist_tracks(self, playlist_id):
        track_ids = [
            track_id for track_id, _ in self.api_call_helper(
                self.sp.playlist_tracks,
                parse_item=lambda item: item['track'],
                kwargs={'playlist_id': playlist_id}
            )
        ]
        return track_ids

    def update_playlist(self, playlist_id, track_ids):
        batch_size = 100
        for i in range(0, len(track_ids), batch_size):
            batch = track_ids[i:i+batch_size]
            f = self.sp.playlist_replace_items if i == 0 else self.sp.playlist_add_items
            f(playlist_id, batch)


    def album_tracks(self, album_id, limit=50, offset=0, market=None):
        url = f"https://api.spotify.com/v1/albums/{album_id}/tracks"
        return self.request(url, params={'market': market, 'limit': limit, 'offset': offset})
    
    def request(self, url, params={}):
        sleep_time = 1
        while True:
            response = requests.get(url, headers=self.headers, params=params)
            if response.status_code != 429:
                break
            retry_after = int(response.headers.get('retry-after', sleep_time))
            retry_after = max(sleep_time, retry_after)
            print(f"Spotify API rate limit exceeded, retrying in {retry_after} seconds")
            time.sleep(retry_after)
            sleep_time *= 2
        data = response.json()
        return data
    
