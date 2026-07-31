#!/usr/bin/env python3
# v10.240 — Ország-Város: a host végtelen írási hurokba került; és a
#           szoba-figyelő hiba után nem épült újra
#
# TÜNET: a host továbbnyomta, a telefonos nézet nem reagált, beakadt.
#
# 1) VÉGTELEN ÍRÁSI HUROK (ez a fő ok)
#    A host feliratkozik a szoba dokumentumára, és a beérkezett válaszokat így
#    tette el:
#        if (Object.keys(na).length) setAnswers(prev => ({...prev, ...na}));
#    Ez MINDIG új objektumot ad vissza, tehát az `answers` referenciája minden
#    pillanatképnél változik. Az `answers` viszont benne van annak az
#    effektnek a függőségeiben, amelyik a teljes ovfjState-et KIÍRJA a szobába.
#    Írás → pillanatkép → új objektum → írás → …
#
#    Mérve (a javítás előtti buildben, 2 játékos, 1 beérkezett válasz):
#        2 másodperc alatt ~14 700 írás UGYANARRA a dokumentumra.
#
#    A Firestore egy dokumentumra kb. 1 írás/másodpercet bír tartósan. Ilyen
#    terhelés mellett a sorbanállás percesre nő, a host fázisváltása pedig
#    egyszerűen nem ér oda a telefonokhoz — pontosan a bejelentett tünet.
#
#    Javítás: csak akkor frissítjük az állapotot, ha tényleg VÁLTOZOTT.
#    A rekordok laposak (string/szám/bool), ezért a sekély összehasonlítás
#    pontos és kulcssorrend-független.
#
# 2) A SZOBA-FIGYELŐ NEM ÉPÜLT ÚJRA HIBA UTÁN
#    A subscribeRoom csak sikeres visszahívást adott át az onSnapshot-nak,
#    hibakezelőt nem. A Firestore a hibás figyelőt MEGSZÜNTETI — kezelő nélkül
#    a képernyő csendben befagy, és magától soha nem tér magához.
#    Javítás: hibakezelő + exponenciális újracsatlakozás, plusz azonnali
#    újracsatlakozás, ha a böngésző jelzi, hogy visszajött a háló.
import sys

P = 'app.src.html'
src = open(P, encoding='utf-8').read()

def sub(old, new, what):
    global src
    assert src.count(old) == 1, '%s: %d talalat' % (what, src.count(old))
    src = src.replace(old, new, 1)

# ── 1. subscribeRoom: hibakezelés + újracsatlakozás ──
sub("""  window.subscribeRoom = function(code, cb) {
    return db.collection('rooms').doc(code).onSnapshot(function(d){ cb(d.exists ? d.data() : null); });
  };""",
    """  // A Firestore a hibara futott figyelot MEGSZUNTETI. Hibakezelo nelkul a
  // kepernyo csendben befagy — a host tovabblep, a telefon marad az utolso
  // allapoton, es magatol soha nem ter magahoz. Ezert: ujracsatlakozas
  // exponencialis varakozassal, es azonnal, ha visszajott a halo.
  window.subscribeRoom = function(code, cb) {
    var stopped = false, inner = null, tries = 0, timer = null;
    function attach() {
      if (stopped) return;
      timer = null;
      inner = db.collection('rooms').doc(code).onSnapshot(
        function(d) { tries = 0; cb(d.exists ? d.data() : null); },
        function(err) {
          console.warn('subscribeRoom', err);
          inner = null;
          if (stopped) return;
          var delay = Math.min(30000, 1000 * Math.pow(2, tries++));
          timer = setTimeout(attach, delay);
        }
      );
    }
    function onOnline() {
      if (stopped || inner || !timer) return;
      clearTimeout(timer); timer = null; tries = 0; attach();
    }
    try { window.addEventListener('online', onOnline); } catch (e) {}
    attach();
    return function() {
      stopped = true;
      if (timer) clearTimeout(timer);
      try { window.removeEventListener('online', onOnline); } catch (e) {}
      if (inner) inner();
    };
  };""",
    'subscribeRoom ujracsatlakozas')

# ── 2. sekély összehasonlító az OVFJ rekordokhoz ──
sub("""const ovfjAKey = id => 'ovfjA' + String(id).replace(/[^a-zA-Z0-9]/g,'x');""",
    """// A szoba-pillanatkepbol jovo rekordok laposak (string/szam/bool), ezert a
// sekely osszehasonlitas pontos — es kulcssorrend-fuggetlen, ami azert kell,
// mert a helyben epitett es a Firestore-bol visszaolvasott objektum kulcsainak
// sorrendje eltérhet.
const ovfjSameRec = (a, b) => {
  if (a === b) return true;
  if (!a || !b || typeof a !== 'object' || typeof b !== 'object') return false;
  const ka = Object.keys(a), kb = Object.keys(b);
  if (ka.length !== kb.length) return false;
  return ka.every(k => a[k] === b[k]);
};
const ovfjAKey = id => 'ovfjA' + String(id).replace(/[^a-zA-Z0-9]/g,'x');""",
    'ovfjSameRec')

# ── 3. a hurok megszuntetese: csak valos valtozasnal frissitunk ──
sub("""      if (Object.keys(na).length) setAnswers(prev => ({...prev, ...na}));
      if (Object.keys(nv).length) setVotes(prev => { const m = {...prev}; Object.entries(nv).forEach(([vk, per]) => { m[vk] = {...(m[vk]||{}), ...per}; }); return m; });""",
    """      // FONTOS: csak akkor allitsunk allapotot, ha TENYLEG valtozott.
      // A `{...prev, ...na}` mindig UJ objektumot ad, es az `answers` benne van
      // annak az effektnek a fuggosegeiben, amelyik kiirja az ovfjState-et a
      // szobaba — igy minden pillanatkep egy ujabb irast szult, az meg egy
      // ujabb pillanatkepet. Vegtelen hurok, masodpercenkent tobb ezer irassal
      // ugyanarra a dokumentumra; a Firestore ~1 iras/mp-et bir tartosan, ezert
      // a host fazisvaltasa nem ert oda a telefonokhoz.
      if (Object.keys(na).length) setAnswers(prev => {
        let changed = false;
        const out = {...prev};
        Object.keys(na).forEach(pid => {
          if (!ovfjSameRec(prev[pid], na[pid])) { out[pid] = na[pid]; changed = true; }
        });
        return changed ? out : prev;
      });
      if (Object.keys(nv).length) setVotes(prev => {
        let changed = false;
        const m = {...prev};
        Object.keys(nv).forEach(vk => {
          const merged = {...(prev[vk]||{}), ...nv[vk]};
          if (!ovfjSameRec(prev[vk], merged)) { m[vk] = merged; changed = true; }
        });
        return changed ? m : prev;
      });""",
    'irasi hurok megszuntetese')

sub("const APP_VERSION = 'v10.239';", "const APP_VERSION = 'v10.240';", 'verzio')
open(P, 'w', encoding='utf-8').write(src)
print('OK — nincs tobbe iras-hurok; a szoba-figyelo ujraepul')
