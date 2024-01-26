from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import time
from datetime import datetime

class Driver():

    def __init__(self):
        self.t0 = time.time()
        self.n_reset = 0
        self._driver = self._new_driver()

    @property
    def driver(self):
        if time.time() - self.t0 > self.n_reset * 60 * 60: # create a new driver if it's been more than an hour
            self._driver.quit()
            self._driver = self._new_driver()
        return self._driver

    def _new_driver(self):

        print('creating new driver at', datetime.now().strftime('%Y-%m-%d %H:%M:%S'))

        self.n_reset += 1

        # Initialize Chrome options
        chrome_options = Options()
        chrome_options.add_argument("--headless")  # Enables headless mode

        # Initialize the Chrome driver with the options
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

        return driver
    
    def get_soup(self, url):
        # Use Beautiful Soup to parse the page source
        return BeautifulSoup(self.get_html(url), 'html.parser')
    
    def get_html(self, url):
        wait_time = 10
        while True:
            try:
                return self.get_html_with_wait(url, wait_time)
            except TimeoutException:
                print('webdriver wait failed', wait_time, datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
                wait_time *= 1.5

    def get_html_with_wait(self, url, wait_time):

        # Open the URL
        self.driver.get(url)

        # Wait for the SVG element with the specific class to appear
        wait = WebDriverWait(self.driver, wait_time)
        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'svg.tournament-bracket.-for-print')))

        # Get the page source after the element is loaded
        page_source = self.driver.page_source
        
        return page_source

    def get_open_matches(self):
        soup = self.get_soup('https://challonge.com/top_albums_2023.svg')
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
