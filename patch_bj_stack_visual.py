#!/usr/bin/env python3
# v9.804 — BJ: labeled results in Többiek + stacked chip pile visual
import io, sys

P = '/home/user/bottle-of-heroes/index.html'
c = io.open(P, encoding='utf-8').read()

# ── 1) BJChipStack → stacked pile visual ──
OLD = """function BJChipStack({ count, size }) {
  const s = size || 44;
  const n = count || 0;
  const grey = n === 0;
  const col = grey ? '#B7BCC2' : n <= 5 ? '#F4977A' : n <= 12 ? '#E8B36A' : T.mint;
  return (
    <div style={{ width:s, height:s, borderRadius:'50%', background:col, position:'relative', display:'grid', placeItems:'center', flexShrink:0, boxShadow:'0 2px 6px rgba(0,0,0,0.2)' }}>
      <div style={{ position:'absolute', inset:Math.max(2, Math.round(s*0.05)), borderRadius:'50%', border:`${Math.max(2, Math.round(s*0.065))}px dashed rgba(255,255,255,0.92)`, boxSizing:'border-box' }} />
      <div style={{ position:'absolute', inset:Math.max(5, Math.round(s*0.2)), borderRadius:'50%', background:'rgba(255,255,255,0.94)' }} />
      <div style={{ position:'relative', textAlign:'center', lineHeight:1 }}>
        <div style={{ fontFamily:T.font, fontWeight:900, fontSize:Math.round(s*0.32), color: grey ? '#8a8f94' : col }}>{n}</div>
        <div style={{ fontSize:Math.max(8, Math.round(s*0.18)), marginTop:1 }}>🍺</div>
      </div>
    </div>
  );
}"""
NEW = """function BJChipStack({ count, size }) {
  const s = size || 44;
  const n = count || 0;
  const grey = n === 0;
  const col = grey ? '#B7BCC2' : n <= 5 ? '#F4977A' : n <= 12 ? '#E8B36A' : T.mint;
  const discs = Math.max(1, Math.min(8, Math.ceil(n / 3)));
  const w = Math.round(s * 0.82);
  const h = Math.max(6, Math.round(s * 0.26));
  const off = Math.max(3, Math.round(h * 0.55));
  const pileH = h + (discs - 1) * off;
  const rim = Math.max(2, Math.round(h * 0.28));
  return (
    <span style={{ display:'inline-flex', alignItems:'center', gap:Math.max(4, Math.round(s*0.12)), flexShrink:0 }}>
      <span style={{ position:'relative', width:w, height:pileH, display:'block' }}>
        {Array.from({ length: discs }).map((_, i) => (
          <span key={i} style={{ position:'absolute', left:0, bottom:i*off, width:w, height:h, borderRadius:'50%', background:col, boxShadow:`inset 0 ${-rim}px 0 rgba(0,0,0,0.18), 0 1px 2px rgba(0,0,0,0.15)`, border:'1.5px solid rgba(255,255,255,0.55)', boxSizing:'border-box' }} />
        ))}
        <span style={{ position:'absolute', left:'20%', right:'20%', bottom:(discs-1)*off + Math.round(h*0.24), height:Math.max(2, Math.round(h*0.3)), borderRadius:'50%', border:'1.5px dashed rgba(255,255,255,0.9)', boxSizing:'border-box' }} />
      </span>
      <span style={{ display:'inline-flex', alignItems:'baseline', gap:2, fontFamily:T.font, fontWeight:900, fontSize:Math.round(s*0.34), color: grey ? '#8a8f94' : col, lineHeight:1, whiteSpace:'nowrap' }}>
        {n}<span style={{ fontSize:Math.max(9, Math.round(s*0.26)) }}>🍺</span>
      </span>
    </span>
  );
}"""
assert OLD in c, 'BJChipStack anchor'
c = c.replace(OLD, NEW)

# ── 2) Többiek: labeled results row ──
OLD2 = """                      {bj.bust[pid] ? '💀' : bjIsBlackjack(hand) ? 'BJ 🂡' : bj.phase === 'results' || bj.stood[pid] ? score : hand.length + ' lap'}
                      {bj.phase === 'results' ? ` · ${(bj.chips || {})[pid] !== undefined ? bj.chips[pid] : stackOf(pid)} 🍺` : ''}"""
NEW2 = """                      {bj.phase === 'results'
                        ? `Lapok: ${bj.bust[pid] ? '💀' : bjIsBlackjack(hand) ? 'BJ 🂡' : score} · Zseton: ${(bj.chips || {})[pid] !== undefined ? bj.chips[pid] : stackOf(pid)} 🍺`
                        : (bj.bust[pid] ? '💀' : bjIsBlackjack(hand) ? 'BJ 🂡' : bj.stood[pid] ? score : hand.length + ' lap')}"""
assert OLD2 in c, 'Tobbiek anchor'
c = c.replace(OLD2, NEW2)

# ── 3) Host ResultsView: label bare score ──
OLD3 = "fontSize:13, color:T.inkSoft }}>{bjScore(hand)}</span>"
NEW3 = "fontSize:13, color:T.inkSoft }}>Lapok: {bjScore(hand)}</span>"
assert c.count(OLD3) == 1, 'host results score anchor'
c = c.replace(OLD3, NEW3)

# ── 4) version bump ──
assert c.count('v9.803') == 1, 'version count'
c = c.replace('v9.803', 'v9.804')

io.open(P, 'w', encoding='utf-8').write(c)
print('patch OK — v9.804')
