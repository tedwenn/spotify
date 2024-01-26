from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import os

def get_soup(url):
    # Use Beautiful Soup to parse the page source
    return BeautifulSoup(get_html(url), 'html.parser')

def get_html(url):

    # ptf = 'tournament.html'

    # # Check if the file already exists
    # if os.path.exists(ptf):
    #     with open(ptf, 'r') as file:
    #         content = file.read()
    #     return content

    # Initialize Chrome options
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # Enables headless mode

    # Initialize the Chrome driver with the options
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

    # Open the URL
    driver.get(url)

    # Wait for the SVG element with the specific class to appear
    wait = WebDriverWait(driver, 10)  # Wait up to 10 seconds (adjust as needed)
    wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'svg.tournament-bracket.-for-print')))

    # Get the page source after the element is loaded
    page_source = driver.page_source

    # Close the driver
    driver.quit()

    # with open(ptf, 'w') as file:
    #     file.write(page_source)
    
    return page_source

def get_open_matches():
    soup = get_soup('https://challonge.com/top_albums_2023.svg')
    open_match_elements = soup.find_all('g', class_='match -open')
    matches = []
    for open_match_element in open_match_elements:
        match_id = int(open_match_element['data-identifier'])
        albums = [title.text for title in open_match_element.find_all('title')]
        matches.append((match_id, albums))
    matches.sort()
    return matches