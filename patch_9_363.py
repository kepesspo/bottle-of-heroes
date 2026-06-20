#!/usr/bin/env python3
"""v9.363 — Remove lavender, ocean, lime, candy themes"""

with open('index.html', 'r', encoding='utf-8') as f:
    html = f.read()

to_remove_keys = ['lavender', 'ocean', 'lime', 'candy']

for key in to_remove_keys:
    start_marker = f'  {key}: {{\n'
    assert start_marker in html, f"FAIL: cant find theme {key}"
    start = html.index(start_marker)
    end = html.index('\n  },\n', start) + len('\n  },\n')
    html = html[:start] + html[end:]

# Update picker - top grid
old_top = """                  {[
                    ['warm','☀️','Meleg'],['dark','🌙','Sötét'],['candy','🍬','Candy'],['lavender','💜','Lavender'],['ocean','🌊','Ocean'],
                    ['peach','🍑','Peach'],['lemon','🍋','Citrom'],['berry','🫐','Berry'],['ice','🩵','Ice'],['slate','🪨','Kő'],
                  ].map(([key, icon, label]) => ("""
new_top = """                  {[
                    ['warm','☀️','Meleg'],['dark','🌙','Sötét'],['peach','🍑','Peach'],['lemon','🍋','Citrom'],['berry','🫐','Berry'],
                    ['ice','🩵','Ice'],['slate','🪨','Kő'],
                  ].map(([key, icon, label]) => ("""
assert old_top in html, "FAIL: picker top"
html = html.replace(old_top, new_top, 1)

# Update green section - remove lime
old_green = "['jade','🪴','Jade'],['mint2','🌿','Menta'],['lime','🍃','Lime'],"
new_green = "['jade','🪴','Jade'],['mint2','🌿','Menta'],"
assert old_green in html, "FAIL: picker green"
html = html.replace(old_green, new_green, 1)

html = html.replace("const APP_VERSION = 'v9.362';", "const APP_VERSION = 'v9.363';")

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(html)

print("Done: v9.363 — removed lavender, ocean, lime, candy")
