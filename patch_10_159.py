# v10.159 — a kijelolt pirula is a tema szinet kapja
#
# Egy kepernyon ketfele "kijelolt" nyelv elt egymas alatt:
#   - a fulsor (Profil / Jatekok / Beerpong / Busz) a tema szinet hasznalja: T.mint
#   - alatta a pirulak (Osszes/Szezon, Mind/Ma/7 nap/Egyedi) T.ink-et — az egy
#     semleges "tinta" szin, vilagos temaban sotetkek, sotetben majdnem feher.
# Ezert nem kovette a temat. Most a fulsorral azonos nyelvet hasznalnak.
#
# Csak a CSOPORTON BELULI kijelolt allapotok valtoznak. A magaban allo T.ink
# hattersu elemek (kod-bekuldo gomb, QR gomb, jelvenysav) maradnak — ott a
# tinta szandekos kiemeles, nem kijeloltseg, es az onInk() tartja olvashatoan.
import io

P = 'app.src.html'
s = io.open(P, encoding='utf-8').read()
orig = s

SITES = [
    # Liga: Osszes / Szezon nezetvalto
    ("background: view === v.k ? T.ink : 'transparent', color: view === v.k ? onInk() : (off ? T.inkMute : T.inkSoft)",
     "background: view === v.k ? T.mint : 'transparent', color: view === v.k ? '#fff' : (off ? T.inkMute : T.inkSoft)"),
    # Liga: szezon-valaszto pirulak
    ("background: seasonId === se.id ? T.ink : T.surface, color: seasonId === se.id ? onInk() : T.inkSoft,",
     "background: seasonId === se.id ? T.mint : T.surface, color: seasonId === se.id ? '#fff' : T.inkSoft,"),
    # Liga: idoszak-szuro (Mind / Ma / 7 nap / Egyedi)
    ("background: period === pr.key ? T.ink : T.surface, color: period === pr.key ? onInk() : T.inkSoft,",
     "background: period === pr.key ? T.mint : T.surface, color: period === pr.key ? '#fff' : T.inkSoft,"),
    # Admin: szezonzaras modja
    ("background: closeMode === m.k ? T.ink : 'transparent', color: closeMode === m.k ? onInk() : T.inkSoft,",
     "background: closeMode === m.k ? T.mint : 'transparent', color: closeMode === m.k ? '#fff' : T.inkSoft,"),
]
for old, new in SITES:
    n = s.count(old)
    assert n == 1, f'{old[:60]!r}: {n} talalat (1 kellene)'
    s = s.replace(old, new)

# Admin alfulek — a sor hosszabb, ezert csak a ket kulcsreszlet cserelodik
i = s.find("<button key={k} onClick={() => setTab(k)}")
assert i > 0, 'nincs admin alful'
line = s[i:s.find('\n', i)]
assert line.count("tab===k ? T.ink") == 1 and line.count("tab===k ? onInk()") == 1, line[:200]
s = s[:i] + line.replace("tab===k ? T.ink", "tab===k ? T.mint").replace("tab===k ? onInk()", "tab===k ? '#fff'") + s[s.find('\n', i):]

s = s.replace("const APP_VERSION = 'v10.158';", "const APP_VERSION = 'v10.159';", 1)
assert "v10.159" in s and s != orig
io.open(P, 'w', encoding='utf-8').write(s)
print('OK — 5 kijelolt-allapot a tema szinere allitva')
