# v10.463 — Gender Reveal: a „zene kész” / „videó kész” jelzés a felső sávból a bal alsó szervezői csipbe
P = 'app.src.html'
s = open(P, encoding='utf-8').read()
def rep(old, new, cnt=1):
    global s
    n = s.count(old)
    assert n == cnt, (n, old[:90])
    s = s.replace(old, new)

rep("const APP_VERSION = 'v10.462';", "const APP_VERSION = 'v10.463';")

# ki a felső sávból
rep("""        {(music.url || music.loading) && <span data-reveal-musicready={music.url ? '1' : '0'} style={{ flexShrink:0, whiteSpace:'nowrap', fontFamily:T.font, fontWeight:800, fontSize:13, color:REVEAL_INK, opacity:0.7 }}>{music.url ? (music.builtin ? '🎵 alapzene kész' : '🎵 zene kész') : `🎵 zene töltődik… ${music.pct || 0}%`}</span>}
        {(video.url || video.loading) && <span data-reveal-videoready={video.url ? '1' : '0'} style={{ flexShrink:0, whiteSpace:'nowrap', fontFamily:T.font, fontWeight:800, fontSize:13, color:REVEAL_INK, opacity:0.7 }}>{video.url ? '🎬 videó kész' : `🎬 videó töltődik… ${video.pct || 0}%`}</span>}
""", "")

# be a bal alsó csipbe (a hang-állapot után) — szervezői infó, ugyanaz a halk nyelv
rep("""          {nWish > 0 && <React.Fragment><span aria-hidden="true" style={{ opacity:0.35 }}>·</span><span aria-hidden="true">💌</span><span data-reveal-wishcount>{nWish}</span></React.Fragment>}""",
"""          {nWish > 0 && <React.Fragment><span aria-hidden="true" style={{ opacity:0.35 }}>·</span><span aria-hidden="true">💌</span><span data-reveal-wishcount>{nWish}</span></React.Fragment>}
          {/* v10.463: a média-állapot is itt (a felső sávból költözött) — a szervezőknek szól */}
          {(music.url || music.loading) && <span data-reveal-musicready={music.url ? '1' : '0'}><span aria-hidden="true" style={{ opacity:0.35 }}>· </span>{music.url ? (music.builtin ? '🎵 alapzene kész' : '🎵 zene kész') : `🎵 zene ${music.pct || 0}%`}</span>}
          {(video.url || video.loading) && <span data-reveal-videoready={video.url ? '1' : '0'}><span aria-hidden="true" style={{ opacity:0.35 }}>· </span>{video.url ? '🎬 videó kész' : `🎬 videó ${video.pct || 0}%`}</span>}""")

open(P, 'w', encoding='utf-8').write(s)
print('ok')
