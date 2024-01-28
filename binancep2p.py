import requests
import json
import time
import sys
import os
from pprint import pprint
import asyncio
import configparser

config = configparser.ConfigParser()
config.read('telegrambot.config')
FX_API = config.get('Section1', 'FX_API')

def request_p2p():

    headers = {
        "Accept": "*/*",
        "Accept-Encoding": "gzip, deflate, br",
        "Accept-Language": "en-GB,en-US;q=0.9,en;q=0.8",
        "Cache-Control": "no-cache",
        "Connection": "keep-alive",
        "Content-Length": "123",
        "content-type": "application/json",
        "Host": "p2p.binance.com",
        "Origin": "https://p2p.binance.com",
        "Pragma": "no-cache",
        "TE": "Trailers",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:88.0) Gecko/20100101 Firefox/88.0"
    }

    data = {
        "asset": "USDT",
        "countries": [],
        "fiat": "HKD",
        "merchantCheck": False,
        "page": 1,
        "payTypes": ["FPS"],
        "proMerchantAds": False,
        "publisherType": None,
        "rows": 20,
        "tradeType": "BUY"
    }

    res = requests.post(
        'https://p2p.binance.com/bapi/c2c/v2/friendly/c2c/adv/search', headers=headers, json=data)
    
    data = []
    # pprint(res.json())
    for r in res.json()["data"]:
        tradeMethodShortName = r["adv"]["tradeMethods"][0]["tradeMethodShortName"]
        price = r["adv"]["price"]
        min_amount = r["adv"]["minSingleTransAmount"]
        max_amount = r["adv"]["maxSingleTransAmount"]

        if tradeMethodShortName == "FPS":
            data.append({
                "price": price,
                "min_amount": min_amount,
                "max_amount": max_amount,
                "tradeMethodShortName": tradeMethodShortName,
            })
            # print(min_amount, "to", max_amount, tradeMethodShortName)
    # print(time.strftime("%d %b %Y %H:%M:%S"))
    # pprint(data)
    # os.system('cls')
    return data

def request_fx():

    headers = {"accept": "application/json"}

    res = requests.post('https://openexchangerates.org/api/latest.json?app_id='+FX_API+'&symbols=HKD&prettyprint=false&show_alternative=false')
    # print(res.json())
    if res.json()["rates"]:
        data = res.json()["rates"]["HKD"]
        # print(data)
    else:
        print("Exchange rates API error")
    
    return data

# request_fx()