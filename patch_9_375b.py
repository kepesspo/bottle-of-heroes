#!/usr/bin/env python3
"""v9.375b — Fix JS syntax error: backtick template literal in JSX settings"""

with open('index.html', 'r', encoding='utf-8') as f:
    html = f.read()

# Fix the broken backtick template literal — use string concat instead
old_line = "                          border: splashStyle===key ? \\`2px solid \\${T.mint}\\` : '2px solid transparent',"
new_line = "                          border: splashStyle===key ? '2px solid ' + T.mint : '2px solid transparent',"

assert old_line in html, "FAIL: broken backtick line"
html = html.replace(old_line, new_line, 1)

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(html)

print("Done: v9.375b — JS syntax fix")
