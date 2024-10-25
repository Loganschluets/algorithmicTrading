import argparse
import csv
import json
import os
import sys
from datetime import datetime, timedelta
from pathlib import Path

import requests
import time
import pandas as pd

#Polygon API key
API_KEY = 'apiKey=RpgkwjK4c_F4MwwPkD8LPoxJEsSTrnFs'

#url for the Polygon API
url = 'https://api.polygon.io/v2/aggs/ticker/AAPL/range/1/minute/2023-01-09/2023-01-09?apiKey=RpgkwjK4c_F4MwwPkD8LPoxJEsSTrnFs'  # Replace with the correct endpoint

today = datetime.now().strftime('%Y-%m-%d')
yesterday = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')

tickers = ['AAPL','NVDA','SBUX','IBM','TSLA','KO','BA','TMUS','SAVE','GE','T','MSFT']

def configure_call(ticker, time, startDate, endDate):
    url = 'https://api.polygon.io/v2/aggs/ticker/'+ticker+'/range/1/'+time+'/' + yesterday + '/' + today + '?apiKey=RpgkwjK4c_F4MwwPkD8LPoxJEsSTrnFs'
    return url
# Function to make the API call
def make_api_call(stockName):
    params = {
        'apiKey': API_KEY,
    }

    try:
        response = requests.get(configure_call(ticker= stockName,
                                           time='minute',
                                           startDate=today,
                                           endDate=yesterday), params=params)
        response.raise_for_status()  # Raise an error for bad responses
        data = response.json()

        #print(json.dumps(data, indent=4))  # Use indent=4 for readability
        print("Successfully requested " + stockName + " data")

        csv_file_name = 'data/'+stockName+'/'+stockName+'_'+yesterday+'.csv'
        if not os.path.isdir('data/'+stockName):
            Path('data/'+stockName).mkdir(parents=True, exist_ok=True)

        if not Path(csv_file_name).exists():
            # Open a file for writing
            with open(csv_file_name, mode='w', newline='') as file:
                writer = csv.writer(file)

                # Write the header (column names)
                writer.writerow(['time', 'trade_volume', 'volume_weight_avg_price', 'open', 'close', 'highest_in_interval', 'lowest_in_interval', 'transactions'])

                # Write the data
                for result in data['results']:
                    writer.writerow(
                        [result['t'], result['v'], result['vw'], result['o'], result['c'], result['h'], result['l'],
                         result['n']])

            print(f"Data has been written to {csv_file_name}")
        else:
            print(f"Data has already been retreived for {csv_file_name}")

    except requests.exceptions.HTTPError as err:
        print(f"HTTP error: {err}")
    except Exception as e:
        print(f"An error occurred: {e}")


def run_continuous_calls():
    currentTime = datetime.now().strftime('%Y-%m-%d')


    for ticker in tickers:
            make_api_call(ticker)
            time.sleep(12)  # Pause for 12 seconds between calls

def is_valid_date(date_str):
    try:
        datetime.strptime(date_str, "%m-%d-%Y")
        return True
    except ValueError:
        #If ValueError is raised, the format is incorrect
        return False

def main():
    run_continuous_calls()


if __name__ == "__main__":
    main()