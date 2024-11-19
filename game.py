import os 
import pandas as pd 

from src.game_utils import *


folder_path = 'data'
print(get_market_data(folder_path,get_random_file(folder_path)))