# v10.180 — teszt / eles adatbazis kapcsolo
#
# A statisztika-kollekciok ket peldanyban leteznek. A MOSTANI, prefix nelkuli
# nevek maradnak a TESZT-adatnak — igy nem kellett egyetlen dokumentumot sem
# mozgatni ("a mostani legyen a teszt"). Az ELES adat uj, 'live_' prefixu
# kollekciokba kerul, tehat uresen, tisztan indul.
#
# Ami NEM valik szet: config (beallitasok, temak), profiles (ugyanazok az
# emberek), rooms (ugyis eldobhato), barDrinks, tasks, party_templates.
# A profilok szandekosan kozosek: ugyanaz az Anna, csak kulon statisztikaval.
import io, re

P = 'app.src.html'
s = io.open(P, encoding='utf-8').read()
orig = s

SPLIT = ['stats', 'statEvents', 'game_stats', 'gameStatEvents', 'usage', 'bp_tournaments']

# ── 1) a segedfuggveny ──
anchor = "  // Shared song blacklist: songs that never load get written here by any user"
assert s.count(anchor) == 1
s = s.replace(anchor, """  // ── Teszt / éles adatbázis ────────────────────────────────
  // A statisztika-kollekciók két példányban léteznek. A MOSTANI, prefix nélküli
  // nevek a TESZT-adatot tartják — így a váltáshoz nem kellett egyetlen
  // dokumentumot sem mozgatni. Az éles adat 'live_' prefixű kollekciókba megy,
  // tehát üresen indul.
  //
  // Alapértelmezés az ÉLES. Teszt módba a kezdőképernyőn a verziószámra
  // háromszor koppintva lehet váltani; az állapot eszközönként él
  // (localStorage), tehát egy teszt-telefon attól még nem viszi teszt módba a
  // többiek telefonját.
  var BOH_SPLIT_COLLECTIONS = %s;
  window.BOH_TESTDB_KEY = 'boh_testdb';
  window.isTestDb = function() {
    try { return localStorage.getItem(window.BOH_TESTDB_KEY) === '1'; } catch (e) { return false; }
  };
  window.setTestDb = function(on) {
    try { localStorage.setItem(window.BOH_TESTDB_KEY, on ? '1' : '0'); } catch (e) {}
  };
  // Minden statisztika-hivas ezen megy at. Futasidoben dont, nem betoltesekor —
  // igy a valtas utan az elso iras mar a helyere kerul.
  function coll(name) {
    var split = BOH_SPLIT_COLLECTIONS.indexOf(name) !== -1;
    return db.collection(split && !window.isTestDb() ? 'live_' + name : name);
  }

""" % str(SPLIT).replace("'", "'") + anchor)

# ── 2) a 18 hivas atvezetese ──
total = 0
for c in SPLIT:
    old = "db.collection('%s')" % c
    n = s.count(old)
    assert n > 0, c
    s = s.replace(old, "coll('%s')" % c)
    total += n
assert total == 18, total
# a definicion belul ne cserelodjon vissza
assert "return db.collection(split &&" in s, 'a coll() sajat hivasa serult'

# a maradek db.collection csak a NEM szetvalasztott kollekciokra mutasson
rest = set(re.findall(r"db\.collection\('([a-zA-Z_]+)'\)", s))
assert not (rest & set(SPLIT)), rest & set(SPLIT)

s = s.replace("const APP_VERSION = 'v10.179';", "const APP_VERSION = 'v10.180';", 1)
assert "v10.180" in s and s != orig
io.open(P, 'w', encoding='utf-8').write(s)
print('OK — coll() bevezetve, %d hivas atvezetve' % total)
