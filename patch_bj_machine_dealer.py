#!/usr/bin/env python3
# v9.797: Blackjack — a gép oszt, nincs emberi osztó; mindenki játszik
import io

P = '/home/user/bottle-of-heroes/index.html'
c = io.open(P, encoding='utf-8').read()

def rep(old, new, cnt=1):
    global c
    assert old in c, 'MISSING: ' + old[:80]
    assert c.count(old) == cnt, 'COUNT %d != %d: %s' % (c.count(old), cnt, old[:80])
    c = c.replace(old, new)

# ── 1) Offline init: mindenki resztvevo ──
rep("""      // Offline: mindenki a host telefonján játszik, a host az osztó
      const parts = players.slice(1).map(p => p.id);""",
"""      // Offline: mindenki a host telefonján játszik, a gép oszt
      const parts = players.map(p => p.id);""")

# ── 2) startRound: nincs osztó-kizárás ──
rep("""    const claimed = isOnline
      ? players.filter(p => takenIds.includes(p.id) && p.id !== bjState.hostId).map(p => p.id)
      : players.slice(1).map(p => p.id);""",
"""    const claimed = isOnline
      ? players.filter(p => takenIds.includes(p.id)).map(p => p.id)
      : players.map(p => p.id);""")

# ── 3) setOfflineDealer törlése ──
rep("""  // Offline osztóváltás az első kör előtt: résztvevők = mindenki, kivéve az osztó
  function setOfflineDealer(did) {
    const parts = players.filter(p => p.id !== did).map(p => p.id);
    const startStack = bjState.startStack || 10;
    const bets = {}; const chips = {};
    parts.forEach(pid => { bets[pid] = 1; chips[pid] = startStack; });
    update({ ...bjState, hostId: did, participants: parts, bets, chips, betsDone: {} });
  }
""", "")

# ── 4) JoiningView: joined lista hostId-kizárás nélkül + felirat ──
rep("    const joined = players.filter(p => takenIds.includes(p.id) && p.id !== bjState.hostId);",
    "    const joined = players.filter(p => takenIds.includes(p.id));")
rep("A játékosok a telefonjukon válasszák ki magukat — te vagy az osztó!",
    "A játékosok a telefonjukon válasszák ki magukat — mindenki a gép ellen játszik!")

# ── 5) JoiningView osztóválasztó blokk törlése ──
rep("""        <div style={{ background:T.surface, borderRadius:18, padding:'14px 16px', boxShadow:T.shadow, marginBottom:12 }}>
          <div style={{ fontFamily:T.font, fontSize:11, fontWeight:T.weightTitle, color:T.inkSoft, textTransform:'uppercase', letterSpacing:'0.07em', marginBottom:10 }}>🎩 Ki az osztó?</div>
          <div style={{ display:'flex', gap:8, overflowX:'auto', paddingBottom:4 }}>
            {players.map(p => {
              const sel = p.id === bjState.hostId;
              return (
                <button key={p.id} onClick={() => update({ ...bjState, hostId: p.id })} style={{ display:'flex', flexDirection:'column', alignItems:'center', gap:5, padding:'8px 10px', borderRadius:12, border:`2px solid ${sel ? T.mint : 'transparent'}`, background: sel ? T.mintSoft : T.surfaceMuted, cursor:'pointer', flexShrink:0, minWidth:64, WebkitTapHighlightColor:'transparent' }}>
                  <BJAvatar p={p} size={34} />
                  <span style={{ fontFamily:T.font, fontWeight:T.weightTitle, fontSize:11, color: sel ? T.mint : T.ink, whiteSpace:'nowrap' }}>{sel ? '🎩 ' : ''}{p.name}</span>
                </button>
              );
            })}
          </div>
        </div>
""", "")

# ── 6) startStack hint: osztó-említés törlése ──
rep("Kiszálláskor: aki ez alatt van, a különbséget issza — aki felette, kiosztja (az osztónak is adhatja! 🎩)",
    "Kiszálláskor: aki ez alatt van, a különbséget issza — aki felette, kiosztja")

# ── 7) Offline BettingView osztóválasztó blokk törlése ──
rep("""      {!isOnline && (bjState.roundsPlayed || 0) === 0 && (
        <div style={{ background:T.surface, borderRadius:18, padding:'12px 14px', boxShadow:T.shadow, marginBottom:12 }}>
          <div style={{ fontFamily:T.font, fontSize:11, fontWeight:T.weightTitle, color:T.inkSoft, textTransform:'uppercase', letterSpacing:'0.07em', marginBottom:8 }}>🎩 Ki az osztó?</div>
          <div style={{ display:'flex', gap:8, overflowX:'auto', paddingBottom:4 }}>
            {players.map(p => {
              const sel = p.id === bjState.hostId;
              return (
                <button key={p.id} onClick={() => setOfflineDealer(p.id)} style={{ display:'flex', flexDirection:'column', alignItems:'center', gap:5, padding:'8px 10px', borderRadius:12, border:`2px solid ${sel ? T.mint : 'transparent'}`, background: sel ? T.mintSoft : T.surfaceMuted, cursor:'pointer', flexShrink:0, minWidth:64, WebkitTapHighlightColor:'transparent' }}>
                  <BJAvatar p={p} size={34} />
                  <span style={{ fontFamily:T.font, fontWeight:T.weightTitle, fontSize:11, color: sel ? T.mint : T.ink, whiteSpace:'nowrap' }}>{sel ? '🎩 ' : ''}{p.name}</span>
                </button>
              );
            })}
          </div>
        </div>
      )}
""", "")

# ── 8) Feliratok: 🎩 Osztó → 🤖 Gép ──
rep("letterSpacing:'0.06em' }}>🎩 Osztó{revealed ? ` — ${bjScore(bjState.dealerHand)}` : ''}</span>",
    "letterSpacing:'0.06em' }}>🤖 Gép{revealed ? ` — ${bjScore(bjState.dealerHand)}` : ''}</span>")
rep("marginBottom:8 }}>🎩 Osztó — {ds}{ds > 21 ? ' (besokallt!)' : ''}",
    "marginBottom:8 }}>🤖 Gép — {ds}{ds > 21 ? ' (besokallt!)' : ''}")
rep("marginTop:8 }}>Az osztó húz… 🎩</div>",
    "marginTop:8 }}>A gép húz… 🤖</div>")
rep("marginBottom:8 }}>🎩 Osztó{revealed ? ` — ${bjScore(bj.dealerHand)}",
    "marginBottom:8 }}>🤖 Gép{revealed ? ` — ${bjScore(bj.dealerHand)}")
rep("  if (dBJ)               return { label:'Osztó Blackjack', delta: -bet };",
    "  if (dBJ)               return { label:'Gép Blackjack 🤖', delta: -bet };")
rep("  if (ds > 21)           return { label:'Osztó besokallt — nyert! 🏆', delta: bet };",
    "  if (ds > 21)           return { label:'A gép besokallt — nyert! 🏆', delta: bet };")
rep("// ═══════════════ BLACKJACK — host (osztó) nézet ═══════════════",
    "// ═══════════════ BLACKJACK — host nézet (a gép oszt) ═══════════════")

# ── 9) Kiszállás gombszövegek egyszerűsítése ──
rep("🚪 Kiszáll {diff < 0 ? `— iszik ${-diff} kortyot` : diff > 0 ? `— kioszt ${diff} kortyot (az osztónak is adhatja 🎩)` : '— nullán van, se nem iszik, se nem oszt'}",
    "🚪 Kiszáll {diff < 0 ? `— iszik ${-diff} kortyot` : diff > 0 ? `— kioszt ${diff} kortyot` : '— nullán van, se nem iszik, se nem oszt'}")
rep("""                const dealerName = players.find(p => p.id === bj.hostId)?.name || 'az osztó';
""", "")
rep("🚪 Kiszállok {diff < 0 ? `— megiszom ${-diff} kortyot` : diff > 0 ? `— kiosztok ${diff} kortyot (${dealerName} 🎩 is kaphat!)` : '— nullán vagyok'}",
    "🚪 Kiszállok {diff < 0 ? `— megiszom ${-diff} kortyot` : diff > 0 ? `— kiosztok ${diff} kortyot` : '— nullán vagyok'}")

# ── 10) Host gift-notice: nincs osztó-jelölés ──
rep("""            const isDealer = String(rpid) === String(bjState.hostId);
            return <div key={rpid} style={{ fontSize:12 }}>{isDealer ? `🎩 Osztó — ${rp?.name || '?'}` : (rp?.name || rpid)}: +{n} korty</div>;""",
"""            return <div key={rpid} style={{ fontSize:12 }}>{rp?.name || rpid}: +{n} korty</div>;""")

# ── 11) Host gift overlay: csak a többi résztvevő, nincs osztó chip ──
rep("""      {giftFor && (() => {
        const dealer = getPlayer(bjState.hostId) || hostPlayer;
        const recips = (bjState.participants || []).filter(pid => pid !== giftFor.pid).map(pid => ({ id: pid, p: getPlayer(pid), isDealer: false }));
        if (dealer && !recips.some(r => r.id === dealer.id)) recips.push({ id: dealer.id, p: dealer, isDealer: true });
        return <BJGiftOverlay pool={giftFor.pool} recipients={recips} onConfirm={hostConfirmGift} onCancel={() => setGiftFor(null)} />;
      })()}""",
"""      {giftFor && (() => {
        const recips = (bjState.participants || []).filter(pid => pid !== giftFor.pid).map(pid => ({ id: pid, p: getPlayer(pid) }));
        return <BJGiftOverlay pool={giftFor.pool} recipients={recips} onConfirm={hostConfirmGift} onCancel={() => setGiftFor(null)} />;
      })()}""")

# hostCashOut: ha nincs címzett, overlay helyett info + kiszállás
rep("""    const diff = ch - startStack;
    if (diff > 0) { setGiftFor({ pid, pool: diff }); return; } // nyereség — kiosztó overlay
    bookDrinks(pid, Math.max(0, -diff));""",
"""    const diff = ch - startStack;
    if (diff > 0) {
      const recips = (bjState.participants || []).filter(rp => rp !== pid);
      if (recips.length) { setGiftFor({ pid, pool: diff }); return; } // nyereség — kiosztó overlay
      alert(`Nincs kinek kiosztani — ${getPlayer(pid)?.name || '?'} szóban ossza ki a ${diff} kortyot! 🍺`);
      update({ ...bjState, cashedOut: { ...(bjState.cashedOut || {}), [pid]: true } });
      return;
    }
    bookDrinks(pid, Math.max(0, -diff));""")

# ── 12) Observer: claim lista mindenkinek ──
rep("    const selectable = players.filter(p => p.id !== bj.hostId);",
    "    const selectable = players;")

# ── 13) Observer gift overlay: nincs osztó chip ──
rep("""      {giftPool !== null && (() => {
        const dealer = players.find(p => p.id === bj.hostId);
        const recips = (bj.participants || []).filter(pid => pid !== playerId).map(pid => ({ id: pid, p: players.find(pp => pp.id === pid), isDealer: false }));
        if (dealer && !recips.some(r => r.id === dealer.id)) recips.push({ id: dealer.id, p: dealer, isDealer: true });
        return <BJGiftOverlay pool={giftPool} recipients={recips} onConfirm={guestConfirmGift} onCancel={() => setGiftPool(null)} />;
      })()}""",
"""      {giftPool !== null && (() => {
        const recips = (bj.participants || []).filter(pid => pid !== playerId).map(pid => ({ id: pid, p: players.find(pp => pp.id === pid) }));
        return <BJGiftOverlay pool={giftPool} recipients={recips} onConfirm={guestConfirmGift} onCancel={() => setGiftPool(null)} />;
      })()}""")

# guestCashOut: ha nincs címzett, overlay helyett info + kiszállás
rep("""    const surplus = Math.max(0, myChips - startStack);
    if (surplus > 0) { setGiftPool(surplus); return; } // nyereség — kiosztó overlay""",
"""    const surplus = Math.max(0, myChips - startStack);
    if (surplus > 0) {
      const others = (bj.participants || []).filter(pid => pid !== playerId);
      if (others.length) { setGiftPool(surplus); return; } // nyereség — kiosztó overlay
      alert(`Nincs kinek kiosztani — mondd be szóban a ${surplus} kortyot! 🍺`);
      bjWrite(code, { ...bj, cashedOut: { ...(bj.cashedOut || {}), [playerId]: true } });
      return;
    }""")

# ── 14) BJGiftOverlay: isDealer címke ki ──
rep("// Kiszállási nyereség-kiosztó overlay — kortyok szétosztása a többiek + az osztó közt",
    "// Kiszállási nyereség-kiosztó overlay — kortyok szétosztása a többi játékos közt")
rep("whiteSpace:'nowrap' }}>{r.isDealer ? `🎩 Osztó — ${r.p?.name || '?'}` : (r.p?.name || r.id)}</span>",
    "whiteSpace:'nowrap' }}>{r.p?.name || r.id}</span>")

# ── 15) Observer várakozó szövegek ──
rep("Várakozás az osztóra… 🎩", "Várakozás a házigazdára… 📱")
rep("Várj, amíg az osztó elindítja a játékot…", "Várj, amíg a házigazda elindítja a játékot…")

# ── 16) Verzióbump ──
assert c.count("'v9.796'") == 1
rep("const APP_VERSION = 'v9.796';", "const APP_VERSION = 'v9.797';")

assert 'setOfflineDealer' not in c
assert 'Ki az osztó?' not in c
io.open(P, 'w', encoding='utf-8').write(c)
print('OK — v9.797 patched')
