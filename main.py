from new_releases import get_new_release_dataframe
from gsheet import write_to_gsheet, read_from_gsheet
from standings import update_log, get_log
from playlister import update_playlist
from spotify_helper import Spotify
from datetime import datetime
from utils import playlist_id
import time

def update_albums(sp):
    update_log_ptf = 'update_albums_log.txt'
    try:
        with open(update_log_ptf, 'r') as f:
            last_run_time = f.readline()
        last_run_time = datetime.strptime(last_run_time, '%Y-%m-%d %H:%M:%S.%f')
        time_difference = datetime.now() - last_run_time
        if time_difference.total_seconds() < 60 * 60 * 8:
            return
    except FileNotFoundError:
        pass

    print('update albums')
    manual_album_uris = list(read_from_gsheet('manual_album_uris')['album_uri'])
    print('manual_album_uris', len(manual_album_uris))
    logged_uris = list(read_from_gsheet('log')['album_uri'])
    print('logged_uris', len(logged_uris))
    override_uris = list(set(manual_album_uris) | set(logged_uris))
    print('override_uris', len(override_uris))
    df = get_new_release_dataframe(sp, override_uris, '2023-12-01', '2024-11-30')
    print('df', df.shape)
    write_to_gsheet(df, 'album_input')
    with open(update_log_ptf, 'w') as f:
        f.write(f'{datetime.now()}')

def main():
    sp = Spotify()
    log = None
    while True:
        if (new_log := get_log()).equals(log):
            time.sleep(1)
            continue
        update_albums(sp)
        next_albums = update_log(10)
        log = new_log
        update_playlist(sp, playlist_id, next_albums)

if __name__ == '__main__':
    main()
