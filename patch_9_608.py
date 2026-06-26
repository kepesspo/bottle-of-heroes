#!/usr/bin/env python3
"""
v9.608 — GameSettings Kész gomb: SheetOverlay footer-be kerül (fix, mindig látható)
"""

with open('index.html', 'r', encoding='utf-8') as f:
    html = f.read()

assert html.count('v9.607') >= 1
html = html.replace('v9.607', 'v9.608', 1)

# ── 1. SheetOverlay hívás: footer prop hozzáadása ────────────────────────────
OLD_SHEET = "      {sheet && <SheetOverlay onClose={() => setSheet(false)}>\n        <GameSettingsContent meta={gameMeta} setMeta={setGameMeta} onDone={() => setSheet(false)} go={go} />\n      </SheetOverlay>}"
NEW_SHEET = """      {sheet && <SheetOverlay onClose={() => setSheet(false)} footer={
        <button onClick={() => setSheet(false)} style={{ width:'100%', padding:'15px', borderRadius:16, background:T.mint, border:'none', color:'#fff', fontFamily:T.font, fontWeight:900, fontSize:17, cursor:'pointer', boxShadow:'0 5px 16px -5px rgba(79,194,160,0.6)' }}>{t('done')}</button>
      }>
        <GameSettingsContent meta={gameMeta} setMeta={setGameMeta} onDone={() => setSheet(false)} go={go} />
      </SheetOverlay>}"""
assert html.count(OLD_SHEET) == 1, f"sheet: {html.count(OLD_SHEET)}"
html = html.replace(OLD_SHEET, NEW_SHEET, 1)
print("OK: SheetOverlay footer Kész gomb")

# ── 2. GameSettingsContent belső Kész gomb törlése ────────────────────────────
OLD_BTN = """      <button onClick={onDone} style={{ width:'100%', padding:'15px', borderRadius:16, background:T.mint, border:'none', color:'#fff', fontFamily:T.font, fontWeight:900, fontSize:17, cursor:'pointer', boxShadow:'0 5px 16px -5px rgba(79,194,160,0.6)', marginTop:20 }}>{t('done')}</button>
    </div>
  );
}"""
NEW_BTN = """    </div>
  );
}"""
assert html.count(OLD_BTN) == 1, f"btn: {html.count(OLD_BTN)}"
html = html.replace(OLD_BTN, NEW_BTN, 1)
print("OK: belső Kész gomb eltávolítva")

print(f"Final size: {len(html):,} chars")
with open('index.html', 'w', encoding='utf-8') as f:
    f.write(html)
print("Written OK.")
