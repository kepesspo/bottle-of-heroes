# v10.337 - A "Jatek inditasa" gomb csak akkor el, ha a halozat mar kesz
#
# A BEJELENTES: "ha tul gyorsan nyomom a jatekmenet utan a jatek inditasa gombot,
# akkor beragad a szoba letrehozasa kepernyo. Amit latok, hogy valaminek a
# letoltese/betoltese nem tortent meg."
#
# KET OK, es a masodik magyarazza a "beragadast":
#
# 1) A szobanyitas az ELSO Firestore-korfordulo. Indulas utan par tizedmasodpercig
#    a halozati csatorna meg epul (`enablePersistence`, long-polling felderites),
#    tehat a legelso iras a leglassabb. A gomb eddig ez alatt is elo volt.
#
# 2) ⚠️ A `config/dbMode` figyelo `location.reload()`-ot hiv, ha az eszkoz
#    gyorsitotarazott teszt/eles beallitasa mas, mint a szerveren levo. Ez a
#    pillanatkep a BETOLTES UTAN par tizeddel erkezik - pont abba az ablakba,
#    amikor a gyors felhasznalo mar a "Toltjuk a szobat" kepernyon all. Az
#    ujratoltes elvagja a folyamatban levo szoba-irast: a kepernyo eltunik,
#    a szoba nem jon letre. Innentol a felhasznalo mar egy MASIK oldalt nez.
#
# A JAVITAS
#   - `window.bohNetReady` + `window.onBohNetReady(cb)`: akkor all keszre, ha az
#     elso `config/dbMode` pillanatkep megjott (szerverrol vagy hibaval), VAGY
#     8 mp utan. Az idokorlat nem elhagyhato: offline is el kell tudni indulni.
#   - A ket "Jatek inditasa" gomb (Jatekok es Jatekmenet kepernyo) addig
#     letiltva, "Betoltes..." felirattal.
#   - Az ujratoltes HALASZTOTT, amig a szoba-letrehozas fut (`window.__bohBusy`).
#     A dbMode valtas ritka; egy folyamatban levo parti-inditast nem szakithat meg.
import io

P = 'app.src.html'
src = io.open(P, encoding='utf-8').read()
orig = src

def sub1(old, new, what):
    global src
    assert src.count(old) == 1, '%s: %d talalat' % (what, src.count(old))
    src = src.replace(old, new)

# --- 1. a keszenlet-jelzo a Firebase-init IIFE-ben ---------------------------
sub1(
"""  // Aki máshol kapcsolt, itt is átáll. Újratöltés kell hozzá: a képernyőn már
  // a MÁSIK adatbázis adata állna, miközben az írás új helyre menne.
  try {
    db.collection('config').doc('dbMode').onSnapshot(function(d) {""",
"""  // ── HALOZATI KESZENLET ────────────────────────────────────────────────────
  // A szobanyitas az ELSO Firestore-korfordulo, es indulas utan par tizedig a
  // csatorna meg epul (persistence, long-polling felderites). Aki azonnal nyomja
  // a "Jatek inditasa"-t, pont ebbe fut bele. A gomb ezert addig letiltva, amig
  // ez a jelzo keszre nem all.
  //
  // Keszre allitja: az elso `config/dbMode` pillanatkep (akar hibaval), vagy egy
  // 8 mp-es idokorlat. Az idokorlat NEM elhagyhato: offline is el kell tudni
  // indulni, csak akkor a felhasznalo dont a "kod nelkul" inditasrol.
  window.bohNetReady = false;
  window._bohNetCbs = [];
  window.onBohNetReady = function (cb) {
    if (window.bohNetReady) { try { cb(); } catch (e) {} return; }
    window._bohNetCbs.push(cb);
  };
  function _bohMarkNetReady() {
    if (window.bohNetReady) return;
    window.bohNetReady = true;
    var cbs = window._bohNetCbs; window._bohNetCbs = [];
    cbs.forEach(function (c) { try { c(); } catch (e) {} });
  }
  setTimeout(_bohMarkNetReady, 8000);

  // Aki máshol kapcsolt, itt is átáll. Újratöltés kell hozzá: a képernyőn már
  // a MÁSIK adatbázis adata állna, miközben az írás új helyre menne.
  try {
    db.collection('config').doc('dbMode').onSnapshot(function(d) {
      // A korfordulo megvolt - innentol a szobanyitas is mehet.
      _bohMarkNetReady();""",
'netReady jelzo')

sub1(
"""      if (v === window.isTestDb()) return;
      window._setTestDbCache(v);
      location.reload();
    }, function() {});""",
"""      if (v === window.isTestDb()) return;
      window._setTestDbCache(v);
      // ⚠️ NEM toltunk ujra parti-inditas kozben. Ez a pillanatkep par
      // tizedmasodperccel a betoltes utan erkezik - pont akkor, amikor a gyors
      // felhasznalo mar a "Toltjuk a szobat" kepernyon all. Az ujratoltes
      // elvagta a folyamatban levo szoba-irast, es a szoba nem jott letre.
      if (window.__bohBusy) { window.__bohPendingReload = true; return; }
      location.reload();
    }, function() { _bohMarkNetReady(); });""",
'reload halasztas')

# --- 2. az App: keszenlet-allapot es a foglaltsag-jelzo ----------------------
sub1(
"  const [creatingRoom, setCreatingRoom] = React.useState(false);",
"""  const [creatingRoom, setCreatingRoom] = React.useState(false);
  // A "Jatek inditasa" gomb eddig el, amig a halozat kesz nem lesz (lasd a
  // Firebase-init `bohNetReady` jelzojet).
  const [netReady, setNetReady] = React.useState(() => typeof window !== 'undefined' && !!window.bohNetReady);
  React.useEffect(() => {
    if (netReady) return;
    if (typeof window.onBohNetReady === 'function') window.onBohNetReady(() => setNetReady(true));
    else setNetReady(true);
  }, []);
  // A szoba-letrehozas alatt a dbMode-valtas ujratoltese HALASZTVA van.
  React.useEffect(() => {
    window.__bohBusy = creatingRoom;
    if (!creatingRoom && window.__bohPendingReload) { window.__bohPendingReload = false; location.reload(); }
  }, [creatingRoom]);""",
'netReady allapot')

# --- 3. a ket "Jatek inditasa" gomb -----------------------------------------
sub1(
"""      <BottomBar>
        <PrimaryButton disabled={(selectedGames || []).length < 1} onClick={() => go('play')}>
          <span>{t('startGame')} ({(selectedGames || []).length})</span>
          <span style={{ display:'block', fontWeight:600, fontSize:12, opacity:0.75, marginTop:2 }}>⏱ kb. {minutes} perc</span>
        </PrimaryButton>
      </BottomBar>""",
"""      <BottomBar>
        <PrimaryButton disabled={(selectedGames || []).length < 1 || !netReady} onClick={() => go('play')}>
          <span>{netReady ? t('startGame') : 'Betöltés…'} ({(selectedGames || []).length})</span>
          <span style={{ display:'block', fontWeight:600, fontSize:12, opacity:0.75, marginTop:2 }}>
            {netReady ? `⏱ kb. ${minutes} perc` : 'Mindjárt indulhat'}
          </span>
        </PrimaryButton>
      </BottomBar>""",
'SetupScreen gomb')

sub1(
"""        <PrimaryButton disabled={selectedGames.length < 1} onClick={() => go(setupFlow ? 'setup' : 'play')}>
          <span>{setupFlow ? 'Tovább' : t('startGame')} ({selectedGames.length})</span>""",
"""        <PrimaryButton disabled={selectedGames.length < 1 || (!setupFlow && !netReady)} onClick={() => go(setupFlow ? 'setup' : 'play')}>
          <span>{setupFlow ? 'Tovább' : (netReady ? t('startGame') : 'Betöltés…')} ({selectedGames.length})</span>""",
'GamesScreen gomb')

# --- 4. a netReady propkent lemegy a ket kepernyore --------------------------
sub1(
"function SetupScreen({ go, players, selectedGames, gameMeta, setGameMeta }) {",
"function SetupScreen({ go, players, selectedGames, gameMeta, setGameMeta, netReady = true }) {",
'SetupScreen signature')
sub1(
"function GamesScreen({ selectedGames, setSelectedGames, gameMeta, setGameMeta, go, players }) {",
"function GamesScreen({ selectedGames, setSelectedGames, gameMeta, setGameMeta, go, players, netReady = true }) {",
'GamesScreen signature')
sub1(
"        {screen==='setup'    && <SetupScreen    go={go} players={players} selectedGames={selectedGames} gameMeta={gameMeta} setGameMeta={setGameMeta} />}",
"        {screen==='setup'    && <SetupScreen    go={go} players={players} selectedGames={selectedGames} gameMeta={gameMeta} setGameMeta={setGameMeta} netReady={netReady} />}",
'SetupScreen prop')
sub1(
"        {screen==='games'    && <GamesScreen    go={go} players={players} selectedGames={selectedGames} setSelectedGames={setSelectedGames} gameMeta={gameMeta} setGameMeta={setGameMeta} />}",
"        {screen==='games'    && <GamesScreen    go={go} players={players} selectedGames={selectedGames} setSelectedGames={setSelectedGames} gameMeta={gameMeta} setGameMeta={setGameMeta} netReady={netReady} />}",
'GamesScreen prop')

sub1("const APP_VERSION = 'v10.336';", "const APP_VERSION = 'v10.337';", 'verzio')

assert src != orig
io.open(P, 'w', encoding='utf-8').write(src)
print('OK - patch_10_337 alkalmazva')
