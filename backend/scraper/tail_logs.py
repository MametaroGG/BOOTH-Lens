import os

paths = ['e:/GitHub/BOOTH-Lens/backend/scraper/scrape_popular.log', 'e:/GitHub/BOOTH-Lens/backend/scraper/scraper.log']
with open('e:/GitHub/BOOTH-Lens/backend/scraper/tail_logs_output.txt', 'w', encoding='utf-8') as out:
    for path in paths:
        out.write(f'--- Tail of {path} ---\n')
        try:
            with open(path, 'r', encoding='utf-8', errors='replace') as f:
                lines = f.readlines()
                for line in lines[-50:]:
                    out.write(line)
        except Exception as e:
            out.write(str(e) + '\n')
