# === scraper.py ===

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
from bs4 import BeautifulSoup
import json
import time

# لیست کشورهای جدید + قبلی‌ها
COUNTRIES = ['us', 'fi', 'de', 'nl', 'it', 'ir', 'ar', 'ru', 'se', 'ae', 'ch', 'tr']

all_proxies = []

def fetch_proxies():
    chrome_options = Options()
    chrome_options.add_argument("--headless=new")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    driver = webdriver.Chrome(options=chrome_options)
    
    for cc in COUNTRIES:
        print(f"\n[+] Processing {cc.upper()}...")
        url = f"https://www.ditatompel.com/proxy/country/{cc}"
        driver.get(url)
        
        try:
            WebDriverWait(driver, 12).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "table tbody tr"))
            )
            
            # تلاش برای نمایش ۱۰۰ ردیف
            try:
                select_element = WebDriverWait(driver, 6).until(
                    EC.presence_of_element_located((By.ID, "rowsPerPage"))
                )
                Select(select_element).select_by_value("100")
                WebDriverWait(driver, 6).until(
                    lambda d: len(d.find_elements(By.CSS_SELECTOR, "table tbody tr")) > 10
                )
            except Exception:
                print(f"  -> Note: Could not expand to 100 rows for {cc.upper()}.")
            
            time.sleep(1.5)
            
            soup = BeautifulSoup(driver.page_source, 'html.parser')
            rows = soup.select("table tbody tr")
            
            print(f"  -> Found {len(rows)} rows.")
            
            for row in rows:
                cols = row.find_all('td')
                if len(cols) < 6: continue
                
                ip_port = cols[0].find('strong').get_text(strip=True) if cols[0].find('strong') else ""
                if ":" not in ip_port: continue
                ip, port = ip_port.split(':', 1)
                
                p_type = cols[1].find('a').get_text(strip=True) if cols[1].find('a') else "HTTP"
                anonymity = cols[2].get_text(strip=True).upper()
                uptime_str = cols[4].get_text(strip=True).replace('%', '')
                uptime = int(uptime_str) if uptime_str.isdigit() else 0
                
                all_proxies.append({
                    "ip": ip,
                    "port": int(port),
                    "type": p_type,
                    "anonymity": anonymity,
                    "cc": cc.upper(),
                    "uptime": uptime,
                    "checked_ts": int(time.time())
                })
        except Exception as e:
            print(f"  -> Error scraping {cc.upper()}: {e}")

    driver.quit()
    
    # حذف تکراری‌ها
    unique_proxies = {f"{p['ip']}:{p['port']}": p for p in all_proxies}.values()
    
    with open('proxies.json', 'w', encoding='utf-8') as f:
        json.dump(list(unique_proxies), f, indent=4, ensure_ascii=False)
    
    print(f"\n[✔] Successfully saved {len(unique_proxies)} unique proxies.")

if __name__ == "__main__":
    fetch_proxies()
