import scraper
import playlister

def main():
    playlist_uri = 'spotify:playlist:6SQv03R7xcSWsS31ihoN0e'
    driver = scraper.Driver()
    for open_matches in driver.get_updated_open_matches():
        playlister.reset_playlist(playlist_uri)
        track_uris = []
        for match_id, albums in open_matches:
            print(match_id, albums)
            album_uri_1, album_uri_2 = [playlister.search_album_uri(album_str) for album_str in albums]
            track_uris.extend(playlister.splice_albums(album_uri_1, album_uri_2))

        print(f'{len(track_uris)} to add to playlist')
        for i in range(0, len(track_uris), 100):
            batch = track_uris[i:i + 100]
            print(f'adding {len(batch)} tracks to playlist')
            playlister.add_tracks_to_playlist(playlist_uri, batch)

if __name__ == '__main__':
    main()
