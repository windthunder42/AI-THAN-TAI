from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import time

def scrape():
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    
    # Setup Chrome
    service = Service() # webdriver_manager 4.x handles install automatically in recent versions but let's be explicit if needed
    # Actually webdriver_manager.chrome.ChromeDriverManager().install() returns path.
    
    driver_path = ChromeDriverManager().install()
    service = Service(driver_path)
    
    driver = webdriver.Chrome(service=service, options=chrome_options)
    
    try:
        url = "https://vietlott.vn/"
        print(f"Navigating to Home: {url}...")
        driver.get(url)
        time.sleep(5)
        
        print(f"Title: {driver.title}")
        
        # Try to click "TRÚNG THƯỞNG" or similar menu
        # Menu structure: Contains "Max 3D Pro"
        
        links = driver.find_elements(By.TAG_NAME, "a")
        target_link = None
        for a in links:
            if "Max 3D Pro" in a.text or "3D Pro" in a.text:
                print(f"Found link text: {a.text}")
                href = a.get_attribute('href')
                print(f"Href: {href}")
                if "max-3d-pro" in href:
                    target_link = href
                    break
        
        if target_link:
             print(f"Navigating to Game Page: {target_link}")
             driver.get(target_link)
             time.sleep(5)
             print(f"Game Page Title: {driver.title}")
             print(f"Game Page URL: {driver.current_url}")
        else:
             print("Could not find Max 3D Pro link on homepage.")
             # Try to find the menu container
             menus = driver.find_elements(By.CSS_SELECTOR, ".menu, .nav, .navigation, #menu, #nav")
             print(f"Found {len(menus)} potential menu containers.")
             for m in menus:
                 print(f"Menu text: {m.text[:100]}...")
                 
             # Save source for manual inspection
             with open("vietlott_source.html", "w", encoding="utf-8") as f:
                 f.write(driver.page_source)
             print("Saved vietlott_source.html")

    except Exception as e:
        print(f"Error: {e}")
    finally:
        driver.quit()

if __name__ == "__main__":
    scrape()
