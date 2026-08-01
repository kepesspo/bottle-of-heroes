#!/usr/bin/env python3
# v10.274 — a buntetes-korty nem veszhet el a Kovi gombnal
#
# A HIBA, AMIT JELEZTEL
#   A buntetes-modalban kiosztott korty megjelent a result bannerben, de a
#   jatekosokra nem kerult ra.
#
# REPRODUKALVA (Szerencsekerek, 3 jatekos)
#     porgetes utan : Sere:0, Kecsi:0, Luca:0     (a nyeremeny meg pendingCommit)
#     buntetes utan : Sere:2, Kecsi:0, Luca:0     (a buntetes rakerult)
#     KOVI utan     : Sere:0, Kecsi:1, Luca:0     (a buntetes ELTUNT)
#
# AZ OK: a pendingCommit PILLANATKEPET tarolt
#   Az `advance*` fuggvenyek nem commitalnak azonnal: kiszamoljak a jatekosok
#   VEGALLAPOTAT, es beteszik a `pendingCommit`-be. A Kovi gomb ezt a kesz
#   tombot irja vissza (`setPlayers(newPlayers)`).
#
#   Ha kozben barmi MAS is hozzanyul a jatekosokhoz — tipikusan egy buntetes a
#   MENÜ-bol vagy a wildcard "Szabalyszego?"-bol —, akkor a Kovi gomb egy olyan
#   allapotot ir vissza, ami meg nem tudott a buntetesrol. A koztes valtozas
#   egyszeruen felulirodik.
#
#   Ez NEM a buntetes hibaja: barmi mas, ami menet kozben modositja a
#   jatekosokat, ugyanigy elveszne.
#
# A JAVITAS: a KULONBSEGET visszuk at, nem a vegallapotot
#   A `pendingCommit` mostantol azt a tombot is eltarolja, AMIBOL a vegallapot
#   szuletett (`basePlayers`). Commitalaskor nem a pillanatkepet irjuk vissza,
#   hanem kiszamoljuk, mennyivel valtozott a pont/korty a pillanatkep ota, es
#   azt adjuk hozza az AKTUALIS ertekhez.
#
#   Ha kozben semmi nem tortent, `current === base`, tehat az eredmeny pontosan
#   a regi `newPlayers` — vagyis a javitas a normal uton semmit nem valtoztat.
#
# KET HELYEN KELL
#   * `commitPending()`         — a Kovi gomb
#   * `flushPendingBeforeEnd()` — a buli lezarasa (ez ugyanezt a pillanatkepet
#     irta vissza, tehat a vegeredmenybol is kiesett volna a buntetes)
import sys

P = 'app.src.html'
src = open(P, encoding='utf-8').read()

def sub(old, new, what):
    global src
    assert src.count(old) == 1, '%s: %d talalat' % (what, src.count(old))
    src = src.replace(old, new, 1)

# ─────────────────────────────────────────────────────────────────────────────
# 1. mergeCommit + a ket commit-ut
# ─────────────────────────────────────────────────────────────────────────────
sub("""  const commitPending = () => {
    if (!pendingCommit || transitioning) return;
    const {newPlayers, fb, newTurn, newGameIdx, newRound} = pendingCommit;
    setPendingCommit(null);
    commitRound(newPlayers, fb, newTurn, newGameIdx, newRound);
  };""",
    """  // A pendingCommit a jatekosok VEGALLAPOTAT tarolja, es a Kovi gomb ezt irta
  // vissza. Ha kozben mas is modositotta a jatekosokat — tipikusan egy BUNTETES
  // a MENÜ-bol vagy a wildcard "Szabalyszego?"-bol —, a visszairas eltorolte.
  // (v10.274, reprodukalva: buntetes utan Sere:2, Kovi utan Sere:0.)
  //
  // Ezert nem a vegallapotot vesszuk at, hanem a KULONBSEGET: mennyivel valtozott
  // a pont/korty a pillanatkep ota, es azt adjuk az AKTUALIS ertekhez. Ha kozben
  // semmi nem tortent, current === base, tehat az eredmeny pontosan `next` —
  // a normal uton ez a javitas semmit nem valtoztat.
  const mergeCommit = (base, next, current) => {
    if (!base || !current || !next) return next;
    const byId = arr => { const m = {}; arr.forEach(p => { m[p.id] = p; }); return m; };
    const b = byId(base), c = byId(current);
    return next.map(n => {
      const bp = b[n.id], cp = c[n.id];
      if (!bp || !cp) return n;   // kozben ki-/bekerult jatekos: marad a next
      return { ...n,
        points: (cp.points || 0) + ((n.points || 0) - (bp.points || 0)),
        drinks: (cp.drinks || 0) + ((n.drinks || 0) - (bp.drinks || 0)) };
    });
  };

  const commitPending = () => {
    if (!pendingCommit || transitioning) return;
    const {newPlayers, basePlayers, fb, newTurn, newGameIdx, newRound} = pendingCommit;
    setPendingCommit(null);
    commitRound(mergeCommit(basePlayers, newPlayers, playersRef.current), fb, newTurn, newGameIdx, newRound);
  };""",
    'commitPending')

sub("""  const flushPendingBeforeEnd = () => {
    const pc = pendingCommit;
    if (pc && pc.newPlayers) {
      setPlayers(pc.newPlayers);
      if (setScoreHistory) setScoreHistory(prev => [...prev, pc.newPlayers.map(p => ({ id: p.id, name: p.name, color: p.color, pts: p.points }))]);
      if (roomCode && typeof syncRoom === 'function') syncRoom(roomCode, { players: pc.newPlayers });
    }
    setPendingCommit(null);
  };""",
    """  const flushPendingBeforeEnd = () => {
    const pc = pendingCommit;
    if (pc && pc.newPlayers) {
      // Ugyanaz a csapda, mint a Kovi gombnal: a pillanatkep visszairasa
      // eltorolne a kozben kiosztott buntetest. Lasd mergeCommit / patch_10_274.py
      const merged = mergeCommit(pc.basePlayers, pc.newPlayers, playersRef.current);
      setPlayers(merged);
      if (setScoreHistory) setScoreHistory(prev => [...prev, merged.map(p => ({ id: p.id, name: p.name, color: p.color, pts: p.points }))]);
      if (roomCode && typeof syncRoom === 'function') syncRoom(roomCode, { players: merged });
    }
    setPendingCommit(null);
  };""",
    'flushPendingBeforeEnd')

# ─────────────────────────────────────────────────────────────────────────────
# 2. A harom advance-ut eltarolja, MIBOL szamolt
# ─────────────────────────────────────────────────────────────────────────────
sub("""      ? players.map(p => p.id===currentPlayer?.id ? {...p, ...(won ? {points: p.points + 1*wcMult} : {drinks: p.drinks + diffDrinks*wcMult})} : p)
      : players;
    setPendingCommit({ newPlayers, fb:won?'win':'lose', newTurn:(turn+1)%Math.max(activePlayers.length,1), newGameIdx:gameIdx+1, newRound:round+1 });""",
    """      ? players.map(p => p.id===currentPlayer?.id ? {...p, ...(won ? {points: p.points + 1*wcMult} : {drinks: p.drinks + diffDrinks*wcMult})} : p)
      : players;
    setPendingCommit({ newPlayers, basePlayers: players, fb:won?'win':'lose', newTurn:(turn+1)%Math.max(activePlayers.length,1), newGameIdx:gameIdx+1, newRound:round+1 });""",
    'advance base')

sub("""      : players;
    setSelectedOpponent(null);
    setPendingCommit({ newPlayers, fb:won?'win':'lose', newTurn:(turn+1)%Math.max(activePlayers.length,1), newGameIdx:gameIdx+1, newRound:round+1 });""",
    """      : players;
    setSelectedOpponent(null);
    setPendingCommit({ newPlayers, basePlayers: players, fb:won?'win':'lose', newTurn:(turn+1)%Math.max(activePlayers.length,1), newGameIdx:gameIdx+1, newRound:round+1 });""",
    'advancePaired base')

sub("""    setPendingCommit({ newPlayers, fb, newTurn:(turn+1)%Math.max(activePlayers.length,1), newGameIdx:gameIdx+1, newRound:round+1 });""",
    """    setPendingCommit({ newPlayers, basePlayers: latestPlayers, fb, newTurn:(turn+1)%Math.max(activePlayers.length,1), newGameIdx:gameIdx+1, newRound:round+1 });""",
    'advanceLoverseny base')

sub("const APP_VERSION = 'v10.273';", "const APP_VERSION = 'v10.274';", 'verzio')
open(P, 'w', encoding='utf-8').write(src)
print('OK — a buntetes tullel a Kovi gombot')
