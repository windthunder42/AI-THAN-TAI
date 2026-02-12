import requests
from bs4 import BeautifulSoup

def find_url():
    url = "https://vietlott.vn/vi/trung-thuong/ket-qua-trung-thuong"
    headers = {'User-Agent': 'Mozilla/5.0'}
    try:
        r = requests.get(url, headers=headers, timeout=10)
        print(f"Hub Status: {r.status_code}")
        soup = BeautifulSoup(r.text, 'html.parser')
        
        links = soup.find_all("a", href=True)
        print(f"Total links: {len(links)}")
        for a in links[:100]:
             href = a['href']
             txt = a.get_text().strip()
             if "max" in href.lower() or "3d" in href.lower():
                 print(f"Potential Match: {txt} -> {href}")
                
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    find_url()
