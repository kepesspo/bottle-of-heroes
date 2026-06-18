#!/usr/bin/env python3
"""patch_9_150.py — Menü fix: typo vezérlés default + tab eltolódás fix"""

with open('index.html', 'r', encoding='utf-8') as f:
    content = f.read()

assert "const APP_VERSION = 'v9.149';" in content
content = content.replace("const APP_VERSION = 'v9.149';", "const APP_VERSION = 'v9.150';")

# ── 1. Fix typo: 'vezerlés' → 'vezérlés' (hiányzó ékezet = egyik tab sem aktív) ──
OLD_DEFAULT = "  const [menuTab, setMenuTab] = useState('vezerlés');"
NEW_DEFAULT  = "  const [menuTab, setMenuTab] = useState('vezérlés');"
assert OLD_DEFAULT in content, "menuTab default not found"
content = content.replace(OLD_DEFAULT, NEW_DEFAULT, 1)

# ── 2. Fix tab content shift: remove left:14/right:14 from absolute tabs
#    Parent already has padding:'0 14px 8px', so left:0/right:0 is correct ──
OLD_ALLAS_TAB = "              <div style={{ visibility: menuTab==='állás' ? 'visible' : 'hidden', position: menuTab==='állás' ? 'relative' : 'absolute', top:0, left:14, right:14, display:'flex', flexDirection:'column', gap:10 }}>"
NEW_ALLAS_TAB = "              <div style={{ visibility: menuTab==='állás' ? 'visible' : 'hidden', position: menuTab==='állás' ? 'relative' : 'absolute', top:0, left:0, right:0, display:'flex', flexDirection:'column', gap:10 }}>"
assert OLD_ALLAS_TAB in content, "állás tab not found"
content = content.replace(OLD_DALLAS_TAB := OLD_ALLAS_TAB, NEW_ALLAS_TAB, 1)

OLD_VEZ_TAB = "              <div style={{ visibility: menuTab==='vezérlés' ? 'visible' : 'hidden', position: menuTab==='vezérlés' ? 'relative' : 'absolute', top:0, left:14, right:14, display:'flex', flexDirection:'column', gap:10 }}>"
NEW_VEZ_TAB = "              <div style={{ visibility: menuTab==='vezérlés' ? 'visible' : 'hidden', position: menuTab==='vezérlés' ? 'relative' : 'absolute', top:0, left:0, right:0, display:'flex', flexDirection:'column', gap:10 }}>"
assert OLD_VEZ_TAB in content, "vezérlés tab not found"
content = content.replace(OLD_VEZ_TAB, NEW_VEZ_TAB, 1)

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(content)

print("OK — v9.150 ready")
