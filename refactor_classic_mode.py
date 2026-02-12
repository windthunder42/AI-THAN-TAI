
import os
import re

app_path = '/Users/duythanhx6/Desktop/AntiGravity/Chọn số/app.py'

# 1. NEW generate_predictions with 'style' param and logic
new_gen_func = r'''
def generate_predictions(game_type, history, hot_nums, cold_nums, pool_size=6, seed=None, bankers=None, style="Modern"):
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
'''

# 2. Update mode_f_hybrid signature and logic to pass style down
new_mode_hybrid_sig = 'def mode_f_hybrid(game_type, history, hot_nums, cold_nums, seed=None, quantum_dob=None, iching_dob=None, bio_score=0.0, bankers=None, style="Modern"):'

# 3. Update main logic to add UI
# UI Chunk to inject: "Prediction Style"
new_classic_ui = r'''
        # --- PREDICTION STYLE UI ---
        pred_style = st.radio("Phong cách dự đoán:", ["🔮 Hiện đại (Modern)", "🎲 Cổ điển (Classic Chaos)"], horizontal=True, help="Hiện đại = Chuẩn xác theo thống kê. Cổ điển = Ngẫu nhiên, phiêu linh.")
        style_val = "Modern" if "Hiện đại" in pred_style else "Classic"
'''

# EXECUTION
try:
    with open(app_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # 1. Replace generate_predictions (Use regex to be safe with multiline)
    # The previous regex worked well.
    content = re.sub(
        r'def generate_predictions\(.*?\):[\s\S]*?return final_result\n',
        new_gen_func,
        content,
        count=1
    )
    
    # 2. Update mode_system_play signature and call
    # Update signature
    content = content.replace(
        'def mode_system_play(game_type, history, hot_nums, cold_nums, system_size=10, seed=None, bankers=None):',
        'def mode_system_play(game_type, history, hot_nums, cold_nums, system_size=10, seed=None, bankers=None, style="Modern"):'
    )
    # Update call inside mode_system_play
    content = content.replace(
        'return generate_predictions(game_type, history, hot_nums, cold_nums, pool_size=system_size, seed=seed, bankers=bankers)',
        'return generate_predictions(game_type, history, hot_nums, cold_nums, pool_size=system_size, seed=seed, bankers=bankers, style=style)'
    )
    
    # 3. Update mode_f_hybrid signature
    content = content.replace(
        'def mode_f_hybrid(game_type, history, hot_nums, cold_nums, seed=None, quantum_dob=None, iching_dob=None, bio_score=0.0, bankers=None):',
        new_mode_hybrid_sig
    )
    # Update mode_system_play call inside mode_f_hybrid
    content = content.replace(
        'ai_pool = mode_system_play(game_type, history, hot_nums, cold_nums, system_size=12, seed=seed, bankers=bankers)',
        'ai_pool = mode_system_play(game_type, history, hot_nums, cold_nums, system_size=12, seed=seed, bankers=bankers, style=style)'
    )
    
    # 4. Inject UI in Main
    # Targeted location: After user_bankers success message, before bio_score.
    # Look for: st.success(f"🎯 Đã khóa mục tiêu: {user_bankers}")
    # Then append the UI code.
    
    anchor = 'st.success(f"🎯 Đã khóa mục tiêu: {user_bankers}")'
    
    if anchor in content:
        content = content.replace(anchor, anchor + "\n" + new_classic_ui)
    else:
        # Fallback if user didn't select bankers?
        # The logic block 'if user_bankers:' is there.
        # But wait, if validation failed, replacing anchor inside the if might be hidden if user selects nothing.
        # We need to place it OUTSIDE the `if user_bankers:` block.
        # It should be before `calculate_biorhythm`.
        
        anchor_2 = '# Calculate Bio-score silently'
        content = content.replace(anchor_2, new_classic_ui + "\n        " + anchor_2)

    # 5. Update call to mode_f_hybrid in Main
    # It passes specific args. We need to add `style=style_val`.
    # Find `bankers=user_bankers` and append `style=style_val`
    content = content.replace(
        'bankers=user_bankers',
        'bankers=user_bankers,\n                style=style_val'
    )

    with open(app_path, 'w', encoding='utf-8') as f:
        f.write(content)
        
    print("Success")

except Exception as e:
    print(f"Error: {e}")
