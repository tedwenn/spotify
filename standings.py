from datetime import datetime, timedelta
from gsheet import read_from_gsheet, add_rows
import pandas as pd
import numpy as np

def get_log():
    log = read_from_gsheet('log')
    log['add_timestamp'] = pd.to_datetime(log['add_timestamp'])
    return log

def get_grade_components(grade):
    if not grade:
        return ('Z', 1)  # 'Z' ensures empty grades are sorted last
    
    base_grade = grade[0]
    modifier = grade[1] if len(grade) > 1 else ''
    
    modifier_rank = 0 if modifier == '+' else 2 if modifier == '-' else 1
    
    return (base_grade, modifier_rank)

def get_standings():
    albums = read_from_gsheet('album_input')
    log = get_log()    
    standings = log.groupby('album_uri').apply(lambda x: x.loc[x['add_timestamp'].idxmax()]).reset_index(drop=True)
    standings['appearances'] = log.groupby('album_uri').size().reset_index(name='count')['count']
    standings['ratings'] = log.groupby('album_uri').apply(lambda x: (x['Rating'] != '').sum()).reset_index(name='ratings')['ratings']
    standings = standings[['album_uri', 'add_timestamp', 'Rating', 'appearances', 'ratings']]
    standings = albums.merge(standings, on='album_uri', how='left')
    standings['appearances'] = standings['appearances'].fillna(0)
    standings['ratings'] = standings['ratings'].fillna(0)
    standings['Rating'] = standings['Rating'].fillna('')
    
    # Apply the get_grade_components function
    standings['grade_components'] = standings['Rating'].apply(get_grade_components)
    
    indices = np.lexsort((
        standings['release_date'],
        standings['add_timestamp'],
        standings['grade_components'].apply(lambda x: x[1]),  # Second-tier sort (modifier)
        standings['grade_components'].apply(lambda x: x[0]),  # First-tier sort (letter grade)
        -standings['ratings'],  # Negative for descending sort
        standings['appearances']
    ))
    standings['priority'] = indices.argsort() + 1
    standings.drop(columns=['grade_components'], inplace=True)
    return standings

def update_log(n_buffer):
    print('update log')
    n_buffer_existing = (get_log()['Rating'] == '').sum()
    if n_buffer_existing < n_buffer:
        n_albums_to_add = n_buffer - n_buffer_existing
        standings = get_standings()
        albums_to_add = standings.sort_values('priority').head(n_albums_to_add).to_dict(orient='records')
        data = [
            [
                next_album[field] for field in ('artist_uri', 'artist_name', 'album_uri', 'album_name', 'release_date')
            ] + [(datetime.now() + timedelta(seconds=0.001 * n)).strftime("%Y-%m-%d %H:%M:%S.%f")]
            for n, next_album in enumerate(albums_to_add)
        ]
        add_rows('log', data)
    
    log = get_log()

    # Filter DataFrame where 'Rating' is an empty string
    empty_ratings = log[log['Rating'] == '']

    # Find the row with the latest 'add_timestamp' for non-empty 'Rating'
    latest_non_empty_rating = log[log['Rating'] != ''].nlargest(1, 'add_timestamp')

    # Concatenate the results
    log = pd.concat([empty_ratings, latest_non_empty_rating])

    # Sort by 'add_timestamp' in ascending order
    log.sort_values('add_timestamp', inplace=True)

    # Get the list of 'album_uri'
    next_albums = log['album_uri'].tolist()
    return next_albums
