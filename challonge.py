from selenium import webdriver
from selenium.common.exceptions import TimeoutException, WebDriverException
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import time
import pandas as pd
from datetime import datetime
from standings import get_standings

class Driver():

    def __init__(self):
        self.t0 = time.time()
        self.n_reset = 0
        self._reset_driver()

    @property
    def driver(self):
        if time.time() - self.t0 > self.n_reset * 60 * 60: # create a new driver if it's been more than an hour
            self._driver.quit()
            self._reset_driver()
        return self._driver

    def _reset_driver(self):

        print('creating new driver at', datetime.now().strftime('%Y-%m-%d %H:%M:%S'))

        self.n_reset += 1

        # # Initialize Chrome options
        chrome_options = Options()
        chrome_options.add_argument("--headless")  # Enables headless mode

        # Initialize the Chrome driver with the options
        self._driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
    
    def get_soup(self, url):
        # specify condition to wait for
        expected_condition_function = EC.presence_of_element_located((By.CSS_SELECTOR, 'svg.tournament-bracket.-for-print'))

        # get the html
        html = self.get_html(url, expected_condition_function=expected_condition_function)

        # Use Beautiful Soup to parse the page source
        bs = BeautifulSoup(html, 'html.parser')
        
        return bs

    def get_open_matches(self):
        print('getting open matches', datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
        soup = self.get_soup('https://challonge.com/top_albums_2024.svg')
        open_match_elements = soup.find_all('g', class_='match -open')
        matches = []
        for open_match_element in open_match_elements:
            match_id = int(open_match_element['data-identifier'])
            albums = [title.text for title in open_match_element.find_all('title')]
            matches.append((match_id, albums))
        matches.sort()
        return matches
    
    def get_updated_open_matches(self):
        open_matches = self.get_open_matches()
        while True:
            new_open_matches = self.get_open_matches()
            if new_open_matches != open_matches:
                open_matches = new_open_matches
                print('new open matches!', datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
                yield new_open_matches
            else:
                time.sleep(5)
        
    def webdriver_wait(self, expected_condition_function, wait_time):
        wait = WebDriverWait(self.driver, wait_time)
        wait.until(expected_condition_function)

    def safe_get(self, url, n_retries=None):
        n_retries = n_retries or 0
        try:
            self.driver.get(url)
        except WebDriverException as e:
            n_retries += 1
            if n_retries > 50: # max_retries
                print('maxed out retries')
                raise e
            print("An error occurred: ", e)
            print('retrying, attempt', n_retries)
            self._reset_driver()
            self.safe_get(url, n_retries)

    def get_html(self, url, expected_condition_function=None):

        self.safe_get(url)

        if expected_condition_function:
            wait_time = 10
            max_wait_time = 5 * 60
            while True:
                try:
                    self.webdriver_wait(expected_condition_function, wait_time)
                    break
                except TimeoutException:
                    print('timed out at', wait_time, 'seconds')
                    wait_time *= 1.2
                    if wait_time > max_wait_time:
                        print('too much waiting! trying again')
                        return self.get_html(url, expected_condition_function)
                    
        page_source = self._driver.page_source # don't want to refresh driver after getting URL
        
        return page_source
    
def get_matchups():

    # get matchups from Challonge and convert them to df
    driver = Driver()
    records = []
    for match_id, albums in driver.get_open_matches():
        for position, album_str in enumerate(albums):
            records.append({
                'match_id': match_id,
                'position': position,
                'album_str': album_str
            })
    df_matchups = pd.DataFrame(records)

    # get standings from Google Sheets
    df_standings = get_standings()
    df_standings = df_standings[df_standings['Rating'] < 'C']
    
    # Create album_str in standings
    df_standings['album_str'] = df_standings['artist_name'] + ' - ' + df_standings['album_name']

    # Join with validation
    df_combined = df_matchups.join(
        df_standings.set_index('album_str'),
        on='album_str',
        validate='1:1'
    )

    # Transform into list of tuples
    result = []
    for match_id, group in df_combined.groupby('match_id'):
        # Sort by position to ensure album_uri_0 and album_uri_1 are in correct order
        group = group.sort_values('position')
        album_uris = tuple(group['album_uri'].tolist())
        result.append((match_id, album_uris))
    
    return result