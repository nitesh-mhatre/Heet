from src.groww import *

import pandas as pd
import os


expiry = '24N21'
data_path = 'data'
symbol = "^NSEI"
interval = 1

current_value = get_value(symbol)
print("Live value is ",current_value)
levels = get_levels(current_value, 50,4)
options = ["PE", "CE"]

print(levels)
dt = datetime.datetime.now()
dt = datetime_to_ms(dt)
_to = dt
_from = dt - 35712000*15

if not os.path.exists(data_path):
    os.makedirs(data_path)
 
 # Open-High-Low-Close  
for level in levels:
  for call in options:
    print(level, expiry , call, _to , _from, interval)
    url = get_url(level, expiry , call, _to , _from, interval)
    df =url_to_df(url)
    df.rename(columns={
      0: 'DT',
      1: 'LO',
      2: 'LH',
      3: 'LL',
      4: 'LC',
      5: 'LV'
    }, inplace=True)
    print(df.head(2))
    url_main = get_main_url(_to, _from, interval)
    df_main = url_to_df(url_main)
    df_main.rename(columns={
      0: 'DT',
      1: 'MO',
      2: 'MH',
      3: 'ML',
      4: 'MC',
      5: 'MV'
    }, inplace=True)
    df_main.drop('MV', axis=1)
    print(df_main.head(2))
    break
  break