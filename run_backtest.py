from backtest_logic import (
    load_real_data, analyze_history, mode_f_hybrid, GAME_CONFIG, 
    calculate_weighted_frequency
)
from datetime import datetime
import json

def run_backtest(game_type="6/55", test_count=30, tickets_per_draw=10):
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
        
        # Predict multiple tickets per draw
        try:
            from backtest_logic import mode_system_play
            import random
            
            best_matches = -1
            best_p_set = set()
            t_set = set(target[:5]) if is_535 else set(target[:6])
            actual_balls = 5 if is_535 else 6
            
            pool = mode_system_play(
                game_type, past_data, hot, cold,
                system_size=12, seed=i*9999, style="Modern"
            )
            
            rng = random.Random(i*9999)
            tickets = []
            if len(pool) >= actual_balls:
                for _ in range(tickets_per_draw):
                    tickets.append(set(rng.sample(pool, actual_balls)))
            else:
                tickets.append(set(pool))
                
            for p_set in tickets:
                matches = len(t_set.intersection(p_set))
                if matches > best_matches:
                    best_matches = matches
                    best_p_set = p_set
                
            hits_distribution[best_matches] = hits_distribution.get(best_matches, 0) + 1
            total_draws += 1
            total_hits += best_matches
            
            if best_matches >= 3:
                print(f"Draw {i}: HIT {best_matches} numbers! Target: {sorted(list(t_set))} | Best Pred: {sorted(list(best_p_set))}")
            
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
    run_backtest("6/55", 500, tickets_per_draw=10)
    run_backtest("5/35", 500, tickets_per_draw=10)
