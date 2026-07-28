# v10.170 — a nehezseg info gombja az app sajat info gombja legyen
#
# Sajat "i" betut rajzoltam egy mentazold korbe. Az appban viszont van mar
# info gomb — atlatszo gomb + BohIcon "info" glifa —, es ugyanebben a
# komponensben, a Modok soraiban ott is van belole harom. Ket kulonbozo info
# gomb egy kepernyon: pont az a fajta elcsuszas, amit egyebkent kerulunk.
import io

P = 'app.src.html'
s = io.open(P, encoding='utf-8').read()
orig = s

old = """          <button aria-label="Nehézségi szintek" onClick={e => { e.stopPropagation(); setDiffSheet(true); }} style={{
            width:20, height:20, borderRadius:'50%', border:'none', padding:0, flexShrink:0,
            background:`${T.mint}22`, color:tierInk(T.mint), cursor:'pointer', display:'grid', placeItems:'center',
            fontFamily:T.font, fontWeight:900, fontSize:12, lineHeight:1 }}>i</button>"""
new = """          <button aria-label="Nehézségi szintek" onClick={e => { e.stopPropagation(); setDiffSheet(true); }}
            style={{ background:'none', border:'none', cursor:'pointer', padding:'2px 4px',
              color:T.inkMute, lineHeight:1, flexShrink:0 }}>
            <BohIcon name="info" size={15} style={{ opacity:0.45 }} />
          </button>"""
assert s.count(old) == 1, 'nem talalom a sajat info gombot'
s = s.replace(old, new)

s = s.replace("const APP_VERSION = 'v10.169';", "const APP_VERSION = 'v10.170';", 1)
assert "v10.170" in s and s != orig
io.open(P, 'w', encoding='utf-8').write(s)
print('OK')
