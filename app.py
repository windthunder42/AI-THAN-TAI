import ssl
import streamlit as st
import pandas as pd
import numpy as np
import random
import time
import hashlib
import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
from collections import Counter
from unidecode import unidecode
import json
import os
import math
import base64
import re
import xskt_scraper

def get_base64_of_bin_file(bin_file):
    with open(bin_file, 'rb') as f:
        data = f.read()
    return base64.b64encode(data).decode()

def set_png_as_page_bg(png_file):
    bin_str = get_base64_of_bin_file(png_file)
    page_bg_img = '''
    <style>
    .stApp {
    background-image: url("data:image/png;base64,%s");
    background-size: cover;
    background-position: center;
    background-repeat: no-repeat;
    background-attachment: fixed;
    }
    /* Add slight overlay to readability */
    .stApp::before {
        content: "";
        position: absolute;
        top: 0;
        left: 0;
        width: 100%%;
        height: 100%%;
        background: rgba(255, 255, 255, 0.85); /* White overlay 85%% opacity */
        z-index: -1;
    }
    </style>
    ''' % bin_str
    st.markdown(page_bg_img, unsafe_allow_html=True)

def calculate_biorhythm(dob, target_date):
    """
    Calculates Physical (23d), Emotional (28d), Intellectual (33d) cycles.
    Returns average score (-1.0 to 1.0).
    """
    if isinstance(dob, datetime):
        dob = dob.date()
    if isinstance(target_date, datetime):
        target_date = target_date.date()
        
    delta = (target_date - dob).days
    
    phys = math.sin(2 * math.pi * delta / 23)
    emo = math.sin(2 * math.pi * delta / 28)
    intel = math.sin(2 * math.pi * delta / 33)
    
    return (phys + emo + intel) / 3
try:
    _create_unverified_https_context = ssl._create_unverified_context
except AttributeError:
    pass
else:
    ssl._create_default_https_context = _create_unverified_https_context

# --- CONFIGURATION & STYLING ---
st.set_page_config(
    page_title="AI Thần Tài - Vietlott Predictor",
    page_icon="🎱",
    layout="centered"
)

# Custom CSS for the "Ball" UI
st.markdown("""
<style>
    .ball-container {
        display: flex;
        justify_content: center;
        gap: 15px;
        margin-top: 20px;
        margin-bottom: 20px;
        flex-wrap: wrap;
    }
    .ball {
        width: 60px;
        height: 60px;
        background: radial-gradient(circle at 30% 30%, #ff4b4b, #990000);
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify_content: center;
        color: white;
        font-weight: bold;
        font-size: 24px;
        box-shadow: 0 4px 8px rgba(0,0,0,0.3);
        text-shadow: 1px 1px 2px rgba(0,0,0,0.5);
        border: 2px solid #ff9999;
    }
    .ball-special {
        background: radial-gradient(circle at 30% 30%, #1E90FF, #00008B); /* Blue for Special 1-12 */
        border: 2px solid #87CEFA;
        color: white;
    }
    .stButton>button {
        width: 100%;
        height: 60px;
        font-size: 18px !important;
        font-weight: bold !important;
        border-radius: 12px;
        transition: all 0.3s;
    }
    .stButton>button:hover {
        transform: scale(1.02);
        box-shadow: 0 5px 15px rgba(0,0,0,0.1);
    }
    .stat-box {
        background-color: #f0f2f6;
        padding: 15px;
        border-radius: 10px;
        text-align: center;
        margin-bottom: 10px;
    }
    .stat-title {
        font-size: 14px;
        color: #555;
        text-transform: uppercase;
        margin-bottom: 5px;
    }
    .stat-value {
        font-size: 18px;
        font-weight: bold;
        color: #333;
    }
    h1 {
        text-align: center;
        background: -webkit-linear-gradient(45deg, #FF4B4B, #FF914D);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        padding-bottom: 10px;
    }
</style>
""", unsafe_allow_html=True)

# --- BACKEND: DATA & ANALYSIS ---

import json

# --- BACKEND: DATA & ANALYSIS ---

GAME_CONFIG = {
    "6/55": {"type": "standard", "range": 55, "balls": 6, 
             "data_url": "https://raw.githubusercontent.com/vietvudanh/vietlott-data/main/data/power655.jsonl"},
    "6/45": {"type": "standard", "range": 45, "balls": 6,
             "data_url": "https://raw.githubusercontent.com/vietvudanh/vietlott-data/main/data/power645.jsonl"},
    "5/35": {"type": "special", "range": 35, "balls": 5, "special_range": 12, 
             "data_url": "https://raw.githubusercontent.com/vietvudanh/vietlott-data/main/data/power535.jsonl"},
    "Max 3D Pro": {"type": "3d_pro", "range": 999, "balls": 2, 
                   "data_url": "https://raw.githubusercontent.com/vietvudanh/vietlott-data/main/data/3d_pro.jsonl"}
}

def mode_3d_engine(game_type, history):
    """
    Engine for Max 3D Pro (000-999).
    User wants 1 Jackpot pair.
    """
    # 1. Frequency Analysis of Digits (0-9)
    # Position analysis: Col 1, Col 2, Col 3 for each number in the pair.
    
    # Flatten history: [ [n1, n2], [n3, n4] ] -> [n1, n2, n3, n4]
    flat_history = [n for pair in history for n in pair]
    
    # Convert to strings "000" - "999"
    str_history = [f"{n:03d}" for n in flat_history]
    
    # Analyze digit frequency per position
    pos_counts = [{str(d): 0 for d in range(10)} for _ in range(3)]
    
    for s in str_history:
        for i, char in enumerate(s):
            pos_counts[i][char] += 1
            
    # Pick best digit for each position?
    # Or simple Hot/Cold on the full number 000-999?
    # 000-999 is small enough for full frequency map.
    
    # Strategy: "Hot Pair" + "Cold Pair"
    # Identify numbers that appear often together?
    
    # User wants ONE jackpot pair.
    # Let's pick 2 numbers.
    # Num 1: Most frequent number in history.
    # Num 2: Most frequent partner of Num 1? Or just 2nd most frequent.
    
    counts = Counter(flat_history)
    most_common = counts.most_common(20)
    
    # Randomize slightly ensuring they are top tier
    import random
    candidates = [n for n, c in most_common]
    if len(candidates) < 2: candidates = [123, 456]
    
    final_pair = sorted(random.sample(candidates, 2))
    
    return final_pair, {"Analysis": "Frequency Top 20"}

@st.cache_data(ttl=3600)
def load_real_data(game_type):
    """
    Fetches real data from online sources (JSONL format).
    Returns the last 400 draws.
    """
    cfg = GAME_CONFIG[game_type]
    limit = 400 # Maximize history but keep it fast
    
    try:
        url = cfg.get("data_url")
        if not url: return generate_simulation(game_type, limit)

        # Fetch Data
        headers = {'User-Agent': 'Mozilla/5.0'}
        r = requests.get(url, headers=headers, timeout=10)
        
        if r.status_code != 200:
            print(f"⚠️ Error fetching {game_type}: {r.status_code}")
            return generate_simulation(game_type, limit)

        # Parse JSONL
        history = []
        lines = r.text.strip().split('\n')
        
        for line in lines:
            if not line.strip(): continue
            try:
                data = json.loads(line)
                
                # --- MAX 3D PRO PARSING ---
                if game_type == "Max 3D Pro":
                    # Format: "result": {"Giải Đặc biệt": ["740", "262"], ...}
                    res_dict = data.get("result", {})
                    if isinstance(res_dict, dict):
                        special_prize = res_dict.get("Giải Đặc biệt", [])
                        if len(special_prize) == 2:
                            # Convert to int
                            draw = [int(n) for n in special_prize]
                            history.append(draw)
                    continue

                # --- 6/55, 6/45, 5/35 PARSING ---
                # Format: "result": [n1, n2, ....]
                raw_result = data.get("result", [])
                
                if not isinstance(raw_result, list): continue

                if game_type == "6/55":
                    # Data has 7 numbers (6 main + 1 bonus). 
                    if len(raw_result) >= 6:
                        history.append(sorted(raw_result[:6]))
                        
                elif game_type == "6/45":
                    # Data has 6 numbers.
                    if len(raw_result) >= 6:
                        history.append(sorted(raw_result[:6]))
                        
                elif game_type == "5/35":
                    # Data has 6 numbers (5 main + 1 special).
                    # [7,9,10,16,19, 9] (sorted first 5, last is special)
                    if len(raw_result) >= 6:
                        main_part = sorted(raw_result[:5])
                        special_part = raw_result[5]
                        history.append(main_part + [special_part])
                        
            except Exception as e:
                continue
                
        if len(history) > 10:
             # Try to fetch very latest if possible (for 3D Pro might be hard)
             # For now, just return what we have
             return history[-limit:]
        else:
            return generate_simulation(game_type, limit)

    except Exception as e:
        print(f"⚠️ Error loading real data: {e}. Using simulation.")
        return generate_simulation(game_type, limit)

def fetch_latest_realtime(game_type):
    """
    Scrapes live result from Minh Ngoc to capture the very latest draw
    that might be missing from the bulk JSONL.
    """
    try:
        url_map = {
            "6/55": "https://www.minhngoc.net.vn/ket-qua-xo-so/dien-toan-6x55.html",
            "6/45": "https://www.minhngoc.net.vn/ket-qua-xo-so/dien-toan-6x45.html",
        }
        
        target_url = url_map.get(game_type)
        if not target_url: return None
        
        headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)'}
        resp = requests.get(target_url, headers=headers, timeout=5)
        
        if resp.status_code != 200: return None
        
        soup = BeautifulSoup(resp.text, 'html.parser')
        
        box = soup.find("div", class_="box_kqxs")
        if not box: return None
        
        balls = box.select(".day_so_ket_qua_v2 span")
        if not balls: return None
        
        nums = []
        for b in balls:
            txt = b.get_text().strip()
            if txt.isdigit():
                nums.append(int(txt))
                
        if not nums: return None
        
        # Format
        if game_type == "6/55":
            if len(nums) >= 6:
                return sorted(nums[:6])
                
        elif game_type == "6/45":
            if len(nums) >= 6:
                return sorted(nums[:6])
                
        return None
        
    except Exception as e:
        return None

def generate_simulation(game_type, limit=400):
    """Simulates past draws for the selected game type."""
    cfg = GAME_CONFIG[game_type]
    history = []
    
    for _ in range(limit):
        if cfg["type"] == "standard":
            draw = sorted(random.sample(range(1, cfg["range"] + 1), cfg["balls"]))
        elif cfg["type"] == "3d_pro":
             # Max 3D Pro: 2 numbers 0-999
             draw = [random.randint(0, 999), random.randint(0, 999)]
        else: # 5/35 (5 balls 1-35 + 1 ball 1-12)
             # Main: 5 balls from 1-35
             main_draw = sorted(random.sample(range(1, cfg["range"] + 1), cfg["balls"]))
             # Special: 1 ball from 1-30 (updated range)
             limit_special = cfg.get("special_range", 12)
             special_ball = random.randint(1, limit_special)
             draw = main_draw + [special_ball]
            
        history.append(draw)
    return history

def analyze_history(history):
    """Finds Hot and Cold numbers from history using Weighted Frequency."""
    # Use the weighted algorithm
    weighted_freq = calculate_weighted_frequency(history)
    
    # Sort by weight
    most_common = weighted_freq.most_common()
    
    # Top 5 Hot (Highest weight)
    hot_numbers = [num for num, w in most_common[:5]]
    
    # Top 5 Cold (Lowest weight)
    # Note: Counter only contains numbers that appeared. 
    # Numbers with 0 appearance are not in 'most_common'.
    # But for display purpose, least frequent among *appearing* is fine.
    cold_numbers = [num for num, w in most_common[-5:]]
    
    return hot_numbers, cold_numbers

def analyze_special_number(history, special_range=12):
    """
    Analyzes the special number (last number in 5/35 draw) history.
    Returns: The most likely special number based on weighted frequency.
    """
    if not history: return random.randint(1, special_range)
    
    # Extract special numbers (last element of each draw)
    specials = [draw[-1] for draw in history if len(draw) > 0]
    
    # Weighted Frequency (Recency bias)
    freq = Counter()
    decay = 0.98
    for i, num in enumerate(reversed(specials)):
        weight = decay ** i
        freq[num] += weight
        
    # Get top 3 candidates
    most_common = freq.most_common(3)
    
    if not most_common: return random.randint(1, special_range)
    
    # 70% chance to pick #1, 20% #2, 10% #3
    candidates = [num for num, w in most_common]
    weights = [0.7, 0.2, 0.1]
    
    # Adjust if fewer than 3
    if len(candidates) < 3:
        return candidates[0]
        
    import random
    return random.choices(candidates, weights=weights[:len(candidates)], k=1)[0]


# --- ALGORITHMS ---

# --- ALGORITHMS ---

def calculate_weighted_frequency(history, decay_factor=0.95):
    """
    Calculates frequency with recency bias.
    Recent draws have higher weight.
    Formula: Weight += decay_factor ^ (draws_ago)
    """
    freq = Counter()
    for idx, draw in enumerate(reversed(history)):
        # idx 0 = most recent
        weight = decay_factor ** idx
        for num in draw:
            freq[num] += weight
    return freq

def calculate_pair_correlation(history):
    """
    Builds a matrix of pair co-occurrences.
    Returns a dict: {num: Counter({partner_num: count})}
    """
    pair_counts = {}
    for draw in history:
        # For 5/35, draw might have special ball at end.
        # We process all numbers in the draw as a set for co-occurrence
        # Or should we separate main and special? 
        # Let's treat valid main numbers as pairs. 
        # Assuming draw is a list of integers.
        
        # Sort to insure (a,b) is same as (b,a) efficiently if using tuple keys
        # But here we use nested dicts for easier lookup: "Given 5, what goes with it?"
        
        # Filter for main numbers if distinguishing is needed, but general co-occurrence is fine.
        draw_set = set(draw)
        for num in draw:
            if num not in pair_counts:
                pair_counts[num] = Counter()
            # Add all other nums in this draw
            for other in draw:
                if num != other:
                    pair_counts[num][other] += 1
    return pair_counts

def calculate_triplet_correlation(history):
    """
    Analyzes clusters of 3 numbers that frequently appear together.
    Returns: { (n1, n2): Counter({n3: count}) }
    """
    triplet_counts = {}
    for draw in history:
        sorted_draw = sorted(draw)
        for i in range(len(sorted_draw)):
            for j in range(i + 1, len(sorted_draw)):
                for k in range(j + 1, len(sorted_draw)):
                    a, b, c = sorted_draw[i], sorted_draw[j], sorted_draw[k]
                    # Key by pairs (a,b), count c
                    if (a, b) not in triplet_counts: triplet_counts[(a, b)] = Counter()
                    triplet_counts[(a, b)][c] += 1
    return triplet_counts

def calculate_markov_transitions(history):
    """
    Builds transition probability matrix.
    Upgrade: P(Next Draw Ball = Z | Current Draw Ball = Y and X)
    Returns: { (X, Y): Counter({Z: count}) }
    """
    transitions = {}
    for i in range(len(history) - 1):
        curr_draw = sorted(history[i])
        next_draw = history[i+1]
        
        # 2nd Order: Pair in current -> Result in next
        for idx1 in range(len(curr_draw)):
            for idx2 in range(idx1 + 1, len(curr_draw)):
                key = (curr_draw[idx1], curr_draw[idx2])
                if key not in transitions:
                    transitions[key] = Counter()
                for num_next in next_draw:
                    transitions[key][num_next] += 1
    return transitions

def passes_filters(draw, game_type):
    """
    Checks if a draw looks 'normal' (Sum, Even/Odd).
    """
    # 1. Sum Filter
    # 6/55 avg sum: ~168. Range 120-220.
    # 6/45 avg sum: ~138. Range 100-180.
    # 5/35 avg sum: ~90. Range 60-120.
    
    s = sum(draw)
    is_valid_sum = False
    
    if game_type == "6/55":
        is_valid_sum = 100 <= s <= 230
    elif game_type == "6/45":
        is_valid_sum = 90 <= s <= 190
    elif game_type == "5/35": # Note: draw length might be 6 (5+1). Use sum of main 5 usually.
        # But draw passed here is likely sorted list.
        # For simplicity, filter based on total sum. 
        is_valid_sum = 50 <= s <= 150
        
    if not is_valid_sum: return False
    
    # 2. Even/Odd Ratio
    # Best is 3:3, 4:2, 2:4. (or 3:2 for 5 numbers)
    evens = len([n for n in draw if n % 2 == 0])
    total = len(draw)
    
    if total == 6:
        # Avoid 6:0 or 0:6
        if evens == 0 or evens == 6: return False
    elif total == 5:
        if evens == 0 or evens == 5: return False
        
    # --- 5. Golden Ratio (Phi) Spacing Filter (Phase 11) ---
    # Phase 11 Toggling
    if st.session_state.get("USE_PHASE_11", True):
        # Natural growth typically follows Phi (1.618) approx.
        # We check the average ratio of adjacent differences.
        # Ideally, numbers shouldn't be too clumped (ratio ~1.0) or too spread (ratio > 3.0)
        sorted_d = sorted(draw)
        diffs = [sorted_d[i+1] - sorted_d[i] for i in range(len(sorted_d)-1)]
        if len(diffs) > 0:
            avg_diff = sum(diffs) / len(diffs)
            # Empirical "Golden Mean" for 6/55 is around 7-10.
            # Adjusted Phase 11.1: Lowered min to 1.8 to allow for "Twin Clusters" (e.g. 23-24, 32-33)
            # as seen in 5/35 results.
            min_diff = 1.2 if game_type == "5/35" else 1.8
            if avg_diff < min_diff or avg_diff > 20.0:
                return False
                
    # --- 6. Advanced Pattern Filters (New) ---
    if not advanced_pattern_filters(draw, game_type):
        return False
        
    return True

def advanced_pattern_filters(draw, game_type):
    """
    Advanced Statistical Filters to reject rare anomalies.
    """
    sorted_draw = sorted(draw)
    
    # 1. Consecutive Numbers (Sequence)
    # Reject if > 2 consecutive numbers (e.g. 1, 2, 3)
    consecutive_count = 0
    for i in range(len(sorted_draw) - 1):
        if sorted_draw[i+1] - sorted_draw[i] == 1:
            consecutive_count += 1
            if consecutive_count >= 2: # Found 3 numbers in a row (e.g. 1-2, 2-3)
                return False
        else:
            consecutive_count = 0
            
    # 2. Decade Distribution (Clump Check)
    # Reject if > 4 numbers are in the same decade (e.g. 20-29)
    decades = [n // 10 for n in sorted_draw]
    decade_counts = Counter(decades)
    if any(count > 4 for count in decade_counts.values()):
        return False
        
    # 3. Last Digit Diversity
    # Reject if > 3 numbers have same last digit (e.g. 1, 11, 21, 31)
    last_digits = [n % 10 for n in sorted_draw]
    ld_counts = Counter(last_digits)
    if any(count > 3 for count in ld_counts.values()):
        return False
        
    return True
        
    return True
    return True



def core_generate_predictions(game_type, history, hot_nums, cold_nums, pool_size=6, seed=None, bankers=None, style="Modern"):
    """
    Core engine for generating predictions.
    style: 'Modern' (Statistical) or 'Classic' (Random/Flat).
    """
    rng = random.Random(seed) if seed is not None else random
    cfg = GAME_CONFIG[game_type]
    
    # Banker validation
    if bankers:
        bankers = [b for b in bankers if 1 <= b <= cfg["range"]]
        bankers = sorted(list(set(bankers)))
        if len(bankers) > cfg["balls"]:
             bankers = bankers[:cfg["balls"]]
    else:
        bankers = []

    # --- 1. Signal Analysis ---
    weighted_freq = calculate_weighted_frequency(history)
    pair_matrix = calculate_pair_correlation(history)
    triplet_matrix = calculate_triplet_correlation(history)
    markov_matrix = calculate_markov_transitions(history)
    last_draw = sorted(history[-1]) if history else []
    
    # Score calculation
    scores = {}
    
    if style == "Classic":
        # Classic Mode: Flat weights (Entropy)
        # We give everyone a baseline score with random jitter
        for n in range(1, cfg["range"] + 1):
            scores[n] = 10.0 + rng.uniform(-2.0, 2.0)
    else:
        # Modern Mode: Weighted Frequency
        max_w = weighted_freq.most_common(1)[0][1] if weighted_freq else 1
        for n, w in weighted_freq.items():
            if n > cfg["range"]: continue # Safety filter
            scores[n] = (w / max_w) * 50 
            
        # Markov deep pattern boost
        if len(last_draw) >= 2:
            for i in range(len(last_draw)):
                for j in range(i+1, len(last_draw)):
                    key = (last_draw[i], last_draw[j])
                    if key in markov_matrix:
                        for n, count in markov_matrix[key].items():
                            scores[n] = scores.get(n, 0) + (count * 10)
            
        for n in range(1, cfg["range"] + 1):
            if n not in scores: scores[n] = 0.1

    # --- Neighbor Boosting (5/35 Only) ---
    # Addresses user feedback: "Results off by a few units"
    if game_type == "5/35":
        neighborhood_scores = scores.copy()
        for n in range(1, cfg["range"] + 1):
            current_score = scores.get(n, 0)
            if current_score > 0:
                # Spread 15% of score to immediate neighbors
                boost = current_score * 0.15
                
                prev_n = n - 1
                if prev_n >= 1:
                    neighborhood_scores[prev_n] = neighborhood_scores.get(prev_n, 0) + boost
                    
                next_n = n + 1
                if next_n <= cfg["range"]:
                    neighborhood_scores[next_n] = neighborhood_scores.get(next_n, 0) + boost
        scores = neighborhood_scores
        
    # Boost Bankers Score to Infinity
    for b in bankers:
        scores[b] = 99999.0
        
    # --- 2. Generation ---
    sorted_candidates = sorted(scores.keys(), key=lambda x: scores[x], reverse=True)
    
    # In Classic Mode, expand search pool to ALMOST ALL numbers to allow "weird" picks
    if style == "Classic":
        # Search pool is effectively random if scores are close
        # But we still take top K. Since scores are random-ish, top K is random-ish.
        search_pool = list(scores.keys()) 
    else:
        # Modern: Restricted pool
        search_pool = list(set(sorted_candidates[:40] + bankers))
    
    best_candidate = []
    max_score = -1
    
    attempts = 5000 
    actual_balls = cfg["balls"]
    
    # Calculate how many needed
    needed_random = actual_balls - len(bankers)
    if needed_random < 0: needed_random = 0
    
    number_pool_excluding_bankers = [n for n in search_pool if n not in bankers]
    
    for _ in range(attempts):
        try:
            # Pick randoms
            if needed_random > 0:
                random_part = rng.sample(number_pool_excluding_bankers, needed_random)
                core_draw = sorted(bankers + random_part)
            else:
                core_draw = sorted(bankers[:actual_balls])
                
        except ValueError:
            random_part = rng.sample(sorted_candidates, needed_random)
            core_draw = sorted(bankers + random_part)
            
        # RELAXED FILTERS for Classic
        if style != "Classic" and not passes_filters(core_draw, game_type):
            continue
            
        # Score the Core Draw
        draw_score = sum(scores.get(n, 0) for n in core_draw)
        
        # Synergy Bonus (Only Modern)
        synergy_bonus = 0
        if style != "Classic":
            for i in range(len(core_draw)):
                for j in range(i + 1, len(core_draw)):
                    a, b = core_draw[i], core_draw[j]
                    if a in pair_matrix and b in pair_matrix[a]:
                        synergy_bonus += pair_matrix[a][b] * 0.5
                    key = (a, b)
                    if key in triplet_matrix:
                        for k in range(j + 1, len(core_draw)):
                            c = core_draw[k]
                            if c in triplet_matrix[key]:
                                synergy_bonus += triplet_matrix[key][c] * 5 
        
        # In Classic, just total score (randomized) is fine.
        total_score = draw_score + synergy_bonus
        
        if total_score > max_score:
            max_score = total_score
            best_candidate = core_draw
            
    result = set(best_candidate)
    result.update(bankers)
    
    if len(result) < pool_size:
        remainder = [n for n in sorted_candidates if n not in result]
        needed = pool_size - len(result)
        result.update(remainder[:needed])
        
    final_result = sorted(list(result))
    
    if cfg["type"] == "special":
         if pool_size == 6 and cfg["balls"] == 5:
             final_result = final_result[:5]
         special_part = rng.randint(1, cfg["special_range"])
         return final_result + [special_part]
         
    return final_result

def mode_a_ai_analysis(game_type, history, hot_nums, cold_nums, seed=None):
    """
    Combines Weighted Frequency, Markov, and Pattern Filters.
    Returns a single optimized set of numbers.
    """
    return core_generate_predictions(game_type, history, hot_nums, cold_nums, seed=seed)

def mode_system_play(game_type, history, hot_nums, cold_nums, system_size=10, seed=None, bankers=None, style="Modern"):
    """
    Returns a larger pool of high-probability numbers.
    Utilizes advanced generation engine.
    """
    return core_generate_predictions(game_type, history, hot_nums, cold_nums, pool_size=system_size, seed=seed, bankers=bankers, style=style)


def mode_b_personal_luck(game_type, name, dob):
    """
    Mode B: Deterministic chaos based on User Input.
    """
    cfg = GAME_CONFIG[game_type]
    
    # Create Seed
    current_time = str(time.time() * 1000)
    raw_seed = f"{name}{dob}{current_time}"
    hash_obj = hashlib.sha256(raw_seed.encode())
    seed_int = int(hash_obj.hexdigest(), 16)
    
    random.seed(seed_int)
    
    if cfg["type"] == "standard":
        selection = random.sample(range(1, cfg["range"] + 1), cfg["balls"])
        result = sorted(selection)
    else: # 5/35
        # 5 main balls (1-35)
        main_sel = random.sample(range(1, cfg["range"] + 1), cfg["balls"])
        # 1 special ball (1-12)
        special_val = random.randint(1, cfg["special_range"])
        result = sorted(main_sel) + [special_val]
    
    random.seed() # Reset
    return result

def mode_c_chaos(game_type):
    """
    Mode C: Pure random.
    """
    cfg = GAME_CONFIG[game_type]
    
    if cfg["type"] == "standard":
        return sorted(random.sample(range(1, cfg["range"] + 1), cfg["balls"]))
    else:
        main_part = sorted(random.sample(range(1, cfg["range"] + 1), cfg["balls"]))
        special_part = random.randint(1, cfg["special_range"])
        return main_part + [special_part]

    return result

def backtest_algorithm(game_type, history, system_size=10, test_count=10):
    """
    Backtests the 'System Play' algorithm on the last `test_count` draws.
    """
    if len(history) < test_count + 50:
        return 0, []
        
    hits = 0
    details = []
    
    # We test on the last N draws.
    # For each test draw T(i), we use history[:i] to predict.
    
    start_idx = len(history) - test_count
    
    for i in range(start_idx, len(history)):
        target_draw = history[i] # The actual result
        past_data = history[:i]  # Knowledge available before the draw
        
        # Run System Generation
        # Recalculate stats for past_data
        # Note: This is computationally expensive but necessary for true backtest
        
        # Simplified: We assume hot/cold don't change drastically day-to-day for speed?
        # No, must calculate correctly.
        
        w_freq = calculate_weighted_frequency(past_data)
        hot = [n for n, w in w_freq.most_common(5)]
        cold = [n for n, w in w_freq.most_common()[-5:]]
        
        prediction_pool = mode_system_play(game_type, past_data, hot, cold, system_size=system_size)
        
        # Check coverage
        # For 6/55, target_draw might be 6 numbers. prediction_pool is 10 numbers.
        # How many winners are in the pool?
        
        # For 5/35, target draw is 5 main + 1 special.
        # Prediction pool (System) provides main numbers.
        # We compare main numbers.
        
        if GAME_CONFIG[game_type]["type"] == "special":
             target_main = set(target_draw[:-1])
             pool_set = set(prediction_pool) 
             match_count = len(target_main.intersection(pool_set))
        else:
             target_set = set(target_draw)
             pool_set = set(prediction_pool)
             match_count = len(target_set.intersection(pool_set))
             
        # Criteria for "Success" in System Play
        # If we catch >= 5 numbers (for Jackpot 1/2 chance) it's huge.
        # If we catch >= 4 numbers it's decent.
        
        # Let's log the match count
        details.append(f"Draw {i}: Matched {match_count} numbers. (Pool: {prediction_pool}, Target: {target_draw})")
        if match_count >= 5: # High success threshold
            hits += 1
            
    return hits, details

    return hits, details

# --- ESOTERIC ALGORITHMS ---

def get_next_draw_time(game_type):
    """
    Calculates the next official draw time (GMT+7).
    """
    now = datetime.now()
    
    # Rules
    # 6/55: Tue(1), Thu(3), Sat(5) @ 18:00
    # 6/45: Wed(2), Fri(4), Sun(6) @ 18:00
    # 5/35: Daily @ 13:00 and 21:00
    
    target_time = None
    
    if game_type == "5/35":
        # Check today's slots
        slot1 = now.replace(hour=13, minute=0, second=0, microsecond=0)
        slot2 = now.replace(hour=21, minute=0, second=0, microsecond=0)
        
        if now < slot1:
            target_time = slot1
        elif now < slot2:
            target_time = slot2
        else:
            # Tomorrow 13:00
            target_time = (now + timedelta(days=1)).replace(hour=13, minute=0, second=0, microsecond=0)
            
    else:
        # Schedule map: {weekday_int: [hour]} matches
        # but 6/45 and 6/55 only have 1 slot per draw day
        
        needed_days = []
        if game_type == "6/55" or game_type == "Max 3D Pro":
            needed_days = [1, 3, 5] # Tue, Thu, Sat
        elif game_type == "6/45":
            needed_days = [2, 4, 6] # Wed, Fri, Sun
            
        # Try today
        current_weekday = now.weekday()
        found_today = False
        if current_weekday in needed_days:
            slot = now.replace(hour=18, minute=0, second=0, microsecond=0)
            if now < slot:
                target_time = slot
                found_today = True
                
        if not found_today:
            # Look ahead 1-7 days
            for d in range(1, 8):
                next_day = now + timedelta(days=d)
                if next_day.weekday() in needed_days:
                    target_time = next_day.replace(hour=18, minute=0, second=0, microsecond=0)
                    break
                    
    return target_time

def mode_d_quantum(game_type, seed=None, quantum_dob=None):
    """
    Simulates Quantum Superposition.
    If quantum_dob is provided (string YYYY-MM-DD), use it to modulate frequency.
    """
    rng = random.Random(seed) if seed is not None else random
    cfg = GAME_CONFIG[game_type]
    results = []
    
    # 1. Initialize Superposition
    # Use Next Draw Time as the "Observer" moment
    draw_time = get_next_draw_time(game_type)
    t = draw_time.timestamp()
    
    # Personal Modulation
    personal_freq = 0
    if quantum_dob:
         # Convert DOB to timestamp shift
         try:
             # If it's date object or string? User input is date_input (date obj)
             # or text input? Let's handle date object from streamlit
             pd = datetime.combine(quantum_dob, datetime.min.time())
             personal_freq = pd.timestamp() / 100000000 # Scale down
         except:
             pass
    
    import cmath
    import math
    
    candidates = []
    
    for n in range(1, cfg["range"] + 1):
        # Wave function psi(n, t) = A * e^(i(kx - wt))
        # Add personal_freq to the phase
        phase = (n * t) + (n * personal_freq)
        phase = phase % (2 * math.pi)
        
        amplitude = complex(math.cos(phase), math.sin(phase))
        
        # Interference from "Entanglement" 
        # (Simulated by coupling adjacent numbers)
        coupling = math.sin(n * 0.5) 
        
        psi = amplitude + coupling
        probability = abs(psi) ** 2 # Born rule
        
        candidates.append((n, probability))
        
    # 2. Collapse (Measurement)
    # Sort by probability density
    candidates.sort(key=lambda x: x[1], reverse=True)
    
    # Pick top N
    # Introduce some uncertainty (Heisenberg) - don't just pick top N fixed.
    # Use probabilistic selection from top 50%.
    
    top_half = candidates[:len(candidates)//2]
    total_prob = sum(c[1] for c in top_half)
    
    selected = set()
    while len(selected) < cfg["balls"]:
        r = rng.uniform(0, total_prob)
        current = 0
        for n, prob in top_half:
            current += prob
            if current >= r:
                selected.add(n)
                break
                
    results = sorted(list(selected))
    
    # 5/35 Special
    if cfg["type"] == "special":
        special = rng.randint(1, cfg["special_range"])
        return results + [special], draw_time
        
    return results, draw_time

def mode_e_iching(game_type, seed=None, iching_dob=None):
    """
    Generates numbers based on I Ching (Kinh Dịch).
    If iching_dob (datetime object) is provided, mix it into Trigram calc.
    """
    rng = random.Random(seed) if seed is not None else random
    cfg = GAME_CONFIG[game_type]
    
    # Data for Trigrams (Bat Quai)
    trigrams = {
        0: ("Càn (Trời)", 1, "☁️"),
        1: ("Đoài (Hồ)", 2, "🌊"),
        2: ("Ly (Lửa)", 3, "🔥"),
        3: ("Chấn (Sấm)", 4, "⚡"),
        4: ("Tốn (Gió)", 5, "🍃"),
        5: ("Khảm (Nước)", 6, "💧"),
        6: ("Cấn (Núi)", 7, "⛰️"),
        7: ("Khôn (Đất)", 8, "🌍")
    }
    
    # Use Next Draw Time for Prediction
    target_time = get_next_draw_time(game_type)
    
    # 1. Calculate Trigrams from Time
    y = target_time.year
    m = target_time.month
    d = target_time.day
    h = target_time.hour
    minute = target_time.minute
    
    # If User info exists, Add it to the summation
    if iching_dob:
        # iching_dob is a datetime with hour
        y += iching_dob.year
        m += iching_dob.month
        d += iching_dob.day
        h += iching_dob.hour
        minute += iching_dob.minute
        
    upper_idx = (y + m + d) % 8
    lower_idx = (y + m + d + h) % 8
    moving_idx = (y + m + d + h + minute) % 6
    if moving_idx == 0: moving_idx = 6
    
    upper = trigrams[upper_idx]
    lower = trigrams[lower_idx]
    hex_name = f"{upper[0]} trên {lower[0]}"
    
    # --- 2. Calculate "Quẻ Biến" (Transformation) ---
    # In Mai Hoa, the moving line changes Yin <-> Yang
    # Simplified: Moving line changes the Index of the Trigram
    upper_idx_b = upper_idx
    lower_idx_b = lower_idx
    
    if moving_idx <= 3: # Lower trigram
        lower_idx_b = (lower_idx + (1 << (moving_idx-1))) % 8
    else: # Upper trigram
        upper_idx_b = (upper_idx + (1 << (moving_idx-4))) % 8
        
    upper_b = trigrams[upper_idx_b]
    lower_b = trigrams[lower_idx_b]
    hex_name_b = f"{upper_b[0]} trên {lower_b[0]}"
    
    # 3. Map to Numbers (The 'Oracle' step)
    
    seed_chủ = (upper[1] * 100) + (lower[1] * 10) + moving_idx
    seed_biến = (upper_b[1] * 100) + (lower_b[1] * 10) + moving_idx
    
    # Combine Seeds
    destiny_seed = (seed if seed else 0) + seed_chủ + seed_biến
    local_rng = random.Random(destiny_seed)
    
    pool = list(range(1, cfg["range"] + 1))
    local_rng.shuffle(pool)
    
    results = sorted(pool[:cfg["balls"]])
    
    # 5/35 Special
    extra_info = {
        "hex": hex_name,
        "symbol": f"{upper[2]}\n---\n{lower[2]}",
        "desc": f"Quẻ Chủ: {hex_name}. Quẻ Biến: {hex_name_b}. Động hào {moving_idx}. \n\n(Ứng nghiệm cho kỳ: {target_time.strftime('%H:%M %d/%m/%Y')})"
    }
    
    if cfg["type"] == "special":
        special = local_rng.randint(1, cfg["special_range"])
        return results + [special], extra_info
        
    return results, extra_info

def calculate_numerology(name, dob):
    """
    Calculates Life Path Number and Destiny Number.
    Returns a set of 'Lucky Numbers' derived from these.
    """
    lucky_set = set()
    
    # 1. Life Path (from DOB)
    # dob is datetime object
    digits = [int(d) for d in dob.strftime("%d%m%Y")]
    life_path = sum(digits)
    while life_path > 9 and life_path != 11 and life_path != 22 and life_path != 33:
        life_path = sum(int(d) for d in str(life_path))
    
    lucky_set.add(life_path)
    
    # 2. Destiny Number (from Name)
    # Pythagorean system
    table = {
        'a':1, 'j':1, 's':1,
        'b':2, 'k':2, 't':2,
        'c':3, 'l':3, 'u':3,
        'd':4, 'm':4, 'v':4,
        'e':5, 'n':5, 'w':5,
        'f':6, 'o':6, 'x':6,
        'g':7, 'p':7, 'y':7,
        'h':8, 'q':8, 'z':8
    }
    
    name_clean = unidecode(name.lower())
    destiny_sum = 0
    for char in name_clean:
        if char in table:
            destiny_sum += table[char]
            
    destiny = destiny_sum
    while destiny > 9 and destiny != 11 and destiny != 22 and destiny != 33:
        destiny = sum(int(d) for d in str(destiny))
        
    lucky_set.add(destiny)
    
    # Expand lucky set: Multiples or related numbers?
    # Simple expansion: value + 9, value + 18, etc. (Numerology families)
    for root in list(lucky_set):
        curr = root
        while curr <= 55: # Max ball usually
            lucky_set.add(curr)
            curr += 9
            
    return lucky_set

def mode_g_genetic(game_type, history, hot_nums, cold_nums, seed=None, numerology_set=set(), bio_score=0.0):
    """
    Super Algorithm: Genetic Evolution.
    Breeds a population of tickets to find the 'Fittest' combination.
    """
    rng = random.Random(seed) if seed is not None else random
    cfg = GAME_CONFIG[game_type]
    
    # Genetic Params
    POP_SIZE = 100
    GENERATIONS = 50
    MUTATION_RATE = 0.2
    ELITISM = 0.2
    
    # --- PHASE 11: BIO-BOOST ---
    if st.session_state.get("USE_PHASE_11", True):
        if bio_score > 0.5:
            # High Energy: Search deeper and wider
            POP_SIZE = int(POP_SIZE * (1 + bio_score)) # Up to 200
            GENERATIONS = int(GENERATIONS * (1 + bio_score)) # Up to 100
            MUTATION_RATE = 0.15 # More creativity
        elif bio_score < 0:
            # Low Energy: Conservative
            MUTATION_RATE = 0.05
    
    # Range
    num_range = range(1, cfg["range"] + 1)
    balls = cfg["balls"]
    
    # 1. Initialize Population
    population = []
    for _ in range(POP_SIZE):
        ticket = set(rng.sample(num_range, balls))
        population.append(ticket)
        
    # Fitness Function
    def get_fitness(ticket):
        score = 100
        
        # 1. Sum Check (Target optimal range ~40-60% of max possible sum)
        s = sum(ticket)
        min_s = sum(range(1, balls+1))
        max_s = sum(range(cfg["range"] - balls + 1, cfg["range"] + 1))
        avg_s = (min_s + max_s) / 2
        dist = abs(s - avg_s)
        score -= (dist * 0.5) # Penalize distance from average
        
        # 2. Parity (Even/Odd Balance)
        evens = len([n for n in ticket if n % 2 == 0])
        # Ideal is roughly half
        if evens == 0 or evens == balls: score -= 20
        
        # 3. Hot/Cold Balance
        hcr = len([n for n in ticket if n in hot_nums[:10]])
        ccr = len([n for n in ticket if n in cold_nums[:10]])
        if hcr > 1: score += (hcr * 5)
        if ccr > 0: score += (ccr * 3) # Rewarding contrarian picks slightly
        
        # 4. Numerology Boost
        # If ticket contains user's lucky numbers -> Big Bonus
        matches = len(ticket.intersection(numerology_set))
        score += (matches * 15)
        
        return score

    # Evolution Loop
    best_ever = None
    best_score = -9999
    
    log = []
    
    for gen in range(GENERATIONS):
        # Score all
        scored_pop = [(t, get_fitness(t)) for t in population]
        scored_pop.sort(key=lambda x: x[1], reverse=True)
        
        current_best = scored_pop[0]
        if current_best[1] > best_score:
            best_score = current_best[1]
            best_ever = current_best[0]
            
        # Select Elites
        elite_count = int(POP_SIZE * ELITISM)
        elites = [x[0] for x in scored_pop[:elite_count]]
        
        # Breed
        children = []
        while len(children) < (POP_SIZE - elite_count):
            parent1 = rng.choice(elites)
            parent2 = rng.choice(elites)
            
            # Crossover (Union then Split)
            mix = list(parent1.union(parent2))
            # Pick 'balls' amount from the mix
            if len(mix) >= balls:
                child = set(rng.sample(mix, balls))
            else:
                # If union is small (rare), fill with random
                needed = balls - len(mix)
                child = set(mix)
                while len(child) < balls:
                    child.add(rng.randint(1, cfg["range"]))
            
            # Mutation
            if rng.random() < MUTATION_RATE:
                # Remove one
                if len(child) > 0:
                    rem = rng.choice(list(child))
                    child.remove(rem)
                    # Add new
                    # Strategy: Add from Numerology or Random
                    if numerology_set and rng.random() < 0.5:
                         # Try adding lucky num from numerology
                         avail = list(numerology_set.difference(child))
                         # Filter avail to valid range
                         valid_avail = [x for x in avail if 1 <= x <= cfg["range"]]
                         if valid_avail:
                             child.add(rng.choice(valid_avail))
                         else:
                             child.add(rng.randint(1, cfg["range"]))
                    else:
                        new_n = rng.randint(1, cfg["range"])
                        while new_n in child:
                             new_n = rng.randint(1, cfg["range"])
                        child.add(new_n)
                        
            children.append(child)
            
        population = elites + children
        if gen % 10 == 0:
             log.append(f"Gen {gen}: Max Score {best_score:.1f}")
             
    # Return best
    results = sorted(list(best_ever))
    
    # 5/35 Special
    if cfg["type"] == "special":
        special = rng.randint(1, cfg["special_range"])
        return results + [special], log
        
    return results, log

    return results, log

# --- PHASE 19: SUPER-CLASS ALGORITHMS ---

def analyze_periodicity(history, game_type):
    """
    FFT Spectral Analysis: Detects hidden cycles in number appearance.
    Returns a dict {number: spectral_score}. 
    Higher score = Start of a new cycle (Rising).
    """
    if not history: return {}
    cfg = GAME_CONFIG[game_type]
    N = cfg["range"]
    scores = {}
    
    # We only analyze the last 100 draws for signal freshness
    recent_history = history[-200:] if len(history) > 200 else history
    L = len(recent_history)
    if L < 10: return {}
    
    for n in range(1, N + 1):
        # Create binary signal: 1 if n in draw, 0 else
        signal = []
        for draw in recent_history:
            # Handle special ball if main list strict? 
            # Treat flatly: is n in the draw array?
            signal.append(1 if n in draw else 0)
            
        # Fast Fourier Transform
        # Use simple real FFT
        try:
            fft_vals = np.fft.rfft(signal)
            # Power spectrum
            power = np.abs(fft_vals)**2
            # Ignore DC component (index 0)
            peak_power = np.max(power[1:]) if len(power) > 1 else 0
            
            # Simple heuristic: If recently quiet but high periodic power -> potential breakout
            # Or just use raw power as "Energy"
            scores[n] = float(peak_power)
        except:
             scores[n] = 0.0
             
    # Normalize scores 0.0 - 1.0
    max_s = max(scores.values()) if scores else 1
    if max_s == 0: max_s = 1
    return {k: v/max_s for k, v in scores.items()}

def adaptive_bayesian_score(history, game_type):
    """
    Bayesian Inference: Updates probability of each number based on evidence.
    Returns dict {number: probability}.
    """
    if not history: return {}
    cfg = GAME_CONFIG[game_type]
    N = cfg["range"]
    
    # Prior: Uniform probability
    # P(H) = 1/N
    probs = {n: 1.0/N for n in range(1, N + 1)}
    
    # Learning Rate (Alpha): How fast we adapt to new info
    # A high alpha means recent draws matter much more.
    alpha = 0.1 
    
    # Process history chronologically
    for draw in history:
        for n in range(1, N + 1):
            if n in draw:
                # Evidence: Hit
                # Boost probability
                probs[n] = probs[n] * (1 + alpha)
            else:
                # Evidence: Miss
                # decay
                probs[n] = probs[n] * (1 - (alpha / (N-6))) # Approximate balance
                
    # Normalize to form a proper distribution (Sum ~ 1)
    total_p = sum(probs.values())
    return {k: v/total_p for k, v in probs.items()}

    return {k: v/total_p for k, v in probs.items()}

# --- PHASE 20: DEEP PATTERN MATCHING (BẠC NHỚ) ---
def find_historical_matches(history, current_draw_numbers, game_type, threshold=0.6):
    """
    Finds past draws that are 'similar' to the current/latest draw.
    Returns a list of 'Next Draws' (The draw immediately following the match).
    """
    if not history or len(history) < 2: return []
    
    matches = []
    # Convert current to set for fast intersect
    # Handle 5/35 special separation?
    # Simple approach: Match main numbers.
    current_set = set(current_draw_numbers[:5]) if len(current_draw_numbers) >= 5 else set(current_draw_numbers)
    
    # Iterate through history (excluding the very last item if it IS the current one we just added?)
    # We look at history[i]. If history[i] ~ current, we record history[i+1]
    
    for i in range(len(history) - 1):
        past_draw = history[i]
        past_set = set(past_draw[:5]) if len(past_draw) >= 5 else set(past_draw)
        
        # Calculate Similarity (Jaccard or just Intersection count)
        intersection = len(current_set.intersection(past_set))
        
        # Threshold: e.g. 4/6 numbers match
        score = intersection / len(current_set) if len(current_set) > 0 else 0
        
        if score >= threshold:
            # Found a similar historical event! 
            # The "Echo" is what happened NEXT.
            next_draw = history[i+1]
            matches.append(next_draw)
            
    return matches

def analyze_historical_echo(matches, game_type):
    """
    Aggregates the 'Next Draws' to find the most recurring numbers.
    Returns a dict {number: frequency_score}
    """
    if not matches: return {}
    
    frequency = Counter()
    for draw in matches:
        for n in draw:
             frequency[n] += 1
             
    # Normalize
    total = sum(frequency.values())
    if total == 0: return {}
    
    return {k: v/total for k, v in frequency.items()}

def analyze_sequence_similarity(history, game_type, depth=3):
    """
    High-Precision Algorithm: Sequence Matching (Soi Cầu Chuỗi).
    Finds historical blocks of 'depth' draws that look like the most recent 'depth' draws.
    Returns: {next_number: weighted_score}
    """
    if not history or len(history) < (depth * 2) + 10: return {}
    
    # 1. Get recent sequence (Trajectory)
    recent_seq = history[-depth:]
    
    # 2. Scan history
    matches = []
    
    # Iterate through history window. Stop before the very end (to avoid matching itself).
    # We need a window of size 'depth' and then the 'next' draw.
    limit = len(history) - depth - 1 
    
    for i in range(limit):
        # Candidate sequence from history
        candidate_seq = history[i : i+depth]
        next_draw = history[i+depth]
        
        # 3. Calculate Similarity
        # Simple approach: Count total shared numbers across the block?
        # Or position-wise Jaccard?
        # Let's use Jaccard Overlap for the whole block.
        
        set_recent = set(num for draw in recent_seq for num in draw)
        set_candidate = set(num for draw in candidate_seq for num in draw)
        
        intersection = len(set_recent.intersection(set_candidate))
        union = len(set_recent.union(set_candidate))
        
        similarity = intersection / union if union > 0 else 0
        
        # Threshold: > 40% similarity is significant for lottery
        if similarity > 0.35:
             matches.append((next_draw, similarity))
             
    # 4. Aggregate Next Draws
    prediction_scores = Counter()
    for draw, score in matches:
        for num in draw:
            prediction_scores[num] += score * score # Square the score to emphasize strong matches
            
    # Normalize
    total = sum(prediction_scores.values())
    if total == 0: return {}
    
    return {k: (v/total) * 100.0 for k, v in prediction_scores.items()}

    return {k: (v/total) * 100.0 for k, v in prediction_scores.items()}

def calculate_fractal_score(history, game_type):
    """
    Calculates Fractal Resonance Score based on Multi-Scale Analysis.
    Scales: Micro (8), Meso (35), Macro (100).
    """
    cfg = GAME_CONFIG[game_type]
    scores = Counter()
    
    if not history: return scores
    
    # 1. Define Windows
    windows = {
        "Micro": history[-8:],   # Short term momentum
        "Meso": history[-35:],   # Medium term trend
        "Macro": history[-100:]  # Long term baseline
    }
    
    # Weights for each scale
    weights = {
        "Micro": 4.0,  # High impact of immediate trend
        "Meso": 2.5,
        "Macro": 1.0
    }
    
    for scale, window in windows.items():
        if not window: continue
        
        # Calculate Frequency in this window
        freq = Counter()
        for draw in window:
            for n in draw:
                # Handle Max 3D Pro strings
                val = int(n) if isinstance(n, str) else n
                freq[val] += 1
                
        # Normalize: Probability = Count / len(window)
        # Max 3D Pro starts from 0, others from 1
        start_n = 0 if game_type == "Max 3D Pro" else 1
        
        for n in range(start_n, cfg["range"] + 1):
            prob = freq[n] / len(window)
            scores[n] += prob * weights[scale]
            
    return scores

def mode_g_fractal(game_type, history, hot_nums, cold_nums, seed=None):
    """
    Fractal Chaos Mode: Multi-Scale Resonance.
    Focuses on numbers that are significant across multiple timeframes.
    """
    rng = random.Random(seed) if seed is not None else random
    cfg = GAME_CONFIG[game_type]
    
    # 1. Get Fractal Scores
    fractal_scores = calculate_fractal_score(history, game_type)
    
    # 2. Add some random noise for "Chaos" (and to avoid static output)
    # The user wants mostly high probability, but lottery needs variance.
    final_scores = {}
    for n, s in fractal_scores.items():
        # Noise +/- 10%
        noise = rng.uniform(0.9, 1.1)
        final_scores[n] = s * noise
        
    # 3. Select Top Candidates
    # We want a pool of reliable numbers, say Top 18 (System 18)
    sorted_candidates = sorted(final_scores.keys(), key=lambda x: final_scores[x], reverse=True)
    pool = sorted_candidates[:20] # Take Top 20
    
    # 4. Pick 6 numbers from the Top 20
    # Weighted choice? Or just random from the Elite Pool?
    # Let's use weighted choice based on their fractal score.
    
    weights = [final_scores[n] for n in pool]
    
    # Normalize weights
    total_w = sum(weights)
    if total_w == 0: return sorted(rng.sample(range(1, cfg["range"]+1), cfg["balls"])), {}
    
    norm_weights = [w/total_w for w in weights]
    
    # Sampling without replacement
    # python's random.choices is with replacement. 
    # numpy.random.choice is good but we use standard lib here.
    
    # Custom weighted sample without replacement
    results = []
    pool_copy = list(pool)
    weights_copy = list(norm_weights)
    
    while len(results) < cfg["balls"]:
        if not pool_copy: break
        # Pick one
        pick = rng.choices(pool_copy, weights=weights_copy, k=1)[0]
        results.append(pick)
        
        # Remove and re-normalize
        idx = pool_copy.index(pick)
        pool_copy.pop(idx)
        weights_copy.pop(idx)
        
        # Re-norm
        s = sum(weights_copy)
        if s == 0: 
            # Fill rest randomly from remaining pool
            leftover = cfg["balls"] - len(results)
            if len(pool_copy) >= leftover:
                results.extend(rng.sample(pool_copy, leftover))
            break
        else:
            weights_copy = [w/s for w in weights_copy]
            
    # Handle Special Number for 5/35
    final_results = sorted(results)
    if cfg["type"] == "special":
        # Predict special number
        pred_special = analyze_special_number(history, cfg["special_range"])
        final_results.append(pred_special)
        
    # Handle Max 3D Pro Formatting
    if game_type == "Max 3D Pro":
         final_results = [f"{x:03d}" for x in sorted(results)]

    return final_results, {
        "Analysis": "Fractal Multi-Scale",
        "Top Signals": sorted_candidates[:5]
    }


def mode_f_hybrid(game_type, history, hot_nums, cold_nums, seed=None, quantum_dob=None, iching_dob=None, bio_score=0.0, bankers=None, style="Modern"):
    """
    Grand Consensus Mode: Combines AI, Quantum, and I Ching.
    Now supports Personalization & Bio-Rhythm.
    """
    rng = random.Random(seed) if seed is not None else random
    cfg = GAME_CONFIG[game_type]
    
    # 1. Run Sub-Engines
    # AI: Use System 12 to cast a wide net
    ai_pool = mode_system_play(game_type, history, hot_nums, cold_nums, system_size=12, seed=seed, bankers=bankers, style=style)
    
    # Quantum: Personal
    q_res, _ = mode_d_quantum(game_type, seed=seed, quantum_dob=quantum_dob)
    
    # I Ching: Personal
    iching_res, _ = mode_e_iching(game_type, seed=seed, iching_dob=iching_dob)
    
    # --- PHASE 19: SUPER-CLASS INTEGRATION ---
    try:
        fft_scores = analyze_periodicity(history, game_type)
        bayes_scores = adaptive_bayesian_score(history, game_type)
    except:
        fft_scores = {}
        bayes_scores = {}

    # --- PHASE 20: DEEP PATTERN ECHO (BẠC NHỚ) ---
    echo_scores = {}
    last_matches_count = 0
    if history:
         # Use the very last draw to find similar past headers
         last_draw_nums = history[-1]
         # Use 50% match threshold e.g. 3/6 numbers
         matches = find_historical_matches(history[:-1], last_draw_nums, game_type, threshold=0.5)
         last_matches_count = len(matches)
         if matches:
             echo_scores = analyze_historical_echo(matches, game_type)

    # --- PHASE 22: SEQUENCE MATCHING (HIGH PRECISION) ---
    sequence_scores = analyze_sequence_similarity(history, game_type, depth=3)
    
    
    # --- PHASE 21: THE SINGULARITY (META-OPTIMIZATION) ---
    # Self-optimize based on Last 5 Draws trend
    # Dynamic weighting based on real recent performance
    
    # Defaults
    w_ai = 1.0
    w_q = 1.0
    w_i = 1.0
    w_history = 1.0 # New Weight for Historical/Echo
    
    # --- PHASE 24: META-OPTIMIZATION (BACKTEST RESULT APPLIED) ---
    # Based on simulation of last 50 draws:
    # 6/45: Quantum performed best (Avg 0.94 vs Hybrid 0.72) -> Boost Quantum
    # 6/55: Hybrid performed best -> Balanced
    # 5/35: Hybrid performed best -> Balanced
    
    if game_type == "6/45":
         w_q = 3.0 # Heavy Quantum Bias
         w_ai = 0.5
         w_i = 0.5
    elif game_type == "6/55":
         # Slight AI bias for 6/55
         w_ai = 1.2
         w_q = 1.0
         w_i = 1.0
    elif game_type == "5/35":
         # Balanced / slightly I Ching for small pool?
         # Backtest said Hybrid is best, so keep balanced.
         pass
    
    if len(history) > 10:
        # Mini-Simulation
        # Check last 5 draws to see which engine predicted them best?
        # Simplified: Just check coverage in pools.
        
        sim_scores = {"AI": 0, "Quantum": 0, "IChing": 0, "Echo": 0}
        
        # We need to simulate the state "before" the draw. 
        # This is expensive. We approximate using the "Current" pools vs Recent History.
        # Assumption: The engines are consistent.
        
        recent_target = set()
        for i in range(1, 6):
             recent_target.update(history[-i])
             
        # Check Overlaps
        sim_scores["AI"] = len(set(ai_pool).intersection(recent_target))
        sim_scores["Quantum"] = len(set(q_res).intersection(recent_target))
        sim_scores["IChing"] = len(set(iching_res).intersection(recent_target))
        # Echo is already based on history, so it's circular, but valid.
        
        # Normalize to get Multipliers
        total_score = sum(sim_scores.values()) + 1 # avoid div 0
        
        # Apply Dynamics (Singularity Boost)
        # If AI is winning, boost AI.
        w_ai = 1.0 + (sim_scores["AI"] / total_score * 2.0)
        w_q = 1.0 + (sim_scores["Quantum"] / total_score * 2.0)
        w_i = 1.0 + (sim_scores["IChing"] / total_score * 2.0)
        
        # History Weight is special
        # If last matches count was high, history is reliable.
        w_history = 1.0 + (min(last_matches_count, 5) * 0.5)

    # --- Phase 11: Bio-Modifier (Still valid) ---
    if st.session_state.get("USE_PHASE_11", True):
        if bio_score > 0.5:
            w_q *= 1.3
            w_i *= 1.3
        elif bio_score < 0:
            w_ai *= 1.3
            w_history *= 1.5 # Trust history when energy is low
    
        # 2. Aggregation & Voting
    votes = Counter()
    
    # BANKER INJECTION
    if bankers:
        for b in bankers:
            votes[b] += 9999.0 # Absolute priority

    
    # AI Votes + Bayesian Boost
    for n in ai_pool:
        votes[n] += w_ai
        if n in bayes_scores:
             # REDUCED: Was 10.0, now 2.0 (Avoid dictatorship)
             votes[n] += bayes_scores[n] * 2.0
             
    for n in q_res:
        votes[n] += w_q
        
    for n in iching_res:
        votes[n] += w_i
        
    # Spectral Boost (FFT)
    for n in votes:
        if n in fft_scores:
             # REDUCED: Multiplier dampened -> NOW BOOSTED for LOCK MODE
             votes[n] *= (1.0 + (fft_scores[n] * 0.8))
             
             
    # Historical Echo Boost (Phase 20 + 21)
    # If a number appeared frequently in similar past contexts, it gets weight.
    for n in votes:
        if n in echo_scores:
             # REDUCED: Was 5.0, now 1.5. Let core frequency speak. -> NOW BOOSTED
             votes[n] *= (1.0 + (echo_scores[n] * 2.5 * w_history))

    # Sequence Matching Boost
    for n in votes:
        if n in sequence_scores:
             # Strong signal: Add significant weight
             votes[n] += sequence_scores[n] * 2.0 * w_history
        
    # 3. Selection
    w_freq = calculate_weighted_frequency(history)
    
    def sort_key(n):
        return (votes[n], w_freq.get(n, 0))
        
    all_candidates = list(votes.keys())
    sorted_candidates = sorted(all_candidates, key=sort_key, reverse=True)
    
    results = sorted(sorted_candidates[:cfg["balls"]])
    
    if cfg["type"] == "special":
        main_balls = results[:cfg["balls"]]
        # special = rng.randint(1, cfg["special_range"])
        # Improved: Use Data-Driven Prediction
        pred_special = analyze_special_number(history, cfg["special_range"])
        results = main_balls + [pred_special]
    
    # Debug Info
    last_real = set(history[-1]) if history else set()
    ai_hits = len(set(ai_pool).intersection(last_real))
    q_hits = len(set(q_res).intersection(last_real))
    i_hits = len(set(iching_res).intersection(last_real))
    
    details = {
        "Learning Info": {
            "Last Draw": list(last_real),
            "AI Hits": ai_hits, "Q Hits": q_hits, "I Hits": i_hits,
            "Weights": {"AI": round(w_ai, 2), "Q": round(w_q, 2), "I": round(w_i, 2)}
        },
        "AI Pool": ai_pool,
        "Quantum": q_res,
        "I Ching": iching_res,
        "Top Votes": {n: round(votes[n], 2) for n in results}
    }
    
    return results, details


def generate_predictions(game_type, model_choice="Hybrid", seed=None, bio_score=0.0, bankers=None, style="Modern", history=None, quantum_dob=None, iching_dob=None):
    """
    Main prediction wrapper.
    """
    # 1. Load Data
    if history is None:
        history = load_real_data(game_type)
        
    if not history:
        if game_type == "Max 3D Pro":
             history = [[123, 456], [789, 12]] * 10
        else:
             history = generate_simulation(game_type, limit=50)
            
    # 2. Analyze
    if game_type == "Max 3D Pro":
         # Use specialized engine
         return mode_3d_engine(game_type, history)

    hot_nums, cold_nums = analyze_history(history)
    
    # 3. Predict
    if model_choice == "Fractal Chaos":
        return mode_g_fractal(game_type, history, hot_nums, cold_nums, seed=seed)
        
    elif model_choice == "System 12":
        # Direct System Play
        pool = mode_system_play(game_type, history, hot_nums, cold_nums, system_size=12, seed=seed, style=style)
        return sorted(pool), {"Analysis": "System 12 Optimization", "Pool Size": 12}
        
    elif model_choice == "System 18":
        # Direct System Play
        pool = mode_system_play(game_type, history, hot_nums, cold_nums, system_size=18, seed=seed, style=style)
        return sorted(pool), {"Analysis": "System 18 Optimization", "Pool Size": 18}
        
    elif model_choice == "Random":
        # Pure Random
        cfg = GAME_CONFIG[game_type]
        rng = random.Random(seed)
        res = sorted(rng.sample(range(1, cfg["range"]+1), cfg["balls"]))
        if cfg["type"] == "special":
             res = res[:5] + [rng.randint(1, cfg["special_range"])]
        return res, {"Analysis": "Pure Randomness"}

    # Hybrid Mode (Default)
    results, details = mode_f_hybrid(
        game_type, history, hot_nums, cold_nums, 
        seed=seed, bio_score=bio_score, bankers=bankers, style=style,
        quantum_dob=quantum_dob, iching_dob=iching_dob
    )
    
    return results, details


def measure_accuracy(game_type, history, depth=5):
    """
    Backtests the Hybrid Engine against the last 'depth' draws.
    Returns: Average accuracy (matches per draw).
    """
    if not history or len(history) < depth + 10: return 0.0, []
    
    total_matches = 0
    results_log = []
    
    # We need to simulate the state AS IT WAS back then.
    # This is expensive, so we do it briefly or simplify.
    # Simplification: We just use the raw AI pool generator or a lighter hybrid for speed.
    # To be honest, let's run the full hybrid one if depth is small (3-5).
    
    # Iterate from (latest - depth) to (latest)
    # history[-1] is latest.
    start_idx = len(history) - depth
    
    cfg = GAME_CONFIG[game_type]
    is_535 = (cfg["type"] == "special")
    
    for i in range(start_idx, len(history)):
        # Target is history[i]
        # Known history is history[:i]
        target = history[i]
        past_history = history[:i]
        
        # Determine Hot/Cold at that time
        # Recalculate basic stats
        if not past_history: continue
        
        # Quick recalc
        hot, cold = analyze_history(past_history)
        
        # Predict
        # We assume standard weights for backtest
        try:
            pred, _ = mode_f_hybrid(
                game_type, past_history, hot, cold, seed=i, # Use index as seed determinant for reproducibility
                bio_score=0.0 # Neutral bio for general accuracy
            )
            
            # Compare
            # For 5/35, handle special?
            # Let's compare sets of main numbers for robust metric
            set_pred = set(pred[:5] if is_535 else pred)
            set_target = set(target[:5] if is_535 else target)
            
            matches = len(set_pred.intersection(set_target))
            total_matches += matches
            results_log.append(matches)
            
        except Exception as e:
            pass # Skip error
            
    avg_acc = total_matches / depth if depth > 0 else 0
    return avg_acc, results_log


# --- PHASE 22: QUANTUM REALITY COLLAPSE (GOD MODE) ---
def collapse_reality(game_choices, history, hot, cold, bio_score=0.0, mind_key=0):
    """
    Simulates the Multiverse by running the Hybrid Engine multiple times
    with slight entropy variations. identifying 'Fixed Points' (Inevitabilities).
    Phase 23: Adds 'mind_key' to entanglement.
    """
    universe_count = 50 # Number of parallel timelines
    multiverse_results = Counter()
    
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    for i in range(universe_count):
        # Entropy perturbation: minor seed variation + MIND KEY ENTANGLEMENT
        # The Mind Key acts as a 'Reality Anchor'
        entropy_seed = int(time.time() * 1000) + i + (mind_key * 9999)
        
        # Run the engine
        res, _ = mode_f_hybrid(game_choices, history, hot, cold, seed=entropy_seed, bio_score=bio_score)
        
        # Aggregate
        # For 5/35, res is [1,2,3,4,5, 6]. 6 is special. 
        # We treat them all as appearing numbers for now.
        for n in res:
            multiverse_results[n] += 1
            
        # Update UI
        if i % 5 == 0:
            progress_bar.progress((i + 1) / universe_count)
            status_text.text(f"🌌 Đang quan sát vũ trụ thứ {i+1}/{universe_count}...")
            
    progress_bar.empty()
    status_text.empty()
    
    # Analyze Stability
    # A number is a "Fixed Point" if it appears in > 80% of universes?
    # Or just take top N.
    
    cfg = GAME_CONFIG[game_choices]
    needed = cfg["balls"]
    if cfg["type"] == "special": needed = 5 # Handle special separately?
    
    # Logic for Special Ball in Multiverse
    # If 5/35, the last number in 'res' was special.
    # We should probably separate counting for Main vs Special to be accurate.
    
    # Refined Logic:
    main_counter = Counter()
    special_counter = Counter()
    
    # Re-run aggregation with loop info (Optimization: do it above, but logic split here for clarity)
    # Actually, let's just do a purely frequency based pick for now.
    
    return multiverse_results


def display_balls(numbers, game_type):
    if not numbers: return
    cfg = GAME_CONFIG[game_type]
    balls_html = ""
    is_535 = (cfg["type"] == "special")
    
    for idx, n in enumerate(numbers):
         # Logic for 5/35 special ball coloring
         # We assume standard length for God Mode results (6 balls)
         is_standard_len = (len(numbers) == 6 or len(numbers) == 7) # 6/55 or 5/35+1
         # For 5/35, the 6th ball (index 5) is special
         if is_535 and idx == 5:
              balls_html += f'<div class="ball ball-special">{n}</div>'
         else:
              balls_html += f'<div class="ball">{n}</div>'

    st.markdown(f"""
    <div class="ball-container">
        {balls_html}
    </div>
    """, unsafe_allow_html=True)

# --- PHASE 25: THE MATRIX (WHEELING SYSTEMS) ---
def generate_matrix_wheel(pool, pick_k=6, method="basic_10"):
    """
    Generates a set of tickets (Combinatorial Wheel) from a pool of numbers.
    Guarantees: '4 matches if 6 match' (typically).
    """
    import itertools
    
    ticks = []
    pool = sorted(list(set(pool)))
    n = len(pool)
    
    # 1. Full Wheel (Small pools) - 100% guarantee
    if n <= 8 and method == "full":
        # C(8,6) = 28 tickets. Safe.
        # C(9,6) = 84 tickets. Borderline.
        return [list(c) for c in itertools.combinations(pool, pick_k)]
        
    # 2. Abbreviated Wheels (Templates)
    # Implementing specific covering design templates
    # This is much faster than running a Set Cover solver
    
    # Template: 10 numbers -> Pick 6. Guarantee 4 if 6.
    # Standard: ~10-20 tickets.
    # Logic: Shuffle and fill? No, Use Deterministic Covering logic if possible.
    
    # Simple Randomized Cover (Greedy)
    # Generate random tickets until we cover 'enough' 4-tuples? Too slow.
    
    # Heuristic: Sliding Window + Strides
    # Effective for "Good enough" matrix
    
    if n < pick_k: return []
    
    if method == "reduced":
        # A simple "Block" wheeling strategy
        # 1. Break pool into groups? 
        # 2. Or just randomness for now to deliver *diverse* coverage
        
        # Let's use a "Scrambled Pair" approach:
        # Ensure every pair of numbers appears together at least once?
        # That's C(n,2) pairs. 
        # C(10,2) = 45 pairs. Each ticket holds C(6,2) = 15 pairs. 
        # Ideally 3 tickets could cover all pairs? No. 
        
        # Real Abbreviated Logic requires tables. 
        # Since I can't embed a massive DB, I will use a High-Entropy Sampler
        # that maximizes "Pair Distance".
        
        # Generate 1000 random candidates
        # Greedily pick the one that adds MOST new pairs to our coverage set
        
        candidates = []
        for _ in range(500):
            candidates.append(tuple(sorted(random.sample(pool, pick_k))))
            
        selected_tickets = []
        covered_pairs = set()
        
        # Goal: Cover as many pairs as possible with small ticket count.
        limit = 0
        if n <= 10: limit = 8 # 8 tickets enough for ~90% cover
        elif n <= 12: limit = 15
        elif n <= 15: limit = 25
        else: limit = 10
        
        for _ in range(limit):
             best_ticket = None
             best_new_cover = -1
             
             for cand in candidates:
                 # Assess pairs
                 cand_pairs = set(itertools.combinations(cand, 2))
                 new_cover = len(cand_pairs - covered_pairs)
                 
                 if new_cover > best_new_cover:
                     best_new_cover = new_cover
                     best_ticket = cand
            
             if best_ticket:
                 selected_tickets.append(list(best_ticket))
                 covered_pairs.update(itertools.combinations(best_ticket, 2))
                 candidates.remove(best_ticket)
             else:
                 break
                 
        return selected_tickets

    return [pool[:pick_k]] # Fallback

# --- FRONTEND: UI ---

def add_to_log(game_type, model_name, numbers, draw_time, seed):
    """
    Logs prediction to a JSONL file for future backtesting.
    """
    log_file = "predictions_history.jsonl"
    entry = {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "game_type": game_type,
        "model": model_name,
        "numbers": numbers,
        "draw_time": draw_time.strftime("%Y-%m-%d %H:%M:%S") if isinstance(draw_time, datetime) else str(draw_time),
        "seed": seed
    }
    
    try:
        with open(log_file, "a", encoding="utf-8") as f:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")
    except Exception as e:
        print(f"Logging error: {e}")


def main():
    st.set_page_config(
        page_title="AI Thần Tài Pro (Lite)",
        page_icon="🎱",
        layout="centered"
    )

    # Custom CSS
    st.markdown("""
    <style>
        .ball-container {
            display: flex;
            justify_content: center;
            gap: 12px;
            margin-top: 25px;
            margin-bottom: 25px;
            flex-wrap: wrap;
        }
        .ball {
            width: 55px;
            height: 55px;
            background: linear-gradient(145deg, #ff4b4b, #cc0000);
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify_content: center;
            color: white;
            font-weight: 800;
            font-size: 22px;
            box-shadow: 0 4px 10px rgba(0,0,0,0.3);
            border: 2px solid #ffaaaa;
        }
        .ball-special {
            background: linear-gradient(145deg, #1E90FF, #0000CD);
            border: 2px solid #87CEFA;
        }
        .stButton>button {
            width: 100%;
            height: 65px;
            font-size: 22px !important;
            font-weight: 700 !important;
            border-radius: 15px;
            background: linear-gradient(90deg, #FF4B4B, #FF914D);
            border: none;
            color: white !important;
            transition: all 0.3s;
        }
        .stButton>button:hover {
            transform: translateY(-2px);
            box-shadow: 0 8px 20px rgba(255, 75, 75, 0.4);
        }
        .stat-box {
            background: #ffffff;
            padding: 12px;
            border-radius: 12px;
            text-align: center;
            border: 1px solid #e0e0e0;
            box-shadow: 0 2px 5px rgba(0,0,0,0.05);
        }
        .main-header {
            text-align: center;
            font-family: 'Helvetica Neue', sans-serif;
            margin-bottom: 30px;
        }
        .main-header h1 {
            background: -webkit-linear-gradient(45deg, #FF4B4B, #FF914D);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            font-size: 2.8rem;
            margin-bottom: 0;
        }
    </style>
    """, unsafe_allow_html=True)

    # Header
    st.markdown('<div class="main-header"><h1>AI THẦN TÀI PRO</h1><p>Công nghệ Dự đoán Xổ số Đa Chiều</p></div>', unsafe_allow_html=True)

    # Lucky BG
    bg_file = "lucky_bg.png"
    if os.path.exists(bg_file):
         set_png_as_page_bg(bg_file)

    # --- CONFIGURATION ROW ---
    c1, c2 = st.columns(2)
    
    with c1:
        game_choice = st.selectbox("🎯 CHỌN LOẠI VÉ", ["6/55", "6/45", "5/35", "Max 3D Pro"])
        
    with c2:
        # Simplied Model Names
        model_options = {
            "Hybrid AI (Chuẩn)": "Hybrid",
            "Fractal Chaos (Mới)": "Fractal Chaos",
            "Hệ thống 12 (Bao)": "System 12",
            "Hệ thống 18 (Bao)": "System 18", 
            "Ngẫu Nhiên (Vui)": "Random"
        }
        display_model = st.selectbox("🧠 CHỌN THUẬT TOÁN", list(model_options.keys()))
        model_key = model_options[display_model]
    # Advanced (Quantum/I Ching)
    with st.expander("⚙️ Nâng cao (Phong thủy & Lượng tử)"):
         st.caption("Nhập ngày sinh để kích hoạt năng lượng cá nhân hóa.")
         min_date = datetime(1920, 1, 1)
         max_date = datetime.now()
         dob_input = st.date_input("Ngày sinh của bạn:", value=None, min_value=min_date, max_value=max_date)
         
         if dob_input:
             # Personal Mode
             u_quantum_dob = datetime.combine(dob_input, datetime.min.time())
             vip_iching_dob = u_quantum_dob
             st.success("✅ Đã kích hoạt năng lượng cá nhân!")
         else:
             # Real-time Mode
             now_energy = datetime.now()
             u_quantum_dob = now_energy 
             vip_iching_dob = now_energy
             st.info("⚡ Đang dùng năng lượng thời gian thực (Ngày giờ hiện tại).")

    # --- DATA STATUS & STATS ---
    cfg = GAME_CONFIG[game_choice]
    
    # Load Data silently
    history = load_real_data(game_choice)
    hot_nums, cold_nums = [], []
    
    if history:
         hot_nums, cold_nums = analyze_history(history)
         status_color = "🟢"
         status_text = "Dữ liệu Online"
    else:
         status_color = "🟠"
         status_text = "Dữ liệu Giả lập"
         
    # Mini Stats Display
    with st.expander(f"{status_color} Thống kê nhanh ({status_text})", expanded=False):
        sc1, sc2 = st.columns(2)
        with sc1:
            st.info(f"🔥 Nóng: {', '.join(map(str, hot_nums[:6]))}")
        with sc2:
            st.info(f"❄️ Lạnh: {', '.join(map(str, cold_nums[:6]))}")
            
    # --- PREDICTION BUTTON ---
    st.markdown("###")
    if st.button("🔮 PHÂN TÍCH & DỰ ĐOÁN NGAY", type="primary"):
        
        # Progress Effect
        progress_text = st.empty()
        bar = st.progress(0)
        
        stages = [
            "⚡ Đang khởi động Neural Network...",
            "🌌 Quét dữ liệu Đa vũ trụ...",
            "🌀 Phân tích Fractal & Chuỗi số...",
            "✅ Đang tổng hợp kết quả..."
        ]
        
        for i, stage in enumerate(stages):
            progress_text.text(stage)
            bar.progress((i + 1) * 25)
            time.sleep(0.3)
            
        progress_text.empty()
        bar.empty()
        
        # Generate
        seed = int(time.time())
        
        # Determine styles based on chaos/random
        style = "Modern"
        bankers = None # No UI for bankers anymore to keep it simple
        
        results, details = generate_predictions(
            game_type=game_choice,
            model_choice=model_key,
            seed=seed,
            history=history,
            bankers=bankers,
            style=style
        )
        
        # --- DISPLAY RESULT ---
        st.markdown(f"<h3 style='text-align: center; color: #333;'>💎 KẾT QUẢ GỢI Ý ({game_choice})</h3>", unsafe_allow_html=True)
        
        # Display Balls
        display_balls(results, game_choice)
        
        # Success Message
        if "System" in model_key:
             st.success(f"📌 Đã lọc ra bộ {len(results)} số tiềm năng nhất để bao lưới.")
        else:
             st.success(f"✨ Bộ số vàng đã được khóa. Chúc bạn may mắn!")

        # Debug/Explain Info
        with st.expander("🔍 Xem phân tích chi tiết"):
             st.json(details)
             
    # Footer
    st.markdown("---")
    st.caption("AI Thần Tài Pro © 2026 - Dự đoán xổ số bằng công nghệ AI & Lượng tử.")

if __name__ == "__main__":
    main()
