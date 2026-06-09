#!/usr/bin/env python3
"""v8.53: Beer Pong stat — nyert bajnokság (bp_tournaments)"""

with open('index.html', 'r', encoding='utf-8') as f:
    content = f.read()

# ── 1. finishSE: bajnok kap +1 bp_tournaments ────────────────────────────────
OLD_FINISH_SE_STATS = """    // Save BP stats for profile players
    if (typeof window.updateStats === 'function') {
      players.forEach(p => {
        if (!p.profileId) return;
        const isWinner = champ && champ.id === p.id;
        window.updateStats(p.profileId, {
          bp_wins: firebase.firestore.FieldValue.increment(isWinner ? 1 : 0),
          bp_losses: firebase.firestore.FieldValue.increment(isWinner ? 0 : 1),
          bp_played: firebase.firestore.FieldValue.increment(1),
        });
      });
    }
  };

  // ── RR confirm"""

NEW_FINISH_SE_STATS = """    // Save BP stats for profile players
    if (typeof window.updateStats === 'function') {
      players.forEach(p => {
        if (!p.profileId) return;
        const isWinner = champ && champ.id === p.id;
        window.updateStats(p.profileId, {
          bp_wins: firebase.firestore.FieldValue.increment(isWinner ? 1 : 0),
          bp_losses: firebase.firestore.FieldValue.increment(isWinner ? 0 : 1),
          bp_played: firebase.firestore.FieldValue.increment(1),
          bp_tournaments: firebase.firestore.FieldValue.increment(isWinner ? 1 : 0),
        });
      });
    }
  };

  // ── RR confirm"""

assert OLD_FINISH_SE_STATS in content, "finishSE stats not found"
content = content.replace(OLD_FINISH_SE_STATS, NEW_FINISH_SE_STATS, 1)
print("✓ finishSE: bp_tournaments hozzáadva")

# ── 2. finishRR: bajnok kap +1 bp_tournaments ────────────────────────────────
OLD_FINISH_RR_STATS = """    if (typeof window.updateStats === 'function') {
      players.forEach(p => {
        if (!p.profileId) return;
        const isWinner = champ && champ.id === p.id;
        window.updateStats(p.profileId, {
          bp_wins: firebase.firestore.FieldValue.increment(isWinner ? 1 : 0),
          bp_losses: firebase.firestore.FieldValue.increment(isWinner ? 0 : 1),
          bp_played: firebase.firestore.FieldValue.increment(1),
        });
      });
    }
  };

  // ── Two-stage group confirm"""

NEW_FINISH_RR_STATS = """    if (typeof window.updateStats === 'function') {
      players.forEach(p => {
        if (!p.profileId) return;
        const isWinner = champ && champ.id === p.id;
        window.updateStats(p.profileId, {
          bp_wins: firebase.firestore.FieldValue.increment(isWinner ? 1 : 0),
          bp_losses: firebase.firestore.FieldValue.increment(isWinner ? 0 : 1),
          bp_played: firebase.firestore.FieldValue.increment(1),
          bp_tournaments: firebase.firestore.FieldValue.increment(isWinner ? 1 : 0),
        });
      });
    }
  };

  // ── Two-stage group confirm"""

assert OLD_FINISH_RR_STATS in content, "finishRR stats not found"
content = content.replace(OLD_FINISH_RR_STATS, NEW_FINISH_RR_STATS, 1)
print("✓ finishRR: bp_tournaments hozzáadva")

# ── 3. StatsScreen BP tab: bajnokság oszlop megjelenítése ────────────────────
OLD_BP_ROW = """                    <div style={{ fontFamily:T.font, fontSize:11, color:T.inkSoft, marginTop:2 }}>
                      {played} meccs · {s.bp_wins||0} győzelem · {s.bp_losses||0} vereség
                    </div>"""

NEW_BP_ROW = """                    <div style={{ fontFamily:T.font, fontSize:11, color:T.inkSoft, marginTop:2 }}>
                      {played} meccs · {s.bp_wins||0} győzelem · {s.bp_losses||0} vereség
                    </div>
                    {(s.bp_tournaments||0) > 0 && (
                      <div style={{ display:'inline-flex', alignItems:'center', gap:3, marginTop:3, background:'rgba(251,191,36,0.15)', borderRadius:999, padding:'2px 8px' }}>
                        <span style={{ fontSize:11 }}>🏆</span>
                        <span style={{ fontFamily:T.font, fontWeight:800, fontSize:11, color:'#B45309' }}>{s.bp_tournaments} bajnokság</span>
                      </div>
                    )}"""

assert OLD_BP_ROW in content, "BP row not found"
content = content.replace(OLD_BP_ROW, NEW_BP_ROW, 1)
print("✓ StatsScreen: bajnokság badge megjelenítve")

# ── 4. Version bump ───────────────────────────────────────────────────────────
OLD_VER = "const APP_VERSION = 'v8.52';"
NEW_VER = "const APP_VERSION = 'v8.53';"
assert OLD_VER in content, "version not found"
content = content.replace(OLD_VER, NEW_VER, 1)

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(content)
print("✓ v8.53 saved")
