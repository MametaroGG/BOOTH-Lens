from bs4 import BeautifulSoup

def test():
    with open('debug_item.html', 'r', encoding='utf-8') as f:
        content = f.read()
    
    soup = BeautifulSoup(content, 'lxml')
    
    # 1. Check all h2/h3 text
    print("--- h2/h3 Texts ---")
    for h in soup.find_all(["h1", "h2", "h3", "h4"]):
        print(f"[{h.name}] '{h.get_text(strip=True)}'")
        if "タグ" in h.get_text():
            print("  ^^ FOUND TAG HEADING candidate")

    # 2. Check all links containing 'search'
    print("\n--- Links with 'search' in href ---")
    count = 0
    for a in soup.find_all("a"):
        href = a.get("href", "")
        if "search" in href:
            count += 1
            print(f"Link {count}: href='{href}', text='{a.get_text(strip=True)}'")
            img = a.find("img")
            if img: print(f"  IMAGE ALT: '{img.get('alt')}'")

    # 3. Try the logic
    tags = []
    tag_heading = next((h for h in soup.find_all(["h1", "h2", "h3", "h4"]) if "タグ" in h.get_text()), None)
    
    if tag_heading:
        print(f"\nTargeting heading: {tag_heading.name}")
        container = tag_heading.find_parent("div") or tag_heading.parent
        tag_links = [a for a in container.find_all("a") if "search" in a.get("href", "")]
        print(f"Links in container: {len(tag_links)}")
        for a in tag_links:
            txt = a.get_text(strip=True)
            if not txt:
                img = a.find("img")
                if img: txt = img.get("alt", "").strip()
            if txt and txt not in tags:
                tags.append(txt)
    
    print(f"\nRESULT TAGS: {tags}")

if __name__ == "__main__":
    test()
