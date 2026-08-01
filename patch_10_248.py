#!/usr/bin/env python3
# v10.248 — a szoba-létrehozás nem ragadhat be némán
#
# A TÜNET: a Játékmenet képernyőn még nem töltöttek be a képek (= rossz háló),
# a felhasználó megnyomja a "Játék indítása" gombot, és a szoba létrehozásánál
# megáll.
#
# AZ OK, végigolvasva a láncot:
#   createRoom = db.collection('rooms').doc(code).set(...)
# és a Firestore-on BE VAN kapcsolva az offline perzisztencia (enablePersistence).
# Ilyenkor az írás HELYBEN azonnal érvényesül, de a visszaadott ígéret CSAK a
# SZERVER NYUGTÁJÁRA oldódik fel. Rossz vagy halott kapcsolaton tehát függőben
# marad — pontosan ugyanaz a hálózati állapot, amitől a képek sem töltődtek be.
#
# Volt rá védelem: egy 15 másodperces időtúllépés. Csakhogy 15 másodperc egy
# olyan képernyőn, ami normálisan fél másodpercig él, felhasználói szemmel
# BEFAGYÁS — és közben semmi nem jelzi, hogy baj van, se kiút nincs.
#
# A JAVÍTÁS három részből áll:
#   1. Kettős indítás elleni zár: amíg fut egy létrehozás, a második gombnyomás
#      nem indít újabb írást (eddig indított volna, saját 15 mp-es órával).
#   2. 4 másodperc után a töltőképernyőn megjelenik, hogy lassú a kapcsolat, és
#      ott helyben lehet OFFLINE indítani — a felhasználó soha nem ragad bent.
#   3. A kemény időtúllépés 15 → 11 mp, hogy a hibaképernyő ne egy örökkévalóság
#      után jöjjön.
#
# Amit NEM csinálunk: nem lépünk be magunktól a játékba a nyugta előtt. A helyi
# írás ugyan azonnal él, de ha sosem ér ki a szerverre, a vendégek nem tudnának
# csatlakozni a kódra — ezt a felhasználónak kell eldöntenie, nem nekünk.
import sys

P = 'app.src.html'
src = open(P, encoding='utf-8').read()

def sub(old, new, what):
    global src
    assert src.count(old) == 1, '%s: %d talalat' % (what, src.count(old))
    src = src.replace(old, new, 1)

# ── 1. állapot a "lassú a kapcsolat" jelzéshez ──
sub("""  const pendingRoomCodeRef = React.useRef(null);
  const roomUnsubRef = React.useRef(null);""",
    """  const pendingRoomCodeRef = React.useRef(null);
  const roomUnsubRef = React.useRef(null);
  // Lassu halonal a szoba-iras nyugtaja sokaig nem jon meg — 4 mp utan
  // kiirjuk, es felkinaljuk az offline inditast. Lasd patch_10_248.py
  const [roomSlow, setRoomSlow] = React.useState(false);
  const roomSlowTimerRef = React.useRef(null);
  const roomBusyRef = React.useRef(false);""",
    'roomSlow state')

# ── 2. attemptRoomCreate: zár + lassú-jelzés + rövidebb időtúllépés ──
sub("""  const attemptRoomCreate = (code) => {
    setRoomCreateError(null);
    setCreatingRoom(true);""",
    """  const attemptRoomCreate = (code) => {
    // Kettos inditas ellen: amig fut egy letrehozas, a masodik gombnyomas ne
    // inditson ujabb irast (sajat oraval, sajat idotullepessel).
    if (roomBusyRef.current) return;
    roomBusyRef.current = true;
    setRoomCreateError(null);
    setRoomSlow(false);
    setCreatingRoom(true);
    clearTimeout(roomSlowTimerRef.current);
    roomSlowTimerRef.current = setTimeout(() => setRoomSlow(true), 4000);""",
    'attemptRoomCreate zar')

sub("""    const roomCreateTimeout = new Promise((_, reject) => setTimeout(() => reject(new Error('Időtúllépés (15 mp) — a szerver nem válaszolt')), 15000));""",
    """    const roomCreateTimeout = new Promise((_, reject) => setTimeout(() => reject(new Error('Időtúllépés (11 mp) — a szerver nem válaszolt')), 11000));""",
    'idotullepes')

sub("""      .then(() => {
        setRoomCode(code);
        if (roomUnsubRef.current) roomUnsubRef.current();""",
    """      .then(() => {
        roomBusyRef.current = false;
        clearTimeout(roomSlowTimerRef.current); setRoomSlow(false);
        setRoomCode(code);
        if (roomUnsubRef.current) roomUnsubRef.current();""",
    'siker ag')

sub("""      .catch((e) => {
        console.error('createRoom failed:', e);
        const msg = e ? ((e.code ? e.code + ' — ' : '') + (e.message || String(e))) : 'ismeretlen hiba';
        setRoomCreateError(msg);
      });""",
    """      .catch((e) => {
        roomBusyRef.current = false;
        clearTimeout(roomSlowTimerRef.current); setRoomSlow(false);
        console.error('createRoom failed:', e);
        const msg = e ? ((e.code ? e.code + ' — ' : '') + (e.message || String(e))) : 'ismeretlen hiba';
        setRoomCreateError(msg);
      });""",
    'hiba ag')

# ── 3. kiút a töltőképernyőn ──
sub("""              <div style={{ fontFamily:T.font, fontSize:13, color:T.inkSoft, textAlign:'center', marginTop:-8 }}>Mindjárt kész</div>""",
    """              <div style={{ fontFamily:T.font, fontSize:13, color:T.inkSoft, textAlign:'center', marginTop:-8 }}>
                {roomSlow ? 'Lassú a kapcsolat — még próbálkozunk…' : 'Mindjárt kész'}
              </div>
              {/* 4 mp utan kiut: soha ne ragadjon bent a felhasznalo. Az offline
                  inditas ugyanaz, mint a hibakepernyon — csak nem kell megvarni
                  az idotullepest hozza. */}
              {roomSlow && (
                <button onClick={() => {
                    roomBusyRef.current = false;
                    clearTimeout(roomSlowTimerRef.current);
                    setRoomSlow(false); setCreatingRoom(false); setRoomCreateError(null);
                    setPrev(screen); setScreen('play');
                  }}
                  style={{ marginTop:14, padding:'12px 20px', borderRadius:16, border:`1.5px solid ${T.inkMute}40`, background:T.surface, fontFamily:T.font, fontWeight:800, fontSize:14, color:T.inkSoft, cursor:'pointer', boxShadow:T.shadowPill }}>
                  Indítás offline (kód nélkül)
                </button>
              )}""",
    'kiut a toltokepernyon')

sub("const APP_VERSION = 'v10.247';", "const APP_VERSION = 'v10.248';", 'verzio')
open(P, 'w', encoding='utf-8').write(src)
print('OK — nincs nema befagyas a szoba letrehozasanal')
