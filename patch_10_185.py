#!/usr/bin/env python3
# v10.185 — Ország-Város: a sor végén + gomb, a mentett szavak alatta
#
# Marad a nyolc sor. A sor végén a pipa helyett + gomb: megnyomva a beírt szó
# lementődik, chipként megjelenik az input alatt, a mező kiürül, jöhet a
# következő. Amit a végén nem mentettél le, az is bent marad értéknek.
#
# A tárolt érték továbbra is EGYETLEN, vesszővel tagolt string. A trükk, hogy
# az utolsó vessző utáni rész a "még gépelem" szó — így a + nem több, mint egy
# vessző hozzáírása. Ezért a beküldés, a szinkron és az ovfjVals változatlan,
# és a bent felejtett szó magától beleszámít.
import sys

P = 'app.src.html'
src = open(P, encoding='utf-8').read()

def sub(old, new, what):
    global src
    assert src.count(old) == 1, '%s: %d talalat' % (what, src.count(old))
    src = src.replace(old, new, 1)

# ─── 1) A sor állapota: mentett szavak + a gépelt szó ───
sub("""          const v = localAns[cat.key]||'';
          const words = parse(v);
          const kept = lim ? words.slice(0, lim) : words;
          const goodCount = kept.filter(w => ovfjLetterOk(w, letter)).length;
          const filled = words.length > 0;""",
    """          const v = localAns[cat.key]||'';
          // Az utolsó vessző utáni rész az, amit épp gépel; ami előtte van, azt
          // már lementette a + gombbal.
          const cutAt = v.lastIndexOf(',');
          const head = cutAt >= 0 ? v.slice(0, cutAt + 1) : '';
          const draft = cutAt >= 0 ? v.slice(cutAt + 1) : v;
          const saved = parse(head);
          const words = parse(v);
          const kept = lim ? words.slice(0, lim) : words;
          const goodCount = kept.filter(w => ovfjLetterOk(w, letter)).length;
          const full = !!lim && saved.length >= lim;
          const canAdd = !submitted && !full && draft.trim().length > 0;
          const addWord = () => {
            if (!canAdd) return;
            setLocalAns(p => ({...p, [cat.key]: head + draft.trim() + ','}));
          };
          const dropWord = (wi) => {
            // Egy elgépelt szó után különben nem lenne visszaút.
            if (submitted) return;
            const rest = saved.filter((_, i) => i !== wi);
            setLocalAns(p => ({...p, [cat.key]: (rest.length ? rest.join(', ') + ',' : '') + draft}));
          };
          const filled = words.length > 0;""",
    'sor allapot')

# ─── 2) A címke melletti badge ───
sub("""                  <span>{cat.label}</span>
                  {lim !== 1 && <span style={{fontWeight:T.weightTitle,color:goodCount?T.mint:T.inkMute}}>{goodCount}/{lim || '∞'}</span>}""",
    """                  <span>{cat.label}</span>
                  {lim !== 1 && (
                    <span style={{fontFamily:T.font,fontWeight:T.weightTitle,fontSize:10,lineHeight:1,
                                  color: goodCount ? '#fff' : T.inkSoft,
                                  background: goodCount ? T.mint : T.inkMute+'2e',
                                  borderRadius:999, padding:'3px 7px'}}>
                      {goodCount}{lim ? '/' + lim : ''}
                    </span>
                  )}""",
    'cimke badge')

# ─── 3) Az input: csak a gépelt szót szerkeszti ───
sub("""                  value={v}
                  onFocus={()=>setFocusIdx(idx)}
                  onBlur={()=>setFocusIdx(f=>f===idx?-1:f)}
                  onChange={e=>!submitted&&setLocalAns(p=>({...p,[cat.key]:e.target.value}))}
                  onKeyDown={e=>{if(e.key==='Enter'&&idx<OVFJ_CATS.length-1)inputRefs.current[idx+1]?.focus();}}
                  disabled={submitted}
                  placeholder={lim === 1 ? `${letter}...` : `${letter}..., ${letter}...`}""",
    """                  value={lim === 1 ? v : draft}
                  onFocus={()=>setFocusIdx(idx)}
                  onBlur={()=>setFocusIdx(f=>f===idx?-1:f)}
                  onChange={e=>{
                    if (submitted) return;
                    // A vessző előtti rész érintetlen marad — csak a gépelt szó változik.
                    const nv = lim === 1 ? e.target.value : head + e.target.value;
                    setLocalAns(p=>({...p,[cat.key]:nv}));
                  }}
                  onKeyDown={e=>{
                    if (e.key !== 'Enter') return;
                    // Az Enter ugyanazt csinálja, mint a + gomb; ha nincs mit
                    // menteni, ugrik a következő kategóriára.
                    if (canAdd) { e.preventDefault(); addWord(); return; }
                    if (idx < OVFJ_CATS.length-1) inputRefs.current[idx+1]?.focus();
                  }}
                  disabled={submitted || full}
                  placeholder={submitted ? '' : full ? 'Megvan mind' : `${letter}...`}""",
    'input')

# ─── 4) A lementett szavak lábléce ───
sub("""                {/* Amit felismertünk. Enélkül nem derülne ki menet közben, hogy
                    egy vessző lemaradt, vagy hogy a negyedik szó már nem számít. */}
                {lim !== 1 && words.length > 0 && (
                  <div style={{display:'flex',flexWrap:'wrap',gap:4,marginTop:5}}>
                    {words.map((w, wi) => {
                      const over = !!lim && wi >= lim;
                      const bad = !ovfjLetterOk(w, letter);
                      const tone = over ? T.inkMute : bad ? T.coral : T.mint;
                      return (
                        <span key={wi} title={over ? 'a limiten felül' : bad ? 'rossz kezdőbetű' : ''}
                          style={{fontFamily:T.font,fontSize:11,fontWeight:T.weightTitle,color:tone,
                                  background:tone+'1f',borderRadius:999,padding:'2px 8px',
                                  textDecoration:(over||bad)?'line-through':'none',opacity:over?0.7:1}}>{w}</span>
                      );
                    })}
                  </div>
                )}""",
    """                {/* A lementett szavak. Koppintásra kikerülnek — egy elgépelt szó
                    után különben nem lenne visszaút. */}
                {lim !== 1 && saved.length > 0 && (
                  <div style={{display:'flex',flexWrap:'wrap',gap:4,marginTop:6}}>
                    {saved.map((w, wi) => {
                      const bad = !ovfjLetterOk(w, letter);
                      const tone = bad ? T.coral : T.mint;
                      return (
                        <button key={wi} onClick={()=>dropWord(wi)} disabled={submitted}
                          title={bad ? 'rossz kezdőbetű — koppints, hogy kivedd' : 'koppints, hogy kivedd'}
                          style={{display:'flex',alignItems:'center',gap:5,border:'none',
                                  fontFamily:T.font,fontSize:11.5,fontWeight:T.weightTitle,color:tone,
                                  background:tone+'20',borderRadius:999,padding:'3px 7px 3px 9px',
                                  cursor:submitted?'default':'pointer',WebkitTapHighlightColor:'transparent',
                                  textDecoration:bad?'line-through':'none'}}>
                          {w}{!submitted && OVFJ_UI.cross(tone, 11)}
                        </button>
                      );
                    })}
                  </div>
                )}""",
    'lablec')

# ─── 5) A sor végén: pipa helyett + ───
sub("""              <div style={{width:24,height:24,borderRadius:'50%',flexShrink:0,display:'grid',placeItems:'center',background:ok?T.mint:'transparent',border:ok?'none':`2px solid ${wrong?T.coral:T.inkMute+'55'}`,transition:'background .2s'}}>
                {ok && <svg width="13" height="13" viewBox="0 0 24 24" fill="none"><path d="M5 13l4 4 10-10" stroke="#fff" strokeWidth="3" strokeLinecap="round" strokeLinejoin="round"/></svg>}
                {wrong && <span style={{color:T.coral,fontFamily:T.font,fontSize:13,fontWeight:900,lineHeight:1}}>!</span>}
              </div>""",
    """              {lim === 1 ? (
                <div style={{width:24,height:24,borderRadius:'50%',flexShrink:0,display:'grid',placeItems:'center',background:ok?T.mint:'transparent',border:ok?'none':`2px solid ${wrong?T.coral:T.inkMute+'55'}`,transition:'background .2s'}}>
                  {ok && <svg width="13" height="13" viewBox="0 0 24 24" fill="none"><path d="M5 13l4 4 10-10" stroke="#fff" strokeWidth="3" strokeLinecap="round" strokeLinejoin="round"/></svg>}
                  {wrong && <span style={{color:T.coral,fontFamily:T.font,fontSize:13,fontWeight:900,lineHeight:1}}>!</span>}
                </div>
              ) : (
                <button onClick={addWord} disabled={!canAdd} aria-label="Szó hozzáadása"
                  title={full ? 'elérted a limitet' : 'a beírt szó mentése'}
                  style={{width:32,height:32,borderRadius:'50%',flexShrink:0,display:'grid',placeItems:'center',padding:0,
                          background: canAdd ? T.mint : 'transparent',
                          border: canAdd ? 'none' : `2px solid ${T.inkMute}55`,
                          cursor: canAdd ? 'pointer' : 'default',
                          transition:'background .2s', WebkitTapHighlightColor:'transparent'}}>
                  <svg width="16" height="16" viewBox="0 0 24 24" fill="none"
                       stroke={canAdd ? '#fff' : T.inkMute} strokeWidth="2.8" strokeLinecap="round">
                    <path d="M12 5v14M5 12h14"/>
                  </svg>
                </button>
              )}""",
    'sor vege')

# ─── verziobump ───
sub("const APP_VERSION = 'v10.184';", "const APP_VERSION = 'v10.185';", 'verzio')

open(P, 'w', encoding='utf-8').write(src)
print('OK — + gomb a sor vegen, lablec a mentett szavakkal, darabszam badge')
