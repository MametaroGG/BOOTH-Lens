import requests
from bs4 import BeautifulSoup
import json

def probe_booth_jsonld(item_id):
    url = f"https://booth.pm/ja/items/{item_id}"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    
    resp = requests.get(url, headers=headers, timeout=10)
    soup = BeautifulSoup(resp.text, "lxml")
    
    script_tag = soup.find("script", type="application/ld+json")
    if script_tag:
        try:
            ld_data = json.loads(script_tag.string)
            with open("probe_output.json", "w", encoding="utf-8") as f:
                json.dump(ld_data, f, indent=2, ensure_ascii=False)
            print("Full JSON-LD saved to probe_output.json")
            offers = ld_data.get("offers", {})
            print(f"Offer Type: {type(offers)}")
            if isinstance(offers, dict):
                print(f"Offer @type: {offers.get('@type')}")
        except Exception as e:
            print(f"Error parsing JSON-LD: {e}")
    else:
        print("No JSON-LD script tag found.")

if __name__ == "__main__":
    probe_booth_jsonld("6654988")
