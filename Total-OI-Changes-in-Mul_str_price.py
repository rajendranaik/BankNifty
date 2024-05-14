# -*- coding: utf-8 -*-
"""
Created on Fri May 10 12:35:23 2024

@author: rajna
"""

import requests
#from bs4 import BeautifulSoup
import pandas as pd
import time
#import os

def get_option_chain_data(symbol, expiry_date):
    url = f"https://www.nseindia.com/api/option-chain-indices?symbol={symbol}"
    headers = {
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'accept-language': 'en,gu;q=0.9,hi;q=0.8',
        'accept-encoding': 'gzip, deflate, br'
    }

    with requests.Session() as session:
        response = session.get(url, headers=headers)
        if response.status_code == 200:
            return response.json()
        else:
            return None

def extract_strike_data(data, strike_price):
    records = data['filtered']['data']
    for record in records:
        if record['strikePrice'] == strike_price:
            return {
                'CE_OI': record['CE']['openInterest'],
                'PE_OI': record['PE']['openInterest']
            }

def calculate_changes(previous_data, current_data):
    return {
        'CE_OI_change': current_data['CE_OI'] - previous_data['CE_OI'],
        'PE_OI_change': current_data['PE_OI'] - previous_data['PE_OI']
    }

def display_changes(changes, strike_price):
    print(f"Strike Price: {strike_price}")
    print("Call Option OI Change:", changes['CE_OI_change'])
    print("Put Option OI Change:", changes['PE_OI_change'])
    print("-"* 30)


def track_oi_changes(symbol, expiry_date, strike_prices, interval=60, store_data=False):
    previous_data = {strike: None for strike in strike_prices}
    data_history = []
    total_call_oi_change = 0
    total_put_oi_change = 0

    while True:
        data = get_option_chain_data(symbol, expiry_date)

        if data:
            for strike_price in strike_prices:
                filtered_data = extract_strike_data(data, strike_price)

                if previous_data[strike_price] is not None:
                    changes = calculate_changes(previous_data[strike_price], filtered_data)
                    display_changes(changes, strike_price)

                    total_call_oi_change += changes['CE_OI_change']
                    total_put_oi_change += changes['PE_OI_change']

                    if store_data:
                        data_history.append({
                            **changes,
                            'strike_price': strike_price,
                            'timestamp': pd.Timestamp.now(),
                            'total_call_oi_change': total_call_oi_change,  # Add total OI changes
                            'total_put_oi_change': total_put_oi_change
                        })

                previous_data[strike_price] = filtered_data.copy()

            # Print total OI changes and difference
              # Separator
            print(f"Total Call OI Change: {total_call_oi_change}")
            print(f"Total Put OI Change: {total_put_oi_change}")
            print("*" * 40)
            print(f"Call OI - Put OI Difference: {total_call_oi_change - total_put_oi_change}")
            print("*" * 40)

        else:
            print("Error: Could not fetch option chain data. Retrying...")

        time.sleep(interval)

# Example usage
symbol = 'BANKNIFTY'
expiry_date = '15-May-2023'
strike_prices = [47500, 47600, 47700, 47800, 47900, 48000, 48100, 48200]  # List your desired strike prices
interval = 120
store_data = True

track_oi_changes(symbol, expiry_date, strike_prices, interval, store_data)
