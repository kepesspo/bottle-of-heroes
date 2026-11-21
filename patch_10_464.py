# v10.464 — Gender Reveal csip: a kész állapot ZÖLD, a „kész" szó nélkül
P = 'app.src.html'
s = open(P, encoding='utf-8').read()
def rep(old, new, cnt=1):
    global s
    n = s.count(old)
    assert n == cnt, (n, old[:90])
    s = s.replace(old, new)

rep("const APP_VERSION = 'v10.463';", "const APP_VERSION = 'v10.464';")
rep("{soundOk ? '🔊 hang kész' : '🔇 kattints egyet a hangért'}",
    "{soundOk ? '🔊 hang' : '🔇 kattints egyet a hangért'}")
rep("""          {(music.url || music.loading) && <span data-reveal-musicready={music.url ? '1' : '0'}><span aria-hidden="true" style={{ opacity:0.35 }}>· </span>{music.url ? (music.builtin ? '🎵 alapzene kész' : '🎵 zene kész') : `🎵 zene ${music.pct || 0}%`}</span>}
          {(video.url || video.loading) && <span data-reveal-videoready={video.url ? '1' : '0'}><span aria-hidden="true" style={{ opacity:0.35 }}>· </span>{video.url ? '🎬 videó kész' : `🎬 videó ${video.pct || 0}%`}</span>}""",
"""          {/* v10.464: kész = ZÖLD, a „kész" szó nélkül (a szín maga az állapot); töltés közben százalék */}
          {(music.url || music.loading) && <span data-reveal-musicready={music.url ? '1' : '0'} style={{ color: music.url ? '#1F6B50' : REVEAL_INK }}><span aria-hidden="true" style={{ opacity:0.35, color:REVEAL_INK }}>· </span>{music.url ? (music.builtin ? '🎵 alapzene' : '🎵 zene') : `🎵 zene ${music.pct || 0}%`}</span>}
          {(video.url || video.loading) && <span data-reveal-videoready={video.url ? '1' : '0'} style={{ color: video.url ? '#1F6B50' : REVEAL_INK }}><span aria-hidden="true" style={{ opacity:0.35, color:REVEAL_INK }}>· </span>{video.url ? '🎬 videó' : `🎬 videó ${video.pct || 0}%`}</span>}""")
open(P, 'w', encoding='utf-8').write(s)
print('ok')
