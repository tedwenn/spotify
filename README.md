# Spotify Bracket Helper
Every year, I take my favorite 64 albums from the year and have them compete in matchups in a bracket, tracked on [challonge.com](https://challonge.com/top_albums_2023).
When I listen to a pair of albums, I like to splice them, so can decide which I prefer without any recency bias.
The process of splicing while adding to a Spotify playlist is kind of a pain, especially when the albums are very different lengths, so I made this program to manage that for me.

This tool allows me to update the contents of my Spotify playlist, based on the data contained within my bracket. I update the bracket online, and my playlist is automatically updated to match it.

Call `python3 main.py` to run the program.

## [scraper.py](scraper.py)

Uses `selenium` and `BeautifulSoup` to read contents of online bracket.
`requests` could not be used, because the essential data of the page is displayed via javascript, rather than HTML, so a headless Chrome browser is used to run the javascript on the page.

I define a class `Driver`, which is essentially a `selenium` wrapper designed to execute exactly what I need.
The core method of the class is `get_updated_open_matches()`, which is a generator function that returns the current set of open matches on the site, every time there's an update.
Even though Chrome is running in a headless mode, every time a new Chrome driver is created, a new Chrome icon appears in the dock, which is very annoying.
To address this, I set the driver to stay open throughout the run, and it refreshes every hour to ensure there are no issues.

## [playlister.py](playlist.py)

This connects to the Spotify API.
It contains functions to convert an artist/album name to a Spotify album URI, pull the tracks for the album, splice the tracks from two albums, and write those spliced tracks to a playlist.

## [main.py](main.py)

Inside the main method, we specify the playlist we want to work with, we use `scraper` to get the latest open matches, and when there are new open matches, we use `playlister` to update the Spotify playlist.
