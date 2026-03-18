import requests
import json
from collections import Counter
import math
import numpy as np
from sklearn.neighbors import NearestNeighbors

class FractalAttractorAnalyzer:
    """
    Applies Chaos Theory and Fractal Geometry concepts.
    Maps historical draws into an N-dimensional phase space and looks for 'Strange Attractors'
    (regions where results tend to 'orbit' or cluster abnormally often).
    """
    def __init__(self, game_type="6/55", dimensions=6):
        self.game_type = game_type
        self.dimensions = dimensions
        
        if "6/55" in game_type:
             self.max_val = 55
        elif "6/45" in game_type:
             self.max_val = 45
        elif "5/35" in game_type:
             self.max_val = 35
             self.dimensions = 5
        else:
             self.max_val = 55
             
        self.phase_space = []
        
    def build_phase_space(self, history):
        """
        Builds the phase space. Each draw is a point in D-dimensional space.
        """
        self.phase_space = []
        for draw in history:
            main_draw = sorted([n for n in draw[:self.dimensions] if 1 <= n <= self.max_val])
            if len(main_draw) == self.dimensions:
                # Normalize for spatial distance calculations
                point = np.array(main_draw) / self.max_val
                self.phase_space.append(point)
                
        self.phase_space = np.array(self.phase_space)
        return len(self.phase_space) > 0

    def find_attractor_centers(self, n_neighbors=15, radius_threshold=0.15):
        """
        Finds dense regions (Attractors) in the phase space.
        Returns a list of 'center of mass' points for these attractors.
        """
        if len(self.phase_space) < n_neighbors:
             return []
             
        # Use Nearest Neighbors to find density
        nbrs = NearestNeighbors(n_neighbors=n_neighbors, algorithm='ball_tree').fit(self.phase_space)
        distances, indices = nbrs.kneighbors(self.phase_space)
        
        # A point is an "Attractor Core" if its N neighbors are very close
        # i.e., average distance to neighbors is low
        avg_distances = np.mean(distances, axis=1)
        
        # Determine strict threshold
        threshold = np.percentile(avg_distances, 5) # Top 5% densest points
        core_indices = np.where(avg_distances <= threshold)[0]
        
        attractors = []
        for idx in core_indices:
            # The attractor center is the mean of this dense cluster
            cluster_points = self.phase_space[indices[idx]]
            center_of_mass = np.mean(cluster_points, axis=0)
            
            # De-normalize back to ticket space
            ticket_center = np.round(center_of_mass * self.max_val).astype(int)
            # Ensure within bounds and unique (approximate)
            ticket_set = set()
            for n in ticket_center:
                val = max(1, min(self.max_val, n))
                # Handle duplicates created by rounding
                while val in ticket_set and val < self.max_val:
                    val += 1
                while val in ticket_set and val > 1:
                    val -= 1
                ticket_set.add(val)
                
            final_ticket = sorted(list(ticket_set))
            if len(final_ticket) == self.dimensions:
                 attractors.append(final_ticket)
                 
        return attractors

    def calculate_fractal_score(self, history):
        """
        For each number 1-max_val, calculate a score based on how often it appears
        in the vicinity of current active attractors.
        """
        scores = {n: 0.1 for n in range(1, self.max_val + 1)}
        
        if not self.build_phase_space(history):
            return scores
            
        # Find general attractors in all history
        attractors = self.find_attractor_centers(n_neighbors=20)
        
        if not attractors:
            return scores
            
        # We give higher weight to numbers that are part of the attractors
        for att_ticket in attractors:
            for num in att_ticket:
                scores[num] += 10.0 # High base score for attractor membership
                
        # Also, check the "Trajectory" - are we moving towards an attractor?
        # (This is advanced Chaos theory: calculating Lyapunov Exponents or simple directional derivatives)
        # For simplicity, if the last few draws are near an attractor, that attractor is "Active"
        
        if len(self.phase_space) >= 5:
             recent_points = self.phase_space[-5:]
             for att_ticket in attractors:
                 att_point = np.array(att_ticket) / self.max_val
                 # Distance from recent trajectory to this attractor
                 dist = np.min([np.linalg.norm(rp - att_point) for rp in recent_points])
                 
                 # If active (very close recently), boost its numbers massively
                 if dist < 0.2:
                     for num in att_ticket:
                         scores[num] += 50.0 / (dist + 0.01)
                         
        return scores

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

def run_backtest(game_type, url):
    history = load_data(url)
    if not history: return

    print(f"\n--- Backtesting Fractal Protocol {game_type} ---")
    analyzer = FractalAttractorAnalyzer(game_type=game_type)
    
    start_idx = 200 # Need enough data to form phase space
    max_matches_18 = 0
    
    for i in range(start_idx, min(start_idx + 100, len(history))): # Test 100 draws for speed
        past_history = history[:i]
        actual_draw = set(history[i])
        
        scores = analyzer.calculate_fractal_score(past_history)
        
        sorted_candidates = sorted(scores.keys(), key=lambda x: scores[x], reverse=True)
        top_18 = sorted_candidates[:18]
        
        matches = len(actual_draw.intersection(set(top_18)))
        if matches > max_matches_18:
            max_matches_18 = matches
            
        if matches >= 5:
            top_6 = sorted_candidates[:6]
            matches_6 = len(actual_draw.intersection(set(top_6)))
            print(f"Draw {i}: Hit {matches} in Top 18 (Top 6 hit: {matches_6})")
            
    print(f"Test Complete. Max matches in Top 18: {max_matches_18}")

if __name__ == "__main__":
    # Test 6/55
    run_backtest("6/55", "https://raw.githubusercontent.com/vietvudanh/vietlott-data/main/data/power655.jsonl")
