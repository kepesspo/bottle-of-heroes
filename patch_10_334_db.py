# v10.334/b — ⚠️ A `db` NEM lathato az app szkriptjebol: a telefonos irasok
# csendben elhaltak.
#
# A `var db = firebase.firestore()` a Firebase-init IIFE-jeben ul, egy KULON
# `<script>` blokkban (app.src.html ~33920). Az alkalmazas a
# `<script type="text/babel">` blokkban van — onnan a `db` egyszeruen nincs
# hatokorben.
#
# Ot helyen bare `db`-vel irtunk, mindegyik `typeof db === 'undefined'` orzovel:
# az orzo MINDIG igaz, tehat a fuggveny visszatert, es a telefon irasa NYOM
# NELKUL elveszett. Nem volt hibauzenet — ez tette lathatatlanna.
#
# Merve: TapperObserverView-ban egy valodi lenyomas utan a szoba `tapperInput`
# mezoje `undefined` maradt.
#
# Ami MUKODOTT es ezert nem tunt fel: a `bjWrite` (Blackjack) es a `syncRoom` /
# `subscribeRoom` — azok `firebase.firestore()`-t hivnak kozvetlenul, illetve az
# init-IIFE-n belul vannak. Ezert ment a Blackjack telefonrol, a Tapper nem.
#
# A javitas EGY forras: `bohRoomRef(code)`.
import io

P = 'app.src.html'
src = io.open(P, encoding='utf-8').read()
orig = src

def sub1(old, new, what):
    global src
    assert src.count(old) == 1, f'{what}: {src.count(old)} talalat'
    src = src.replace(old, new)

# ── 1. a kozos hozzaferes ────────────────────────────────────────────────────
HELPER = """// ⚠️ A `db` a Firebase-init IIFE-jeben ul (kulon <script>), tehat INNEN, az app
// szkriptjebol nem lathato. Aki bare `db`-t irt, annak a `typeof db ===
// 'undefined'` orzoje MINDIG igaz volt: a telefon irasa nyom nelkul elveszett,
// hibauzenet nelkul. Ezert megy minden szoba-iras EZEN keresztul.
function bohRoomRef(code) {
  if (!code) return null;
  try { return firebase.firestore().collection('rooms').doc(code); } catch (e) { return null; }
}

function bjWrite(code, ns) {"""
sub1("function bjWrite(code, ns) {", HELPER, 'bohRoomRef beszurasa')

# ── 2. Kisebb/Nagyobb — a host torli a feldolgozott tippet ───────────────────
sub1("""      if (typeof db !== 'undefined') db.collection('rooms').doc(roomCode).update({ kisebbGuess: null }).catch(() => {});""",
     """      const _r = bohRoomRef(roomCode); if (_r) _r.update({ kisebbGuess: null }).catch(() => {});""",
     'Kisebb host-torles')

# ── 3. Tapper — a host sajat tavoli irasa ────────────────────────────────────
sub1("""  const writeTapperState = (playerName, down) => {
    if (!roomCode || !playerName || typeof db === 'undefined') return;
    db.collection('rooms').doc(roomCode).update({ [`tapperInput.${playerName}`]: down }).catch(() => {});
  };""",
     """  const writeTapperState = (playerName, down) => {
    const ref = playerName ? bohRoomRef(roomCode) : null;
    if (!ref) return;
    ref.update({ [`tapperInput.${playerName}`]: down }).catch(() => {});
  };""",
     'Tapper host-iras')

# ── 4. Kisebb/Nagyobb observer — a telefon tippje ────────────────────────────
sub1("""  const sendGuess = (guess) => {
    if (!myPlayer || typeof db === 'undefined' || voted || !isMyTurn) return;""",
     """  const sendGuess = (guess) => {
    const ref = myPlayer && !voted && isMyTurn ? bohRoomRef(code) : null;
    if (!ref) return;""",
     'Kisebb observer orzo')
sub1("""    db.collection('rooms').doc(code).update({ kisebbGuess: { pid: myPlayer.id, guess, ts } }).catch(() => {});""",
     """    ref.update({ kisebbGuess: { pid: myPlayer.id, guess, ts } }).catch(() => {});""",
     'Kisebb observer iras')

# ── 5. Tapper observer — a telefon nyomasa ───────────────────────────────────
sub1("""  const setRemote = (down) => {
    if (!myPlayer || typeof db === 'undefined') return;
    clearTimeout(writeRef.current);
    writeRef.current = setTimeout(() => {
      db.collection('rooms').doc(code).update({ [`tapperInput.${myPlayer.name}`]: down }).catch(() => {});
    }, 30);
  };""",
     """  const setRemote = (down) => {
    const ref = myPlayer ? bohRoomRef(code) : null;
    if (!ref) return;
    clearTimeout(writeRef.current);
    writeRef.current = setTimeout(() => {
      ref.update({ [`tapperInput.${myPlayer.name}`]: down }).catch(() => {});
    }, 30);
  };""",
     'Tapper observer iras')

# ── 6. Idoparbaj observer — az uj felulet ugyanezen az uton ir ───────────────
sub1("""  const write = (payload) => {
    if (!me || typeof db === 'undefined') return;
    const tok = Date.now().toString(36) + Math.random().toString(36).slice(2, 6);
    db.collection('rooms').doc(code).update({ ['idoInput.' + me.id]: { ...payload, tok } }).catch(() => {});
  };""",
     """  const write = (payload) => {
    const ref = me ? bohRoomRef(code) : null;
    if (!ref) return;
    const tok = Date.now().toString(36) + Math.random().toString(36).slice(2, 6);
    ref.update({ ['idoInput.' + me.id]: { ...payload, tok } }).catch(() => {});
  };""",
     'Idoparbaj observer iras')

assert src != orig
io.open(P, 'w', encoding='utf-8').write(src)
print('OK — patch_10_334_db alkalmazva')
