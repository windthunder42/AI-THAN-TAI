import random
from collections import defaultdict

class AdvancedCombinatorics:
    """
    Implements Maximum Hamming Distance logic to generate tickets from a pool.
    This guarantees that the N tickets bought are as spread out as possible,
    minimizing overlapping pairs/triplets, thus maximizing coverage space.
    """
    def __init__(self, game_type="6/55"):
        self.game_type = game_type
        if "6/55" in game_type:
             self.balls = 6
        elif "6/45" in game_type:
             self.balls = 6
        elif "5/35" in game_type:
             self.balls = 5
        else:
             self.balls = 6
             
    def hamming_distance(self, ticket1, ticket2):
        """
        Calculates how many numbers differ between two tickets (sets).
        Max distance for 6 balls is 6 (completely disjoint).
        Example: {1,2,3,4,5,6} and {1,2,7,8,9,10} share 2 numbers.
        Distance = 6 - 2 = 4
        """
        intersection = len(set(ticket1).intersection(set(ticket2)))
        return self.balls - intersection

    def generate_max_distance_tickets(self, pool, num_tickets, bankers=None):
        """
        Greedy approach to pick 'num_tickets' from the 'pool' that maximize
        the minimum Hamming distance between any pair of tickets.
        """
        if bankers is None:
            bankers = []
            
        pool = list(set([p for p in pool if p not in bankers]))
        needed_balls = self.balls - len(bankers)
        
        if needed_balls <= 0:
            return [sorted(bankers[:self.balls])] * num_tickets
            
        # If pool is too small to even generate 1 ticket, pad it
        if len(pool) < needed_balls:
            padding = list(range(1, 56)) # Fallback
            for p in padding:
                if p not in pool and p not in bankers:
                    pool.append(p)
                if len(pool) >= needed_balls:
                    break
        
        # 1. Generate a large candidate set from the pool
        num_candidates = min(5000, max(500, num_tickets * 50))
        candidates = []
        for _ in range(num_candidates):
            try:
                draw = sorted(random.sample(pool, needed_balls))
                candidates.append(draw)
            except Exception:
                pass
                
        # 2. Select tickets maximizing distances
        if not candidates:
            return []
            
        selected = [candidates.pop(0)] # Start with random candidate
        
        while len(selected) < num_tickets and candidates:
            best_candidate = None
            best_min_dist = -1
            
            # Subsample candidates if too large to speed up
            eval_candidates = random.sample(candidates, min(200, len(candidates)))
            
            for candidate in eval_candidates:
                # Find distance to closest already selected ticket
                min_dist_to_selected = min(self.hamming_distance(candidate, s) for s in selected)
                
                if min_dist_to_selected > best_min_dist:
                    best_min_dist = min_dist_to_selected
                    best_candidate = candidate
                    
            if best_candidate:
                selected.append(best_candidate)
                if best_candidate in candidates:
                    candidates.remove(best_candidate)
            else:
                break
                
        # Combine with bankers
        final_tickets = []
        for s in selected:
            final_tickets.append(sorted(list(set(bankers + s))))
            
        return final_tickets

# Testing
if __name__ == "__main__":
    combinatorics = AdvancedCombinatorics("6/45")
    pool = list(range(1, 21)) # Pool of 20 numbers
    
    print("Generating 5 tickets maximizing spread from a pool of 1-20...")
    tickets = combinatorics.generate_max_distance_tickets(pool, num_tickets=5, bankers=[5])
    
    for i, t in enumerate(tickets):
        print(f"Ticket {i+1}: {t}")
        
    # Check distances
    for i in range(len(tickets)):
         for j in range(i+1, len(tickets)):
              dist = combinatorics.hamming_distance(tickets[i], tickets[j])
              print(f"Dist between T{i+1} and T{j+1} = {dist}")
