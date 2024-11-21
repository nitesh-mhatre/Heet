import torch
import torch.nn as nn
import torch.optim as optim
import random
import numpy as np

class DQN(nn.Module):
    def __init__(self, input_size, action_size):
        super(DQN, self).__init__()
        self.fc1 = nn.Linear(input_size, 1024)
        self.fc2 = nn.Linear(1024, 512)
        self.fc3 = nn.Linear(512, 512)
        self.fc4 = nn.Linear(512, 256)
        self.fc5 = nn.Linear(256, 256)
        self.fc6 = nn.Linear(256, 128)
        self.fc7 = nn.Linear(128, 128)
        self.fc8 = nn.Linear(128, 128)
        self.fc9 = nn.Linear(128, 128)
        self.fc10 = nn.Linear(128, action_size)

    def forward(self, x):
        x = torch.relu(self.fc1(x))
        x = torch.relu(self.fc2(x))
        x = torch.relu(self.fc3(x))
        x = torch.relu(self.fc4(x))
        x = torch.relu(self.fc5(x))
        x = torch.relu(self.fc6(x))
        x = torch.relu(self.fc7(x))
        x = torch.relu(self.fc8(x))
        x = torch.relu(self.fc9(x))
        x = self.fc10(x)
        return x

class TradingAgent:
    def __init__(self, state_size, action_size, lr=0.001):
        self.model = DQN(state_size, action_size)
        self.optimizer = optim.Adam(self.model.parameters(), lr=lr)
        self.criterion = nn.MSELoss()
        self.memory = []  # Replay buffer
        self.gamma = 0.99  # Discount factor
        self.epsilon = 1.0  # Exploration rate
        self.epsilon_decay = 0.995
        self.epsilon_min = 0.01

    def act(self, state):
        if np.random.rand() < self.epsilon:
            return np.random.choice([0, 1, 2])  # Random action
        state = torch.tensor(state, dtype=torch.float32)
        q_values = self.model(state)
        return torch.argmax(q_values).item()

    def remember(self, state, action, reward, next_state, done):
        self.memory.append((state, action, reward, next_state, done))

    def replay(self, batch_size):
        if len(self.memory) < batch_size:
            return
        batch = random.sample(self.memory, batch_size)
        for state, action, reward, next_state, done in batch:
            state = np.array(state, dtype=np.float32)  # Ensure numeric type
            next_state = np.array(next_state, dtype=np.float32)  # Ensure numeric type
            
            # Convert state and next_state into tensors
            state = torch.tensor(state, dtype=torch.float32)
            next_state = torch.tensor(next_state, dtype=torch.float32)

            target = reward
            if not done:
                # Detach next_state tensor for future reward calculation
                next_state_tensor = next_state.clone().detach()  # Detach the tensor to stop gradient tracking
                target += self.gamma * torch.max(self.model(next_state_tensor))

            # Get current Q-values for the state
            q_values = self.model(state)
            target_f = q_values.clone().detach()
            target_f[action] = target  # Set the target for the chosen action

            # Calculate loss and backpropagate
            loss = self.criterion(q_values, target_f)
            self.optimizer.zero_grad()
            loss.backward()
            self.optimizer.step()

    def save_model(self, file_path):
        """Save the model and optimizer state."""
        torch.save({
            'model_state_dict': self.model.state_dict(),
            'optimizer_state_dict': self.optimizer.state_dict(),
            'epsilon': self.epsilon
        }, file_path)
        print(f"Model saved to {file_path}")

    def load_model(self, file_path):
        """Load the model and optimizer state."""
        checkpoint = torch.load(file_path)
        self.model.load_state_dict(checkpoint['model_state_dict'])
        self.optimizer.load_state_dict(checkpoint['optimizer_state_dict'])
        self.epsilon = checkpoint['epsilon']
        print(f"Model loaded from {file_path}")