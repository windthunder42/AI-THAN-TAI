import requests
from bs4 import BeautifulSoup
import re # Added for re.compile

def debug_minhngoc():
    # URL for Max 3D Pro (XSKT)
    # Valid URL: https://xskt.com.vn/max-3d-pro
    url = "https://xskt.com.vn/max-3d-pro"
    headers = {'User-Agent': 'Mozilla/5.0'}
    
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status() # Check for HTTP errors
        
        with open("xskt_max3dpro.html", "w", encoding="utf-8") as f:
            f.write(response.text)
            
        print("Successfully saved xskt_max3dpro.html")
        
        # Analyze briefly
        soup = BeautifulSoup(response.text, 'html.parser') # Changed parser to html.parser
        # Look for the result box
        # Max 3D Pro often has class "box_kq" or similar
        # Or look for "Giải Đặc Biệt"
        
        special_prize = soup.find(string=re.compile("Giải Đặc Biệt"))
        if special_prize:
            print(f"Found Special Prize anchor: {special_prize}")
            # The value usually follows in a class like "gdb" or "giaidb"
        else:
                print(f"Body Child: {child.name}, Classes: {child.get('class')}")

    except Exception as e:
        print(e)

if __name__ == "__main__":
    debug_minhngoc()
