import requests
import json
import re

# کشورهایی که نیاز داری
COUNTRIES = ['us', 'fi', 'de', 'nl', 'it']
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
}

all_proxies = []

def fetch_proxies():
    for cc in COUNTRIES:
        url = f"https://www.ditatompel.com/proxy/country/{cc}?rowsPerPage=100"
        try:
            print(f"Fetching data for {cc.upper()}...")
            response = requests.get(url, headers=HEADERS, timeout=15)
            
            # استخراج دیتای SvelteKit
            match = re.search(r'(?:proxies|dtData):\{.*?items:(\[.*?\]),total:', response.text)
            if match:
                raw_items = match.group(1)
                # تبدیل آبجکت جاوااسکریپت به جیسون استاندارد
                raw_items = re.sub(r'([{,]\s*)([a-zA-Z0-9_]+)\s*:', r'\1"\2":', raw_items)
                raw_items = raw_items.replace("'", '"')
                
                # رفع ارور کلمات رزرو شده خاص تو سورس مبدا (مثل undefined)
                raw_items = re.sub(r':\s*undefined\b', ':-1', raw_items)
                
                data = json.loads(raw_items)
                all_proxies.extend(data)
                print(f"  -> Added {len(data)} proxies from {cc.upper()}")
            else:
                print(f"  -> No data matched for {cc.upper()}")
                
        except Exception as e:
            print(f"Error on {cc.upper()}: {e}")

    # ذخیره در فایل جیسون
    with open('proxies.json', 'w', encoding='utf-8') as f:
        json.dump(all_proxies, f, indent=4, ensure_ascii=False)
    
    print(f"\nSuccessfully saved {len(all_proxies)} total proxies to proxies.json")

if __name__ == "__main__":
    fetch_proxies()
