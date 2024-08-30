import yaml

with open('config.yaml', 'r') as file:
    config = yaml.safe_load(file)

client_id = config['client_id']
client_secret = config['client_secret']
username = config['username']
playlist_id = config['playlist_id']
google_project_id = config['google_project_id']