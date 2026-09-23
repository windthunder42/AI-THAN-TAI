import numpy as np
import random
from collections import Counter
import math
from sklearn.neighbors import NearestNeighbors
import networkx as nx

# ==============================================================================
# ALGORITHM FOR 6/55 (POWER 6/55): DEEP FRACTAL ATTRACTORS
# Logic: Massive state space (29M). We rely on Topological Density.
# ==============================================================================
class Algorithm655:
    def __init__(self):
        self.balls = 6
        self.max_val = 55
        self.phase_space = []
        self.markov_transitions = {}
        self.frequencies = Counter()

    def fit(self, history):
        self._build_phase_space(history)
        self._build_markov(history)
        for idx, draw in enumerate(reversed(history)):
            weight = 0.98 ** idx
            for n in draw[:6]:
                if 1 <= n <= self.max_val:
                    self.frequencies[n] += weight

    def _build_phase_space(self, history):
        self.phase_space = []
        for draw in history:
            main_draw = sorted([n for n in draw[:self.balls] if 1 <= n <= self.max_val])
            if len(main_draw) == self.balls:
                self.phase_space.append(np.array(main_draw) / self.max_val)
        self.phase_space = np.array(self.phase_space)

    def _build_markov(self, history):
        self.markov_transitions = {}
        for i in range(len(history) - 1):
            curr = history[i][:6]
            nxt = history[i+1][:6]
            for num in curr:
                if num not in self.markov_transitions:
                    self.markov_transitions[num] = Counter()
                for next_num in nxt:
                    self.markov_transitions[num][next_num] += 1

    def predict_jackpot_pool(self, history, pool_size=18):
        if not history:
            return sorted(random.sample(range(1, 56), pool_size))
            
        last_draw = history[-1][:6]
        
        scores = {n: 0.1 for n in range(1, 56)}
        if len(self.phase_space) >= 20:
            nbrs = NearestNeighbors(n_neighbors=10, algorithm='ball_tree').fit(self.phase_space)
            distances, indices = nbrs.kneighbors(self.phase_space)
            threshold = np.percentile(np.mean(distances, axis=1), 10)
            core_indices = np.where(np.mean(distances, axis=1) <= threshold)[0]
            
            attractors = []
            for idx in core_indices:
                center = np.round(np.mean(self.phase_space[indices[idx]], axis=0) * 55).astype(int)
                attractors.append(center)
                
            recent = self.phase_space[-3:] if len(self.phase_space) >= 3 else self.phase_space
            for att in attractors:
                dist = np.min([np.linalg.norm(r - (att/55)) for r in recent])
                for num in att:
                    if 1 <= num <= 55:
                        scores[num] += 15.0 / (dist + 0.01)
                        
        max_f = max(self.frequencies.values()) if self.frequencies else 1
        for num in last_draw:
            if num in self.markov_transitions:
                total_t = sum(self.markov_transitions[num].values())
                for nxt, count in self.markov_transitions[num].items():
                    if 1 <= nxt <= 55:
                        scores[nxt] += (count / total_t) * 40
                        
        total_scores = {}
        for n in range(1, 56):
            total_scores[n] = (self.frequencies.get(n, 0)/max_f)*30 + scores.get(n, 0)*0.7
            
        pool = []
        evens = 0
        sorted_cands = sorted(total_scores.keys(), key=lambda k: total_scores[k], reverse=True)
        for num in sorted_cands:
            if len(pool) >= pool_size: break
            if num % 2 == 0 and evens >= pool_size * 0.6: continue
            pool.append(num)
            if num % 2 == 0: evens += 1
            
        if len(pool) < pool_size:
            rem = [x for x in sorted_cands if x not in pool]
            pool.extend(rem[:pool_size - len(pool)])
            
        return sorted(pool)

# ==============================================================================
# ALGORITHM FOR 6/45 (MEGA 6/45): K-MEANS MARKOV HYBRID
# Logic: Medium space (8M). Relies heavily on Markov Chains and tighter spacing.
# ==============================================================================
class Algorithm645:
    def __init__(self):
        self.balls = 6
        self.max_val = 45
        self.markov_transitions = {}
        self.frequencies = Counter()

    def fit(self, history):
        self.markov_transitions = {}
        self.frequencies = Counter()
        for i in range(len(history) - 1):
            curr = history[i][:6]
            nxt = history[i+1][:6]
            for num in curr:
                if num not in self.markov_transitions:
                    self.markov_transitions[num] = Counter()
                for next_num in nxt:
                    self.markov_transitions[num][next_num] += 1
                    
        for idx, draw in enumerate(reversed(history)):
            weight = 0.95 ** idx # Faster decay for 6/45
            for n in draw[:6]:
                if 1 <= n <= self.max_val:
                    self.frequencies[n] += weight

    def predict_jackpot_pool(self, history, pool_size=15):
        if not history:
            return sorted(random.sample(range(1, 46), pool_size))
            
        last_draw = history[-1][:6]
        
        scores = {n: 0.1 for n in range(1, 46)}
        
        max_f = max(self.frequencies.values()) if self.frequencies else 1
        for num in last_draw:
            if num in self.markov_transitions:
                total_t = sum(self.markov_transitions[num].values())
                for nxt, count in self.markov_transitions[num].items():
                    if 1 <= nxt <= 45:
                        scores[nxt] += (count / total_t) * 60 # Higher Markv influence
                        
        # Entropy balancing logic tailored for 6/45 spacing (~7 spaces)
        total_scores = {}
        for n in range(1, 46):
            total_scores[n] = (self.frequencies.get(n, 0)/max_f)*40 + scores.get(n, 0)
            
        sorted_cands = sorted(total_scores.keys(), key=lambda k: total_scores[k], reverse=True)
        
        pool = []
        for num in sorted_cands:
            if len(pool) >= pool_size: break
            pool.append(num)
            
        return sorted(pool)

# ==============================================================================
# ALGORITHM FOR 5/35 (MAX 3D PRO): GRAPH-THEORETIC SYNERGY
# Logic: Small space (324k). Numbers act like social networks (edges).
# ==============================================================================
class Algorithm535:
    def __init__(self):
        self.balls = 5
        self.max_val = 35
        self.graph = nx.Graph()
        self.node_weights = Counter()
        
    def fit(self, history):
        self.graph.clear()
        self.node_weights.clear()
        for n in range(1, 36):
            self.graph.add_node(n)
            
        decay = 0.99
        for idx, draw in enumerate(reversed(history)):
            weight = decay ** idx
            main_balls = [n for n in draw[:5] if 1 <= n <= 35]
            for n in main_balls:
                self.node_weights[n] += weight
                
            for i in range(len(main_balls)):
                for j in range(i+1, len(main_balls)):
                    u, v = main_balls[i], main_balls[j]
                    if self.graph.has_edge(u, v):
                        self.graph[u][v]['weight'] += weight
                    else:
                        self.graph.add_edge(u, v, weight=weight)

    def predict_jackpot_pool(self, history, pool_size=12):
        if not history:
            return sorted(random.sample(range(1, 36), pool_size))
            
        last_draw = history[-1][:5]
        scores = {n: 0.1 for n in range(1, 36)}
        
        try:
            pr = nx.pagerank(self.graph, weight='weight')
        except:
            pr = {n: 0.01 for n in range(1, 36)}
            
        activation_energy = {n: 0.0 for n in range(1, 36)}
        for n in last_draw:
            if n in self.graph:
                for neighbor in self.graph.neighbors(n):
                    activation_energy[neighbor] += self.graph[n][neighbor]['weight']
                    
        max_w = max(self.node_weights.values()) if self.node_weights else 1
        
        for n in range(1, 36):
            base_freq = (self.node_weights.get(n, 0) / max_w) * 20
            page_rank = pr.get(n, 0) * 1000
            pulse = activation_energy.get(n, 0) * 10
            scores[n] = base_freq + page_rank + pulse
            
        sorted_cands = sorted(scores.keys(), key=lambda k: scores[k], reverse=True)
        
        pool = []
        odds = 0
        for num in sorted_cands:
            if len(pool) >= pool_size: break
            if num % 2 != 0 and odds >= pool_size * 0.7: continue
            pool.append(num)
            if num % 2 != 0: odds += 1
            
        if len(pool) < pool_size:
            rem = [x for x in sorted_cands if x not in pool]
            pool.extend(rem[:pool_size - len(pool)])
            
        return sorted(pool)
