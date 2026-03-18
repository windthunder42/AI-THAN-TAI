import requests
import json
from collections import Counter
import random

def load_data_3d_pro():
    url = "https://raw.githubusercontent.com/vietvudanh/vietlott-data/main/data/3d_pro.jsonl"
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
                    res = data.get("result", {})
                    # Get Special Prize (2 numbers)
                    special = res.get("Giải Đặc biệt", [])
                    if len(special) >= 2:
                        # Append as a list of strings ["123", "456"]
                        history.append(special[:2]) 
                except:
                    continue
        return history
    except Exception as e:
        print(f"Error: {e}")
        return []

def calculate_whole_number_fractal(history):
    """
    Fractal Analysis on WHOLE numbers (000-999).
    """
    scores = Counter()
    if not history: return scores
    
    # Flatten window for analysis
    # Window input: [ ["123", "456"], ... ]
    
    windows = {
        "Micro": history[-8:],     # Last 8 draws (16 numbers)
        "Meso": history[-30:],     # Last 30 draws (60 numbers)
        "Macro": history[-100:]    # Last 100 draws (200 numbers)
    }
    
    weights = { "Micro": 4.0, "Meso": 2.5, "Macro": 1.0 }
    
    for scale, window in windows.items():
        if not window: continue
        
        freq = Counter()
        count = 0
        for pair in window:
            for num_str in pair:
                freq[num_str] += 1
                count += 1
                
        # Normalize
        for num_str, c in freq.items():
            prob = c / count
            scores[num_str] += prob * weights[scale]
            
    return scores

def generate_candidates(scores, count=20):
    """
    Pick Top N numbers based on Fractal Score.
    """
    # Sort by score desc
    sorted_items = scores.most_common(count)
    return [item[0] for item in sorted_items]

def run_backtest():
    history = load_data_3d_pro()
    if not history: return

    print(f"\n--- Backtesting Max 3D Pro (Fractal Chaos) ---")
    print(f"Total draws: {len(history)}")
    
    start_idx = 100
    
    hits_1 = 0
    hits_2 = 0 # Both in same draw
    total_draws = 0
    
    print(f"Simulating from draw {start_idx} to {len(history)-1}...")
    
    for i in range(start_idx, len(history)):
        past_history = history[:i]
        actual_pair = set(history[i])
        
        # Calculate Scores
        scores = calculate_whole_number_fractal(past_history)
        
        # Generate Top 20 Candidates
        candidates = generate_candidates(scores, count=20)
        
        cand_set = set(candidates)
        
        matches = len(actual_pair.intersection(cand_set))
        
        if matches == 1:
            hits_1 += 1
        elif matches == 2:
            hits_2 += 1
            print(f"*** JACKPOT DOUBLE HIT at Draw {i}: Found {actual_pair} in Top 20! ***")
            
        total_draws += 1

    print("-" * 30)
    print(f"Backtest Results (Top 20 Candidates) over {total_draws} draws:")
    print(f"1 Number Match (Partial): {hits_1} ({(hits_1/total_draws)*100:.2f}%)")
    print(f"2 Numbers Match (Jackpot/Perfect): {hits_2} ({(hits_2/total_draws)*100:.2f}%)")
    print(f"Any Match (At least 1): {hits_1 + hits_2} ({((hits_1 + hits_2)/total_draws)*100:.2f}%)")

if __name__ == "__main__":
    # Fix seed for reproducibility in backtest
    random.seed(42) 
    run_backtest()
