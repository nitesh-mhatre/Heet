import numpy as np
import pandas as pd

class TradingEnvironment:
    def __init__(self, candles_df, balance_df, chart_df, initial_balance=10000):
        self.candles_df = candles_df  # Nifty 50 candles (dynamic per step)
        self.balance_df = balance_df  # Static account details
        self.chart_df = chart_df      # Static market context
        self.balance = initial_balance
        self.current_step = 60  # Start after the first 60 days of data
        self.actions = ['buy', 'sell', 'hold']
        self.holdings = []  # List to track individual purchase prices
        self.done = False
    
    def reset(self):
        self.current_step = 60
        self.balance = 10000
        self.holdings = []
        self.done = False
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
        current_price = self.candles_df.iloc[self.current_step]['close']

        if action == 0:  # Buy one unit
            if self.balance >= current_price:  # Ensure sufficient balance
                self.holdings.append(current_price)
                self.balance -= current_price
        elif action == 1:  # Sell all holdings
            if self.holdings:  # Ensure there are holdings to sell
                total_sell_value = len(self.holdings) * current_price
                total_buy_cost = sum(self.holdings)
                profit = total_sell_value - total_buy_cost
                self.balance += total_sell_value
                self.holdings = []  # Clear holdings after selling

        # Update step
        self.current_step += 1
        if self.current_step >= len(self.candles_df):
            self.done = True

        # Calculate reward
        net_worth = self.balance + sum(self.holdings)
        reward = net_worth - self.balance

        return self._get_observation(), reward, self.done  # Return `self.done` instead of incorrect referenc