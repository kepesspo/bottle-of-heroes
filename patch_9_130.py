#!/usr/bin/env python3
"""patch_9_130.py — ZeneGame: Firestore-based shared blacklist for non-loading songs"""

with open('index.html', 'r', encoding='utf-8') as f:
    content = f.read()

assert "const APP_VERSION = 'v9.129';" in content
content = content.replace("const APP_VERSION = 'v9.129';", "const APP_VERSION = 'v9.130';")

# ── 1. Add global blacklist cache + loader after db is initialized ──
OLD_DB_INIT = "  db.enablePersistence({ synchronizeTabs: true }).catch(function(e) {\n    // failed-precondition = multiple tabs; unimplemented = browser doesn't support it\n  });"

NEW_DB_INIT = """  db.enablePersistence({ synchronizeTabs: true }).catch(function(e) {
    // failed-precondition = multiple tabs; unimplemented = browser doesn't support it
  });

  // Shared song blacklist: songs that never load get written here by any user
  window._zeneBadIds = new Set();
  window._zeneBadLoaded = false;
  window.loadZeneBadList = function() {
    return db.collection('zene_blacklist').get().then(function(snap) {
      snap.forEach(function(doc) { window._zeneBadIds.add(doc.id); });
      window._zeneBadLoaded = true;
      // also sync to localStorage
      try {
        window._zeneBadIds.forEach(function(id) { localStorage.setItem('znobad_' + id, '1'); });
      } catch(e) {}
    }).catch(function() { window._zeneBadLoaded = true; });
  };
  window.markZeneBad = function(spotifyId) {
    if (window._zeneBadIds.has(spotifyId)) return;
    window._zeneBadIds.add(spotifyId);
    try { localStorage.setItem('znobad_' + spotifyId, '1'); } catch(e) {}
    db.collection('zene_blacklist').doc(spotifyId).set({ bad: true, ts: firebase.firestore.FieldValue.serverTimestamp() }).catch(function() {});
  };
  // Load blacklist eagerly on startup
  window.loadZeneBadList();"""

assert OLD_DB_INIT in content, "db init not found"
content = content.replace(OLD_DB_INIT, NEW_DB_INIT, 1)

# ── 2. Update filteredSongs: use window._zeneBadIds + localStorage ──
OLD_FILTER = """    // Filter out blacklisted songs (failed to load previously)
    try {
      const good = songs.filter(s => !localStorage.getItem('znobad_' + s.spotifyId));
      if (good.length >= 5) songs = good;
    } catch(e) {}"""

NEW_FILTER = """    // Filter out blacklisted songs (shared Firestore list + local fallback)
    try {
      const good = songs.filter(s =>
        !window._zeneBadIds?.has(s.spotifyId) && !localStorage.getItem('znobad_' + s.spotifyId)
      );
      if (good.length >= 5) songs = good;
    } catch(e) {}"""

assert OLD_FILTER in content, "filter block not found"
content = content.replace(OLD_FILTER, NEW_FILTER, 1)

# ── 3. Use window.markZeneBad instead of direct localStorage in skipAndBlacklist ──
OLD_BLACKLIST_CALL = """      // Blacklist this song so it never appears again
      try { localStorage.setItem('znobad_' + song.spotifyId, '1'); } catch(e) {}"""

NEW_BLACKLIST_CALL = """      // Blacklist this song globally (Firestore + localStorage)
      window.markZeneBad && window.markZeneBad(song.spotifyId);"""

assert OLD_BLACKLIST_CALL in content, "blacklist call not found"
content = content.replace(OLD_BLACKLIST_CALL, NEW_BLACKLIST_CALL, 1)

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(content)

print("OK — v9.130 ready")
