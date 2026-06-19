#!/usr/bin/env python3

with open('index.html', 'r', encoding='utf-8') as f:
    html = f.read()

# ── 1. SorrendTab: back to conditional render (Set-based sync handles snap-back)
old = """              {/* SORREND — always mounted, visibility toggled */}
              <div style={{ visibility: menuTab==='sorrend' ? 'visible' : 'hidden', position:'absolute', top:0, left:14, right:14, bottom:0, overflowY:'auto' }}>
                <SorrendTab players={players} setPlayers={setPlayers} turn={turn} setTurn={setTurn} pendingCommit={pendingCommit} setPendingCommit={setPendingCommit} />
              </div>"""
new = """              {/* SORREND */}
              {menuTab==='sorrend' && (
                <div style={{ position:'absolute', top:0, left:14, right:14, bottom:0, overflowY:'auto' }}>
                  <SorrendTab players={players} setPlayers={setPlayers} turn={turn} setTurn={setTurn} pendingCommit={pendingCommit} setPendingCommit={setPendingCommit} />
                </div>
              )}"""
assert old in html, "FAIL: sorrend div"
html = html.replace(old, new, 1)

# ── 2. Service worker: bump cache version to force reload
import re
sw_ver = re.search(r"const CACHE_VERSION = '([^']+)'", html)
if sw_ver:
    old_sv = sw_ver.group(0)
    # increment last number
    ver = sw_ver.group(1)
    new_sv = old_sv.replace(ver, ver + '-b')
    html = html.replace(old_sv, new_sv, 1)
    print(f"SW cache: {old_sv} -> {new_sv}")
else:
    print("No service worker cache version found")

# ── version bump
html = html.replace("const APP_VERSION = 'v9.284';", "const APP_VERSION = 'v9.285';")

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(html)

print("Done: v9.285 — SorrendTab conditional, SW cache bust")
