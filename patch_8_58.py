#!/usr/bin/env python3
"""v8.58: Beer Pong — bajnokság nevének megadása a config sheetben"""

with open('index.html', 'r', encoding='utf-8') as f:
    content = f.read()

# ── 1. BeerPongConfigSheet: tournamentName input a fejléc alá ─────────────────
OLD_HEADER = """        <div style={{ textAlign:'center', fontFamily:T.font, fontWeight:900, fontSize:18, color:T.ink, textTransform:'uppercase', letterSpacing:'-0.01em', padding:'12px 0 6px' }}>Beer Pong beállítások</div>

        {/* Mode */}"""

NEW_HEADER = """        <div style={{ textAlign:'center', fontFamily:T.font, fontWeight:900, fontSize:18, color:T.ink, textTransform:'uppercase', letterSpacing:'-0.01em', padding:'12px 0 6px' }}>Beer Pong beállítások</div>

        {/* Bajnokság neve */}
        <input
          value={config.tournamentName || ''}
          onChange={e => setConfig(c => ({...c, tournamentName: e.target.value.slice(0,32)}))}
          placeholder="Bajnokság neve (pl. Nyári Kupa 2026)"
          style={{
            width:'100%', boxSizing:'border-box',
            background:T.bgSoft, border:'1.5px solid rgba(26,42,74,0.10)', borderRadius:14,
            padding:'12px 14px', fontFamily:T.font, fontWeight:800,
            fontSize:15, color:T.ink, outline:'none', marginBottom:4,
          }}
        />

        {/* Mode */}"""

assert OLD_HEADER in content, "Config header not found"
content = content.replace(OLD_HEADER, NEW_HEADER, 1)
print("✓ tournamentName input hozzáadva")

# ── 2. BeerpongGame: tournamentName kiolvasása a bpCfg-ből ───────────────────
OLD_BPCFG = """  const MATCH_MINUTES = bpCfg.matchMinutes ?? 5;
  const MODE = bpCfg.mode || 'egyeni';"""

NEW_BPCFG = """  const MATCH_MINUTES = bpCfg.matchMinutes ?? 5;
  const MODE = bpCfg.mode || 'egyeni';
  const TOURNAMENT_NAME = bpCfg.tournamentName || '';"""

assert OLD_BPCFG in content, "bpCfg section not found"
content = content.replace(OLD_BPCFG, NEW_BPCFG, 1)
print("✓ TOURNAMENT_NAME kiolvasva")

# ── 3. BP végeredmény képernyő: bajnokság neve megjelenítése ─────────────────
# Find the BP champion display - look for the "bajnok" trophy display
OLD_CHAMP = """          <div style={{ fontFamily:T.font, fontSize:14, color:T.inkSoft }}>Beer Pong Bajnok! 🍺</div>"""

NEW_CHAMP = """          <div style={{ fontFamily:T.font, fontSize:14, color:T.inkSoft }}>Beer Pong Bajnok! 🍺</div>
          {TOURNAMENT_NAME ? <div style={{ fontFamily:T.font, fontWeight:700, fontSize:13, color:T.inkMute, marginTop:-4 }}>{TOURNAMENT_NAME}</div> : null}"""

assert OLD_CHAMP in content, "champion display not found"
content = content.replace(OLD_CHAMP, NEW_CHAMP, 1)
print("✓ Bajnokság neve a végeredményen")

# ── 4. Version bump ───────────────────────────────────────────────────────────
OLD_VER = "const APP_VERSION = 'v8.57';"
NEW_VER = "const APP_VERSION = 'v8.58';"
assert OLD_VER in content, "version not found"
content = content.replace(OLD_VER, NEW_VER, 1)

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(content)
print("✓ v8.58 saved")
