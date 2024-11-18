from src.groww import *

import pandas as pd 

expiry = ''
symbol = "^NSEI"

current_value = get_value(symbol)

print("Live value is ",current_value)

levels = get_levels(current_value, 50,6)

print(levels)
