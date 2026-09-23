import csv
from quantum_jackpot_predictor import QuantumFractalPredictor
import time

def load_csv_history(filepath):
    history = []
    try:
        with open(filepath, 'r') as f:
            reader = csv.reader(f)
            next(reader) # Skip header
            for row in reader:
                try:
                    # Mega 6/45 format: Date, Draw_ID, Ball_1, Ball_2, Ball_3, Ball_4, Ball_5, Ball_6
                    draw = [int(x) for x in row[2:8]]
                    history.append(sorted(draw))
                except Exception as e:
                    pass
    except Exception as e:
        print(f"Error loading {filepath}: {e}")
    return history

def run_ultimate_backtest():
    print("==================================================")
    print("   QUANTUM-FRACTAL ENSEMBLE BACKTEST (MEGA 6/45)   ")
    print("==================================================")
    
    filepath = 'history_6_45.csv'
    history = load_csv_history(filepath)
    print(f"Total draws loaded: {len(history)}")
    
    if len(history) < 200:
        print("Not enough history for deep backtesting.")
        return
        
    # We test the entire history or a large portion
    test_draws = len(history) - 200 # Skip first 200 for initial training
    start_idx = 200
    
    predictor = QuantumFractalPredictor(balls=6, max_val=45)
    
    pool_size = 18
    hits_distribution = {i:0 for i in range(7)}
    jackpots_found = 0
    total_score = 0
    
    start_time = time.time()
    for i in range(start_idx, len(history)):
        past_history = history[:i]
        actual_draw = history[i]
        
        predictor.fit(past_history)
        
        # Predict the super pool
        predicted_pool = predictor.predict_jackpot_pool(past_history, pool_size=pool_size)
        
        # Check hits
        hits = len(set(predicted_pool).intersection(set(actual_draw)))
        hits_distribution[hits] += 1
        total_score += hits
        
        if hits == 6:
            jackpots_found += 1
            print(f"*** JACKPOT CAUGHT! Draw {i} ***")
            print(f"  Pool: {predicted_pool}")
            print(f"  Actual: {actual_draw}")
        elif hits >= 5:
            print(f"Draw {i}: Hits {hits}/6 in {pool_size}-number pool.")

    end_time = time.time()
    
    print("==================================================")
    print("                 BACKTEST RESULTS                  ")
    print("==================================================")
    print(f"Total Draws Tested : {test_draws}")
    print(f"Time Taken         : {end_time - start_time:.2f} seconds")
    print(f"Average Hits       : {total_score / test_draws:.4f} balls/draw")
    print(f"Total JACKPOTS CAUGHT (6/6) in {pool_size}-ball pool: {jackpots_found}")
    print("\nHit Distribution:")
    for h, count in hits_distribution.items():
        print(f"  {h} Hits : {count} times")
    print("==================================================")

if __name__ == '__main__':
    run_ultimate_backtest()
