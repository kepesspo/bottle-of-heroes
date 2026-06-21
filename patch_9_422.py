#!/usr/bin/env python3
"""v9.422 — Kvíz ikon és banner beágyazás"""
import base64

with open('index.html', 'r', encoding='utf-8') as f:
    src = f.read()

# 1. Load images
with open('/root/.claude/uploads/ac37e0ea-6dd5-542a-9365-8ab2fbe09fab/7083c79a-kvizicon.png','rb') as f:
    icon_b64 = base64.b64encode(f.read()).decode()
with open('/root/.claude/uploads/ac37e0ea-6dd5-542a-9365-8ab2fbe09fab/2f957172-kviz.png','rb') as f:
    banner_b64 = base64.b64encode(f.read()).decode()

icon_data  = f"data:image/png;base64,{icon_b64}"
banner_data = f"data:image/png;base64,{banner_b64}"

# 2. Embed into IMGS object — find last entry before closing brace
# The IMGS object ends with something like:   'last_key': 'data:...',\n};
# We insert after cardbattle_banner (or whatever is last)
MARKER = "'cardbattle_banner.png':"
assert MARKER in src, 'cardbattle_banner marker not found'

# Find the end of that entry's value (ends with ',')
idx = src.index(MARKER)
# Find the next entry start or closing }; after this point
# We'll insert our two new entries right before the closing }; of IMGS
IMGS_CLOSE = '\n};'
# find the IMGS closing after the marker
close_idx = src.index(IMGS_CLOSE, idx)

INSERT = (
    f"\n  'quiz_icon.png': '{icon_data}',"
    f"\n  'quiz_banner.png': '{banner_data}',"
)

src = src[:close_idx] + INSERT + src[close_idx:]
print('IMGS entries added')

# 3. Update quiz game definition to use IMGS references
OLD_QUIZ_IMG = "img:IMGS['quiz_icon.png'], banner:IMGS['quiz_banner.png']"
if OLD_QUIZ_IMG in src:
    print('quiz img already uses IMGS refs')
else:
    # Try plain string version
    OLD_QUIZ_STR = "img:'quiz_icon.png', banner:'quiz_banner.png'"
    if OLD_QUIZ_STR in src:
        src = src.replace(OLD_QUIZ_STR, OLD_QUIZ_IMG, 1)
        print('quiz img refs updated')
    else:
        # Check what's there
        idx2 = src.find("id:'quiz'")
        if idx2 < 0:
            idx2 = src.find('id:"quiz"')
        snippet = src[idx2:idx2+300] if idx2 >= 0 else '(quiz not found)'
        print('quiz game snippet:', snippet[:200])

# 4. Version bump
assert "const APP_VERSION = 'v9.421';" in src
src = src.replace("const APP_VERSION = 'v9.421';", "const APP_VERSION = 'v9.422';", 1)

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(src)

print('v9.422 OK')
