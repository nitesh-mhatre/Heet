import numpy as np
import pandas as pd
from environment import TradingEnvironment
from agent import TradingAgent
import os

from game import get_game

def train(env, agent, episodes, batch_size, save_path="trading_model.pth", save_every=10):
    for episode in range(episodes):
        state = env.reset()
        
        # Flatten candles and chart to 1D, balance is already 1D
        state = np.concatenate([
            state['candles'].flatten().astype(np.float32), 
            state['balance'].flatten().astype(np.float32), 
            state['chart'].flatten().astype(np.float32)
        ])
        
        total_reward = 0
        
        while not env.done:
            action = agent.act(state)
            next_state, reward, done = env.step(action)
            
            # Flatten the next state similarly
            next_state = np.concatenate([
                next_state['candles'].flatten().astype(np.float32), 
                next_state['balance'].flatten().astype(np.float32), 
                next_state['chart'].flatten().astype(np.float32)
            ])
            
            agent.remember(state, action, reward, next_state, done)
            state = next_state
            total_reward += reward
            
            if done:
                print(f"Episode: {episode + 1}, Reward: {total_reward}")
                break
        
        agent.replay(batch_size)
        agent.epsilon = max(agent.epsilon_min, agent.epsilon * agent.epsilon_decay)

        # Save the model every `save_every` episodes
        if (episode + 1) % save_every == 0:
            agent.save_model(save_path)

if __name__ == "__main__":
    # Replace these with real data frames
    no_of_games = 1
    while True:
      os.system('clear')
      print(no_of_games, ' No of Games' )
      
      try:
        candles_df, balance_df, chart_df , opt = get_game()
        env = TradingEnvironment(candles_df, balance_df, chart_df)
        state_size = 60 * 10 + 9 + 50 * 5  # Flattened sizes of candles, balance, and chart
        action_size = 3  # Buy, Sell, Hold
    
        agent = TradingAgent(state_size, action_size)
    
        # Load an existing model if it exists
        
    
        # Train the model
        
        if opt == 'CE':
          model_path = "ce_model.pth"
        else:
          model_path = "pe_model.pth"
        
        if os.path.exists(model_path):
            agent.load_model(model_path)
          
        train(env, agent, episodes=30, batch_size=32, save_path=model_path)
        
        no_of_games += 1
      except Exception as e:
        print(e)
        break
    