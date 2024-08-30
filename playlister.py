def update_playlist(sp, playlist_id, next_albums):
    playlist_track_ids = sp.get_playlist_tracks(playlist_id)
    next_album_ids = [album.split(':')[-1] for album in next_albums]
    updated_track_ids = [track_id for album_id in next_album_ids for track_id in sp.get_album_tracks(album_id)]
    if playlist_track_ids != updated_track_ids:
        sp.update_playlist(playlist_id, updated_track_ids)
        if updated_track_ids != sp.get_playlist_tracks(playlist_id):
            raise Exception('Playlist update failed')