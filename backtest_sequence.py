import numpy as np
import requests
import json
import os
from collections import Counter
from tensorflow.keras.models import Sequential, load_model
from tensorflow.keras.layers import LSTM, Dense, Dropout
from tensorflow.keras.utils import to_categorical

# Config
SEQ_LENGTH = 10 # Number of past draws to look at
EPOCHS = 20
BATCH_SIZE = 32

class DeepSequencePredictor:
    def __init__(self, game_type="6/55"):
        self.game_type = game_type
        if "6/55" in game_type:
             self.balls = 6
             self.max_val = 55
        elif "6/45" in game_type:
             self.balls = 6
             self.max_val = 45
        elif "5/35" in game_type:
             self.balls = 5
             self.max_val = 35
        else:
             self.balls = 6
             self.max_val = 55
             
        self.model = None
        self.model_path = f"lstm_model_{game_type.replace('/', '')}.h5"

    def preprocess_data(self, history):
        """
        Converts list of draws into sequential data suitable for LSTM.
        Input X: Sequence of last 'SEQ_LENGTH' draws.
        Output Y: The next draw (encoded as multi-hot vector).
        """
        print(f"Preprocessing {len(history)} draws for deep learning...")
        X, Y = [], []
        
        for i in range(len(history) - SEQ_LENGTH):
            # Input sequence (List of multi-hot vectors)
            seq = history[i : i + SEQ_LENGTH]
            x_seq = []
            for draw in seq:
                 # Ensure we only process main balls
                 main_draw = [n for n in draw[:self.balls] if 1 <= n <= self.max_val]
                 multi_hot = np.zeros(self.max_val)
                 for num in main_draw:
                     multi_hot[num - 1] = 1 # 0-indexed
                 x_seq.append(multi_hot)
            X.append(x_seq)
            
            # Target (Next draw multi-hot)
            target_draw = [n for n in history[i + SEQ_LENGTH][:self.balls] if 1 <= n <= self.max_val]
            y_multi_hot = np.zeros(self.max_val)
            for num in target_draw:
                y_multi_hot[num - 1] = 1
            Y.append(y_multi_hot)
            
        return np.array(X), np.array(Y)

    def build_model(self):
        """Builds the LSTM network architecture."""
        model = Sequential()
        model.add(LSTM(128, return_sequences=True, input_shape=(SEQ_LENGTH, self.max_val)))
        model.add(Dropout(0.2))
        model.add(LSTM(64))
        model.add(Dropout(0.2))
        model.add(Dense(self.max_val, activation='sigmoid')) # Sigmoid for multi-label classification
        
        model.compile(optimizer='adam', loss='binary_crossentropy', metrics=['accuracy'])
        self.model = model

    def train(self, history, force_retrain=False):
        """Trains the LSTM model on history data."""
        if not force_retrain and os.path.exists(self.model_path):
             print("Loading existing LSTM model...")
             self.model = load_model(self.model_path)
             return True
             
        if len(history) < SEQ_LENGTH * 2:
             print("Not enough data to train LSTM.")
             return False
             
        X, Y = self.preprocess_data(history)
        
        if len(X) == 0:
             return False
             
        print("Training LSTM model...")
        self.build_model()
        
        # Train
        self.model.fit(X, Y, epochs=EPOCHS, batch_size=BATCH_SIZE, verbose=1, validation_split=0.1)
        
        # Save
        self.model.save(self.model_path)
        print(f"Model saved to {self.model_path}")
        return True

    def predict_next_marginal_probabilities(self, history):
        """
        Predicts the probability of each number appearing in the next draw.
        Returns: Dict of {number: predicted_probability}
        """
        if self.model is None:
             if os.path.exists(self.model_path):
                  self.model = load_model(self.model_path)
             else:
                  return {n: 0.1 for n in range(1, self.max_val + 1)}
                  
        if len(history) < SEQ_LENGTH:
             return {n: 0.1 for n in range(1, self.max_val + 1)}
             
        recent_seq = history[-SEQ_LENGTH:]
        x_seq = []
        for draw in recent_seq:
             main_draw = [n for n in draw[:self.balls] if 1 <= n <= self.max_val]
             multi_hot = np.zeros(self.max_val)
             for num in main_draw:
                 multi_hot[num - 1] = 1
             x_seq.append(multi_hot)
             
        input_data = np.array([x_seq]) # Shape: (1, SEQ_LENGTH, max_val)
        
        predictions = self.model.predict(input_data)[0] # Shape: (max_val,)
        
        prob_dict = {}
        for i, prob in enumerate(predictions):
             prob_dict[i + 1] = float(prob)
             
        return prob_dict

# Load data function reused for testing
def load_data(url):
    print(f"Loading data from {url}...")
    try:
        r = requests.get(url, timeout=10)
        history = []
        if r.status_code == 200:
            lines = r.text.strip().split('\n')
            for line in lines:
                if not line.strip(): continue
                try:
                    data = json.loads(line)
                    raw_result = data.get("result", [])
                    if len(raw_result) >= 6:
                        history.append(sorted(raw_result[:6]))
                except:
                    continue
        return history
    except Exception as e:
        print(f"Error: {e}")
        return []

if __name__ == "__main__":
    print("Testing Deep Sequence Model...")
    url = "https://raw.githubusercontent.com/vietvudanh/vietlott-data/main/data/power655.jsonl"
    history = load_data(url)
    
    if history:
        predictor = DeepSequencePredictor(game_type="6/55")
        # For testing, just take the last 500 draws to speed up training
        train_data = history[-500:] 
        
        predictor.train(train_data, force_retrain=True)
        
        probs = predictor.predict_next_marginal_probabilities(train_data)
        
        # Sort and show top 10 highest probability numbers
        sorted_probs = sorted(probs.items(), key=lambda x: x[1], reverse=True)
        print("Top 10 predicted numbers for next draw:")
        for num, p in sorted_probs[:10]:
             print(f"Number {num:02d}: {p:.4f}")
