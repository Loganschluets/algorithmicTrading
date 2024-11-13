
import csv
import os
from datetime import datetime, timedelta
from pathlib import Path

import pandas as pd
import requests
import time

#Polygon API key
API_KEY = 'apiKey=RpgkwjK4c_F4MwwPkD8LPoxJEsSTrnFs'

url = 'https://api.polygon.io/v2/aggs/ticker/AAPL/range/1/minute/2023-01-09/2023-01-09?apiKey=RpgkwjK4c_F4MwwPkD8LPoxJEsSTrnFs'  # Replace with the correct endpoint

today = datetime.now().strftime('%Y-%m-%d')
yesterday = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')

tickers = ['IBM','NVDA','SBUX','AAPL','TSLA','KO','BA','TMUS','CVX'
           'SAVE','GE','T','MSFT','HPQ','HOG','F','V','X','W','C','A',
          'G','H','J','K','L','INTC','MMM','WOOF','TGT','XOM','BP','SHEL']

HOLIDAYS = [
    # Full market holidays
    '2024-01-01',
    '2024-01-15',
    '2024-02-19',
    '2024-03-29',
    '2024-05-27',
    '2024-06-19',
    '2024-07-04',
    '2024-09-02',
    '2024-11-28',
    '2024-12-25',

    # Early closures
    '2024-07-03',
    '2024-11-29',
    '2024-12-24',
]

def configure_call(ticker, time, startDate, endDate):
    url = 'https://api.polygon.io/v2/aggs/ticker/'+ticker+'/range/1/'+time+'/' + yesterday + '/' + today + '?apiKey=RpgkwjK4c_F4MwwPkD8LPoxJEsSTrnFs'
    return url

def get_last_n_trading_days(n):
    trading_days = []
    current_date = datetime.now() - timedelta(days=1)

    # convert holidays to datetime objects for comparison
    holiday_dates = {datetime.strptime(date, '%Y-%m-%d').date() for date in HOLIDAYS}

    while len(trading_days) < n:
        if current_date.weekday() < 5 and current_date.date() not in holiday_dates:
            trading_days.append(current_date)
        current_date -= timedelta(days=1)

    trading_days.reverse()
    return trading_days


# Function to configure API URL
def configure_call(ticker, date, multiplier, interval):

    date = date.strftime('%Y-%m-%d')
    #date2 = endDate.strftime('%Y-%m-%d')
    url = f'https://api.polygon.io/v2/aggs/ticker/{ticker}/range/{multiplier}/{interval}/{date}/{date}?apiKey=RpgkwjK4c_F4MwwPkD8LPoxJEsSTrnFs'
    return url

def make_api_call(stockName, date, multiplier, interval, max_retries=10, retry_delay=12):

    #creates directory for stock if not already made
    if not os.path.isdir(f'data_{multiplier}_{interval}/' + stockName):
        Path(f'data_{multiplier}_{interval}/' + stockName).mkdir(parents=True, exist_ok=True)
        print(f"created {stockName} directory")

    printDate = date.strftime('%Y-%m-%d')
    csv_file_name = f'data_{multiplier}_{interval}/'+stockName+'/'+stockName+'_'+printDate+'.csv'
    params = {
        'apiKey': API_KEY,
    }
    retries = 0
    success = False


    if Path(csv_file_name).exists() == False:
        fileWriteEligible = True
    else:
        if pd.read_csv(csv_file_name).empty == True:
            fileWriteEligible = True
        else:
            fileWriteEligible = False

    """checks if file doesn't exist OR
    if it does exist and is empty
    
    if either of these conditions are met makes the request
    otherwise returns false and skips timer"""
    if fileWriteEligible:
        while not success and retries < max_retries:
            try:
                response = requests.get(
                    configure_call(ticker= stockName, date=date, multiplier=multiplier, interval=interval),
                    params=params)
                response.raise_for_status()
                data = response.json()

                #print(json.dumps(data, indent=4))  # Use indent=4 for readability

                with open(csv_file_name, mode='w', newline='') as file:
                    writer = csv.writer(file)

                    # Write the header (column names)
                    writer.writerow(['time', 'trade_volume', 'volume_weight_avg_price', 'open', 'close', 'highest_in_interval', 'lowest_in_interval', 'transactions'])

                    # Write the data
                    for result in data['results']:
                        writer.writerow(
                            [result['t'], result['v'], result['vw'], result['o'], result['c'], result['h'], result['l'],
                             result['n']])

                #Exit the loop after successful retrieval
                print("Successfully wrote " + stockName + " data for " + printDate)
                success = True

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

        return True

    else:

        print(f"data already written to file: {csv_file_name}")
        return False

def run_continuous_calls():

    """Define days here"""
    trading_days = get_last_n_trading_days(6)

    for ticker in tickers:
        for date in trading_days:

            """CONFIGURE MAIN CALL HERE"""
            """This line defines data time interval, ticker and date"""
            makeCall = make_api_call(ticker, date, '30', 'minute')

            if makeCall:
                time.sleep(12)

    #for date in trading_days:

        """CONFIGURE MAIN CALL HERE"""
        """This line defines data time interval, ticker and date"""
        #makeCall = make_api_call("GOOGL", date, '15', 'minute')

        """checks to see if call actually has to be made. If data was already retrieved then
        skip call and check next one"""
        """
        if makeCall:
            time.sleep(12)"""

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
