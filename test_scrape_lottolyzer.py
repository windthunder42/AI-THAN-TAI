import requests
from bs4 import BeautifulSoup

def test_lottolyzer_655():
    # Attempt to scrape Page 1 of 6/55 history
    url = "https://en.lottolyzer.com/history/vietnam/power-655"
    headers = {'User-Agent': 'Mozilla/5.0'}
    
    try:
        r = requests.get(url, headers=headers)
        soup = BeautifulSoup(r.text, 'lxml')
        print(f"Page Title: {soup.title.string if soup.title else 'No Title'}")
        
        table = soup.find('table')
        if not table:
            print("No table found")
            return

        rows = table.find_all('tr')
        print(f"Found {len(rows)} rows.")
        
        for i, row in enumerate(rows[:5]):
            cols = row.find_all('td')
            if not cols: continue # Header row usually th
            
            # Print content to understand mapping
            # content = [c.get_text().strip() for c in cols]
            # print(f"Row {i}: {content}")
            
            # Usually:
            # Col 0: Draw?
            # Col 1: Date
            # Col 2: Results (Main)
            # Col 3: Bonus?
            
            if len(cols) >= 3:
                win_text = cols[2].get_text().strip()
                bonus_text = cols[3].get_text().strip() if len(cols) > 3 else "N/A"
                print(f"Row {i} | Main: {win_text} | Bonus: {bonus_text}")
                
    except Exception as e:
        print(e)

if __name__ == "__main__":
    test_lottolyzer_655()
