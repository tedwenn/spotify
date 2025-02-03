import requests
from datetime import datetime
import os
import time

def get_slots():
    url = "https://api.resy.com/4/find"
    
    params = {
        "lat": "0",
        "long": "0",
        "day": "2024-08-22",
        "party_size": "2",
        "venue_id": "51480"
    }
    
    headers = {
        "Authorization": 'ResyAPI api_key="VbWk7s3L4KiK5fzlO7JD3Q5EYolJI7n5"',
        "x-resy-auth-token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJFUzI1NiJ9.eyJleHAiOjE3MjY3Nzk2MTIsInVpZCI6MTU3NjM5NywiZ3QiOiJjb25zdW1lciIsImdzIjpbXSwibGFuZyI6ImVuLXVzIiwiZXh0cmEiOnsiZ3Vlc3RfaWQiOjExMDYxOTQzfX0.AHe8hAMPTStUIawtY8PrCHsXJMawayHj-qtiSM5-ofIufoW76UyfbwPPjghvujw8I0oZQFbfWXKBA9IVkrdwGwujASbc9MaGcNeArXdwZbDKPCJUKynju7eUwOWBIILipXxdqfui-yAoeDquvNGXq4-ZnUhIMhQiPDeJyibLY1xNTxae",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36",
        "Accept": "application/json",
        "Accept-Language": "en-US,en;q=0.9",
        "Referer": "https://resy.com/",
        "Origin": "https://resy.com"
    }
    
    response = requests.get(url, params=params, headers=headers)
    return response.json()['results']['venues'][0].get('slots')

if __name__ == "__main__":
    while True:
        slots = get_slots()
        for slot in slots:
            print(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
            print(slot.get('availability'))
            print(slot.get('date'))
            if slot.get('date').get('start') <= '2024-08-22 19:30:00':
                for _ in range(5):
                    os.system('say "RESERVATION AVAILABLE!."')
        print(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        print("Sleeping for 2 minutes")
        time.sleep(60 * 2)  # Check every 2 minutes