import random
import numpy as np
import json
import os

class HybridRLAgent:
    """
    Reinforcement Learning (RL) Agent using Q-Learning to optimize the combination
    of different prediction modes (AI, Genetic, Quantum, I Ching, LSTM, Fractal).
    """
    def __init__(self, game_type="6/55", learning_rate=0.1, discount_factor=0.9, epsilon=0.2):
        self.game_type = game_type
        self.lr = learning_rate
        self.gamma = discount_factor
        self.epsilon = epsilon
        
        # Define actions: Which mode to trust heavily today
        self.actions = ["MODE_A_AI", "MODE_G_GENETIC", "MODE_LSTM", "MODE_FRACTAL", "EQUAL_WEIGHTS"]
        self.n_actions = len(self.actions)
        
        # State space is simplified: [Trend_Volatility, Recency_Coverage]
        # Discretized into a small Q-Table
        self.q_table = {}
        self.model_path = f"rl_agent_{game_type.replace('/', '')}.json"
        self.load_q_table()

    def get_state(self, history):
        """
        Calculates the current 'State' of the lottery environment based on the last 10 draws.
        State features (discretized to reduce state space):
        1. Volatility: High if many new numbers appear, Low if same numbers repeat.
        2. Average Sum: Low, Medium, High
        """
        if len(history) < 10:
            return "DEFAULT_STATE"
            
        recent = history[-10:]
        
        # Feature 1: Volatility (Number of unique numbers in last 10 draws)
        # Max is 10 * 6 = 60. 
        unique_nums = len(set(n for draw in recent for n in draw))
        if unique_nums < 30: vol = "LOW_VOL"
        elif unique_nums < 45: vol = "MED_VOL"
        else: vol = "HIGH_VOL"
        
        # Feature 2: Sum Trend (Average sum of last 5 draws vs historical average)
        recent_sums = [sum(draw) for draw in history[-5:]]
        avg_sum = sum(recent_sums) / len(recent_sums)
        
        if "6/55" in self.game_type: benchmark = 168
        elif "6/45" in self.game_type: benchmark = 138
        else: benchmark = 90
        
        if avg_sum < benchmark * 0.9: sum_trend = "LOW_SUM"
        elif avg_sum > benchmark * 1.1: sum_trend = "HIGH_SUM"
        else: sum_trend = "MED_SUM"
        
        state = f"{vol}_{sum_trend}"
        
        if state not in self.q_table:
             self.q_table[state] = [0.0] * self.n_actions
             
        return state

    def choose_action(self, state):
        """
        Epsilon-Greedy policy for Action selection.
        """
        if state not in self.q_table:
             self.q_table[state] = [0.0] * self.n_actions
             
        if random.uniform(0, 1) < self.epsilon:
            # Explore
            action_idx = random.randint(0, self.n_actions - 1)
        else:
            # Exploit
            action_idx = np.argmax(self.q_table[state])
            
        return action_idx, self.actions[action_idx]

    def update_q_table(self, state, action_idx, reward, next_state):
        """
        Q-Learning Update rule:
        Q(s,a) = Q(s,a) + alpha * [Reward + gamma * max(Q(s', a')) - Q(s,a)]
        """
        if next_state not in self.q_table:
             self.q_table[next_state] = [0.0] * self.n_actions
             
        current_q = self.q_table[state][action_idx]
        max_next_q = np.max(self.q_table[next_state])
        
        new_q = current_q + self.lr * (reward + self.gamma * max_next_q - current_q)
        self.q_table[state][action_idx] = new_q
        self.save_q_table()

    def calculate_reward(self, chosen_tickets, actual_draw):
        """
        Calculates ROI (Return on Investment) style reward.
        If a ticket hits 3, 4, 5, or 6 numbers, give exponential reward.
        """
        total_reward = -0.5 # Small penalty for buying tickets
        
        for ticket in chosen_tickets:
            matches = len(set(ticket).intersection(set(actual_draw)))
            if matches == 3: total_reward += 1.0
            elif matches == 4: total_reward += 5.0
            elif matches == 5: total_reward += 50.0
            elif matches == 6: total_reward += 1000.0
            
        return total_reward

    def save_q_table(self):
        try:
            with open(self.model_path, "w") as f:
                json.dump(self.q_table, f)
        except:
            pass
            
    def load_q_table(self):
        if os.path.exists(self.model_path):
            try:
                with open(self.model_path, "r") as f:
                    self.q_table = json.load(f)
            except:
                pass

    def get_mode_weights(self, action_name):
        """
        Translates the RL Action into configuration weights for the Hybrid combinator.
        """
        # Base format: {"AI": w, "Genetic": w, "Quantum": w, "IChing": w, "LSTM": w, "Fractal": w}
        weights = {"AI": 1.0, "Genetic": 1.0, "Quantum": 1.0, "IChing": 1.0, "LSTM": 1.0, "Fractal": 1.0}
        
        if action_name == "MODE_A_AI":
             weights["AI"] = 3.0
        elif action_name == "MODE_G_GENETIC":
             weights["Genetic"] = 3.0
        elif action_name == "MODE_LSTM":
             weights["LSTM"] = 4.0
        elif action_name == "MODE_FRACTAL":
             weights["Fractal"] = 4.0
        # EQUAL_WEIGHTS keeps them all at 1.0
        
        # Normalize weights to sum to 1.0 roughly
        total = sum(weights.values())
        return {k: v/total for k, v in weights.items()}

if __name__ == "__main__":
    agent = HybridRLAgent("6/55")
    # Simulate a state
    dummy_history = [sorted(random.sample(range(1, 46), 6)) for _ in range(500)]
    state = agent.get_state(dummy_history)
    
    action_idx, action_name = agent.choose_action(state)
    weights = agent.get_mode_weights(action_name)
    
    print(f"Current State: {state}")
    print(f"Action Chosen: {action_name}")
    print(f"Configuration Weights: {weights}")
