import requests
import json
import re
import time

# لیست کشورهای هدف
COUNTRIES = ['us', 'fi', 'de', 'nl', 'it']
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
}

all_proxies = []

def fetch_proxies():
    for cc in COUNTRIES:
        print(f"\n[+] Fetching data for {cc.upper()}...")
        
        # حلقه برای خواندن 10 صفحه (هر صفحه 10 پروکسی = مجموعا 100 پروکسی برای هر کشور)
        for page in range(1, 11):
            url = f"https://www.ditatompel.com/proxy/country/{cc}?page={page}"
            try:
                response = requests.get(url, headers=HEADERS, timeout=15)
                
                # پیدا کردن آرایه حاوی اطلاعات از سورس SvelteKit
                match = re.search(r'(?:proxies|dtData):\{.*?items:(\[.*?\]),total:', response.text)
                if match:
                    raw_items = match.group(1)
                    
                    # تبدیل آبجکت جاوااسکریپت به جیسون استاندارد و رفع باگ‌های سینتکس
                    raw_items = re.sub(r'([{,]\s*)([a-zA-Z0-9_]+)\s*:', r'\1"\2":', raw_items)
                    raw_items = raw_items.replace("'", '"')
                    raw_items = re.sub(r':\s*undefined\b', ':-1', raw_items)
                    
                    data = json.loads(raw_items)
                    
                    if not data:
                        print(f"  -> Page {page}: Empty data. Stopping pagination for {cc.upper()}.")
                        break
                        
                    all_proxies.extend(data)
                    print(f"  -> Page {page}: Successfully extracted {len(data)} proxies.")
                else:
                    print(f"  -> Page {page}: No data structure found. Might be end of list.")
                    break
                    
            except Exception as e:
                print(f"  -> Error on {cc.upper()} Page {page}: {e}")
                break
            
            # یک ثانیه توقف بین هر درخواست برای جلوگیری از بلاک شدن آی‌پی توسط کلودفلر سایت مبدا
            time.sleep(1)

    # فیلتر کردن پروکسی‌های تکراری احتمالی بر اساس آی‌پی و پورت
    unique_proxies = {f"{p['ip']}:{p['port']}": p for p in all_proxies}.values()
    
    # ذخیره در فایل جیسون
    with open('proxies.json', 'w', encoding='utf-8') as f:
        json.dump(list(unique_proxies), f, indent=4, ensure_ascii=False)
    
    print(f"\n[✔] Successfully saved {len(unique_proxies)} unique proxies to proxies.json")

if __name__ == "__main__":
    fetch_proxies()
