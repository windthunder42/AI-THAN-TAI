
import json
import requests
import random
import time
from datetime import datetime
from collections import Counter
import math
import hashlib

# 1. Fetch 5/35 Result
def fetch_535_history():
    # Use Vietlott-data github (may not be real-time for today)
    # If today is Feb 5th, github might only have up to Feb 4th.
    # We will try to fetch, if not latest, use known recent result.
    url = "https://raw.githubusercontent.com/vietvudanh/vietlott-data/main/data/power535.jsonl"
    resp = requests.get(url)
    data = []
    for line in resp.text.strip().split('\n'):
        if not line: continue
        try:
             j = json.loads(line)
             res = j.get("result", [])
             date_str = j.get("date", "")
             if len(res) >= 6:
                 main = sorted(res[:5])
                 special = res[5]
                 data.append({
                     "date": date_str,
                     "main": main,
                     "special": special,
                     "full": main + [special]
                 })
        except: pass
    return data

# 2. Check Predictions Log
def check_log(history):
    latest_draw = history[-1]
    print(f"🏁 KẾT QUẢ KỲ QUAY GẦN NHẤT ({latest_draw['date']}):")
    print(f"   🔴 Bóng chính: {latest_draw['main']}")
    print(f"   🔵 Bóng đặc biệt: {latest_draw['special']}")
    print("-" * 40)
    
    print("📜 KIỂM TRA LỊCH SỬ DỰ ĐOÁN (20 MỚI NHẤT):")
    
    log_path = "predictions_history.jsonl"
    if not os.path.exists(log_path):
        print("   ❌ Không tìm thấy file nhật ký dự đoán.")
        return

    found = False
    with open(log_path, 'r', encoding='utf-8') as f:
        # Read reverse
        lines = f.readlines()
        
        count = 0
        for line in reversed(lines):
            try:
                if count >= 30: break
                rec = json.loads(line)
                if rec.get("game_type") != "5/35": continue
                count += 1
                
                print(f"\n🕒 Thời gian tạo: {rec['timestamp']}")
                print(f"   Phương pháp: {rec['model']}")
                pred = rec['numbers']
                print(f"   🔢 Bộ số vé: {pred}")
                
                # Check if it has 'bankers' key? (JSON might vary)
                # Compare
                if len(pred) >= 5:
                     # 5/35 prediction might be 6 numbers (5+1) or just 6 main numbers?
                     # Let's assume first 5 are main or first N-1 are main.
                     
                     # If length 6: 
                     # usually [m1, m2, m3, m4, m5, s1]
                     pred_main = set(pred[:-1])
                     pred_spec = pred[-1]
                     
                     target_main = set(latest_draw['main'])
                     target_spec = latest_draw['special']
                     
                     matches = pred_main.intersection(target_main)
                     spec_match = (pred_spec == target_spec)
                     
                     match_msg = f"{len(matches)} số chính"
                     if spec_match: match_msg += " + 1 số đặc biệt"
                     
                     print(f"   👉 KẾT QUẢ: Trúng {match_msg} {list(matches) if matches else ''}")
                     
                found = True
                
            except Exception as e:
                pass

if __name__ == "__main__":
    try:
        import os
        h = fetch_535_history()
        if h:
            check_log(h)
        else:
            print("Lỗi tải dữ liệu.")
    except Exception as e:
        print(f"Lỗi script: {e}")
