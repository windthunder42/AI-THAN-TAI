import requests
from bs4 import BeautifulSoup
import datetime
import re

def scrape_5x35_30days():
    """
    Scrapes the last 30 days of Lotto 5/35 results from xskt.com.vn.
    Returns a list of dictionaries:
    [
        {
            "date": "DD/MM/YYYY",
            "time": "13h" or "21h",
            "draw_id": "00455",
            "results": [n1, n2, n3, n4, n5], # integers
            "special": n_special # integer
        },
        ...
    ]
    """
    url = "https://xskt.com.vn/xslotto-5-35/30-ngay"
    try:
        # Use a realistic user agent to avoid being blocked
        headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36"
        }
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        html = response.text
    except Exception as e:
        print(f"Error fetching data: {e}")
        return []

    soup = BeautifulSoup(html, 'html.parser')
    data = []

    # Each draw is contained within a div with class 'box-ketqua'
    # structure:
    # <div class="box-ketqua">
    #   <h2>...<a ...> ngày 11/02</a>...</h2>
    #   <div class="box-table">
    #      <table class="result">
    #          <tr><td ... kmt>...<b>#00455 (13h)</b>...</td></tr>
    #          <tr>...<td class="megaresult"><em>09 20 23 26 34 <span>10</span></em></td>...</tr>
    
    results_boxes = soup.find_all('div', class_='box-ketqua')
    
    current_year = datetime.datetime.now().year
    
    for box in results_boxes:
        try:
            # Extract Date
            h2 = box.find('h2')
            if not h2:
                continue
            
            date_link = h2.find('a', href=re.compile(r'/ngay-'))
            if not date_link:
                continue
                
            date_text = date_link.text.strip() # " ngày 11/02"
            # Extract day and month
            match_date = re.search(r'(\d+)/(\d+)', date_text)
            if not match_date:
                # Try explicit year if present or assume structure
                 match_date = re.search(r'(\d+)-(\d+)', date_text)

            if match_date:
                day = int(match_date.group(1))
                month = int(match_date.group(2))
                # Simple logic to handle year boundary if needed, but for 30 days it's usually clear.
                # If parsed month is greater than current month + 1, it might be previous year? 
                # Actually xskt might not show year. We assume current year, unless it's Dec/Jan transition.
                # For safety, let's just stick to current year and maybe adjust if future date.
                
                # Better: check the link href, e.g. /xslotto-5-35/ngay-11-2
                # Sometimes it might have year.
                # Let's rely on the text for now.
                draw_date = f"{day:02d}/{month:02d}/{current_year}" 
            else:
                continue

            # Extract Draw ID and Time
            table = box.find('table', class_='result')
            if not table:
                continue
            
            kmt_td = table.find('td', class_='kmt')
            if not kmt_td:
                continue
            
            kmt_text = kmt_td.text.strip() # "Kỳ mở thưởng: #00455 (13h)"
            
            # Regex to find ID and Time
            match_id_time = re.search(r'#(\d+)\s*\((\d+h)\)', kmt_text)
            if not match_id_time:
                 match_id_time = re.search(r'#(\d+)', kmt_text)
                 time_str = "Unknown"
                 draw_id = match_id_time.group(1) if match_id_time else "Unknown"
            else:
                draw_id = match_id_time.group(1)
                time_str = match_id_time.group(2)

            # Extract Numbers
            megaresult = table.find('td', class_='megaresult')
            if not megaresult:
                continue
                
            em_tag = megaresult.find('em')
            if not em_tag:
                continue
            
            # The structure inside em is: "09 20 23 26 34 <span>10</span>"
            # Text content of em includes the span text if we just do .text
            # But we want to separate special number in span.
            
            special_span = em_tag.find('span')
            if special_span:
                special_num = int(special_span.text.strip())
                # Get the text part before the span
                # We can navigate usable child nodes
                main_text = em_tag.contents[0].strip() if em_tag.contents else ""
                main_nums = [int(n) for n in main_text.split() if n.isdigit()]
            else:
                # Maybe no special number or different formatting?
                # Assume last is special if only text? No, xskt usually puts span for special in 5/35
                # Let's try to parse all text
                all_text = em_tag.text.strip()
                nums = [int(n) for n in all_text.split() if n.isdigit()]
                if len(nums) == 6:
                    main_nums = nums[:5]
                    special_num = nums[5]
                else:
                    # Fallback
                    main_nums = nums
                    special_num = None
            
            entry = {
                "date": draw_date,
                "time": time_str,
                "draw_id": draw_id,
                "results": main_nums,
                "special": special_num
            }
            data.append(entry)

        except Exception as e:
            print(f"Error parsing box: {e}")
            continue

    return data

if __name__ == "__main__":
    # Test run
    data = scrape_5x35_30days()
    print(f"Found {len(data)} draws.")
    for d in data[:5]:
        print(d)
