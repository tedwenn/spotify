import pandas as pd

def create_new_release_row(album_id, sp=None, album=None, artist_id=None, artist=None):
    if not album:
        album = sp.sp.album(album_id)
    if not artist:
        if not artist_id:
            artist_id = album['artists'][0]['id']
        artist = sp.sp.artist(artist_id)
    return ('spotify:artist:' + artist_id, artist['name'], 'spotify:album:' + album_id, album['name'], album['release_date'])

def get_new_release_dataframe(sp, override_uris, start_window, end_window):
    album_ids = set()
    n_artists = 0
    new_releases = []
    for artist_id, artist in sp.get_followed_artists():
        print('checking artist', artist_id, artist['name'])
        for album_id, album in sp.get_artist_albums(artist_id, start_window, end_window):
            if album_id in album_ids:
                continue
            album_ids.add(album_id)
            nr_row = create_new_release_row(album_id, album=album, artist_id=artist_id, artist=artist)
            new_releases.append(nr_row)
        n_artists += 1
        print('n_artists', n_artists, 'n_albums', len(album_ids))
    print('checking override_uris', len(override_uris))
    for album_uri in override_uris:
        album_id = album_uri.split(':')[-1]
        if album_id in album_ids:
            continue
        album_ids.add(album_id)
        nr_row = create_new_release_row(album_id, sp=sp)
        new_releases.append(nr_row)
    print('n_albums', len(album_ids))
    df = pd.DataFrame(new_releases, columns=['artist_uri', 'artist_name', 'album_uri', 'album_name', 'release_date'])
    df = df.sort_values('release_date', ascending=True)
    return df