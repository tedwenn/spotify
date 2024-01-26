import requests

url = 'https://challonge.com/top_albums_2023.svg'

response = requests.get(url)

print(response.text)