import time
import urllib.request
import ssl
import os
import re

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

LOG_FILE = os.path.join(os.path.dirname(__file__), "cloudflared.log")

def get_current_url():
    try:
        if os.path.exists(LOG_FILE):
            with open(LOG_FILE, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()
                matches = re.findall(r"https://[a-zA-Z0-9-]+\.trycloudflare\.com", content)
                if matches:
                    return matches[-1]
    except Exception:
        pass
    return "https://benefits-textbook-dear-treatments.trycloudflare.com"

if __name__ == "__main__":
    while True:
        url = get_current_url() + "/login"
        try:
            req = urllib.request.Request(url, headers={'User-Agent': 'TallerCR-KeepAlive/1.0'})
            with urllib.request.urlopen(req, timeout=10, context=ctx) as resp:
                pass
        except Exception:
            pass
        time.sleep(20)
