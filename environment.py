import numpy as np
import pandas as pd

class TradingEnvironment:
    def __init__(self, candles_df, balance_df, chart_df, initial_balance=1500):
        self.candles_df = candles_df  # Nifty 50 candles (dynamic per step)
        self.balance_df = balance_df  # Static account details
        self.chart_df = chart_df      # Static market context
        self.balance = initial_balance
        self.current_step = 60  # Start after the first 60 days of data
        self.actions = ['buy', 'sell', 'hold']
        self.holdings = []  # List to track individual purchase prices
        self.done = False
        
        self.no_positive = 0
        self.negative = 0
        self.profit = 0
        self.history = []
        self.last_trade_step = 60  # Track the step of the last trade

    def reset(self):
        current_price = self.candles_df.iloc[self.current_step-1]['LC']
        print(self.no_positive, self.negative, int(self.balance +(len(self.holdings) * (current_price-1))) ,self.current_step)
        print(pd.DataFrame( self.history , columns= ['order', 'No', 'at', 'balance']))
        print("-----------------------------------")
        self.current_step = 60
        self.balance = 1500
        self.holdings = []
        self.done = False
        self.no_positive = 0
        self.negative = 0
        self.profit = 0
        self.last_trade_step = 60
        self.history = []
        return self._get_observation()

    def _get_observation(self):
        # Get the recent 60 candles data, static balance, and static market chart
        obs = {
            'candles': self.candles_df.iloc[self.current_step - 60:self.current_step].values,  # Last 60 candles
            'balance': self.balance_df.values,  # Static account details
            'chart': self.chart_df.values       # Static market context
        }
        return obs
        
    def get_rewards(self, action):
      current_price = self.candles_df.iloc[self.current_step]['LC']
      next_60_min = self.candles_df.iloc[self.current_step:self.current_step + 120] if self.current_step + 120 < len(self.candles_df) else self.candles_df.iloc[self.current_step:]
      next_20_min = self.candles_df.iloc[self.current_step:self.current_step + 20] if self.current_step + 20 < len(self.candles_df) else self.candles_df.iloc[self.current_step:]
      next_30_min = self.candles_df.iloc[self.current_step:self.current_step + 30] if self.current_step + 30 < len(self.candles_df) else self.candles_df.iloc[self.current_step:]
  
      reward = 0
  
      if action == 0:  # Buy
          if self.balance >= current_price:
              # Check for potential profit in the next 60 minutes
              max_future_price_idx = next_60_min['LC'].idxmax()
              max_future_price = next_60_min['LC'].loc[max_future_price_idx]
  
              # Check for a deep decrement
              min_future_price_idx = next_60_min['LC'].idxmin()
              min_future_price = next_60_min['LC'].loc[min_future_price_idx]
  
              if max_future_price > current_price * 1.1 and max_future_price - current_price > 5:
                  if (
                      min_future_price_idx > max_future_price_idx  # Ensure min comes after max
                      or min_future_price > current_price * 0.95  # Ensure min isn't too low before max
                  ):
                      # Check if averaging is possible
                      if self.holdings :
                          if len(self.holdings) < 4 and current_price < min(self.holdings) * 0.9:
                              reward = 25 #a strong buy signal
                          else:
                              reward = -10  # Positive reward for buying under favorable conditions
                      else:
                          reward = 10
                  else:
                      reward = -5  # Negative reward for insufficient deep decrement
              else:
                  reward = -10  # Negative reward for no significant profit potential
          else:
              reward = -10  # Negative reward for insufficient balance
          if len(self.holdings)>2:
              reward -= len(self.holdings)*10
  
      elif action == 1:  # Sell
          if self.holdings:
              # Check if the market is falling in the next 20 minutes
              if next_20_min['LC'].min() < current_price or next_30_min['LC'].max() <= current_price:
                  reward = 10  * int(current_price -min(self.holdings))  # Positive reward for selling at the right time
              else:
                  reward = -5  # Negative reward for holding during unfavorable conditions
          else:
              reward = -10  # Negative reward for selling without holdings
  
      elif action == 2:  # Hold
          buy_reward = self.get_rewards(0)
          sell_reward = self.get_rewards(1)
  
          if buy_reward < 0 and sell_reward < 0:
              reward = 60  # Positive reward for holding when both buy and sell are unfavorable
          else:
              reward = -4  # Negative reward for not taking action when better options exist
  
      # Adjust reward based on correctness of action
      if action in [0, 1] and reward > 0:
          reward *= 1.2  # Add 10% bonus for correct action
      elif reward < 0:
          reward *= 1.1  # Increase penalty by 10% for incorrect action
  
      return reward

    def step(self, action):
        current_price = self.candles_df.iloc[self.current_step]['LC']
        previous_price = self.candles_df.iloc[self.current_step - 1]['LC'] if self.current_step > 60 else current_price
        
        reward = self.get_rewards(action)

        if action == 0:  # Buy one unit
            if self.balance >= current_price:  # Ensure sufficient balance
                self.holdings.append(current_price)
                self.balance -= (current_price+1)
                self.last_trade_step = self.current_step  # Update last trade step
                self.history.append(('buy', self.current_step ,current_price, self.balance ))
        elif action == 1:  # Sell all holdings
            if self.holdings:  # Ensure there are holdings to sell
                total_sell_value = len(self.holdings) * (current_price-1)
                total_buy_cost = sum(self.holdings)
                self.profit = total_sell_value - total_buy_cost
                self.balance += total_sell_value
                self.holdings = []  # Clear holdings
                self.last_trade_step = self.current_step  # Update last trade step
                self.history.append(('sell', self.current_step ,current_price, self.balance ))

                if self.profit > 0:
                    self.no_positive += 1
                elif self.profit < 0:
                    self.negative += 1

        # Update step
        self.current_step += 1
        
        if self.current_step >= len(self.candles_df):
            self.done = True
        if self.negative > 4:
            self.done = True
        if (len(self.holdings) * current_price) + self.balance < 1410:
            self.done = True
        if len(self.holdings)>6:
            self.done =True
        
        if self.done and reward >= 0:
            self.done = False
            
        # update balance_df
        #print(self.balance_df)
        self.balance_df['current_step'] = self.current_step
        self.balance_df['balance'] = self.balance
        self.balance_df['sum_hold'] = sum(self.holdings)
        self.balance_df['no_hold'] =  len(self.holdings)
        self.balance_df['pos'] = self.no_positive
        self.balance_df['neg'] = self.negative
        self.balance_df['last_trade'] = self.last_trade_step
        

        return self._get_observation(), reward, self.done
        