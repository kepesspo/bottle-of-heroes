# v10.160 (b) — lathato fogaskerek a beallithato jatekokon
#
# Eddig a het jatek beallito lapja KIZAROLAG 500 ms-os hosszu nyomasra nyilt,
# es semmi nem jelezte, hogy egyaltalan letezik. Gyakorlatilag lathatatlan
# funkcio volt. Most kap egy gombot az info gomb parjakent — a hosszu nyomas
# is megmarad gyorsitasnak annak, aki mar tudja.
import io

P = 'app.src.html'
s = io.open(P, encoding='utf-8').read()
orig = s

# Kozos kis komponens, hogy a harom csempe ne csusszon el egymastol.
anchor = "const GAME_CONFIG_IDS = "
assert s.count(anchor) == 1
s = s.replace(anchor, """// A kartyan ulo fogaskerek. Ugyanaz a forma, mint az info gomb, csak a masik
// sarokban — igy ranezesre latszik, hogy a jateknak van sajat beallitasa.
function ConfigDot({ onOpen, pos }) {
  if (!onOpen) return null;
  return (
    <button onClick={e => { e.stopPropagation(); onOpen(); }} aria-label="Beállítások" style={Object.assign({
      position:'absolute', zIndex:3, borderRadius:'50%', border:'none', padding:0,
      background:T.surface, cursor:'pointer', display:'grid', placeItems:'center',
      boxShadow:'0 2px 6px rgba(0,0,0,0.12), 0 0 0 1px rgba(20,30,50,0.04)', color:T.inkSoft,
    }, pos)}>
      <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke={T.mintDeep} strokeWidth="2.4"
           strokeLinecap="round" strokeLinejoin="round">
        <circle cx="12" cy="12" r="3.2"/>
        <path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 1 1-2.83 2.83l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 1 1-4 0v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 1 1-2.83-2.83l.06-.06a1.65 1.65 0 0 0 .33-1.82 1.65 1.65 0 0 0-1.51-1H3a2 2 0 1 1 0-4h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 1 1 2.83-2.83l.06.06A1.65 1.65 0 0 0 9 4.6a1.65 1.65 0 0 0 1-1.51V3a2 2 0 1 1 4 0v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 1 1 2.83 2.83l-.06.06a1.65 1.65 0 0 0-.33 1.82V9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 1 1 0 4h-.09a1.65 1.65 0 0 0-1.51 1z"/>
      </svg>
    </button>
  );
}

""" + anchor)

# ── a harom csempe ── az info gombbal szemkozti sarokba
SITES = [
    # NetflixTile: az info gomb top:6/left:6 — a fogaskerek a jobb felso sarokba
    ("""        <button onClick={e => { e.stopPropagation(); onInfo(); }} style={{
          position: 'absolute', top: 6, left: 6,""",
     """        <ConfigDot onOpen={onLongPress} pos={{ top:6, right:6, width:26, height:26 }} />
        <button onClick={e => { e.stopPropagation(); onInfo(); }} style={{
          position: 'absolute', top: 6, left: 6,"""),
    # GameTile: az info gomb top:-9/left:-7
    ("""      <button onClick={e => { e.stopPropagation(); onInfo(); }} style={{
        position:'absolute', top:-9, left:-7, width:28, height:28, zIndex:2,""",
     """      <ConfigDot onOpen={onLongPress} pos={{ top:-9, right:-7, width:28, height:28 }} />
      <button onClick={e => { e.stopPropagation(); onInfo(); }} style={{
        position:'absolute', top:-9, left:-7, width:28, height:28, zIndex:2,"""),
    # FavTile: sorkartya, nincs info gomb — a jobb felso sarokba kerul
    ("""      {/* Color accent bar — a saroktól behúzva, hogy ne lógjon ki a lekerekített élen */}""",
     """      <ConfigDot onOpen={onLongPress} pos={{ top:-8, right:-6, width:26, height:26 }} />
      {/* Color accent bar — a saroktól behúzva, hogy ne lógjon ki a lekerekített élen */}"""),
]
for old, new in SITES:
    n = s.count(old)
    assert n == 1, f'{old[:60]!r}: {n} talalat (1 kellene)'
    s = s.replace(old, new)

assert s != orig
io.open(P, 'w', encoding='utf-8').write(s)
print('OK — fogaskerek mind a harom csempen')
