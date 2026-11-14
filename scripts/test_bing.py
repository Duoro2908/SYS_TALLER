import urllib.request
import urllib.parse
import re
import json

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
}

def search_bing_images(query):
    url = f"https://www.bing.com/images/search?q={urllib.parse.quote(query)}&form=HDRSC2&first=1"
    req = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            content = resp.read().decode('utf-8', errors='ignore')
            # Bing embeds murl in the html: murl&quot;:&quot;http...
            murls = re.findall(r'murl&quot;:&quot;(https?://[^&]+)&quot;', content)
            print(f"Bing found {len(murls)} images for '{query}'")
            return murls[:5]
    except Exception as e:
        print(f"Error on Bing for '{query}':", e)
        return []

if __name__ == '__main__':
    queries = [
        'filtro aire akt cr4',
        'filtro aire loncin sx2',
        'filtro aire moto loncin 250',
        'filtro aire moto genesis sx1',
        'filtro aire suzuki dr200 gxt200'
    ]
    for q in queries:
        urls = search_bing_images(q)
        for u in urls[:2]:
            print("  ->", u)

