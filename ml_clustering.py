import numpy as np
from sklearn.cluster import KMeans
from collections import Counter
import json
import os
import random

class TicketClustering:
    """
    Applies Machine Learning (K-Means) to historical lottery draws
    to find 'Giao thức giải' (Ticket Protocols/Clusters).
    """
    def __init__(self, game_type="6/55", n_clusters=20):
        self.game_type = game_type
        self.n_clusters = n_clusters
        self.kmeans = None
        self.cluster_centers = None
        self.history = []
        
        # Configuration based on game type
        if "6/55" in game_type:
            self.balls = 6
            self.max_val = 55
        elif "6/45" in game_type:
            self.balls = 6
            self.max_val = 45
        elif "5/35" in game_type:
            self.balls = 5  # We only cluster the main 5 balls for simplicity
            self.max_val = 35
        else:
            self.balls = 6
            self.max_val = 55

    def extract_features(self, draw):
        """
        Converts a raw draw (e.g., [5, 12, 23, 34, 45, 50]) into a feature vector.
        Features:
        0: Sum of numbers
        1: Number of evens
        2: Number of odds
        3: Number of primes
        4: Range (Max - Min)
        5: Average distance between adjacent numbers
        6-11: The normalized numbers themselves (0-1 range)
        """
        # Ensure we only take the main balls (ignore special ball if present in raw draw)
        main_draw = sorted(draw[:self.balls])
        
        # Basic stats
        s = sum(main_draw)
        evens = sum(1 for n in main_draw if n % 2 == 0)
        odds = len(main_draw) - evens
        
        primes = {2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53}
        prime_count = sum(1 for n in main_draw if n in primes)
        
        spread = main_draw[-1] - main_draw[0] if len(main_draw) > 1 else 0
        
        diffs = [main_draw[i+1] - main_draw[i] for i in range(len(main_draw)-1)]
        avg_diff = sum(diffs) / len(diffs) if diffs else 0
        
        # Normalized numbers
        norm_nums = [n / self.max_val for n in main_draw]
        
        # Combine features
        # Weighting: We give more weight to the structural properties (sum, even/odd, spread) 
        # than the exact numbers to find general "patterns" rather than near-identical tickets.
        features = [
            s / (self.balls * self.max_val),  # Normalized sum
            evens / self.balls,
            odds / self.balls,
            prime_count / self.balls,
            spread / self.max_val,
            avg_diff / self.max_val
        ] + norm_nums
        
        return np.array(features)

    def fit(self, history):
        """
        Trains the K-Means model on historical data.
        """
        self.history = [d for d in history if len(d) >= self.balls]
        if len(self.history) < self.n_clusters:
            print("Not enough history to cluster.")
            return False
            
        # Extract features for all historical draws
        X = np.array([self.extract_features(draw) for draw in self.history])
        
        # Train K-Means
        self.kmeans = KMeans(n_clusters=self.n_clusters, random_state=42, n_init=10)
        self.kmeans.fit(X)
        self.cluster_centers = self.kmeans.cluster_centers_
        
        return True
        
    def predict_next_cluster(self):
        """
        Uses Markov-style transitions or recent frequency to predict which cluster
        is most likely to hit next.
        """
        if self.kmeans is None or not self.history:
            return random.randint(0, self.n_clusters - 1)
            
        # Get cluster assignments for history
        X = np.array([self.extract_features(draw) for draw in self.history])
        labels = self.kmeans.predict(X)
        
        # Option 1: Find the most common cluster recently (hot cluster)
        recent_labels = labels[-50:] # Look at last 50 draws
        if len(recent_labels) == 0:
            return random.randint(0, self.n_clusters - 1)
            
        counts = Counter(recent_labels)
        most_common = counts.most_common(1)[0][0]
        
        # Option 2: Transition matrix (Cluster A -> Cluster B)
        # For simplicity, we just return the most frequent recent cluster
        # or randomly pick among the top 3 hot clusters
        top_3 = [label for label, count in counts.most_common(3)]
        
        # 60% chance top 1, 30% top 2, 10% top 3
        weights = [0.6, 0.3, 0.1]
        
        if len(top_3) < 3:
            return top_3[0]
            
        predicted = random.choices(top_3, weights=weights[:len(top_3)], k=1)[0]
        return predicted

    def generate_ticket_from_cluster(self, target_cluster_id, max_attempts=5000):
        """
        Generates a valid ticket that belongs to the target cluster.
        """
        if self.kmeans is None:
            # Fallback to random if not trained
            return sorted(random.sample(range(1, self.max_val + 1), self.balls))
            
        target_center = self.cluster_centers[target_cluster_id]
        
        best_ticket = None
        best_distance = float('inf')
        
        # Random search approach (can be optimized with Genetic Algo, but random search is fast enough for 5k attempts)
        for _ in range(max_attempts):
            candidate = sorted(random.sample(range(1, self.max_val + 1), self.balls))
            features = self.extract_features(candidate)
            
            # Calculate distance to target cluster center
            dist = np.linalg.norm(features - target_center)
            
            if dist < best_distance:
                best_distance = dist
                best_ticket = candidate
                
        return best_ticket

# Example Usage:
if __name__ == "__main__":
    # Dummy history
    dummy_history = [sorted(random.sample(range(1, 46), 6)) for _ in range(500)]
    
    clusterer = TicketClustering(game_type="6/45", n_clusters=15)
    clusterer.fit(dummy_history)
    
    target = clusterer.predict_next_cluster()
    print(f"Predicted next cluster ID: {target}")
    
    ticket = clusterer.generate_ticket_from_cluster(target)
    print(f"Generated ticket belonging to cluster {target}: {ticket}")
