import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)

import pandas as pd 
import os
import datetime
import pytz
import numpy as np
import requests
from yahoo_fin import stock_info
import os
import time

def get_url(level : int, expiry : str, call : str , _to : int, _from : int, interval :int):
  
  url = f'https://groww.in/v1/api/stocks_fo_data/v1/charting_service/delayed/chart/exchange/NSE/segment/FNO/NIFTY{expiry}{level}{call}?endTimeInMillis={_to}&intervalInMinutes={interval}&startTimeInMillis={_from}'
  return url
  
def url_to_df(url):
  #1:o,2:h,3:l,4:c
  res = requests.get(url)
  data = res.json()['candles']
  df = pd.DataFrame(data)
  return df
  
def get_main_url(_to, _from, interval):
  url_main = f'https://groww.in/v1/api/charting_service/v2/chart/delayed/exchange/NSE/segment/CASH/NIFTY?endTimeInMillis={_to}&intervalInMinutes={interval}&startTimeInMillis={_from}'
  return url_main
 
def get_levels(value : int, step : int, _range : int):
  '''
  This function return list of index values in given range
  value : int -> Current value of stock
  step  : int -> Step of FO market 
  _range : int -> Number of index from mid level i e. value
  '''
  
  first_level = int(step * int(value/step))
  
  if first_level <  value:
    first_level += step
  
  calls = [ i for i in range(first_level-(step*_range), first_level+(step*_range), step)]
  return calls

def get_value(stock : str):
  '''
  Use yahoo_fin to get live stock price 
  stock : str -> Stock symbol as per yahoo_fin
  '''
  return stock_info.get_live_price(stock)
  
def datetime_to_ms(dt):
  '''
  Convert datetime object into milliseconds
  
  dt : datetime.datetime -> datetime object 
  '''
  epoch = datetime.datetime(1970, 1, 1)
  delta = dt - epoch
  milliseconds = int(delta.total_seconds() * 1000)
  return milliseconds
  
  
def ms_to_datetime(ms : int):
  '''
  ms : int -> milliseconds
  This function returns date time object by converting milliseconds into datetime
  '''
  return datetime.datetime.fromtimestamp(ms, pytz.timezone('Asia/Kolkata'))