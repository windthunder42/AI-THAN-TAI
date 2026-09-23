import sys
import os
import json
from collections import Counter

# Add path if needed
sys.path.append('.')

import app
from algorithm_genetic import GeneticLotteryEngine
from ml_clustering import TicketClustering
from advanced_combinatorics import AdvancedCombinatorics
from rl_hybrid_agent import HybridRLAgent
from backtest_sequence import DeepSequencePredictor
from backtest_fractal import FractalAttractorAnalyzer

game_type = "6/45"
history = app.load_real_data(game_type)
hot_nums, cold_nums = app.analyze_history(history)

predictions = []

# Method 1: Core App Gen
res1 = app.core_generate_predictions(game_type, history, hot_nums, cold_nums, pool_size=6)
predictions.append(res1)
print(f"Core App: {res1}")

# Method 2: Genetic
try:
    engine_ga = GeneticLotteryEngine(game_type)
    res2 = engine_ga.run_evolution(history, pop_size=50, generations=20)
    # res2 is likely a list of lists or one list
    if isinstance(res2[0], list):
        res2_flat = res2[0]
    else:
        res2_flat = res2
    predictions.append(res2_flat)
    print(f"Genetic: {res2_flat}")
except Exception as e:
    print(f"Genetic Error: {e}")

# Method 3: ML Clustering
try:
    tc = TicketClustering(game_type)
    res3 = tc.cluster_and_predict(history, n_clusters=3, tickets_per_cluster=1)
    if res3:
        predictions.append(res3[0])
        print(f"Clustering: {res3[0]}")
except Exception as e:
    print(f"Clustering Error: {e}")

# Method 4: RL Agent
try:
    rl = HybridRLAgent(game_type)
    rl.train(history[-100:], episodes=50)
    res4 = rl.predict(history[-100:])
    predictions.append(res4)
    print(f"RL Agent: {res4}")
except Exception as e:
    print(f"RL Error: {e}")

# Compile results
all_nums = []
for p in predictions:
    all_nums.extend(p)

counter = Counter(all_nums)
top_6 = [n for n, c in counter.most_common(6)]
print("----------------")
print(f"Final Ensemble (Most Common): {sorted(top_6)}")

