import requests
import json
from collections import Counter
import math

# Re-implement core logic here for standalone testing
def calculate_fractal_score_535(history, range_limit=35):
    """
    Calculates Fractal Resonance Score for Main Numbers (1-35).
    Scales: Micro (8), Meso (35), Macro (100).
    """
    scores = Counter()
    if not history: return scores
    
    windows = {
        "Micro": history[-8:],
        "Meso": history[-35:],
        "Macro": history[-100:]
    }
    
    weights = {
        "Micro": 4.0,
        "Meso": 2.5,
        "Macro": 1.0
    }
    
    for scale, window in windows.items():
        if not window: continue
        freq = Counter()
        for draw in window:
            # draw is [n1, n2, n3, n4, n5, special]
            # We ONLY analyze the first 5 for the main pool
            main_nums = draw[:5]
            for n in main_nums:
                freq[n] += 1
                
        for n in range(1, range_limit + 1):
            prob = freq[n] / len(window)
            scores[n] += prob * weights[scale]
            
    return scores

def analyze_special_535(history):
    """
    Balanced Frequency: Last 30 draws.
    Simple but effective for small range (1-12).
    """
    if not history: return 1
    
    specials = [d[5] for d in history if len(d) >= 6]
    if not specials: return 1
    
    # Last 30
    window = specials[-30:]
    c = Counter(window)
    
    # Get Top 3
    top = c.most_common(3)
    if not top: return specials[-1]
    
    # Pick the best one that WAS NOT the very last result (avoid immediate repeat)
    last_val = specials[-1]
    
    for val, count in top:
        if val != last_val:
            return val
            
    return top[0][0]

def load_data_535():
    url = "https://raw.githubusercontent.com/vietvudanh/vietlott-data/main/data/power535.jsonl"
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
                    # 5/35 format: [n1, n2, n3, n4, n5, special]
                    if len(raw_result) >= 6:
                        main_part = sorted(raw_result[:5])
                        special_part = raw_result[5]
                        history.append(main_part + [special_part])
                except:
                    continue
        return history
    except Exception as e:
        print(f"Error: {e}")
        return []

def run_backtest():
    history = load_data_535()
    if not history: return

    print(f"\n--- Backtesting 5/35 (Fractal Chaos) ---")
    print(f"Total draws: {len(history)}")
    
    start_idx = 100
    
    results_main = {3: 0, 4: 0, 5: 0} # Max 5 main numbers
    special_hit_count = 0
    jackpot_1_hits = 0 # 5 Main + 1 Special
    jackpot_2_hits = 0 # 5 Main only
    
    print(f"Simulating from draw {start_idx} to {len(history)-1}...")
    
    for i in range(start_idx, len(history)):
        past_history = history[:i]
        actual_draw = history[i] # [n1...n5, special]
        
        actual_main = set(actual_draw[:5])
        actual_special = actual_draw[5]
        
        # 1. Predict Main Numbers
        scores = calculate_fractal_score_535(past_history)
        sorted_candidates = sorted(scores.keys(), key=lambda x: scores[x], reverse=True)
        
        # We pick Top 12 (System 12) to see coverage
        top_candidates = sorted_candidates[:12]
        
        # 2. Predict Special Number
        pred_special = analyze_special_535(past_history)
        
        # Check Main Matches
        matches_main = len(actual_main.intersection(set(top_candidates)))
        
        # Check Special Match
        match_special = (pred_special == actual_special)
        
        if matches_main >= 3:
            results_main[matches_main] = results_main.get(matches_main, 0) + 1
            
        if matches_main == 5:
            jackpot_2_hits += 1
            if match_special:
                jackpot_1_hits += 1
                print(f"*** JACKPOT 1 HIT (5+1) AT DRAW {i} ***")
            else:
                print(f"Draw {i}: Jackpot 2 Hit (5/5 Main) in Top 8!")
                
        if match_special:
            special_hit_count += 1

    print("-" * 30)
    print(f"Backtest Results (Top 8 Candidates) over {len(history)-start_idx} draws:")
    print(f"3 Main Matches: {results_main.get(3,0)}")
    print(f"4 Main Matches: {results_main.get(4,0)}")
    print(f"5 Main Matches (Jackpot 2 Potential): {results_main.get(5,0)}")
    print("-" * 30)
    print(f"Special Number Hits (1/12): {special_hit_count}")
    print(f"Jackpot 1 Hits (5 Main + Special): {jackpot_1_hits}")
    print(f"Accuracy for Special: {(special_hit_count / (len(history)-start_idx)) * 100:.2f}%")

if __name__ == "__main__":
    run_backtest()
