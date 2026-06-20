#!/usr/bin/env python3
"""v9.396 — Beer Pong beállítások: téma-tudatos gombok (sötét módban is jó)"""

with open('index.html', 'r', encoding='utf-8') as f:
    html = f.read()

# ── 1-stage tournament type buttons ──────────────────────────────────────────
old_1stage = """                <button key={t.key} onClick={() => setConfig(c => ({...c, tournamentType:t.key}))}
                  style={{ display:'flex', alignItems:'center', gap:12, padding:'13px 14px', borderRadius:15, cursor:'pointer', border: on?'1.5px solid '+T.mint:'1.5px solid rgba(26,42,74,0.10)', background: on?T.mintSoft:'#fff', marginBottom:0, textAlign:'left' }}>"""

new_1stage = """                <button key={t.key} onClick={() => setConfig(c => ({...c, tournamentType:t.key}))}
                  style={{ display:'flex', alignItems:'center', gap:12, padding:'13px 14px', borderRadius:15, cursor:'pointer', border: on?'1.5px solid '+T.mint:'1.5px solid '+T.inkMute+'28', background: on?T.mintSoft:T.surface, marginBottom:0, textAlign:'left' }}>"""

assert old_1stage in html, "FAIL: 1stage btns"
html = html.replace(old_1stage, new_1stage, 1)

# ── 2-stage tournament type buttons ──────────────────────────────────────────
old_2stage = """                <button key={t.key} onClick={() => setConfig(c => ({...c, tournamentType:t.key}))}
                  style={{ display:'flex', alignItems:'center', gap:12, padding:'13px 14px', borderRadius:15, cursor:'pointer', border: on?'1.5px solid '+T.mint:'1.5px solid rgba(26,42,74,0.10)', background: on?T.mintSoft:'#fff', marginBottom:0, textAlign:'left' }}>"""

new_2stage = """                <button key={t.key} onClick={() => setConfig(c => ({...c, tournamentType:t.key}))}
                  style={{ display:'flex', alignItems:'center', gap:12, padding:'13px 14px', borderRadius:15, cursor:'pointer', border: on?'1.5px solid '+T.mint:'1.5px solid '+T.inkMute+'28', background: on?T.mintSoft:T.surface, marginBottom:0, textAlign:'left' }}>"""

assert old_2stage in html, "FAIL: 2stage btns"
html = html.replace(old_2stage, new_2stage, 1)

html = html.replace("const APP_VERSION = 'v9.395';", "const APP_VERSION = 'v9.396';")

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(html)

print("Done: v9.396 — Beer Pong beállítások gombok téma-tudatos")
