from bs4 import BeautifulSoup

def analyze():
    with open('xskt_max3dpro.html', 'r', encoding='utf-8') as f:
        html = f.read()
    
    soup = BeautifulSoup(html, 'lxml')
    
    # helper to print parents
    def print_parents(tag):
        parents = [p.name + (' id='+p.get('id') if p.get('id') else '') + (' class='+str(p.get('class')) if p.get('class') else '') for p in tag.parents]
        print(" > ".join(parents[:3]))

    # Find text "Giải Đặc Biệt"
    tags = soup.find_all(string=lambda text: text and "Giải Đặc Biệt" in text)
    for t in tags:
        print(f"Found keyword: {t.strip()}")
        print_parents(t.parent)
        # Print content of parent
        print(t.parent.parent.prettify()[:500])
    
    # helper to print structure of a box
    def print_box(box):
        lines = box.get_text().split('\n')
        print(f"Text preview: {lines[:5]}")
        # Look for numbers
        # patterns like 01 05 10...
        
    # Find div with class containing 'box_kq'
    boxes = soup.find_all('div', class_=lambda c: c and 'box_kq' in c)
    print(f"Found {len(boxes)} boxes with class 'box_kq*'")
    for box in boxes:
        print(f"Box Class: {box.get('class')}")
        # print_box(box)
        
    # Find any table
    tables = soup.find_all('table')
    print(f"Found {len(tables)} tables.")
    for table in tables:
        # Check if table has class related to vietlott
        cls = table.get('class', [])
        print(f"Table classes: {cls}")
        # Print a few rows
        rows = table.find_all('tr')
        if rows:
             print(f"  Rows: {len(rows)}")
             print(f"  Row 1 text: {rows[0].get_text()[:100].strip()}")

if __name__ == "__main__":
    analyze()
