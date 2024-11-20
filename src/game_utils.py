import os
import pandas as pd 
import random
from groww import ms_to_datetime

def get_random_file(path):

    if not os.path.exists(path):
        print("The specified path does not exist.")
        return None

    if not os.path.isdir(path):
        print("The specified path is not a directory.")
        return None

    files = [file for file in os.listdir(path) if os.path.isfile(os.path.join(path, file))]

    if not files:
        print("No files found in the specified directory.")
        return None
        
    return random.choice(files)
    
def get_market_data(folder,file):
  path = os.path.join(folder, file)
  df = pd.read_csv(path)
  df = df[['DT','LO','LH','LL','LC','LV','MO','MH','ML','MC']]
  
  
  DT = ms_to_datetime(df.iloc[0, 'DT'])
  
  level , option , expiry, _ = file.split('-')
  return df, level , option , expiry
  
