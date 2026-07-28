# v10.162 (c) — a Jatekmenet oldal uj elrendezese
#
#  - a "JÁTÉKMENET" felirat kikerul a torzsbol: a fejlecben mar ott van
#  - a beallitasok kulon feher dobozokba kerulnek
#  - nehezseg + jateksorrend + max korok EGY kozos dobozba
#  - minden doboz olyan szeles, mint a felso osszefoglalo (ugyanaz a stilus,
#    ugyanaz a szulo — igy nem tud elcsuszni egymastol)
import io

P = 'app.src.html'
s = io.open(P, encoding='utf-8').read()
orig = s

old = """        <Section title="Játékmenet">
          <GameSettingsContent meta={gameMeta} setMeta={setGameMeta} />
        </Section>"""
assert s.count(old) == 1
s = s.replace(old, """        {/* A "Játékmenet" felirat itt nem kell — a fejlécben már ott van. */}
        {[['modes'], ['difficulty', 'order', 'maxRounds'], ['other']].map((grp, i) => (
          <div key={i} style={{ ...cardStyle, marginTop:12, padding:'14px 16px' }}>
            <GameSettingsContent meta={gameMeta} setMeta={setGameMeta} group={grp} />
          </div>
        ))}""")

# kozos dobozstilus: a felso osszefoglalo es minden alatta levo doboz ugyanazt
# hasznalja, kulonben ranezesre kulonbozo szelesek lennenek
old_sum = """        <div style={{ display:'flex', gap:10, background:T.surface, borderRadius:16, padding:'12px 14px', boxShadow:T.shadow }}>"""
assert s.count(old_sum) == 1
s = s.replace(old_sum, """        <div style={{ ...cardStyle, display:'flex', gap:10, padding:'12px 14px' }}>""")

anchor = "  const headStyle = {"
assert s.count(anchor) == 1
s = s.replace(anchor, """  // Minden doboz ugyanezt hasznalja — a szelesseguk igy nem tud elcsuszni.
  const cardStyle = { background:T.surface, borderRadius:16, boxShadow:T.shadow };
""" + anchor)

# a tobbi doboz is a kozos stilust hasznalja
s = s.replace("""              background:T.surface, border:'none', borderRadius:16, padding:'12px 14px',
                  boxShadow:T.shadow, cursor:'pointer', minHeight:64,""",
"""              ...cardStyle, border:'none', padding:'12px 14px', cursor:'pointer', minHeight:64,""")
s = s.replace("""            <div style={{ background:T.surface, borderRadius:16, padding:16, boxShadow:T.shadow,
              fontFamily:T.font, fontSize:13, color:T.inkMute, lineHeight:1.6 }}>""",
"""            <div style={{ ...cardStyle, padding:16,
              fontFamily:T.font, fontSize:13, color:T.inkMute, lineHeight:1.6 }}>""")
s = s.replace("""                <div key={p.id} style={{ display:'flex', alignItems:'center', gap:12,
                  background:T.surface, borderRadius:16, padding:'10px 14px', boxShadow:T.shadow, minHeight:60 }}>""",
"""                <div key={p.id} style={{ ...cardStyle, display:'flex', alignItems:'center', gap:12,
                  padding:'10px 14px', minHeight:60 }}>""")

s = s.replace("const APP_VERSION = 'v10.161';", "const APP_VERSION = 'v10.162';", 1)
assert "v10.162" in s and s != orig
io.open(P, 'w', encoding='utf-8').write(s)
print('OK')
