import os 
import pandas as pd 
import numpy as np
from src.game_utils import *
from src.groww import datetime_to_ms

def get_game():
  folder_path = 'data'
  df, level , option , expiry =  get_market_data(folder_path,get_random_file(folder_path))
  print( level , option , expiry )
  DT = df.loc[0, 'DT'][:10]
  
  calls = {'CE' : 1 , 'PE': -1}
  call = calls[option]
  
  # read daily data
  df_daily = pd.read_csv('day_output/final.csv')
  df_daily['DT'] = df_daily['DT'].apply(lambda x : x[:10])
  df_daily = get_rows_around_student(df_daily, DT, 'DT')
  df_daily =  df_daily[[ 'DO', 'DH', 'DL', 'DC','DT2' ]]
  
  # Extra info 
  balance_df = pd.DataFrame(np.array([[level, call, 0, 500, 0,0,0,0,0]]), columns=['leval', 'opt', 'current_step', 
'balance', 'sum_hold', 'no_hold', 'pos','neg', 
'last_trade'
  ])
  
  # main df
  df['DT'] = pd.to_datetime(df['DT'])
  df['DT'] = (df['DT'].astype('int64') // 10**6)
  
  return df ,balance_df, df_daily, option