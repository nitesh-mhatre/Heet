from src.groww import *

import pandas as pd
import os


expiry = '24D05'
data_path = 'data'
symbol = "^NSEI"
interval = 1
interval_day = 1440

current_value = get_value(symbol)
levels = get_levels(current_value, 50,8)
options = ["PE", "CE"]

dt = datetime.datetime.now()
dt = datetime_to_ms(dt)
_to = dt
_from = dt - 35712000*30
_from_day = dt - 35712000*1000

if not os.path.exists(data_path):
  os.makedirs(data_path)

if not os.path.exists(data_path+'/day_data'):
  os.makedirs(data_path+'/day_data')
 # Open-High-Low-Close
 
day_path = data_path+'/day_data/'
url_day = get_main_url(_to, _from_day, interval_day)
df_day = url_to_df(url_day)
df_day.rename(columns={
  0: 'DT',
  1: 'DO',
  2: 'DH',
  3: 'DL',
  4: 'DC',
  5: 'DV'
}, inplace=True)
df_day.to_csv(f'{day_path}{_from}.csv')
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
    df_main.drop('MV', axis=1, inplace=True)
    df_result = pd.merge(df, df_main, on='DT')
    file = f'data/{level}-{call}-{expiry}-{len(df_result)}.csv'
    df_result.to_csv(file)
    