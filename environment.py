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
        self.last_trade_step = 50  # Track the step of the last trade

    def reset(self):
        current_price = self.candles_df.iloc[self.current_step - 1]['LC']
        print(self.no_positive, self.negative, int(self.balance + (len(self.holdings) * (current_price - 1))), self.current_step)
        print(pd.DataFrame(self.history, columns=['order', 'No', 'at', 'balance', 'reward']))
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
        obs = {
            'candles': self.candles_df.iloc[self.current_step - 60:self.current_step].values,
            'balance': self.balance_df.values,
            'chart': self.chart_df.values
        }
        return obs

    def get_rewards(self, action):
        current_price = self.candles_df.iloc[self.current_step]['LC']
        
        next_60_min = self.candles_df.iloc[self.current_step:self.current_step + 60] if self.current_step + 60 < len(self.candles_df) else self.candles_df.iloc[self.current_step:]
        
        next_15_min = self.candles_df.iloc[self.current_step:self.current_step + 15] if self.current_step + 15 < len(self.candles_df) else self.candles_df.iloc[self.current_step:]

        reward = 0
           
        if action == 0:  # Buy
            max_future_price = next_60_min['LC'].max()
            
            min_future_price = next_15_min['LC'].min()
            
            if self.balance >= current_price and len(self.holdings)==0 and min_future_price > current_price*0.95:
                if max_future_price > current_price * 1.05:
                    reward = 100 + (max_future_price - current_price) * 0.1
                else:
                    reward = -25
                    
            elif len(self.holdings)>1:
                if (sum(self.holdings)/len(self.holdings))> 0.95*current_price and min_future_price > current_price*0.9 :
                    reward += 90 +  (max_future_price - current_price) * 0.1
                else:
                    reward -=25
                  
            else:
                reward = -30

        elif action == 1:  # Sell
            if self.holdings:
                avg_buy_price = sum(self.holdings) / len(self.holdings)
                if current_price > 1.2* avg_buy_price:
                    reward = 100 + (current_price - avg_buy_price) * 0.15
                    
                elif current_price > 1.04* avg_buy_price:
                    reward = 60 + (current_price - avg_buy_price) * 0.34
                else:
                    reward = -30
            else:
                reward = -10

        elif action == 2:  # Hold
            buy_reward = self.get_rewards(0)
            sell_reward = self.get_rewards(1)
            if buy_reward < 0 and sell_reward < 0:
                reward = 60
            else:
                reward = -20
                
                
        if (self.current_step- self.last_trade_step ) > 4 and action in (0, 1):
            reward -= 5
        

        return reward

    def step(self, action):
        current_price = self.candles_df.iloc[self.current_step]['LC']
        reward = self.get_rewards(action)

        if action == 0:  # Buy
            if self.balance >= current_price:
                self.holdings.append(current_price)
                self.balance -= (current_price + 1)
                self.last_trade_step = self.current_step
                self.history.append(('buy', self.current_step, current_price, self.balance, reward))

        elif action == 1:  # Sell
            if self.holdings:
                total_sell_value = len(self.holdings) * (current_price - 1)
                total_buy_cost = sum(self.holdings)
                self.profit = total_sell_value - total_buy_cost
                self.balance += total_sell_value
                self.holdings = []
                self.last_trade_step = self.current_step
                self.history.append(('sell', self.current_step, current_price, self.balance, reward))

                if self.profit > 0:
                    self.no_positive += 1
                elif self.profit < 0:
                    self.negative += 1

        self.current_step += 1
        
        reward += (self.current_step - 60)/10
        #reward += round((self.balance + sum(self.holdings))* 1 / 1500, 3)

        # Termination Conditions
        if self.current_step >= len(self.candles_df):
            self.done = True
            final_profit = self.balance + len(self.holdings) * current_price - 1500
            reward += final_profit * 0.1

        if self.negative >= 5 or self.balance < 0.7 * 1500:
            self.done = True
            #reward -= 100

        if len(self.holdings) > 4 or any(h < current_price * 0.5 for h in self.holdings):
            self.done = True
            #reward -= 100

        if self.current_step - self.last_trade_step > 60:
            self.done = True
            #reward -= 100
            
        if reward > 0 and self.done == True:
            self.done = False
        
        if self.done:
            reward -= 100

        # Update Balance Information
        self.balance_df['current_step'] = self.current_step
        self.balance_df['balance'] = self.balance
        self.balance_df['sum_hold'] = sum(self.holdings)
        self.balance_df['no_hold'] = len(self.holdings)
        self.balance_df['pos'] = self.no_positive
        self.balance_df['neg'] = self.negative
        self.balance_df['last_trade'] = self.last_trade_step

        return self._get_observation(), reward, self.done

