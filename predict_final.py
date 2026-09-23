import sys
import app
from collections import Counter
import random

game_type = "6/55"
cfg = app.GAME_CONFIG[game_type]
history = app.load_real_data(game_type)
hot_nums, cold_nums = app.analyze_history(history)

predictions = []

# 1. Core Generator (Mode A)
try:
    res1 = app.core_generate_predictions(game_type, history, hot_nums, cold_nums, pool_size=6)
    predictions.append(res1)
except Exception as e:
    print(f"Core Error: {e}")

# 2. Genetic Algorithm
try:
    from algorithm_genetic import GeneticLotteryEngine
    engine = GeneticLotteryEngine(game_type, cfg, history, population_size=50, generations=10)
    res2 = engine.run()
    # Genetic might return a list of lists of lists or just list of lists
    if res2 and isinstance(res2[0], list):
        # Taking the first ticket
        predictions.append(res2[0])
    else:
        predictions.append(res2)
except Exception as e:
    print(f"Genetic Error: {e}")

# 3. Clustering
try:
    from ml_clustering import TicketClustering
    tc = TicketClustering(game_type=game_type, n_clusters=5)
    tc.fit(history)
    cluster_id = tc.predict_next_cluster()
    res3 = tc.generate_ticket_from_cluster(cluster_id)
    if res3:
        predictions.append(res3)
except Exception as e:
    print(f"Clustering Error: {e}")

# 4. Quantum/Graph Theory
try:
    from quantum_jackpot_predictor import Algorithm655
    algo = Algorithm655()
    algo.fit(history)
    res4_pool = algo.predict_jackpot_pool(history, pool_size=6)
    if res4_pool:
        predictions.append(res4_pool)
except Exception as e:
    print(f"Quantum Error: {e}")

# Flatten everything properly
all_nums = []
for p in predictions:
    for item in p:
        if isinstance(item, list):
            for n in item:
                all_nums.append(n)
        else:
            all_nums.append(item)

counter = Counter(all_nums)
top_6 = [n for n, c in counter.most_common(6)]
final_set = sorted(top_6)

print("\n==================================")
print("Kết quả tổng hợp từ tất cả các phương pháp:")
for i, method in enumerate(["Core Generator", "Genetic", "Clustering", "Quantum"], 1):
    if i <= len(predictions):
        print(f"{method}: {predictions[i-1]}")
print(f"\nDãy số 6/55 tối ưu cuối cùng: {final_set}")
print("==================================")
