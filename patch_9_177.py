#!/usr/bin/env python3
"""patch_9_177.py — BeerPong: 'Következő meccs' push notification minden eszközre"""

with open('index.html', 'r', encoding='utf-8') as f:
    content = f.read()

assert "const APP_VERSION = 'v9.176';" in content
content = content.replace("const APP_VERSION = 'v9.176';", "const APP_VERSION = 'v9.177';")

# ── 1. Register service worker + request notification permission (after </script> that has APP_VERSION) ──
# Find the splash inline script end to insert SW registration after Firebase init
OLD_SW_HOOK = "window.subscribeRoom = function(code, cb) {"
NEW_SW_HOOK = """window.subscribeRoom = function(code, cb) {"""

# Actually insert SW registration right at the top of the app JS (before React renders)
# Find a safe early insertion point: right before the APP_VERSION const
OLD_APPVER = "const APP_VERSION = 'v9.177';"
NEW_APPVER = """const APP_VERSION = 'v9.177';

// ── Service Worker + Notification permission ──
if ('serviceWorker' in navigator) {
  navigator.serviceWorker.register('./sw.js').catch(() => {});
}
window._bohRequestNotifPermission = function() {
  if (!('Notification' in window)) return;
  if (Notification.permission === 'default') {
    Notification.requestPermission().catch(() => {});
  }
};
window._bohShowNotif = function(title, body) {
  if (!('Notification' in window) || Notification.permission !== 'granted') return;
  if (navigator.serviceWorker?.controller) {
    navigator.serviceWorker.ready.then(reg => {
      reg.showNotification(title, { body, icon: './icon-192.png', badge: './icon-192.png', tag: 'bp-match', renotify: true });
    }).catch(() => { new Notification(title, { body }); });
  } else {
    try { new Notification(title, { body }); } catch(e) {}
  }
};"""
assert OLD_APPVER in content, "APP_VERSION not found"
content = content.replace(OLD_APPVER, NEW_APPVER, 1)

# ── 2. Request notification permission when BeerPong game mounts ──
OLD_BP_INIT = "  const bpCfg = gameMeta?.beerpongConfig || {};"
NEW_BP_INIT = """  const bpCfg = gameMeta?.beerpongConfig || {};
  React.useEffect(() => { if (typeof window._bohRequestNotifPermission === 'function') window._bohRequestNotifPermission(); }, []);"""
assert OLD_BP_INIT in content, "BeerPong bpCfg not found"
content = content.replace(OLD_BP_INIT, NEW_BP_INIT, 1)

# ── 3. Helper to get current match players from any tournament type ──
# Add after the playLastMinuteBeep function
OLD_AFTER_BEEP = """  React.useEffect(() => {
    if (timerRunning) {
      timerRef.current = setInterval(() => {
        setTimerSecs(s => {
          if (s === 61) playLastMinuteBeep();"""
NEW_AFTER_BEEP = """  const notifyCurrentMatch = (p1name, p2name) => {
    if (!roomCode || typeof syncRoom !== 'function') return;
    syncRoom(roomCode, { bpNotif: { p1: p1name || '?', p2: p2name || '?', ts: Date.now() } });
  };

  React.useEffect(() => {
    if (timerRunning) {
      timerRef.current = setInterval(() => {
        setTimerSecs(s => {
          if (s === 61) playLastMinuteBeep();"""
assert OLD_AFTER_BEEP in content, "after beep hook not found"
content = content.replace(OLD_AFTER_BEEP, NEW_AFTER_BEEP, 1)

# ── 4. Trigger notify when SE current match changes ──
OLD_SE_NEXT = "      // Next pending in current round (skip TBD placeholders)\n      const nextInRound = nr[curRound].findIndex(m => m.winner === null && !m.tbd);\n      if (nextInRound !== -1) { setSeCurMatch(nextInRound); return nr; }"
NEW_SE_NEXT = """      // Next pending in current round (skip TBD placeholders)
      const nextInRound = nr[curRound].findIndex(m => m.winner === null && !m.tbd);
      if (nextInRound !== -1) {
        setSeCurMatch(nextInRound);
        const nm = nr[curRound][nextInRound];
        if (nm?.p1 && nm?.p2) notifyCurrentMatch(nm.p1.name, nm.p2.name);
        return nr;
      }"""
assert OLD_SE_NEXT in content, "SE next match not found"
content = content.replace(OLD_SE_NEXT, NEW_SE_NEXT, 1)

# ── 5. Trigger notify when advancing to next SE round ──
OLD_SE_ROUND = "        if (nextPre !== -1) { setSeCurRound(curRound + 1); setSeCurMatch(nextPre); return nr; }"
NEW_SE_ROUND = """        if (nextPre !== -1) {
          setSeCurRound(curRound + 1); setSeCurMatch(nextPre);
          const nm = nr[curRound + 1][nextPre];
          if (nm?.p1 && nm?.p2) notifyCurrentMatch(nm.p1.name, nm.p2.name);
          return nr;
        }"""
assert OLD_SE_ROUND in content, "SE next round not found"
content = content.replace(OLD_SE_ROUND, NEW_SE_ROUND, 1)

# ── 6. Trigger notify when RR advances ──
OLD_RR_ADVANCE = "      if (nextIdx !== -1) { setRrIdx(nextIdx); }"
NEW_RR_ADVANCE = """      if (nextIdx !== -1) {
        setRrIdx(nextIdx);
        const nm2 = nm[nextIdx];
        if (nm2?.p1 && nm2?.p2) notifyCurrentMatch(nm2.p1.name, nm2.p2.name);
      }"""
assert OLD_RR_ADVANCE in content, "RR advance not found"
content = content.replace(OLD_RR_ADVANCE, NEW_RR_ADVANCE, 1)

# ── 7. Show notification on all clients when bpNotif changes in observer ──
OLD_OBSERVER_SNAP = """        setRoom(prev => {
          if (prev && prev.players && data.players) {
            data.players.forEach((p, i) => {
              const pp = prev.players[i];
              if (!pp) return;
              if (p.points > pp.points) { setPulseId(p.id+':p'); setTimeout(()=>setPulseId(null),700); }
              else if (p.drinks > pp.drinks) { setPulseId(p.id+':d'); setTimeout(()=>setPulseId(null),700); }
            });
          }
          return data;
        });"""
NEW_OBSERVER_SNAP = """        setRoom(prev => {
          if (prev && prev.players && data.players) {
            data.players.forEach((p, i) => {
              const pp = prev.players[i];
              if (!pp) return;
              if (p.points > pp.points) { setPulseId(p.id+':p'); setTimeout(()=>setPulseId(null),700); }
              else if (p.drinks > pp.drinks) { setPulseId(p.id+':d'); setTimeout(()=>setPulseId(null),700); }
            });
          }
          // Beer pong match notification
          if (data.bpNotif && (!prev?.bpNotif || data.bpNotif.ts !== prev.bpNotif.ts)) {
            if (typeof window._bohShowNotif === 'function') {
              window._bohShowNotif('🏓 Következő meccs!', data.bpNotif.p1 + ' vs ' + data.bpNotif.p2);
            }
          }
          return data;
        });"""
assert OLD_OBSERVER_SNAP in content, "observer snap not found"
content = content.replace(OLD_OBSERVER_SNAP, NEW_OBSERVER_SNAP, 1)

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(content)

print("OK — v9.177 ready")
