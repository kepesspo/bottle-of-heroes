#!/usr/bin/env python3
# v10.262 — Result Banner: világos kártya, felül állapotcsíkkal
#
# A teli zöld/piros banner helyett ugyanaz a kártya-minta, ami a játékokban is
# fut: avatar, kicsi nagybetűs felirat, név, jobbra a szám. Az állapotot egy
# vékony csík mondja meg a tetején (zöld / piros / félig-félig / palaszürke).
#
# A JÓVÁHAGYOTT DESIGN (mockup: „A" változat, hibrid sorokkal)
#   - a kártya MINDIG 300 px magas — 1 nyertes, 1 vesztes vagy vegyes, mindegy.
#     Ha csak egy kimenet van, az kapja a teljes magasságot nagyobb avatarral
#     és névvel, így nem marad üres fél.
#   - EGY fő az adott oldalon → a megszokott sor (nagy avatar, név nagyban)
#   - KETTŐ vagy több → avatarok + felirat, a névsor a sor ALATT, teli
#     szélességben, két sorig. A váltás oldalanként dől el.
#   - a szám (pont/korty) MINDKÉT formában ugyanabban a jobb oldali oszlopban
#     áll, 26 px-en — nem kell két helyen keresni ugyanazt.
#   - a wildcard-jelvény a csíkon lovagol, középen: bal oldalt avatar, jobb
#     oldalt a szám, középen mindig üres a hely.
#   - a jegyzet nem ismétli a metrikát: a „+1 pont" kikerül belőle.
#
# A KICSI SÁV (S3)
#   56 px magas, és UGYANOLYAN SZÉLES, mint a nagy kártya — a lekicsinyítés nem
#   ugrik szélességet. Csak az marad rajta, ami cselekvés: KI ISZIK ÉS MENNYIT.
#   A győztest a nagy kártya már megünnepelte; a részletekért vissza lehet nyitni.
#
# A NAGY KÁRTYÁRÓL KIKERÜLT AZ ✕ GOMB: ugyanazt csinálta, mint a kártyára
# koppintás (kicsinyítés), és az új elrendezésben pont a szám oszlopára esett
# volna. A „koppints a kicsinyítéshez" felirat alatta megmaradt.
#
# Az állapot-színek SZÁNDÉKOSAN függetlenek a témától, ahogy eddig is: az „ice"
# témában a T.mint kék, azzal a győzelem nem lenne olvasható.
import sys, re

P = 'app.src.html'
src = open(P, encoding='utf-8').read()
lines = src.split('\n')

START = '      {/* ResultBanner — split (winners/losers) with legacy fallback */}'
i = lines.index(START)
# a blokk vege: az elso "      })()}" a start utan
j = i
while lines[j] != '      })()}':
    j += 1
assert '{/* footer' in lines[j + 2], 'nem a vart blokkvege: %r' % lines[j + 2]

NEW = r'''      {/* ResultBanner — vilagos kartya, felul allapotcsikkal. Lasd patch_10_262.py */}
      {gameResult && (() => {
        const norm = arr => (Array.isArray(arr)?arr:[]).map(x => typeof x === 'string' ? players.find(p=>p.name===x) : (x && x.player ? x.player : x)).filter(Boolean);
        let winners = norm(gameResult.winners);
        let losers  = norm(gameResult.losers);
        if (!gameResult.winners && !gameResult.losers) {
          const rp = gameResult.playerName ? players.find(p => p.name === gameResult.playerName) : null;
          const subPl = gameResult.subtitle ? gameResult.subtitle.split(', ').map(s => { const nm = s.split(':')[0].trim(); return players.find(p => p.name === nm); }).filter(Boolean) : [];
          const grp = subPl.length >= 2 ? subPl : (rp ? [rp] : []);
          if (gameResult.correct) winners = grp; else losers = grp;
        }
        const hasWin = winners.length > 0, hasLose = losers.length > 0;
        const drinks = gameResult.drinks || 0;
        const neutral = !hasWin && !hasLose;
        const neutralPos = neutral && drinks === 0 && gameResult.correct !== false;
        const isDraw = gameResult.draw === true;

        // Allapot-szinek — SZANDEKOSAN fuggetlenek a tematol: az "ice" temaban
        // pl. a T.mint kek, azzal a gyozelem nem lenne olvashato.
        const WIN_C = '#2E9A70', LOSE_C = '#D0574C', DRAW_C = '#6E7C93';
        const glow = isDraw ? DRAW_C : ((hasWin && !hasLose) || neutralPos ? WIN_C : LOSE_C);
        const soloCard = neutral || !(hasWin && hasLose);   // egyetlen kimenet → nagyobb betu/avatar

        // A jegyzetbol kiszedjuk, amit a metrika ugyis kiir.
        const cleanNote = t => String(t || '').replace(/\+1 pont\s*/g, '')
          .replace(/^[\s·—–-]+/, '').replace(/[\s·—–-]+$/, '').trim();
        const note = [cleanNote(gameResult.winNote), cleanNote(gameResult.loseNote),
                      neutral ? '' : cleanNote(gameResult.subtitle)].filter(Boolean).join(' · ');

        // FONTOS: ezek a "komponensek" a renderen BELUL keletkeznek, tehat minden
        // ujrarajzolaskor uj fuggveny-azonossagot kapnanak. Ha JSX-kent hasznalnank
        // oket (<Pile />), a React mas tipusnak latna es ujramountolna a reszfat —
        // a profilkep <img>-je minden korben ujraepulne. Ezert SIMA FUGGVENYHIVAS.
        const Pile = ({ list, max, size, overlap, borderW }) => {
          const shown = list.slice(0, max), extra = Math.max(0, list.length - max);
          return (
            <div style={{ display:'flex', alignItems:'center', flexShrink:0 }}>
              {shown.map((p, i) => (
                <div key={p.id||i} style={{ width:size, height:size, borderRadius:'50%', background:p.color||'#8894A8', display:'grid', placeItems:'center', overflow:'hidden', border: i ? `${borderW}px solid ${T.surface}` : 'none', marginLeft: i===0?0:-overlap, zIndex: shown.length-i, flexShrink:0, boxShadow: i===0 ? '0 2px 6px rgba(20,30,50,0.16)' : 'none' }}>
                  {p.img ? <img src={p.img} alt="" style={{ width:size, height:size, objectFit:'cover', display:'block' }} />
                         : <span style={{ fontFamily:T.font, fontWeight:900, fontSize:Math.round(size*0.42), color:'#fff' }}>{(p.name||'?').charAt(0).toUpperCase()}</span>}
                </div>
              ))}
              {extra > 0 && (
                <div style={{ width:size, height:size, borderRadius:'50%', background:'#8894A8', display:'grid', placeItems:'center', border:`${borderW}px solid ${T.surface}`, marginLeft:-overlap, fontFamily:T.font, fontWeight:900, fontSize:Math.round(size*0.36), color:'#fff', flexShrink:0 }}>+{extra}</div>
              )}
            </div>
          );
        };

        const Metric = ({ value, unit, color }) => (
          <div style={{ flexShrink:0, display:'flex', flexDirection:'column', alignItems:'center', gap:3, minWidth:52 }}>
            <span style={{ fontFamily:T.font, fontWeight:900, fontSize: soloCard ? 32 : 26, lineHeight:1, letterSpacing:'-0.03em', color, fontVariantNumeric:'tabular-nums' }}>{value}</span>
            <span style={{ fontFamily:T.font, fontWeight:900, fontSize:9, letterSpacing:'0.13em', color:T.inkMute, lineHeight:1 }}>{unit}</span>
          </div>
        );

        // EGY fo → a megszokott sor. KETTO vagy tobb → avatarok + felirat,
        // a nevsor a sor ALATT teli szelessegben (ott sokkal tobb nev fer ki).
        const Row = ({ list, kind, first }) => {
          const col = isDraw ? DRAW_C : (kind === 'win' ? WIN_C : LOSE_C);
          const kicker = isDraw ? 'Döntetlen'
            : kind === 'win' ? (list.length > 1 ? 'Nyertesek' : 'Nyertes')
                             : (list.length > 1 ? 'Isznak' : 'Iszik');
          const value = kind === 'win' ? '+1' : String(drinks);
          const unit = kind === 'win' ? 'PONT' : 'KORTY';
          const kickerEl = (
            <span style={{ fontFamily:T.font, fontWeight:900, fontSize: soloCard ? 10.5 : 9.5, letterSpacing:'0.16em', textTransform:'uppercase', lineHeight:1, color:col }}>{kicker}</span>
          );
          const rowStyle = { flex:1, minHeight:0, display:'flex', alignItems:'center', gap:12, padding:'12px 16px',
                             borderTop: first ? 'none' : `1px solid ${T.inkMute}22` };
          if (list.length === 1) {
            const av = soloCard ? 64 : 46;
            return (
              <div style={rowStyle}>
                {Pile({ list, max:1, size:av, overlap:0, borderW:3 })}
                <div style={{ flex:1, minWidth:0 }}>
                  {kickerEl}
                  <div style={{ fontFamily:T.font, fontWeight:900, fontSize: soloCard ? 27 : 20, color:T.ink, lineHeight:1.15, letterSpacing:'-0.02em', marginTop:4, overflow:'hidden', textOverflow:'ellipsis', whiteSpace:'nowrap' }}>{list[0].name}</div>
                </div>
                {Metric({ value, unit, color:col })}
              </div>
            );
          }
          return (
            <div style={{ ...rowStyle, flexDirection:'column', alignItems:'stretch', justifyContent:'center', gap:9 }}>
              <div style={{ display:'flex', alignItems:'center', gap:11 }}>
                {Pile({ list, max:2, size: soloCard ? 48 : 42, overlap: soloCard ? 14 : 12, borderW:2.5 })}
                <div style={{ flex:1, minWidth:0 }}>{kickerEl}</div>
                {Metric({ value, unit, color:col })}
              </div>
              <div style={{ fontFamily:T.font, fontWeight:800, fontSize: soloCard ? 15.5 : 14.5, color:T.ink, lineHeight:1.35,
                            display:'-webkit-box', WebkitLineClamp: soloCard ? 3 : 2, WebkitBoxOrient:'vertical', overflow:'hidden' }}>
                {list.map(p => p.name).join(' · ')}
              </div>
            </div>
          );
        };

        const NeutralRow = () => (
          <div style={{ flex:1, minHeight:0, display:'flex', alignItems:'center', gap:12, padding:'12px 16px' }}>
            <div style={{ width:56, height:56, borderRadius:'50%', background: neutralPos ? `${WIN_C}1A` : `${LOSE_C}1A`, display:'grid', placeItems:'center', flexShrink:0 }}>
              <BohIcon name={neutralPos ? (/(Döntetlen|Draw)/i.test(gameResult.subtitle||'') ? 'draw' : 'star') : 'beer'} size={28} />
            </div>
            <div style={{ flex:1, minWidth:0, fontFamily:T.font, fontWeight:900, fontSize:19, color:T.ink, lineHeight:1.2, wordBreak:'break-word' }}>
              {gameResult.subtitle || (neutralPos ? 'Kész!' : 'Inni kell!')}
            </div>
            {drinks > 0 && Metric({ value:String(drinks), unit:'KORTY', color: LOSE_C })}
          </div>
        );

        // A csik: felig-felig, ha nyertes ES vesztes is van.
        const Stripe = () => (
          <div style={{ height:6, flexShrink:0, display:'flex' }}>
            {hasWin && hasLose ? (
              <React.Fragment>
                <span style={{ flex:1, background:WIN_C }} /><span style={{ flex:1, background:LOSE_C }} />
              </React.Fragment>
            ) : (
              <span style={{ flex:1, background: isDraw ? DRAW_C : (hasWin || neutralPos ? WIN_C : LOSE_C) }} />
            )}
          </div>
        );

        // ── A KICSI SAV (S3): csak az marad, ami cselekves — ki iszik es mennyit ──
        const drinkSide = hasLose ? losers : winners;
        const miniCol = drinks ? (isDraw ? DRAW_C : LOSE_C) : WIN_C;
        const miniLabel = drinkSide.length === 0
          ? (gameResult.subtitle || (neutralPos ? 'Kész!' : 'Inni kell!'))
          : (drinkSide.length >= 3 ? drinkSide.length + ' fő' : drinkSide.map(p => p.name).join(', '));
        const MiniBar = ({ onClose }) => (
          <div style={{ background:T.surface, borderRadius:16, overflow:'hidden', width:'100%',
                        boxShadow:'0 -2px 10px rgba(20,30,50,0.10), 0 8px 22px rgba(20,30,50,0.22)' }}>
            <div style={{ height:4, display:'flex' }}>
              {hasWin && hasLose ? (
                <React.Fragment><span style={{ flex:1, background:WIN_C }} /><span style={{ flex:1, background:LOSE_C }} /></React.Fragment>
              ) : (<span style={{ flex:1, background: isDraw ? DRAW_C : (hasWin || neutralPos ? WIN_C : LOSE_C) }} />)}
            </div>
            <div style={{ height:52, display:'flex', alignItems:'center', gap:10, padding:'0 12px' }}>
              {drinkSide.length > 0 && Pile({ list: drinkSide, max:2, size:36, overlap:11, borderW:2 })}
              <div style={{ flex:1, minWidth:0, fontFamily:T.font, fontWeight:900, fontSize:14, color:T.ink, overflow:'hidden', textOverflow:'ellipsis', whiteSpace:'nowrap' }}>{miniLabel}</div>
              <div style={{ flexShrink:0, display:'flex', alignItems:'baseline', gap:5 }}>
                <span style={{ fontFamily:T.font, fontWeight:900, fontSize:24, letterSpacing:'-0.03em', color:miniCol, fontVariantNumeric:'tabular-nums' }}>{drinks ? drinks : '+1'}</span>
                <span style={{ fontFamily:T.font, fontWeight:900, fontSize:9, letterSpacing:'0.13em', color:T.inkMute }}>{drinks ? 'KORTY' : 'PONT'}</span>
              </div>
              {onClose && (
                <button onClick={onClose} aria-label="Bezárás" style={{ width:22, height:22, borderRadius:'50%', border:'none', background:`${T.inkMute}2A`, color:T.inkSoft, fontSize:11, fontWeight:900, lineHeight:1, cursor:'pointer', display:'grid', placeItems:'center', padding:0, flexShrink:0 }}>✕</button>
              )}
            </div>
          </div>
        );
        // A kicsi sav UGYANOLYAN SZELES, mint a nagy kartya — a lekicsinyites
        // igy nem ugrik szelesseget.
        const CARD_W = { width:'80vw', minWidth:260, maxWidth:340 };

        if (resultMinimized === 'shrinking' || resultMinimized === true) {
          const showPill = resultMinimized === true;
          return (
            <React.Fragment>
              {resultMinimized === 'shrinking' && (
                <div style={{ position:'fixed', inset:0, zIndex:250, display:'flex', alignItems:'center', justifyContent:'center', animation:'backdropFadeOut .35s ease forwards', pointerEvents:'none' }}>
                  <div style={{ ...CARD_W, animation:'resultShrinkOut .35s cubic-bezier(.4,0,.6,1) forwards' }} onAnimationEnd={() => setResultMinimized(true)}>
                    {MiniBar({})}
                  </div>
                </div>
              )}
              {showPill && (
                <div key={'mini-' + gameResult.ts} onClick={() => setResultMinimized(false)}
                     style={{ position:'fixed', bottom:'calc(96px + env(safe-area-inset-bottom, 0px))', left:'50%', transform:'translateX(-50%)', ...CARD_W, zIndex:45, animation:'miniBarIn .25s ease-out', cursor:'pointer' }}>
                  {MiniBar({ onClose: e => { e.stopPropagation(); setGameResult(null); setResultMinimized(false); } })}
                </div>
              )}
            </React.Fragment>
          );
        }

        const anim = hasWin && !hasLose ? 'resultCalmIn .3s ease-out forwards' : 'resultLoseIn .5s ease-out forwards';
        const wcBadge = gameResult.effect && WC_EFFECTS[gameResult.effect] ? WC_EFFECTS[gameResult.effect].badge : null;
        return (
          <div key={'banner-' + gameResult.ts} onClick={() => setResultMinimized(true)} style={{ position:'fixed', inset:0, zIndex:250, display:'flex', flexDirection:'column', alignItems:'center', justifyContent:'center', gap:12, background:'rgba(0,0,0,0.35)', backdropFilter:'blur(3px)', WebkitBackdropFilter:'blur(3px)' }}>
            {/* Fix magassag → a kartya merete mindig ugyanaz, 1 fo / 2 fo / csapat eseten is */}
            <div style={{ ...CARD_W, height:300, position:'relative', background:T.surface, borderRadius:22, overflow:'hidden', display:'flex', flexDirection:'column', animation:anim, boxShadow:`0 20px 70px ${glow}66, 0 5px 0 rgba(20,30,50,0.07)` }}>
              {Stripe()}
              {/* A wildcard-jelveny a csikon lovagol, kozepen: bal oldalt avatar,
                  jobb oldalt a szam, kozepen viszont mindig ures a hely. */}
              {wcBadge && (
                <div style={{ position:'absolute', top:0, left:'50%', transform:'translateX(-50%)', zIndex:2, background:T.yellow, color:'#5B4508', borderRadius:'0 0 10px 10px', padding:'4px 11px 4.5px', fontFamily:T.font, fontWeight:900, fontSize:9.5, letterSpacing:'0.1em', textTransform:'uppercase', whiteSpace:'nowrap', boxShadow:'0 2px 6px rgba(20,30,50,0.16)' }}>{wcBadge}</div>
              )}
              <div style={{ flex:1, minHeight:0, display:'flex', flexDirection:'column' }}>
                {neutral && NeutralRow()}
                {hasWin && Row({ list: winners, kind:'win', first:true })}
                {hasLose && Row({ list: losers, kind:'lose', first: !hasWin })}
              </div>
              {note && (
                <div style={{ flexShrink:0, padding:'0 16px 12px', fontFamily:T.font, fontWeight:700, fontSize:11.5, color:T.inkMute, lineHeight:1.4, display:'-webkit-box', WebkitLineClamp:2, WebkitBoxOrient:'vertical', overflow:'hidden' }}>
                  <BohText text={note} size={11} />
                </div>
              )}
            </div>
            <span style={{ fontFamily:T.font, fontSize:11, fontWeight:700, color:'rgba(255,255,255,0.7)' }}>koppints a kicsinyítéshez</span>
          </div>
        );
      })()}'''

lines[i:j + 1] = NEW.split('\n')
src = '\n'.join(lines)
assert src.count("koppints a kicsinyítéshez") == 1, 'duplikalt felirat'
src = src.replace("const APP_VERSION = 'v10.261';", "const APP_VERSION = 'v10.262';", 1)
open(P, 'w', encoding='utf-8').write(src)
print('OK — uj Result Banner')
