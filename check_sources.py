import requests
from datetime import datetime

def check_github_freshness():
    urls = {
        "6/55": "https://raw.githubusercontent.com/vietvudanh/vietlott-data/main/data/power655.jsonl",
        "6/45": "https://raw.githubusercontent.com/vietvudanh/vietlott-data/main/data/mega645.jsonl"
    }
    
    for game, url in urls.items():
        try:
            # Range header to just get last part? JSONL appends to end usually.
            # But raw github might not support range on dynamic raw? It supports but let's just get head.
            # Actually, let's get the last 1000 bytes.
            headers = {"Range": "bytes=-1000"} 
            # Note: Github raw might ignore range.
            r = requests.get(url, timeout=5)
            
            print(f"--- {game} ---")
            if r.status_code == 200 or r.status_code == 206:
                lines = r.text.strip().split('\n')
                last_line = lines[-1]
                print(f"Last Line: {last_line}")
            else:
                print(f"Status: {r.status_code}")
        except Exception as e:
            print(f"Error {game}: {e}")

def check_xskt_max3dpro():
    url = "https://xskt.com.vn/xs-max-3d-pro"
    # Or 30 days
    url_30 = "https://xskt.com.vn/xs-max-3d-pro/30-ngay"
    
    try:
        r = requests.get(url_30, headers={'User-Agent': 'Mozilla/5.0'}, timeout=5)
        print(f"--- Max 3D Pro (xskt) ---")
        if r.status_code == 200:
            print("Success fetching 30 days Max 3D Pro")
            # Check content specific
            if "Max 3D Pro" in r.text or "max3dpro" in r.text:
                print("Content validated.")
        else:
             print(f"Failed: {r.status_code}")
    except Exception as e:
        print(f"Error Max 3D Pro: {e}")

if __name__ == "__main__":
    check_github_freshness()
    check_xskt_max3dpro()
