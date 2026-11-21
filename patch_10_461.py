# v10.461 — Gender Reveal: beépített visszaszámláló zene (assets/reveal_countdown_music.mp3)
#  - ha a Szülők nem töltöttek fel saját zenét, ez szól a dobpergés helyett
#  - a 10 ütés a 10 számváltásra van igazítva (0,55 mp levágva az elejéről, 3% gyorsítás)
#  - ha a zene a visszaszámláláson belül magától véget ér, nincs halkítás (különben az utolsó ütés elveszne)
P = 'app.src.html'
s = open(P, encoding='utf-8').read()
def rep(old, new, cnt=1):
    global s
    n = s.count(old)
    assert n == cnt, (n, old[:90])
    s = s.replace(old, new)

rep("const APP_VERSION = 'v10.460';", "const APP_VERSION = 'v10.461';")

rep("const REVEAL_MUSIC_MAX = 20 * 1024 * 1024;   // v10.458: a visszaszámlálás zenéje (pár perces mp3 is bőven belefér)",
    "const REVEAL_MUSIC_MAX = 20 * 1024 * 1024;   // v10.458: a visszaszámlálás zenéje (pár perces mp3 is bőven belefér)\n"
    "// v10.461: beépített zene, ha a Szülők nem töltöttek fel sajátot. 9,7 mp, a 10 ütése a 10 számváltásra esik.\n"
    "const REVEAL_DEFAULT_MUSIC = 'assets/reveal_countdown_music.mp3';")

# useRevealVideo: a meta állapota is kifelé megy (a beépített zene ebből tudja, hogy van-e feltöltött)
rep("""  }, [meta.loaded, m.vid, m.uploading]);
  return st;
}""",
"""  }, [meta.loaded, m.vid, m.uploading]);
  return Object.assign({}, st, { metaLoaded: meta.loaded, has: !!m.vid, uploading: !!m.uploading });
}
// v10.461: a visszaszámlálás zenéje — a feltöltött, vagy ha nincs, a beépített. A beépítettet is
// Blob-URL-ként adjuk (a service worker cache-first válasza a médiaelem Range-kérésére Safariban
// elakadhat); ha a fetch nem megy (file://), a sima útvonal.
function useRevealMusic() {
  const up = useRevealVideo('revealAudio');
  const useDef = up.metaLoaded && !up.has && !up.uploading;
  const [def, setDef] = React.useState({ url:null, loading:false });
  React.useEffect(() => {
    if (!useDef || def.url) return;
    let dead = false; setDef({ url:null, loading:true, pct:0 });
    fetch(REVEAL_DEFAULT_MUSIC).then(r => { if (!r.ok) throw new Error('http'); return r.blob(); })
      .then(b => { if (!dead) setDef({ url: URL.createObjectURL(b.type ? b : new Blob([b], { type:'audio/mpeg' })), loading:false, pct:100, builtin:true }); })
      .catch(() => { if (!dead) setDef({ url: REVEAL_DEFAULT_MUSIC, loading:false, pct:100, builtin:true }); });
    return () => { dead = true; };
  }, [useDef]);
  return useDef ? def : up;
}""")

rep("  const music = useRevealVideo('revealAudio');             // v10.458: a visszaszámlálás zenéje",
    "  const music = useRevealMusic();                          // v10.458: a visszaszámlálás zenéje (v10.461: beépített is)")
rep("{music.url ? '🎵 zene kész' : `🎵 zene töltődik… ${music.pct || 0}%`}",
    "{music.url ? (music.builtin ? '🎵 alapzene kész' : '🎵 zene kész') : `🎵 zene töltődik… ${music.pct || 0}%`}")

# a halkítás csak akkor, ha a zene túlnyúlna a visszaszámláláson
rep("fiv = setInterval(() => { const left = total - (performance.now() - t0) / 1000; try { a.volume = Math.max(0, vol * Math.min(1, left / fade)); } catch(e) {} }, 50);",
    "// v10.461: ami magától véget ér a „0” előtt (a beépített zene 9,7 mp), azt nem halkítjuk — az utolsó ütés kell\n"
    "      fiv = setInterval(() => { if (a.duration && a.duration <= total + 0.3) return; const left = total - (performance.now() - t0) / 1000; try { a.volume = Math.max(0, vol * Math.min(1, left / fade)); } catch(e) {} }, 50);")

# Szülők: a sor a beépített zenét írja ki; a hangerő mindig kint (mindig van zene)
rep("""    emptyText="Nincs — a dobpergés szól" delTitle="Zene törlése" delText="A visszaszámlálás alatt a dobpergés fog szólni." gone="Zene törölve" />;""",
    """    emptyText="Beépített visszaszámláló zene" delTitle="Saját zene törlése" delText="A visszaszámlálás alatt a beépített zene fog szólni." gone="Zene törölve" />;""")
rep("  if (!(meta.v || {}).vid && !(mus.v || {}).vid) return null;\n",
    "  // v10.461: zene mindig van (a beépített), tehát a hangerő is mindig számít\n")
rep("// v10.458: a visszaszámlálás zenéje — ha van, a dobpergés HELYETT szól, a „0\" előtt elhalkul",
    "// v10.458: a visszaszámlálás zenéje — ha van, a dobpergés HELYETT szól, a „0\" előtt elhalkul.\n// v10.461: feltöltés nélkül a beépített zene (REVEAL_DEFAULT_MUSIC) szól.")

open(P, 'w', encoding='utf-8').write(s)
print('ok')
