#!/usr/bin/env python3
# v10.259 — a QR-jelvény lekerül a KÖR gyűrűről
#
# A korty-kapszula miatt a QR-gomb a gyűrű jobb FELSŐ sarkába került, és ott
# most egy harmadik dolog nyomakodik egy amúgy is sűrű jelvényre. Nem is kell
# oda: a MENÜ-ben ott a szobakód sor, rajta ugyanez a QR-gomb ÉS a megosztás
# link — vagyis a csatlakoztatás nem veszik el, csak egy koppintással odébb van.
#
# A showRoomQR állapot és a RoomQR megjelenítés marad — a MENÜ gombja használja.
import sys

P = 'app.src.html'
src = open(P, encoding='utf-8').read()

def sub(old, new, what):
    global src
    assert src.count(old) == 1, '%s: %d talalat' % (what, src.count(old))
    src = src.replace(old, new, 1)

sub("""              {/* A QR-gomb a jobb FELSO sarokba kerult: a jobb also sarkot most a
                  korty-szam foglalja. */}
              {roomCode && (
                <button onClick={(e) => { e.stopPropagation(); setShowRoomQR(true); }} title="QR kód — csatlakozás" style={{ position:'absolute', right:-3, top: stakeText ? -3 : undefined, bottom: stakeText ? undefined : -3, width:22, height:22, borderRadius:'50%', border:`2px solid ${T.surface}`, background:T.mint, color:'#fff', cursor:'pointer', display:'grid', placeItems:'center', boxShadow:'0 2px 6px rgba(0,0,0,0.25)', padding:0, zIndex:3 }}>
                  <svg width="12" height="12" viewBox="0 0 24 24" fill="currentColor"><path d="M3 3h6v6H3V3zm2 2v2h2V5H5zm8-2h6v6h-6V3zm2 2v2h2V5h-2zM3 15h6v6H3v-6zm2 2v2h2v-2H5zm10-2h2v2h-2v-2zm4 0h2v2h-2v-2zm-4 4h2v2h-2v-2zm2 2h2v2h-2v-2zm2-2h2v2h-2v-2z"/></svg>
                </button>
              )}
            </div>""",
    """              {/* QR-jelveny NINCS a gyurun: a MENU-ben ott a szobakod sor ugyanezzel
                  a QR-gombbal es a megosztas linkkel. Egy koppintassal odebb, cserebe
                  a jelveny nem zsufolodik tele. */}
            </div>""",
    'QR jelveny torlese')

sub("const APP_VERSION = 'v10.258';", "const APP_VERSION = 'v10.259';", 'verzio')
open(P, 'w', encoding='utf-8').write(src)
print('OK — nincs QR a gyurun')
