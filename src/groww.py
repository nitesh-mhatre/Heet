import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)

import pandas as pd
import requests


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