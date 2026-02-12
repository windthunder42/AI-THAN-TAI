from backtest_logic import (
    load_real_data, analyze_history, GAME_CONFIG,
    mode_f_hybrid, mode_d_quantum, mode_e_iching, mode_g_genetic
)
import statistics

def run_simulation(game_type="6/55", days=50):
    print(f"\n🚀 SIMULATION: {game_type} (Last {days} draws)")
    history = load_real_data(game_type)
    if len(history) < days + 50:
        print("Not enough data.")
        return

    # Models to test
    models = {
        "Hybrid": mode_f_hybrid,
        "Quantum": mode_d_quantum,
        "I Ching": mode_e_iching,
        "Genetic": mode_g_genetic
    }
    
    results = {name: {"hits": [], "jackpot": 0, "near_miss": 0} for name in models}
    
    start_idx = len(history) - days
    
    cfg = GAME_CONFIG[game_type]
    is_535 = (cfg["type"] == "special")
    needed = 5 if is_535 else 6
    
    for i in range(start_idx, len(history)):
        target = history[i] # Full draw including special if 5/35
        past_data = history[:i]
        
        # Pre-calc hot/cold for models that need it
        hot, cold = analyze_history(past_data)
        
        # Target Set for comparison
        # 5/35: Compare mainly first 5 numbers for regular prize, 6th for special?
        # Let's target the MAIN PRIZE (Jackpot 1/2) -> Matches in the set of drawn numbers.
        # For 5/35, matching 5 numbers is Jackpot 1.
        # For 6/55, matching 6 numbers is Jackpot 1.
        
        t_set = set(target[:5]) if is_535 else set(target[:6])
        
        seed_val = i * 777 # Deterministic seed
        
        for name, func in models.items():
            try:
                # Call model with appropriate args
                # Inspect signature? Or just try/except
                # Hybrid: game_type, history, hot, cold, seed...
                # Quantum: game_type, seed...
                # I Ching: game_type, seed...
                # Genetic: game_type, history, hot, cold, seed...
                
                prediction = []
                if name == "Hybrid":
                    prediction, _ = func(game_type, past_data, hot, cold, seed=seed_val)
                elif name == "Quantum":
                    prediction, _ = func(game_type, seed=seed_val)
                elif name == "I Ching":
                    prediction, _ = func(game_type, seed=seed_val)
                elif name == "Genetic":
                    prediction, _ = func(game_type, past_data, hot, cold, seed=seed_val)
                else:
                    continue
                    
                # Evaluate
                p_set = set(prediction[:5]) if is_535 else set(prediction[:6])
                matches = len(t_set.intersection(p_set))
                
                results[name]["hits"].append(matches)
                if matches == needed:
                    results[name]["jackpot"] += 1
                elif matches == needed - 1:
                    results[name]["near_miss"] += 1
                    
            except Exception as e:
                # print(f"Error {name}: {e}")
                pass

    # Report for this game type
    print(f"--- Results for {game_type} ---")
    best_model = None
    best_avg = -1
    
    for name, stats in results.items():
        avg = statistics.mean(stats["hits"]) if stats["hits"] else 0
        max_h = max(stats["hits"]) if stats["hits"] else 0
        jp = stats["jackpot"]
        nm = stats["near_miss"]
        
        print(f"  {name:<10} | Avg: {avg:.2f} | Max: {max_h} | JP: {jp} | Near: {nm}")
        
        # Selection Logic
        # Priority: Jackpot > Near Miss > Avg
        # Score = (JP * 100) + (NM * 10) + Avg
        score = (jp * 100) + (nm * 10) + avg
        
        if score > best_avg:
            best_avg = score
            best_model = name
            
    print(f"🏆 BEST MODEL for {game_type}: {best_model}\n")
    return best_model

if __name__ == "__main__":
    b1 = run_simulation("6/55", 50)
    b2 = run_simulation("6/45", 50)
    b3 = run_simulation("5/35", 50)
