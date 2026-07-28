#!/usr/bin/env python3
# v10.181 — a teszt/eles kapcsolo GLOBALIS lesz
#
# Eszkozonkent tarolva az volt a baj, hogy ugyanazon a bulin az egyik telefon
# teszt-, a masik eles adatot irt volna — a parti statisztikaja ketfele esne.
# Mostantol a config/dbMode dokumentum dont mindenkinek.
#
# A localStorage megmarad, de mar csak GYORSITOTARKENT: a coll() szinkron dont
# (minden statisztika-hivasnal), a Firestore valasza viszont csak par tized
# masodperccel a betoltes utan erkezik. A gyorsitotar nelkul az elso par iras
# meg a regi helyre menne.
import sys

P = 'app.src.html'
src = open(P, encoding='utf-8').read()

OLD = """  // Alapértelmezés az ÉLES. Teszt módba a kezdőképernyőn a verziószámra
  // háromszor koppintva lehet váltani; az állapot eszközönként él
  // (localStorage), tehát egy teszt-telefon attól még nem viszi teszt módba a
  // többiek telefonját.
  var BOH_SPLIT_COLLECTIONS = ['stats', 'statEvents', 'game_stats', 'gameStatEvents', 'usage', 'bp_tournaments'];
  window.BOH_TESTDB_KEY = 'boh_testdb';
  window.isTestDb = function() {
    try { return localStorage.getItem(window.BOH_TESTDB_KEY) === '1'; } catch (e) { return false; }
  };
  window.setTestDb = function(on) {
    try { localStorage.setItem(window.BOH_TESTDB_KEY, on ? '1' : '0'); } catch (e) {}
  };
"""
assert src.count(OLD) == 1, 'testdb blokk: %d' % src.count(OLD)

NEW = """  // Alapértelmezés az ÉLES. Teszt módba a kezdőképernyőn a verziószámra
  // háromszor koppintva lehet váltani.
  //
  // A beállítás GLOBÁLIS: a config/dbMode dokumentum dönt, nem az eszköz — így
  // nem eshet ketté egy buli statisztikája attól, hogy az egyik telefon teszt
  // módban maradt. A localStorage csak gyorsítótár: a coll() szinkron dönt,
  // a Firestore válasza viszont csak a betöltés után pár tizeddel érkezik.
  var BOH_SPLIT_COLLECTIONS = ['stats', 'statEvents', 'game_stats', 'gameStatEvents', 'usage', 'bp_tournaments'];
  window.BOH_TESTDB_KEY = 'boh_testdb';
  window.isTestDb = function() {
    try { return localStorage.getItem(window.BOH_TESTDB_KEY) === '1'; } catch (e) { return false; }
  };
  window._setTestDbCache = function(on) {
    try { localStorage.setItem(window.BOH_TESTDB_KEY, on ? '1' : '0'); } catch (e) {}
  };
  window.setTestDb = function(on) {
    // Helyben azonnal — hogy a visszajelzés ne várjon a hálózatra.
    window._setTestDbCache(on);
    try {
      return db.collection('config').doc('dbMode').set({ test: !!on, ts: Date.now() });
    } catch (e) { return Promise.resolve(); }
  };
  // Aki máshol kapcsolt, itt is átáll. Újratöltés kell hozzá: a képernyőn már
  // a MÁSIK adatbázis adata állna, miközben az írás új helyre menne.
  try {
    db.collection('config').doc('dbMode').onSnapshot(function(d) {
      var v = !!(d && d.exists && d.data() && d.data().test);
      if (v === window.isTestDb()) return;
      window._setTestDbCache(v);
      location.reload();
    }, function() {});
  } catch (e) {}
"""
src = src.replace(OLD, NEW, 1)

# A visszajelzo szoveg mar nem csak errol az eszkozrol szol.
OLD_TOAST = """          {dbToast
            ? 'Teszt adatbázis bekapcsolva — a statisztika mostantól a teszt-adatokhoz megy.'
            : 'Éles adatbázis — a statisztika mostantól élesbe megy.'}"""
assert src.count(OLD_TOAST) == 1, 'toast szoveg: %d' % src.count(OLD_TOAST)
NEW_TOAST = """          {dbToast
            ? 'Teszt adatbázis — mostantól MINDEN eszközön a teszt-adatokhoz megy a statisztika.'
            : 'Éles adatbázis — mostantól MINDEN eszközön élesbe megy a statisztika.'}"""
src = src.replace(OLD_TOAST, NEW_TOAST, 1)

# verziobump
assert src.count("const APP_VERSION = 'v10.180';") == 1
src = src.replace("const APP_VERSION = 'v10.180';", "const APP_VERSION = 'v10.181';", 1)

open(P, 'w', encoding='utf-8').write(src)
print('OK — a kapcsolo globalis lett (config/dbMode)')
