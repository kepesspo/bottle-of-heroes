#!/usr/bin/env python3
# v10.242 — Blackjack: biztosítás (insurance) + lapszétválasztás (split)
#
# ── A MODELL VÁLTOZÁSA ────────────────────────────────────────────────────────
# Eddig minden a JÁTÉKOSHOZ volt kötve: hands[pid], bets[pid], stood[pid], …
# Split után viszont nem a játékos, hanem a KÉZ az alapegység.
#
# Megoldás: kéz-kulcs. Az első kéz kulcsa maga a pid, a split-kezeké pid+'#1',
# pid+'#2', … Így az összes eddigi map ugyanabban az alakban működik tovább
# (hands[kulcs], bets[kulcs], stood[kulcs], …), egy régi — split nélküli —
# szoba pedig változatlanul olvasható marad: ott a pid az egyetlen kéz-kulcs.
# A sorrendet a handKeys[pid] tömb tartja, nem prefix-találgatás.
#
# ── BIZTOSÍTÁS ───────────────────────────────────────────────────────────────
# Csak akkor, ha az osztó Ászt mutat. Új 'insurance' fázis a leosztás után:
# mindenki EGYSZERRE dönt (a telefonján vagy a hoston). A tét fele, 1-re
# kerekítve (a 4. döntésed szerint). 2:1-et fizet.
#   Figyelem: 1 zsetonos tétnél a fele 1-re kerekítve azt jelenti, hogy az
#   osztó Blackjackje +1 zsetont hoz (−1 fő tét, +2 biztosítás). Ez tudatos
#   döntés volt, nem hiba — csak jelezzük, hogy nem véletlen.
# Ha az osztónak tényleg Blackjackje van, a kör azonnal az eredményekre ugrik.
#
# ── SPLIT ────────────────────────────────────────────────────────────────────
# Azonos ÉRTÉKŰ első két lap (K+10 is), újabb ugyanakkora tét, két külön kéz.
# Re-split engedve, összesen 4 kézig (kaszinó-szokás).
# Ász-split: kezenként PONTOSAN egy lap, tovább nem játszható, nem osztható.
# Split után a 21 NEM Blackjack — 1:1-et fizet (fromSplit jelöli).
import sys

P = 'app.src.html'
src = open(P, encoding='utf-8').read()

def sub(old, new, what):
    global src
    assert src.count(old) == 1, '%s: %d talalat' % (what, src.count(old))
    src = src.replace(old, new, 1)

# ═══════════ 1. Segédfüggvények + bjAdvanceTurn kéz-alapúra ═══════════
sub("""function bjAdvanceTurn(state) {
  const parts = state.participants || [];
  const rem = parts.filter(pid => !state.stood[pid] && !state.bust[pid]);
  if (rem.length === 0) return { ...state, phase:'dealer', currentTurn:null };
  const curIdx = parts.indexOf(state.currentTurn);
  const next = rem.find(pid => parts.indexOf(pid) > curIdx) || rem[0];
  return { ...state, currentTurn: next };
}""",
"""// ── Kéz-kulcs: split óta a KÉZ az alapegység, nem a játékos ──────────────
// Az első kéz kulcsa maga a pid, a split-kezeké pid+'#1', pid+'#2', …
// Így a hands/bets/stood/bust/doubled map-ek alakja NEM változott, és egy régi
// (split nélküli) szoba is olvasható marad. A sorrendet a handKeys[pid] tartja.
const BJ_MAX_HANDS = 4;
function bjPidOfHand(hk) { return String(hk).split('#')[0]; }
function bjHandsOf(state, pid) {
  const ks = ((state || {}).handKeys || {})[pid];
  return (ks && ks.length) ? ks : [pid];
}
function bjAllHandKeys(state) {
  const out = [];
  ((state || {}).participants || []).forEach(pid => bjHandsOf(state, pid).forEach(k => out.push(k)));
  return out;
}
function bjRankOf(card) { return String(card).replace(/[\\u2660\\u2665\\u2666\\u2663]/g, ''); }
function bjIsAceCard(card) { return bjRankOf(card) === 'A'; }
// Azonos ERTEKU par (K+10 is), nem csak azonos rang
function bjPairValue(hand) {
  if (!hand || hand.length !== 2) return null;
  const a = bjCardValue(bjRankOf(hand[0])), b = bjCardValue(bjRankOf(hand[1]));
  return a === b ? a : null;
}
function bjChipsOf(state, pid, fallback) {
  const c = ((state || {}).chips || {})[pid];
  return c === undefined ? fallback : c;
}
// A jatekos OSSZES kezere feltett tet — ez foglalja le a zsetonjait
function bjCommitted(state, pid) {
  return bjHandsOf(state, pid).reduce((s, k) => s + (((state || {}).bets || {})[k] || 0), 0);
}
function bjIsHandBJ(state, hk) {
  // Split utan a 21 NEM Blackjack — 1:1-et fizet
  return bjIsBlackjack(((state || {}).hands || {})[hk] || []) && !(((state || {}).fromSplit || {})[hk]);
}
function bjCanSplit(state, hk, chipsAvail) {
  if (!state || !state.allowSplit) return false;
  const pid = bjPidOfHand(hk);
  const hand = (state.hands || {})[hk] || [];
  if (bjPairValue(hand) === null) return false;
  if ((state.aceSplit || {})[hk]) return false;          // asz-splitet nem osztunk tovabb
  if ((state.doubled || {})[hk]) return false;
  if (bjHandsOf(state, pid).length >= BJ_MAX_HANDS) return false;
  const bet = (state.bets || {})[hk] || 1;
  return chipsAvail >= bjCommitted(state, pid) + bet;
}
function bjCanDouble(state, hk, chipsAvail) {
  if (!state) return false;
  const pid = bjPidOfHand(hk);
  const hand = (state.hands || {})[hk] || [];
  if (hand.length !== 2) return false;
  if ((state.doubled || {})[hk]) return false;
  if ((state.aceSplit || {})[hk]) return false;
  const bet = (state.bets || {})[hk] || 1;
  return chipsAvail >= bjCommitted(state, pid) + bet;
}
function bjDoSplit(state, hk) {
  const pid = bjPidOfHand(hk);
  const hand = (state.hands || {})[hk] || [];
  if (hand.length !== 2) return state;
  const keys = bjHandsOf(state, pid);
  let n = 1; while (keys.includes(pid + '#' + n)) n++;
  const nk = pid + '#' + n;
  const deck = [...state.deck];
  const h1 = [hand[0], bjPop(deck)];
  const h2 = [hand[1], bjPop(deck)];
  const order = [...keys];
  order.splice(order.indexOf(hk) + 1, 0, nk);
  const aces = bjIsAceCard(hand[0]);
  let ns = { ...state, deck,
    hands: { ...state.hands, [hk]: h1, [nk]: h2 },
    bets: { ...state.bets, [nk]: (state.bets || {})[hk] || 1 },
    handKeys: { ...(state.handKeys || {}), [pid]: order },
    fromSplit: { ...(state.fromSplit || {}), [hk]: true, [nk]: true },
    aceSplit: aces ? { ...(state.aceSplit || {}), [hk]: true, [nk]: true } : (state.aceSplit || {}),
  };
  if (aces) {
    // Asz-split: kezenkent PONTOSAN egy lap, utana automatikusan all
    ns.stood = { ...ns.stood, [hk]: true, [nk]: true };
    ns = bjAdvanceTurn(ns);
  }
  return ns;
}
// ── Biztositas ──────────────────────────────────────────────────────────────
// A tet fele, 1-re kerekitve; annyit tehet fel, amennyi a fo teten FELUL van.
function bjInsuranceAmount(state, pid) {
  const bet = ((state || {}).bets || {})[pid] || 1;
  const want = Math.max(1, Math.round(bet / 2));
  const chips = ((state || {}).chips || {})[pid];
  if (chips === undefined) return want;
  return Math.max(0, Math.min(want, chips - bet));
}
function bjInsuranceResult(state, pid) {
  const ins = ((state || {}).insurance || {})[pid] || 0;
  if (!ins) return { ins: 0, delta: 0 };
  return { ins, delta: bjIsBlackjack((state || {}).dealerHand) ? ins * 2 : -ins };
}
function bjAfterInsurance(state) {
  // Az oszto belenez a lapjaba: ha Blackjack, a kor azonnal ver
  if (bjIsBlackjack(state.dealerHand)) return { ...state, phase:'dealer', currentTurn:null };
  const rem = bjAllHandKeys(state).filter(k => !state.stood[k] && !state.bust[k]);
  return { ...state, phase: rem.length ? 'playing' : 'dealer', currentTurn: rem[0] || null };
}
// Egy jatekos teljes koregyenlege: minden keze + a biztositas
function bjPlayerDelta(state, pid) {
  let d = 0;
  bjHandsOf(state, pid).forEach(k => { d += bjResultFor(state, k).delta; });
  d += bjInsuranceResult(state, pid).delta;
  return d;
}

function bjAdvanceTurn(state) {
  const keys = bjAllHandKeys(state);
  const rem = keys.filter(k => !state.stood[k] && !state.bust[k]);
  if (rem.length === 0) return { ...state, phase:'dealer', currentTurn:null };
  const curIdx = keys.indexOf(state.currentTurn);
  const next = rem.find(k => keys.indexOf(k) > curIdx) || rem[0];
  return { ...state, currentTurn: next };
}""",
    'kez-kulcs helperek')

# ═══════════ 2. bjDeal: kéz-kulcsok + biztosítás-fázis ═══════════
sub("""  const stood = {};
  (state.participants || []).forEach(pid => { if (bjIsBlackjack(hands[pid])) stood[pid] = true; });
  const rem = (state.participants || []).filter(pid => !stood[pid]);
  return { ...state, phase: rem.length ? 'playing' : 'dealer', deck, hands, dealerHand, stood, bust: {}, doubled: {}, currentTurn: rem[0] || null };""",
"""  const stood = {};
  (state.participants || []).forEach(pid => { if (bjIsBlackjack(hands[pid])) stood[pid] = true; });
  const handKeys = {};
  (state.participants || []).forEach(pid => { handKeys[pid] = [pid]; });
  const base = { ...state, deck, hands, dealerHand, stood, bust: {}, doubled: {},
                 handKeys, fromSplit: {}, aceSplit: {}, insurance: {}, insDone: {} };
  // Biztositas csak akkor, ha az oszto ASZT mutat — a kor megall, mindenki
  // egyszerre dont, es csak utana kezdodik a jatek.
  if (state.allowIns && bjIsAceCard(dealerHand[0])) return { ...base, phase:'insurance', currentTurn:null };
  const rem = (state.participants || []).filter(pid => !stood[pid]);
  return { ...base, phase: rem.length ? 'playing' : 'dealer', currentTurn: rem[0] || null };""",
    'bjDeal')

# ═══════════ 3. bjResultFor: kéz-kulcs + split-21 nem Blackjack ═══════════
sub("""function bjResultFor(state, pid) {
  const ds = bjScore(state.dealerHand), dBJ = bjIsBlackjack(state.dealerHand);
  const hand = state.hands[pid] || [], ps = bjScore(hand), pBJ = bjIsBlackjack(hand);
  const bet = state.bets[pid] || 1;
  if (state.bust[pid])   return { label:'Besokallt 💀', delta: -bet };""",
"""// FIGYELEM: a masodik parameter mostantol KEZ-kulcs, nem jatekos-azonosito.
// Split nelkul a ketto ugyanaz, ezert a regi hivasok is helyesek maradnak.
function bjResultFor(state, hk) {
  const ds = bjScore(state.dealerHand), dBJ = bjIsBlackjack(state.dealerHand);
  const hand = state.hands[hk] || [], ps = bjScore(hand);
  const pBJ = bjIsHandBJ(state, hk);
  const pid = hk;
  const bet = state.bets[hk] || 1;
  if (state.bust[hk])    return { label:'Besokallt 💀', delta: -bet };""",
    'bjResultFor fej')

# ═══════════ 4. a kör indítása: a beállítások bekerülnek az állapotba ═══════════
sub("""    update({ ...bjState, phase:'betting', participants: parts, chips, bets, betsDone: {}, deck: bjNewDeck(), hands: {}, dealerHand: [], stood: {}, bust: {}, doubled: {}, currentTurn: null, brokeDrank });""",
"""    // A ket bovites kapcsoloja BEKERUL az allapotba, hogy a telefon is
    // ugyanabbol olvassa — ne kelljen neki a gameMeta.
    update({ ...bjState, phase:'betting', participants: parts, chips, bets, betsDone: {}, deck: bjNewDeck(), hands: {}, dealerHand: [], stood: {}, bust: {}, doubled: {}, currentTurn: null, brokeDrank,
             allowIns: bjAllowIns, allowSplit: bjAllowSplit,
             handKeys: {}, fromSplit: {}, aceSplit: {}, insurance: {}, insDone: {} });""",
    'startRound')

sub("""function BlackjackGame({ players, roomCode, gameIdx, gameMeta, onAdvance, onSetHideFooter, onLiveDrinkUpdate, onSetBuszSwitch }) {""",
"""function BlackjackGame({ players, roomCode, gameIdx, gameMeta, onAdvance, onSetHideFooter, onLiveDrinkUpdate, onSetBuszSwitch }) {
  const bjCfg = (gameMeta && gameMeta.blackjackConfig) || {};
  const bjAllowIns = bjCfg.insurance !== false;     // alapbol BE
  const bjAllowSplit = bjCfg.split !== false;       // alapbol BE""",
    'config olvasas')

# ═══════════ 5. kiosztás: kezenkénti elszámolás + biztosítás ═══════════
sub("""      const chips = { ...(bjState.chips || {}) };
      (bjState.participants || []).forEach(pid => {
        const r = bjResultFor(preState, pid);
        chips[pid] = Math.max(0, (chips[pid] === undefined ? stackOf(pid) : chips[pid]) + r.delta);
      });""",
"""      const chips = { ...(bjState.chips || {}) };
      // Split ota egy jatekosnak tobb keze is lehet — mindegyik kulon dol el,
      // es a biztositas is ide jon (az a jatekoshoz tartozik, nem a kezhez).
      (bjState.participants || []).forEach(pid => {
        const d = bjPlayerDelta(preState, pid);
        chips[pid] = Math.max(0, (chips[pid] === undefined ? stackOf(pid) : chips[pid]) + d);
      });""",
    'dealer elszamolas')

sub("const APP_VERSION = 'v10.241';", "const APP_VERSION = 'v10.242';", 'verzio')
open(P, 'w', encoding='utf-8').write(src)
print('OK — 1. resz: modell (kez-kulcs), biztositas-fazis, elszamolas')
