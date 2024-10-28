
import csv
import os
from datetime import datetime, timedelta
from pathlib import Path

import requests
import time

#Polygon API key
API_KEY = 'apiKey=RpgkwjK4c_F4MwwPkD8LPoxJEsSTrnFs'

url = 'https://api.polygon.io/v2/aggs/ticker/AAPL/range/1/minute/2023-01-09/2023-01-09?apiKey=RpgkwjK4c_F4MwwPkD8LPoxJEsSTrnFs'  # Replace with the correct endpoint

today = datetime.now().strftime('%Y-%m-%d')
yesterday = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')

tickers = ['AAPL','NVDA','SBUX','IBM','TSLA','KO','BA','TMUS','SAVE','GE','T','MSFT']

def configure_call(ticker, time, startDate, endDate):
    url = 'https://api.polygon.io/v2/aggs/ticker/'+ticker+'/range/1/'+time+'/' + yesterday + '/' + today + '?apiKey=RpgkwjK4c_F4MwwPkD8LPoxJEsSTrnFs'
    return url

def get_last_30_trading_days():
    trading_days = []
    current_date = datetime.now()
    current_date -= timedelta(days=1)
    while len(trading_days) < 30:
        if current_date.weekday() < 5:
            trading_days.append(current_date)
        current_date -= timedelta(days=1)
    trading_days.reverse()
    return trading_days

# Function to configure API URL
def configure_call(ticker, date):

    date = date.strftime('%Y-%m-%d')
    #date2 = endDate.strftime('%Y-%m-%d')
    url = f'https://api.polygon.io/v2/aggs/ticker/{ticker}/range/1/minute/{date}/{date}?apiKey=RpgkwjK4c_F4MwwPkD8LPoxJEsSTrnFs'
    return url

def make_api_call(stockName, date, max_retries=10, retry_delay=12):
    params = {
        'apiKey': API_KEY,
    }
    retries = 0
    success = False
    while not success and retries < max_retries:
        try:
            response = requests.get(configure_call(ticker= stockName, date=date), params=params)
            response.raise_for_status()  # Raise an error for bad responses
            data = response.json()

            printDate = date.strftime('%Y-%m-%d')

            #print(json.dumps(data, indent=4))  # Use indent=4 for readability
            print("Successfully requested " + stockName + " data for "+printDate)

            csv_file_name = 'data/'+stockName+'/'+stockName+'_'+printDate+'.csv'
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

            success = True  # Exit the loop after successful retrieval

        except (requests.exceptions.HTTPError, ValueError) as err:
            retries += 1
            print(f"Attempt {retries} failed for {stockName} on {date.strftime('%Y-%m-%d')}: {err}")

            if retries < max_retries:
                print(f"Retrying in {retry_delay} seconds...")
                time.sleep(retry_delay)

            else:
                print(f"Failed to retrieve data for {stockName} on {date.strftime('%Y-%m-%d')} after {max_retries} attempts.")

        except Exception as e:
            print(f"An unexpected error occurred: {e}")

            break


def run_continuous_calls():

    trading_days = get_last_30_trading_days()

    trading_days.clear()

    trading_day = (datetime.now() - timedelta(days=1))

    trading_days.append(trading_day)
    for ticker in tickers:
        for date in trading_days:
            make_api_call(ticker, date)
            time.sleep(12)

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
