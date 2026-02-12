import requests
from bs4 import BeautifulSoup

url = "https://en.lottolyzer.com/history/vietnam/lotto-5_slash_35"
try:
    r = requests.get(url)
    soup = BeautifulSoup(r.text, 'lxml')
    table = soup.find('table')
    rows = table.find_all('tr')
    for i, row in enumerate(rows[:5]):
        print(f"Row {i}:")
        cells = row.find_all(['td', 'th'])
        for j, cell in enumerate(cells):
            print(f"  Col {j}: {cell.get_text().strip().replace('\\n', ' ')}")
            
except Exception as e:
    print(e)
