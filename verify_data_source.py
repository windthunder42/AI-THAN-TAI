import requests
import json
from datetime import datetime

GAME_CONFIG = {
    "6/55": {"data_url": "https://raw.githubusercontent.com/vietvudanh/vietlott-data/main/data/power655.jsonl"},
    "6/45": {"data_url": "https://raw.githubusercontent.com/vietvudanh/vietlott-data/main/data/power645.jsonl"},
    "5/35": {"data_url": "https://raw.githubusercontent.com/vietvudanh/vietlott-data/main/data/power535.jsonl"}
}

def check_freshness():
    print("--- Checking Data Source Freshness ---")
    headers = {'User-Agent': 'Mozilla/5.0'}
    
    for game, cfg in GAME_CONFIG.items():
        url = cfg["data_url"]
        try:
            print(f"\nChecking {game}...")
            r = requests.get(url, headers=headers, timeout=10)
            if r.status_code != 200:
                print(f"❌ Failed to fetch {game}: {r.status_code}")
                continue
                
            lines = r.text.strip().split('\n')
            if not lines:
                print(f"❌ Empty data for {game}")
                continue
                
            last_line = lines[-1]
            data = json.loads(last_line)
            date_str = data.get("date")
            result = data.get("result")
            
            print(f"✅ {game} Latest Entry:")
            print(f"   Date: {date_str}")
            print(f"   Result: {result}")
            
            # Simple check against today
            try:
                # date format in json usually YYYY-MM-DD or DD/MM/YYYY
                # Let's inspect
                pass
            except:
                pass
                
        except Exception as e:
            print(f"❌ Error checking {game}: {e}")

if __name__ == "__main__":
    check_freshness()
