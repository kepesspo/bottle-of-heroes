# v10.172 — a wildcard percalapu lett, nem korszamolos
#
# A korkadencia nem huzhato ra a magukban futo jatekokra: a Busz osszesen ~6
# korlepest csinal, tehat 5-os gyakorisagnal pontosan EGY wildcardot kapna az
# egesz jatek alatt, tetszoleges ponton. A Power Hour a sajat 60 perces oraja
# szerint fut. Nincs olyan korszam, ami mindketton ertelmes.
#
# Az ido viszont minden jatekra ugyanaz. Es a modell mar eddig is idoszakot
# kezelt: az activeWildcard beall es a KOVETKEZO wildcardig ervenyben marad,
# vegig latszik egy savban — a percalapu valtas ehhez jobban illik.
import io

P = 'app.src.html'
s = io.open(P, encoding='utf-8').read()
orig = s

# ── 1) beallitas: "Hanyadik koronkent?" helyett perc-tartomany ──
old_ui = """                    <span style={{ fontFamily:T.font, fontWeight:800, fontSize:13, color:T.inkSoft, flex:1 }}>Hányadik körönként?</span>
                    <div style={{ display:'flex', gap:4 }}>
                      {[3,5,7,10].map(n => {
                        const sel = (meta.wildcardFreq || 5) === n;"""
assert s.count(old_ui) == 1
s = s.replace(old_ui, """                    <span style={{ fontFamily:T.font, fontWeight:800, fontSize:13, color:T.inkSoft, flex:1 }}>Milyen gyakran?</span>
                    <div style={{ display:'flex', gap:4 }}>
                      {WILDCARD_RANGES.map(n => {
                        const sel = (meta.wildcardMin || 8) === n.lo;""")
old_btn = """                        return <button key={n} onClick={() => setMeta({...meta, wildcardFreq:n})} style={{ width:38, padding:'8px 0', borderRadius:10, border:'none', cursor:'pointer', """
assert s.count(old_btn) == 1
s = s.replace(old_btn, """                        return <button key={n.lo} onClick={() => setMeta({...meta, wildcardMin:n.lo, wildcardMax:n.hi})} style={{ width:52, padding:'8px 0', borderRadius:10, border:'none', cursor:'pointer', """)

# a gomb felirata — a sor vegen all, `>{n}</button>` alakban
old_lbl = "transition:'all .15s' }}>{n}</button>;"
assert s.count(old_lbl) == 1, s.count(old_lbl)
s = s.replace(old_lbl, "transition:'all .15s' }}>{n.label}</button>;")

# a tartomanyok egy helyen
anchor = "const SOLO_GAME_IDS = "
assert s.count(anchor) == 1
s = s.replace(anchor, """// A wildcard percalapu: ezekbol a tartomanyokbol sorsol veletlen idopontot.
// (Korabban korszamolo volt — az a magukban futo jatekokra nem volt rahuzhato.)
const WILDCARD_RANGES = [
  { lo: 4,  hi: 8,  label: '4–8' },
  { lo: 8,  hi: 15, label: '8–15' },
  { lo: 15, hi: 25, label: '15–25' },
  { lo: 25, hi: 40, label: '25–40' },
];

""" + anchor)

# ── 2) a kivalto logika: idozito a modulo helyett ──
# a blokk sorokkal, nem szo szerinti egyezessel: a Szerencsekor sora hosszu es
# konnyu elgepelni, a jelolok viszont egyertelmuek
lines = s.split('\n')
i0 = next(i for i, l in enumerate(lines) if 'const wcFreq = gameMeta?.wildcardFreq' in l)
i1 = next(i for i in range(i0, i0 + 40)
          if lines[i].strip() == '}' and 'setRoundPopup(null), duration + 500' in lines[i - 2])
blk = '\n'.join(lines[i0:i1 + 1])
assert 'isWildcardRound' in blk and 'setActiveWildcard' in blk and 'lucky' in blk, 'gyanus blokk'
assert blk.count('setRoundPopup') == 3, blk.count('setRoundPopup')
lines[i0:i1 + 1] = [
    "        // A wildcardot mar nem a korszam hozza, hanem az idozito (lasd lentebb).",
    "        if (showCounter) {",
    "          setRoundPopup({ round: newRound, wildcard: null, showRound: true, leaving: false });",
    "          setTimeout(() => setRoundPopup(p => p ? {...p, leaving:true} : p), 1500);",
    "          setTimeout(() => setRoundPopup(null), 2000);",
    "        }",
]
s = '\n'.join(lines)
assert 'wildcardFreq' not in s, 'maradt wildcardFreq'

assert s != orig
io.open(P, 'w', encoding='utf-8').write(s)
print('OK — UI + a regi kivalto logika eltavolitva')
