import random
import numpy as np
from collections import Counter

class DeltaFilter:
    """
    Implements the Delta System logic to filter distinct lottery combinations.
    """
    def __init__(self, game_type, config):
        self.game_type = game_type
        self.range = config["range"]
        self.balls = config["balls"]
        # Common Delta constraints (can be tuned per game)
        # For 6/55, deltas are usually small (1-15).
        self.max_delta_threshold = self.range // 2 
    
    def get_deltas(self, numbers):
        """
        Calculate deltas for a sorted list of numbers.
        d1 = n1
        d2 = n2 - n1
        ...
        """
        sorted_nums = sorted(numbers)
        deltas = []
        deltas.append(sorted_nums[0]) # First number is the first delta from 0
        for i in range(1, len(sorted_nums)):
            deltas.append(sorted_nums[i] - sorted_nums[i-1])
        return deltas
    
    def is_valid(self, numbers):
        """
        Check if a ticket passes the Delta filter.
        """
        if len(numbers) != self.balls: return False
        if len(set(numbers)) != self.balls: return False # Must be unique
        if any(n < 1 or n > self.range for n in numbers): return False
        
        deltas = self.get_deltas(numbers)
        
        # Rule 1: No delta should be excessively large (reduces 'wasted' space)
        # Exception: Max 3D Pro is different (it's 3-digit numbers), this logic applies to Matrix games (6/55, etc)
        if self.game_type == "Max 3D Pro": return True
        
        # Constraint: Most deltas should be small (< 15)
        small_deltas = sum(1 for d in deltas if d <= 15)
        if small_deltas < (self.balls - 2): 
            return False # Too many large gaps -> "Spread too thin"
            
        # Constraint: Delta 1 (first number) is rarely huge
        if deltas[0] > 25: return False
        
        return True

class GeneticLotteryEngine:
    """
    Optimizes coverage using Genetic Algorithm.
    """
    def __init__(self, game_type, config, history, population_size=200, generations=30):
        self.game_type = game_type
        self.cfg = config
        self.history = history
        self.pop_size = population_size
        self.generations = generations
        self.delta_filter = DeltaFilter(game_type, config)
        self.rng = random.Random()
        
        # Pre-calculate Hot Numbers / Frequent Pairs for Fitness
        self.hot_stats = self._analyze_history()

    def _analyze_history(self):
        # basic freq map
        ctr = Counter()
        for draw in self.history:
            ctr.update(draw)
        return ctr

    def _create_individual(self):
        """Create a valid random ticket."""
        attempts = 0
        while attempts < 100:
            nums = sorted(self.rng.sample(range(1, self.cfg["range"] + 1), self.cfg["balls"]))
            if self.delta_filter.is_valid(nums):
                return nums
            attempts += 1
        # Fallback
        return sorted(self.rng.sample(range(1, self.cfg["range"] + 1), self.cfg["balls"]))

    def _fitness(self, individual):
        """
        Calculate how 'good' a ticket is.
        Factors:
        1. Historical Resonance (Sum of frequencies of its numbers)
        2. Even/Odd balance (Bonus)
        3. Sum Check (Bonus)
        """
        # 1. Frequency Score
        freq_score = sum(self.hot_stats.get(n, 0) for n in individual)
        
        # 2. Balance Bonus (Odd/Even should be roughly equal)
        odds = sum(1 for n in individual if n % 2 != 0)
        balance_penalty = abs(odds - (self.cfg["balls"] / 2.0)) * 5
        
        # 3. Sum Range check (Normal distribution usually)
        # Expected sum ~ balls * (range/2)
        expected_sum = self.cfg["balls"] * (self.cfg["range"] / 2.0)
        actual_sum = sum(individual)
        sum_penalty = abs(actual_sum - expected_sum) / 2.0
        
        # 4. Sequence Penalty (No 3 consecutive numbers)
        seq_penalty = 0
        sorted_ind = sorted(individual)
        consecutive_count = 0
        for i in range(len(sorted_ind) - 1):
            if sorted_ind[i+1] - sorted_ind[i] == 1:
                consecutive_count += 1
                if consecutive_count >= 2:
                    seq_penalty += 500  # Massive penalty for 3-in-a-row
            else:
                consecutive_count = 0
                
        # 5. Gap Efficiency (Avoid clumps by enforcing reasonable deltas)
        deltas = self.delta_filter.get_deltas(sorted_ind)
        gap_penalty = 0
        if self.game_type != "Max 3D Pro":
            for d in deltas[1:]:  # Check differences between numbers
                if d == 0:
                    gap_penalty += 1000 # Duplicates are fatal
                elif d > 15:
                    gap_penalty += (d - 15) * 2
        
        return freq_score - balance_penalty - sum_penalty - seq_penalty - gap_penalty

    def _crossover(self, p1, p2):
        """Uniform Crossover."""
        # Mix gene pool
        pool = sorted(list(set(p1 + p2)))
        # Try to pick valid subset
        if len(pool) < self.cfg["balls"]: return p1
        
        child = sorted(self.rng.sample(pool, self.cfg["balls"]))
        return child

    def _mutate(self, individual):
        """Randomly change one number."""
        if self.rng.random() < 0.2: # 20% mutation chance
            idx = self.rng.randint(0, self.cfg["balls"]-1)
            new_val = self.rng.randint(1, self.cfg["range"])
            while new_val in individual:
                new_val = self.rng.randint(1, self.cfg["range"])
            individual[idx] = new_val
            individual.sort()
        return individual

    def run(self):
        """Execute the evolution."""
        # init population
        population = [self._create_individual() for _ in range(self.pop_size)]
        
        for g in range(self.generations):
            # Sort by fitness desc
            population.sort(key=self._fitness, reverse=True)
            
            # Elitism: keep top 20%
            elite_count = int(self.pop_size * 0.2)
            next_gen = population[:elite_count]
            
            # Breed the rest
            while len(next_gen) < self.pop_size:
                p1 = self.rng.choice(population[:50]) # Pick from top 50
                p2 = self.rng.choice(population[:50])
                child = self._crossover(p1, p2)
                child = self._mutate(child)
                next_gen.append(child)
            
            population = next_gen
            
        # Return unique top results
        population.sort(key=self._fitness, reverse=True)
        
        # Dedup logic
        unique_results = []
        seen = set()
        for ind in population:
            t = tuple(ind)
            if t not in seen:
                unique_results.append(ind)
                seen.add(t)
            if len(unique_results) >= 10: break
            
        return unique_results, {"Generations": self.generations, "Best Fitness": self._fitness(unique_results[0])}
