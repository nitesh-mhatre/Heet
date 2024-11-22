import numpy as np
import pandas as pd

class TradingEnvironment:
    def __init__(self, candles_df, balance_df, chart_df, initial_balance=500):
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
        print(self.no_positive, self.negative, self.balance,self.current_step)
        print(pd.DataFrame( self.history , columns= ['order', 'No', 'at', 'balance']))
        print("-----------------------------------")
        self.current_step = 60
        self.balance = 500
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

    def step(self, action):
        current_price = self.candles_df.iloc[self.current_step]['LC']
        previous_price = self.candles_df.iloc[self.current_step - 1]['LC'] if self.current_step > 60 else current_price
        
        

        if action == 0:  # Buy one unit
            if self.balance >= current_price:  # Ensure sufficient balance
                self.holdings.append(current_price)
                self.balance -= current_price
                self.last_trade_step = self.current_step  # Update last trade step
                self.history.append(('buy', self.current_step ,current_price, self.balance ))
        elif action == 1:  # Sell all holdings
            if self.holdings:  # Ensure there are holdings to sell
                total_sell_value = len(self.holdings) * current_price
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
        if (len(self.holdings) * current_price) + self.balance < 410:
            self.done = True
            
        # update balance_df
        #print(self.balance_df)
        self.balance_df['current_step'] = self.current_step
        self.balance_df['balance'] = self.balance
        self.balance_df['sum_hold'] = sum(self.holdings)
        self.balance_df['no_hold'] =  len(self.holdings)
        self.balance_df['pos'] = self.no_positive
        self.balance_df['neg'] = self.negative
        self.balance_df['last_trade'] = self.last_trade_step
        
        
        # Calculate net worth
        net_worth = (len(self.holdings) * current_price) + self.balance
        
        reward = 0
        # Rewarding logic
        if action == 0:  # Buyin
            # Reward/Penalty for buying
            if current_price < previous_price:
                reward += 200  # Reward for buying at a lower price
            else:
                reward -= 100  # Penalty for buying at a higher pric
            # Penalty for consecutive buys
            if len(self.history) >= 2 and self.history[-2][0] == 'buy':
                reward -= 1000
                
            if len(self.history) >= 2 and self.history[-2][0] == 'sell':
                reward -= 10000
        elif action == 1:  # Selling# Reward/Penalty for selling
            if self.profit > 0:
                if 10*self.profit > current_price:
                  reward = 100000
                  
                reward += self.profit * 1500  # Strong reward for profit
                if current_price > previous_price:
                    reward += 100  # Extra reward for selling at a peak
            else:
                reward += self.profit * 5  # Reduced penalty for loss
                reward -= 200
            
        else:  # Holding
          if current_price > previous_price:
            reward += 150  # Slight reward for holding in an uptrend
          else:
            reward -= 5  # Penalize holding in a downtrend

        # Reward for increasing balance
        if action in (0,1):
          reward += min(10, (net_worth - 500) * 1)

        # Penalize for inactivity (no trades in the last 90 steps)
        if self.current_step - self.last_trade_step > 60:
            reward -= 50  # Penalty for inactivity
            
        if self.current_step - self.last_trade_step < 3 and action in (0,1):
            reward -= 1000
            
        reward = reward / 100

        return self._get_observation(), reward, self.done
        