#!/usr/bin/env python3
# v10.196 — Anagramma: a mockup szerinti elrendezés
#
# Eddig szet volt szorva a kepernyon: kor-idozito, alatta a helyek, alatta a
# betuk, kozottuk pontok. A terv szerint a feladat EGY kartyan ul (felirat +
# helyek + ido), a betuk pedig kulon, "BETŰK" cimke alatt — igy latszik, hogy
# a betuket kell a helyekre pakolni.
#
# A betu-lapkak halvany, kulonbozo szinuek, sotet betuvel: fehér betű a telt
# szinen kisebb meretben elmosodott, es a negy szin ismetlodott ot betunel.
import sys

P = 'app.src.html'
src = open(P, encoding='utf-8').read()

def sub(old, new, what):
    global src
    assert src.count(old) == 1, '%s: %d talalat' % (what, src.count(old))
    src = src.replace(old, new, 1)

# ─── betű-lapka színek ───
sub("""  const TILE_COLORS = [T.mint, T.mint, T.coral, T.yellow];""",
    """  // Hat kulonbozo halvany szin: het betunel sem ismetlodik ket szomszed, es
  // a sotet betu rajtuk minden temaban olvashato marad.
  const TILE_COLORS = ['#F2C4C4', '#CFC2EE', '#BFE3C9', '#BFD8EF', '#F2DDA8', '#EFC9DE'];""",
    'lapka szinek')

# ─── a teljes render ujraszervezese ───
OLD = src[src.index("""      {/* Arc timer */}"""):src.index("""      {/* Hidden phase: Start button */}""")]
NEW = """      {/* A feladat egy kártyán: felirat + helyek + idő. Külön elemekként
          szétszórva nem látszott, hogy ezek együtt egy feladvány. */}
      <div style={{ width:'100%', boxSizing:'border-box', background:T.surface, borderRadius:18,
                    padding:'18px 14px', boxShadow:T.shadow,
                    display:'flex', flexDirection:'column', alignItems:'center', gap:14 }}>
        <div style={{ fontFamily:T.font, fontWeight:900, fontSize:14, color:T.ink, letterSpacing:'0.1em' }}>RAKD KI A SZÓT!</div>

        {/* Helyek */}
        <div style={{ display:'flex', gap:8, flexWrap:'wrap', justifyContent:'center' }}>
          {word.split('').map((_, i) => (
            <div key={i} style={{
              width:48, height:54, borderRadius:12,
              background: i < pressed.length ? T.mint+'26' : T.inkMute+'1a',
              border: `2px solid ${i < pressed.length ? T.mint : 'transparent'}`,
              display:'grid', placeItems:'center',
              fontFamily:T.font, fontWeight:900, fontSize:24, color:T.ink,
              transition:'all .12s',
            }}>
              {i < pressed.length ? shuffled[pressed[i]] : ''}
            </div>
          ))}
        </div>

        {/* Idő — pirulában, hogy a kártya része legyen */}
        {phase === 'playing' && (
          <div style={{ display:'flex', alignItems:'center', gap:8, background: timerColor+'1f',
                        borderRadius:999, padding:'8px 18px' }}>
            <BohIcon name="timer" size={16} />
            <span style={{ fontFamily:T.font, fontWeight:900, fontSize:19, color:timerColor,
                           fontVariantNumeric:'tabular-nums', lineHeight:1 }}>
              {'00:' + String(Math.ceil(timeLeft)).padStart(2,'0')}
            </span>
          </div>
        )}

"""
src = src.replace(OLD, NEW, 1)

# a Start gomb es az eredmeny-uzenetek a kartyan BELUL zarjanak
sub("""      {/* Hidden phase: Start button */}
      {phase === 'hidden' && (""",
    """        {/* Hidden phase: Start button */}
        {phase === 'hidden' && (""",
    'start nyito')
sub("""        <button onClick={startGame} style={{ padding:'12px 32px', background:`${T.mint}22`, border:`2px solid ${T.mint}`, color:T.mint, fontFamily:T.font, fontWeight:700, fontSize:16, borderRadius:14, cursor:'pointer' }}>
          ▶ Start!
        </button>
      )}""",
    """          <button onClick={startGame} style={{ padding:'12px 32px', background:`${T.mint}22`, border:`2px solid ${T.mint}`, color:T.mint, fontFamily:T.font, fontWeight:700, fontSize:16, borderRadius:14, cursor:'pointer' }}>
            ▶ Start!
          </button>
        )}""",
    'start gomb')

sub("""      {/* Won */}
      {phase === 'won' && (
        <div style={{ textAlign:'center', animation:'popIn .3s' }}>
          <BohIcon name="party" size={29} />
          <div style={{ fontFamily:T.font, fontWeight:800, fontSize:17, color:T.mint, marginTop:4 }}>{t('anagrammaWin')} {word}</div>
        </div>
      )}

      {/* Lost */}
      {phase === 'lost' && (
        <div style={{ textAlign:'center', animation:'popIn .3s' }}>
          <div style={{ fontSize:32 }}>⏱️</div>
          <div style={{ fontFamily:T.font, fontWeight:700, fontSize:15, color:T.coral, marginTop:4 }}>{t('anagrammaTimeUp')} <strong>{word}</strong></div>
        </div>
      )}


    </div>
  );
}""",
    """        {/* Won */}
        {phase === 'won' && (
          <div style={{ textAlign:'center', animation:'popIn .3s' }}>
            <BohIcon name="party" size={29} />
            <div style={{ fontFamily:T.font, fontWeight:800, fontSize:17, color:T.mint, marginTop:4 }}>{t('anagrammaWin')} {word}</div>
          </div>
        )}

        {/* Lost */}
        {phase === 'lost' && (
          <div style={{ textAlign:'center', animation:'popIn .3s' }}>
            <div style={{ fontSize:32 }}>⏱️</div>
            <div style={{ fontFamily:T.font, fontWeight:700, fontSize:15, color:T.coral, marginTop:4 }}>{t('anagrammaTimeUp')} <strong>{word}</strong></div>
          </div>
        )}
      </div>

      {/* BETŰK — a cimke a kartya ala bujik, igy latszik, hogy a lapkak
          a fenti helyekhez tartoznak. */}
      {phase !== 'hidden' && (
        <div style={{ marginTop:-24, background:T.surface, borderRadius:999, padding:'5px 14px', boxShadow:T.shadowPill,
                      fontFamily:T.font, fontWeight:900, fontSize:10, color:T.inkSoft, letterSpacing:1.6 }}>BETŰK</div>
      )}

      {/* Betű-lapkák */}
      <div style={{ display:'flex', gap:9, flexWrap:'wrap', justifyContent:'center' }}>
        {phase === 'hidden'
          ? word.split('').map((_, i) => (
              <div key={i} style={{ width:56, height:64, borderRadius:14, background:T.inkMute+'22', display:'grid', placeItems:'center' }}>
                <span style={{ fontFamily:T.font, fontWeight:900, fontSize:26, color:T.inkMute }}>?</span>
              </div>
            ))
          : shuffled.map((letter, i) => {
              const used = pressed.includes(i);
              return (
                <div key={i} onClick={() => handleTap(i)} style={{
                  width:56, height:64, borderRadius:14,
                  background: used ? T.inkMute+'26' : wrongFlash ? T.coral : TILE_COLORS[i % TILE_COLORS.length],
                  boxShadow: used ? 'none' : T.shadowPill,
                  display:'grid', placeItems:'center',
                  fontFamily:T.font, fontWeight:900, fontSize:30,
                  color: used ? T.inkMute : (wrongFlash ? '#fff' : T.ink),
                  opacity: used ? 0.5 : 1,
                  transform: used ? 'translateY(3px)' : 'none',
                  cursor: used || phase !== 'playing' ? 'default' : 'pointer',
                  userSelect:'none', transition:'all .1s',
                }}>{letter}</div>
              );
            })}
      </div>
    </div>
  );
}""",
    'lapkak + zaras')

sub("const APP_VERSION = 'v10.195';", "const APP_VERSION = 'v10.196';", 'verzio')
open(P, 'w', encoding='utf-8').write(src)
print('OK — Anagramma elrendezes a mockup szerint')
