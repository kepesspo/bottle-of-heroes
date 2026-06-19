#!/usr/bin/env python3

with open('index.html', 'r', encoding='utf-8') as f:
    html = f.read()

# Revert v9.283 undoLast change — remove localStorage/Firestore sync lines
old = """  const undoLast = () => {
    if (!undoRef.current) return;
    const { players: p, turn: t, gameIdx: g, round: r } = undoRef.current;
    undoRef.current = null;
    setCanUndo(false);
    setPlayers(p); setTurn(t); setGameIdx(g); setRound(r);
    setPendingCommit(null); setTransitioning(false); transRef.current = false;
    // Revert localStorage so refresh also shows old scores
    try { localStorage.setItem('boh_session', JSON.stringify({ players: p, turn: t, gameIdx: g, round: r, selectedGames, gameMeta })); } catch(e) {}
    // Revert Firestore so polling doesn't snap back to new scores
    if (roomCode && typeof syncRoom === 'function') syncRoom(roomCode, { players: p, turn: t, gameIdx: g, round: r });
  };"""
new = """  const undoLast = () => {
    if (!undoRef.current) return;
    const { players: p, turn: t, gameIdx: g, round: r } = undoRef.current;
    undoRef.current = null;
    setCanUndo(false);
    setPlayers(p); setTurn(t); setGameIdx(g); setRound(r);
    setPendingCommit(null); setTransitioning(false); transRef.current = false;
  };"""
assert old in html, "FAIL: undoLast"
html = html.replace(old, new, 1)

html = html.replace("const APP_VERSION = 'v9.285';", "const APP_VERSION = 'v9.286';")

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(html)

print("Done: v9.286 — undoLast revert (debug: isolate startup issue)")
