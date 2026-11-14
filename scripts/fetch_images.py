import urllib.request
import urllib.parse
import json
import re
import os

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36'
}

def get_duckduckgo_images(query, max_results=3):
    print(f"Searching images for: {query}")
    # Step 1: get vqd token
    url = f"https://duckduckgo.com/?q={urllib.parse.quote(query)}&iax=images&ia=images"
    req = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            html = resp.read().decode('utf-8')
            match = re.search(r'vqd=([\d-]+)', html) or re.search(r'vqd=\"([\d-]+)\"', html)
            if not match:
                print("Could not find vqd")
                return []
            vqd = match.group(1)
            
        # Step 2: query i.js
        api_url = f"https://duckduckgo.com/i.js?l=us-en&o=json&q={urllib.parse.quote(query)}&vqd={vqd}&f=,,,&p=1"
        req_api = urllib.request.Request(api_url, headers=headers)
        with urllib.request.urlopen(req_api, timeout=10) as resp:
            data = json.loads(resp.read().decode('utf-8'))
            results = data.get('results', [])
            image_urls = [r['image'] for r in results if 'image' in r][:max_results]
            print(f"Found {len(image_urls)} images for {query}:")
            for u in image_urls:
                print("  ", u)
            return image_urls
    except Exception as e:
        print("Error fetching images:", e)
        return []

if __name__ == '__main__':
    for q in [
        'filtro aire akt cr4 repuesto',
        'filtro aire loncin lx250gy-3 sx2',
        'filtro aire moto loncin 250 sx3',
        'filtro aire moto genesis sx1',
        'filtro aire genesis gxt 200'
    ]:
        get_duckduckgo_images(q, 2)

