import os
import pandas as pd 
import random

import os
import random
import json

def get_random_file(path):
    # Check if the specified path exists and is a directory
    
    json_path = 'record.json'
    
    if not os.path.exists(path):
        print("The specified path does not exist.")
        return None
    if not os.path.isdir(path):
        print("The specified path is not a directory.")
        return None
    
    # Get the list of files in the directory
    files = [file for file in os.listdir(path) if os.path.isfile(os.path.join(path, file))]
    if not files:
        print("No files found in the specified directory.")
        return None
    
    # Select a random file
    selected_file = random.choice(files)

    # Ensure the JSON file exists or create it
    if not os.path.exists(json_path):
        with open(json_path, 'w') as json_file:
            json.dump({}, json_file)  # Initialize with an empty dictionary
    
    # Load existing JSON data
    with open(json_path, 'r') as json_file:
        file_data = json.load(json_file)
    
    # Update the file usage count in the JSON data
    if selected_file in file_data:
        file_data[selected_file] += 1
    else:
        file_data[selected_file] = 1
    
    # Save the updated JSON data
    with open(json_path, 'w') as json_file:
        json.dump(file_data, json_file, indent=4)
        print('record saved')
    
    return selected_file

    
def get_market_data(folder,file):
  path = os.path.join(folder, file)
  df = pd.read_csv(path)
  df = df[['DT','LO','LH','LL','LC','LV','MO','MH','ML','MC']]
  level , option , expiry, _ = file.split('-')
  return df, level , option , expiry
  

def get_rows_around_student(df, value, column_name):
  index = df.index[df[column_name] == value].tolist()
  
  if not index:
      raise ValueError(f" '{value}' not found in DataFrame.")
  
  index = index[0]
  start_idx = max(0, index - 50)
  return df.iloc[start_idx:index]