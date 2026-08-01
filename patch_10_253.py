#!/usr/bin/env python3
# v10.253 — Reakció: a rekord és az átlag KÜLÖN kártyára kerül
#
# A v10.252-ben a viszonyítás egy apró sorként bújt meg a sáv alatt. A kérés:
# legyen ugyanolyan doboz, mint a fölötte lévő (aktuális eredmény), csak ebben
# a rekord és az átlag álljon — így ki is tölt valamennyit a képernyőből.
#
# Az elrendezés egy három hasábos rács: név | 🏅 REKORD | 📊 ÁTLAG. A két
# szám-hasáb jobbra zárt és fix szélességű, hogy a számjegyek egymás alá
# essenek (tabular-nums), különben a "58 ms" és a "412 ms" elcsúszna.
#
# Az "ÚJ REKORD" jelvény a rekord-cellába kerül, közvetlenül a szám alá —
# oda, amire vonatkozik.
#
# Ami NEM változik: a számok továbbra is tartalmazzák a mostani kört (vagyis
# ugyanazok, mint ami a statisztikában lesz), a jelvény csak valódi
# rekorddöntésnél jár, és profil nélküli játékos nem kerül a kártyára.
# Ha egyik játékosnak sincs profilja, a kártya el is marad.
import sys

P = 'app.src.html'
src = open(P, encoding='utf-8').read()

def sub(old, new, what):
    global src
    assert src.count(old) == 1, '%s: %d talalat' % (what, src.count(old))
    src = src.replace(old, new, 1)

# ── 1. a sáv alatti sor kikerül a kártya-sorból ──
sub("""            {/* Viszonyitas: egy szam onmagaban nem mond semmit. A rekord es az
                atlag MAR TARTALMAZZA a mostani kort — vagyis ugyanaz, mint ami
                a statisztikaban lesz. Profil nelkuli jatekosnal nincs sor. */}
            {(() => {
              const h = histOf(player, ms);
              if (!h) return null;
              return (
                <div style={{ display:'flex', alignItems:'center', gap:8, marginTop:7, flexWrap:'wrap' }}>
                  {h.isRecord && (
                    <span style={{ fontFamily:T.font, fontWeight:900, fontSize:10, letterSpacing:0.6, textTransform:'uppercase',
                                   color:'#fff', background:T.mint, borderRadius:999, padding:'3px 8px' }}>★ Új rekord</span>
                  )}
                  <span style={{ fontFamily:T.font, fontWeight:700, fontSize:11.5, color:T.inkMute, letterSpacing:0.2 }}>
                    Rekord <b style={{ color:T.inkSoft, fontVariantNumeric:'tabular-nums' }}>{h.best} ms</b>
                  </span>
                  <span style={{ width:3, height:3, borderRadius:'50%', background:T.inkMute, opacity:0.6 }} />
                  <span style={{ fontFamily:T.font, fontWeight:700, fontSize:11.5, color:T.inkMute, letterSpacing:0.2 }}>
                    Átlag <b style={{ color:T.inkSoft, fontVariantNumeric:'tabular-nums' }}>{h.avg} ms</b>
                  </span>
                </div>
              );
            })()}
          </div>
        ))}
      </div>
      {/* Az atlag a mostani frissites ota gyulik — a rekord a regi adatbol is
          megvan. Ezt egyszer megmondjuk, hogy ne tunjon hibanak. */}
      {players2.some(x => { const h = histOf(x.player, x.ms); return h && h.avg === h.best && h.best === x.ms; }) && (
        <div style={{ fontFamily:T.font, fontSize:11, color:T.inkMute, textAlign:'center', marginTop:-6 }}>
          Az átlag most kezdett gyűlni — több kör után lesz beszédes.
        </div>
      )}""",
    """          </div>
        ))}
      </div>
      {/* Viszonyitas KULON kartyan, ugyanolyan dobozban mint a mostani eredmeny.
          A szamok MAR TARTALMAZZAK ezt a kort — vagyis ugyanazok, mint amik a
          statisztikaban lesznek. Profil nelkuli jatekos nem kerul bele; ha
          egyiknek sincs profilja, a kartya elmarad. */}
      {(() => {
        const hist = players2.map(x => ({ ...x, h: histOf(x.player, x.ms) })).filter(x => x.h);
        if (!hist.length) return null;
        const fresh = hist.some(x => x.h.avg === x.h.best && x.h.best === x.ms);
        const head = { fontFamily:T.font, fontWeight:900, fontSize:10.5, letterSpacing:0.8, textTransform:'uppercase',
                       color:T.inkMute, textAlign:'right', minWidth:78 };
        const num  = { fontFamily:T.font, fontWeight:900, fontSize:19, fontVariantNumeric:'tabular-nums', textAlign:'right', minWidth:78 };
        return (
          <div style={{ width:'100%', background:T.surface, borderRadius:20, padding:'16px 16px 14px', boxShadow:T.shadow }}>
            <div style={{ display:'grid', gridTemplateColumns:'1fr auto auto', columnGap:14, rowGap:14, alignItems:'center' }}>
              <span />
              <span style={head}>🏅 Rekord</span>
              <span style={head}>📊 Átlag</span>
              {hist.map((x, i) => (
                <React.Fragment key={i}>
                  <span style={{ fontFamily:T.font, fontWeight:800, fontSize:15, color:T.ink,
                                 overflow:'hidden', textOverflow:'ellipsis', whiteSpace:'nowrap' }}>
                    {x.player?.name || (i === 0 ? 'Kihívó' : 'Ellenfél')}
                  </span>
                  <span style={{ display:'flex', flexDirection:'column', alignItems:'flex-end', gap:3 }}>
                    <span style={{ ...num, color: x.h.isRecord ? T.mint : T.ink }}>{x.h.best} ms</span>
                    {x.h.isRecord && (
                      <span style={{ fontFamily:T.font, fontWeight:900, fontSize:9, letterSpacing:0.6, textTransform:'uppercase',
                                     color:'#fff', background:T.mint, borderRadius:999, padding:'2px 7px' }}>★ Új rekord</span>
                    )}
                  </span>
                  <span style={{ ...num, color:T.inkSoft }}>{x.h.avg} ms</span>
                </React.Fragment>
              ))}
            </div>
            {/* Az atlag a mostani frissites ota gyulik — a rekord a regi adatbol
                is megvan. Ezt megmondjuk, hogy ne tunjon hibanak. */}
            {fresh && (
              <div style={{ fontFamily:T.font, fontSize:11, color:T.inkMute, textAlign:'center', marginTop:14, lineHeight:1.4 }}>
                Az átlag most kezdett gyűlni — több kör után lesz beszédes.
              </div>
            )}
          </div>
        );
      })()}""",
    'kulon kartya')

sub("const APP_VERSION = 'v10.252';", "const APP_VERSION = 'v10.253';", 'verzio')
open(P, 'w', encoding='utf-8').write(src)
print('OK — rekord + atlag kulon kartyan')
