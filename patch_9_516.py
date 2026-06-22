import base64, re

with open('index.html', 'r', encoding='utf-8') as f:
    html = f.read()

# Load images
with open('/root/.claude/uploads/ac37e0ea-6dd5-542a-9365-8ab2fbe09fab/28eb4b05-utvesztoicon.png', 'rb') as f:
    icon_b64 = base64.b64encode(f.read()).decode()
with open('/root/.claude/uploads/ac37e0ea-6dd5-542a-9365-8ab2fbe09fab/743c59ef-utveszto.png', 'rb') as f:
    banner_b64 = base64.b64encode(f.read()).decode()

icon_data = f"data:image/png;base64,{icon_b64}"
banner_data = f"data:image/png;base64,{banner_b64}"

# 1. Add images to IMGS object (after quiz_banner)
old_imgs = "  'quiz_banner.png': 'data:image/png;base64,"
assert old_imgs in html, "quiz_banner not found"

# Find the end of the quiz_banner line
idx = html.index(old_imgs)
end_of_line = html.index("',\n", idx) + 3

insert_here = end_of_line
new_entries = (
    f"  'utveszto_icon.png': '{icon_data}',\n"
    f"  'utveszto_banner.png': '{banner_data}',\n"
)
html = html[:insert_here] + new_entries + html[insert_here:]

# 2. Update GAMES entry: img:null, banner:null -> img:IMGS[...], banner:IMGS[...]
old_game = "{ id:'utveszto', roundTime:'slow', name:'Útvesztő', difficulty:'nehéz', category:'Páros', emoji:'🗺️', symbol:null, img:null, banner:null, color:'#7c3aed'"
new_game = "{ id:'utveszto', roundTime:'slow', name:'Útvesztő', difficulty:'nehéz', category:'Páros', emoji:'🗺️', symbol:null, img:IMGS['utveszto_icon.png'], banner:IMGS['utveszto_banner.png'], color:'#7c3aed'"
assert old_game in html, "game entry not found"
html = html.replace(old_game, new_game, 1)

# 3. Bump version
old_ver = "const APP_VERSION = 'v9.515';"
new_ver = "const APP_VERSION = 'v9.516';"
assert old_ver in html, "version not found"
html = html.replace(old_ver, new_ver, 1)

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(html)

print("Done! v9.516")
