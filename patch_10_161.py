# v10.161 — a Jatekmenet oldal ket finomitasa
#
# 1) A jatekmenet-beallitasok kartya-doboza kikerul. A GameSettingsContent-nek
#    sajat belso tagolasa van (pirulak, kapcsolok), a kore huzott feher lap csak
#    egy felesleges reteg volt: elvitte a szeleket es a fuggoleges helyet.
# 2) A kortyolasi limit osszecsukhato lett, alapbol zarva. Opcionalis dolog,
#    ritkan nyulnak hozza — ne tolja le a lenyeget a kepernyorol.
import io

P = 'app.src.html'
s = io.open(P, encoding='utf-8').read()
orig = s

# ── a Section kapjon osszecsukhato valtozatot ──
# Az allapot a SetupScreen-ben ul, nem a Section-ben: a Section a rendereles
# soran ujra letrejon, sajat useState-je minden rendernel nullazodna.
old_section = """  const Section = ({ title, sub, children }) => (
    <div style={{ marginTop:18 }}>
      <div style={{ fontFamily:T.font, fontWeight:900, fontSize:12, letterSpacing:'0.1em',
        textTransform:'uppercase', color:T.inkMute, marginBottom:8 }}>{title}</div>
      {sub && <div style={{ fontFamily:T.font, fontSize:12, color:T.inkMute, marginBottom:10, lineHeight:1.5 }}>{sub}</div>}
      {children}
    </div>
  );"""
new_section = """  const headStyle = { fontFamily:T.font, fontWeight:900, fontSize:12, letterSpacing:'0.1em',
    textTransform:'uppercase', color:T.inkMute, textAlign:'left' };
  const Section = ({ title, sub, badge, open, onToggle, children }) => (
    <div style={{ marginTop:18 }}>
      {onToggle ? (
        <button onClick={onToggle} style={{ width:'100%', display:'flex', alignItems:'center', gap:8,
          background:'transparent', border:'none', cursor:'pointer', padding:'0 2px 8px' }}>
          <span style={{ ...headStyle, flex:1 }}>{title}</span>
          {badge && <span style={{ fontFamily:T.font, fontSize:11, fontWeight:700, color:T.mintDeep,
            background:T.mintSoft, borderRadius:999, padding:'2px 8px' }}>{badge}</span>}
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" style={{ flexShrink:0,
            transform: open ? 'rotate(0deg)' : 'rotate(-90deg)', transition:'transform .2s' }}>
            <path d="M6 9l6 6 6-6" stroke={T.inkMute} strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round"/>
          </svg>
        </button>
      ) : (
        <div style={{ ...headStyle, marginBottom:8 }}>{title}</div>
      )}
      {(!onToggle || open) && <>
        {sub && <div style={{ fontFamily:T.font, fontSize:12, color:T.inkMute, marginBottom:10, lineHeight:1.5 }}>{sub}</div>}
        {children}
      </>}
    </div>
  );"""
assert s.count(old_section) == 1
s = s.replace(old_section, new_section)

# ── 1) a jatekmenet doboz nelkul ──
old_gm = """        <Section title="Játékmenet">
          <div style={{ background:T.surface, borderRadius:16, padding:'4px 14px 14px', boxShadow:T.shadow }}>
            <GameSettingsContent meta={gameMeta} setMeta={setGameMeta} />
          </div>
        </Section>"""
assert s.count(old_gm) == 1
s = s.replace(old_gm, """        <Section title="Játékmenet">
          <GameSettingsContent meta={gameMeta} setMeta={setGameMeta} />
        </Section>""")

# ── 2) a kortyolasi limit osszecsukhato, alapbol zarva ──
old_lim = """          <Section title="Kortyolási limit"
            sub="Ha valaki eléri a sajátját, a kör végén figyelmeztetünk. Üresen hagyva nincs limit. A profilhoz mentődik, tehát a következő bulira is megmarad.">"""
assert s.count(old_lim) == 1
s = s.replace(old_lim, """          <Section title="Kortyolási limit"
            open={limitsOpen} onToggle={() => setLimitsOpen(v => !v)}
            badge={limitCount > 0 ? limitCount + ' beállítva' : null}
            sub="Ha valaki eléri a sajátját, a kör végén figyelmeztetünk. Üresen hagyva nincs limit. A profilhoz mentődik, tehát a következő bulira is megmarad.">""")

old_state = "  const [limitsLoaded, setLimitsLoaded] = React.useState(false);"
assert s.count(old_state) == 1
s = s.replace(old_state, old_state + "\n  const [limitsOpen, setLimitsOpen] = React.useState(false);")

# a jelvenyhez: hany jatekosnak van limitje
old_wp = "  const withProfile = (players || []).filter(p => p.profileId);"
assert s.count(old_wp) == 1
s = s.replace(old_wp, old_wp + "\n  const limitCount = withProfile.filter(p => Number(limits[p.profileId]) > 0).length;")

s = s.replace("const APP_VERSION = 'v10.160';", "const APP_VERSION = 'v10.161';", 1)
assert "v10.161" in s and s != orig
io.open(P, 'w', encoding='utf-8').write(s)
print('OK')
