# -*- coding: utf-8 -*-
import base64

with open('index.html', 'r', encoding='utf-8') as f:
    html = f.read()

# Load banners
def b64img(fname):
    with open(fname, 'rb') as f:
        return f"data:image/png;base64,{base64.b64encode(f.read()).decode('ascii')}"

busz_data    = b64img('busz.png')
memoria_data = b64img('memoria.png')

# 1. Add to IMGS object — insert after imposztor_banner entry
old_anchor = "  'imposztor_banner.png':"
idx = html.find(old_anchor)
line_end = html.find('\n', idx)
old_line = html[idx:line_end+1]
new_line = old_line + f"  'busz_banner.png': '{busz_data}',\n  'memoria_banner.png': '{memoria_data}',\n"
assert old_anchor in html, "IMGS anchor not found"
html = html.replace(old_line, new_line, 1)

# 2. Add banner field to busz game
old_busz = "{ id:'busz',      name:'Busz',                  difficulty:'nehéz',   category:'Csapat', emoji:'🚌', symbol:IMGS['busz_symbol.png'], img:IMGS['busz_icon.png'],"
new_busz = "{ id:'busz',      name:'Busz',                  difficulty:'nehéz',   category:'Csapat', emoji:'🚌', symbol:IMGS['busz_symbol.png'], img:IMGS['busz_icon.png'], banner:IMGS['busz_banner.png'],"
assert old_busz in html, "Busz game def not found"
html = html.replace(old_busz, new_busz, 1)

# 3. Add banner field to memoria game
old_mem = "{ id:'memoria',   name:'Memória',               difficulty:'nehéz',   category:'Csapat', emoji:'🧩', symbol:IMGS['memoria_symbol.png'], img:IMGS['memoria_icon.png'],"
new_mem = "{ id:'memoria',   name:'Memória',               difficulty:'nehéz',   category:'Csapat', emoji:'🧩', symbol:IMGS['memoria_symbol.png'], img:IMGS['memoria_icon.png'], banner:IMGS['memoria_banner.png'],"
assert old_mem in html, "Memoria game def not found"
html = html.replace(old_mem, new_mem, 1)

# 4. Version bump
assert 'Verzió 5.58 · DNR · 2026.06.02 14:30' in html, "Version not found"
html = html.replace('Verzió 5.58 · DNR · 2026.06.02 14:30', 'Verzió 5.59 · DNR · 2026.06.02 15:00', 1)

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(html)

print("Done — v5.59")
