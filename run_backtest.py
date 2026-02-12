from backtest_logic import (
    load_real_data, analyze_history, mode_f_hybrid, GAME_CONFIG, 
    calculate_weighted_frequency
)
from datetime import datetime
import json

def run_backtest(game_type="6/55", test_count=30):
    print(f"\n--- Backtesting {game_type} (Last {test_count} draws) ---\n")
    
    # 1. Load full history
    # We call load_real_data but need to bypass cache? 
    # backtest_logic has a mock cache decorator -> returns func.
    full_history = load_real_data(game_type)
    
    if len(full_history) < test_count + 50:
        print("Not enough data to backtest.")
        return

    # 2. Iterate
    start_idx = len(full_history) - test_count
    total_hits = 0
    total_draws = 0
    hits_distribution = {0:0, 1:0, 2:0, 3:0, 4:0, 5:0, 6:0, 7:0}
    
    # Config
    cfg = GAME_CONFIG[game_type]
    is_535 = (cfg["type"] == "special")
    
    # We simulate the prediction for each past draw
    # Prediction: Hybrid Mode
    
    for i in range(start_idx, len(full_history)):
        target = full_history[i]
        past_data = full_history[:i] # Knowledge cutoff
        
        # Recalc hot/cold
        # Note: analyze_history relies on `st.session_state`? 
        # Check backtest_logic.py: analyze_history only uses numpy/collections. Safe.
        hot, cold = analyze_history(past_data)
        
        # Predict
        # Use a deterministic seed based on index to be reproducible but 'random' for that day
        # In real app we used next_draw_time timestamp. Here we use i * 9999
        seed_val = i * 9999
        
        # Mocking bio/dob
        # Mode F Hybrid requires quantum_dob/iching_dob
        # We'll pass None or defaults
        try:
            pred_res, details = mode_f_hybrid(
                game_type, past_data, hot, cold,
                seed=seed_val,
                bio_score=0.5, # Neutral/High
                style="Modern"
            )
            
            # Compare
            # Standardize for comparison
            # 6/55: target is [n1, n2, n3, n4, n5, n6, (bonus?)]
            # pred is [n1...n6]
            
            # If 6/55 data has 7 items, take first 6
            t_set = set(target[:6])
            p_set = set(pred_res[:6])
            
            if is_535:
                # 5/35: target is [m1..m5, special]
                # pred is [m1..m5, special]
                # Let's count MATCHING MAIN NUMBERS separately from SPECIAL?
                # Usually backtest counts "How many numbers did I catch?"
                # Simple intersection of main numbers
                t_set = set(target[:5])
                p_set = set(pred_res[:5])
                
            matches = len(t_set.intersection(p_set))
            hits_distribution[matches] = hits_distribution.get(matches, 0) + 1
            total_draws += 1
            total_hits += matches
            
            # Print significant hits
            if matches >= 3:
                print(f"Draw {i}: HIT {matches} numbers! Target: {sorted(list(t_set))} | Pred: {sorted(list(p_set))}")
            
        except Exception as e:
            print(f"Error at draw {i}: {e}")
            
    # Report
    print("\n--- RESULTS ---")
    print(f"Total Drws: {total_draws}")
    print(f"Avg Match : {total_hits / total_draws:.2f}")
    print("\nDistribution:")
    for k in sorted(hits_distribution.keys()):
        count = hits_distribution[k]
        pct = (count / total_draws) * 100
        bar = "█" * int(count)
        print(f"  {k} matches: {count} ({pct:.1f}%) {bar}")

if __name__ == "__main__":
    run_backtest("6/55", 50)
    run_backtest("5/35", 50)
