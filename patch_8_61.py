#!/usr/bin/env python3
"""v8.61: Bíró Bence hozzáadása a profile listához"""

with open('index.html', 'r', encoding='utf-8') as f:
    content = f.read()

OLD = """    { id:'preset_bacsi',  name:'Bacsinszki Dániel',  nickname:'Bacsi',  color:'#F97316' },
  ];"""
NEW = """    { id:'preset_bacsi',  name:'Bacsinszki Dániel',  nickname:'Bacsi',  color:'#F97316' },
    { id:'preset_bb',     name:'Bíró Bence',           nickname:'BB',     color:'#8B5CF6' },
  ];"""

assert OLD in content, "PRESET_PLAYERS end not found"
content = content.replace(OLD, NEW, 1)
print("✓ Bíró Bence hozzáadva")

OLD_VER = "const APP_VERSION = 'v8.60';"
NEW_VER = "const APP_VERSION = 'v8.61';"
assert OLD_VER in content
content = content.replace(OLD_VER, NEW_VER, 1)

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(content)
print("✓ v8.61 saved")
