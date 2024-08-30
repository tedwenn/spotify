import gspread
from gspread_dataframe import set_with_dataframe
from oauth2client.service_account import ServiceAccountCredentials
import os
import pandas as pd
from functools import wraps
import time
import random
from utils import google_project_id

# Get the path to the home directory
home_dir = os.path.expanduser("~")

# Append the path to the Documents directory and the JSON key file
json_key_file_path = os.path.join(home_dir, 'Documents', f'{google_project_id}.json')

# Use the JSON key file you downloaded when you created your Google Sheets API service account
scope = ['https://spreadsheets.google.com/feeds',
            'https://www.googleapis.com/auth/drive']
credentials = ServiceAccountCredentials.from_json_keyfile_name(json_key_file_path, scope)
gc = gspread.authorize(credentials)

# todo handle gspread.exceptions.APIError: APIError: [503]: The service is currently unavailable.
def exponential_backoff(retries_limit=100):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            retries = 0
            while True:
                try:
                    return func(*args, **kwargs)
                except gspread.exceptions.APIError as e:
                    if e.response.status_code == 429 and retries < retries_limit:
                        # Exceeded quota, wait and retry with exponential backoff
                        quota_limit_value = int(e.response.json().get('error', {}).get('details', [{}])[0].get('metadata', {}).get('quota_limit_value', 0))
                        wait_time = max(2 ** retries, quota_limit_value) + random.random() - 0.5
                        retries += 1
                        print(f"Gsheet quota exceeded, retrying in {wait_time} seconds, retry {retries}/{retries_limit}.")
                        time.sleep(wait_time)
                    else:
                        raise e
        return wrapper
    return decorator

@exponential_backoff()
def open_gsheet(sheet_name):
    return gc.open(sheet_name)

# Open the Google Spreadsheet
spreadsheet = open_gsheet('2024 Albums')

@exponential_backoff()
def write_to_gsheet(df, worksheet_name):

    # Select the sheet in the Spreadsheet
    worksheet = spreadsheet.worksheet(worksheet_name)

    # Clear the entire sheet before writing new data
    worksheet.clear()

    # Write the DataFrame, df, to the Google Spreadsheet
    set_with_dataframe(worksheet, df)

@exponential_backoff()
def read_from_gsheet(worksheet_name):
    # Select the sheet
    worksheet = spreadsheet.worksheet(worksheet_name)

    # Get all the records of the data
    data = worksheet.get_all_records()

    # Convert to a DataFrame
    df = pd.DataFrame(data)

    return df

def add_rows(worksheet_name, data):
    worksheet = spreadsheet.worksheet(worksheet_name)
    worksheet.append_rows(data, value_input_option="USER_ENTERED")