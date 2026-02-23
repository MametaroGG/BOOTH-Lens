import sys
content = open('vector_db.py', 'r', encoding='utf-8').read()
old_part = '''                            try:
                            await asyncio.sleep(0.01) # Throttle
                            
                            is_url = img_rel_path.startswith("http://") or img_rel_path.startswith("https://")'''

new_part = '''                            try:
                                await asyncio.sleep(0.01) # Throttle
                                
                                is_url = img_rel_path.startswith("http://") or img_rel_path.startswith("https://")'''

content = content.replace(old_part, new_part)

# Also fix the rest of the block by a simpler regex pass in python
import re
# Find the exact text from if is_url: down to img_count += 1
# and prepend 4 spaces to each line
block_start = content.find('                            if is_url:')
block_end = content.find('                            except Exception as img_e:')

if block_start != -1 and block_end != -1:
    block = content[block_start:block_end]
    lines = block.split('\n')
    new_lines = []
    for line in lines:
        if line.strip(): # if not completely empty
            if line.startswith('                            '):
                new_lines.append('    ' + line)
            else:
                new_lines.append(line)
        else:
            new_lines.append(line)
    
    new_block = '\n'.join(new_lines)
    content = content[:block_start] + new_block + content[block_end:]

open('vector_db.py', 'w', encoding='utf-8').write(content)
