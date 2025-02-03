import random
import hashlib

def update_playlist_albums(sp, playlist_id, next_albums):
    next_album_ids = [album.split(':')[-1] for album in next_albums]
    updated_track_ids = [track_id for album_id in next_album_ids for track_id in sp.get_album_tracks(album_id)]
    update_playlist_tracks(sp, playlist_id, updated_track_ids)
        
def update_playlist_tracks(sp, playlist_id, updated_track_ids):
    playlist_track_ids = sp.get_playlist_tracks(playlist_id)
    if playlist_track_ids != updated_track_ids:
        print('updating playlist')
        sp.update_playlist(playlist_id, updated_track_ids)
        if updated_track_ids != sp.get_playlist_tracks(playlist_id):
            raise Exception('Playlist update failed')
        
def get_deterministic_seed(album_uris):
    """Create a deterministic seed from album URIs."""
    # Sort to ensure same pair of albums always generates same seed
    sorted_uris = sorted(album_uris)
    # Create a hash of the combined URIs
    combined = '_'.join(sorted_uris).encode('utf-8')
    return int(hashlib.md5(combined).hexdigest(), 16)
        
def update_playlist_albums_matchups(sp, playlist_id, matchups):
    updated_track_ids = []
    for _, albums in matchups:
        tracks_0, tracks_1 = [sp.get_album_tracks(album_uri.split(':')[-1]) for album_uri in albums]
        short = tracks_0 if len(tracks_0) < len(tracks_1) else tracks_1
        long = tracks_1 if short == tracks_0 else tracks_0

        # Create seeded random shuffle
        seed = get_deterministic_seed(albums)
        rng = random.Random(seed)
        rng.shuffle(short)
        rng.shuffle(long)

        result = []
        while short:
            n = len(long) // (len(short) + 1)
            for _ in range(n):
                result.append(long.pop(0))
            result.append(short.pop(0))
        while long:
            result.append(long.pop(0))
        updated_track_ids.extend(result)

    update_playlist_tracks(sp, playlist_id, updated_track_ids)