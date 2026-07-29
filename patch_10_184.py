#!/usr/bin/env python3
# v10.184 — Ország-Város: több szó egy kategóriához
#
# A kör indítása előtt választható, hány szót lehet írni kategóriánként:
# 1 / 2 / 3 / bármennyi. Alapértelmezés az 1 — aki nem nyúl hozzá, annak a
# játék betűre pontosan olyan marad, mint eddig.
#
# A szavakat vesszővel soroljuk egy mezőbe, nem külön inputokba: nyolc kategória
# × 3 mező huszonnégy input lenne egy telefonon, időre. A tárolt érték továbbra
# is egyetlen string — ezért a szinkron es a regi korok valtozatlanul mukodnek,
# csak maskepp OLVASSUK.
import sys

P = 'app.src.html'
src = open(P, encoding='utf-8').read()

def sub(old, new, what):
    global src
    assert src.count(old) == 1, '%s: %d talalat' % (what, src.count(old))
    src = src.replace(old, new, 1)

# ══════════════ 1) Olvasó segédek + érvényesség ══════════════
OLD = """function ovfjVoteKey(round, pid, catKey) { return 'r' + round + '_' + pid + '_' + catKey; }
// Érvényesség: üres / rossz kezdőbetű / egyező (case-insensitive, trim)
function ovfjBuildValidity(answers, letter, round) {
  const recs = Object.values(answers || {}).filter(a => a && a.round === round);
  const dup = {};
  OVFJ_CATS.forEach(cat => {
    const freq = {};
    recs.forEach(a => { const v = String(a[cat.key]||'').trim().toLowerCase(); if (v) freq[v] = (freq[v]||0)+1; });
    dup[cat.key] = new Set(Object.keys(freq).filter(v => freq[v] > 1));
  });
  return (pid, catKey) => {
    const a = (answers||{})[pid];
    const val = String((a && a[catKey]) || '').trim();
    if (!val) return { val, valid:false, reason:'üres' };
    if (!ovfjLetterOk(val, letter)) return { val, valid:false, reason:'✗ betű' };
    if (dup[catKey].has(val.toLowerCase())) return { val, valid:false, reason:'× egyező' };
    return { val, valid:true, reason:null };
  };
}"""

NEW = """// Hány szó írható egy kategóriához. 0 = bármennyi; a hiányzó érték 1, hogy egy
// régi szoba (vagy egy régebbi kliens) a megszokott játékot hozza.
function ovfjLimit(v) {
  if (v === 0 || v === '0') return 0;
  const n = Number(v);
  return Number.isFinite(n) && n > 0 ? Math.floor(n) : 1;
}
// Egy kategória szavai. A mezőben vesszővel elválasztva állnak — a tárolt érték
// továbbra is egyetlen string, ezért a szinkron és a régi körök változatlanok.
function ovfjVals(rec, catKey, limit) {
  const out = [];
  String((rec && rec[catKey]) || '').split(',').forEach(s => { const v = s.trim(); if (v) out.push(v); });
  const lim = ovfjLimit(limit);
  return lim ? out.slice(0, lim) : out;
}
// A 0. válasz kulcsa a régi marad — így egy már beérkezett szavazat nem vész el.
function ovfjVoteKey(round, pid, catKey, idx) {
  const base = 'r' + round + '_' + pid + '_' + catKey;
  return idx ? base + '_' + idx : base;
}
// Érvényesség: üres / rossz kezdőbetű / egyező / ismétlés. Kategóriánként TÖMBÖT
// ad vissza, szavanként egy bejegyzést.
function ovfjBuildValidity(answers, letter, round, limit) {
  const recs = Object.values(answers || {}).filter(a => a && a.round === round);
  const dup = {};
  OVFJ_CATS.forEach(cat => {
    const freq = {};
    recs.forEach(a => {
      // Egy játékos ismétlése nem tesz mást "egyezővé" — az önismétlés külön eset.
      const seen = new Set();
      ovfjVals(a, cat.key, limit).forEach(v => {
        const k = v.toLowerCase();
        if (seen.has(k)) return;
        seen.add(k);
        freq[k] = (freq[k]||0) + 1;
      });
    });
    dup[cat.key] = new Set(Object.keys(freq).filter(v => freq[v] > 1));
  });
  return (pid, catKey) => {
    const vals = ovfjVals((answers||{})[pid], catKey, limit);
    if (!vals.length) return [{ val:'', valid:false, reason:'üres' }];
    const own = new Set();
    return vals.map(val => {
      const k = val.toLowerCase();
      if (!ovfjLetterOk(val, letter)) return { val, valid:false, reason:'✗ betű' };
      // Enélkül "Ausztria, Ausztria, Ausztria" három pont lenne.
      if (own.has(k)) { return { val, valid:false, reason:'× ismétlés' }; }
      own.add(k);
      if (dup[catKey].has(k)) return { val, valid:false, reason:'× egyező' };
      return { val, valid:true, reason:null };
    });
  };
}
// A kör indítása előtti választó. Négy gomb, mert a negyedik ("bármennyi") nem
// szám — csúszka nem tudná kifejezni.
function OVFJLimitPicker({ value, onChange }) {
  const cur = ovfjLimit(value);
  return (
    <div style={{background:T.surface,borderRadius:14,padding:'11px 13px',boxShadow:T.shadow,display:'flex',flexDirection:'column',gap:9}}>
      <div style={{fontFamily:T.font,fontWeight:T.weightTitle,fontSize:12.5,color:T.ink}}>Hány szó egy kategóriához?</div>
      <div style={{display:'flex',gap:6}}>
        {[{v:1,l:'1'},{v:2,l:'2'},{v:3,l:'3'},{v:0,l:'Bármennyi'}].map(o => {
          const on = cur === o.v;
          return (
            <button key={o.v} onClick={()=>onChange(o.v)}
              style={{flex: o.v===0 ? 2.2 : 1, padding:'9px 0', borderRadius:11, cursor:'pointer',
                      border:`1.5px solid ${on?T.mint:T.surfaceMuted}`, background:on?T.mint:'transparent',
                      color:on?'#fff':T.inkSoft, fontFamily:T.font, fontWeight:T.weightTitle, fontSize:13,
                      WebkitTapHighlightColor:'transparent'}}>{o.l}</button>
          );
        })}
      </div>
      <div style={{fontFamily:T.font,fontSize:11,color:T.inkSoft,lineHeight:1.45}}>
        {cur === 1
          ? 'Kategóriánként egy szó — a megszokott játék.'
          : 'Vesszővel sorold fel őket. Minden elfogadott szó 1 pont, az ismételt szó nem ér.'}
      </div>
    </div>
  );
}"""
sub(OLD, NEW, 'validity/voteKey blokk')

# ══════════════ 2) Szavazó nézet — szavanként egy sor ══════════════
sub("""function OVFJVotingView({ letter, round, players, answers, myPid, myVotes, onVote, tallies }) {
  const validity = ovfjBuildValidity(answers, letter, round);""",
    """function OVFJVotingView({ letter, round, players, answers, myPid, myVotes, onVote, tallies, limit }) {
  const validity = ovfjBuildValidity(answers, letter, round, limit);""",
    'VotingView fejlec')

OLD_BODY = """          {participants.map(p => {
            const vi = validity(p.id, cat.key);
            const isMe = p.id === myPid;
            const vk = ovfjVoteKey(round, p.id, cat.key);
            const mv = myVotes[vk];
            const tl = tallies ? (tallies[vk] || {yes:0,no:0}) : null;"""
NEW_BODY = """          {participants.map(p => validity(p.id, cat.key).map((vi, ai) => {
            const isMe = p.id === myPid;
            const vk = ovfjVoteKey(round, p.id, cat.key, ai);
            const mv = myVotes[vk];
            const tl = tallies ? (tallies[vk] || {yes:0,no:0}) : null;
            // A nevet csak az első szónál írjuk ki, de a helye megmarad — így a
            // szavak egy oszlopban állnak akkor is, ha valaki hármat írt.
            const showName = ai === 0;"""
sub(OLD_BODY, NEW_BODY, 'VotingView sor-fej')

sub("""              <div key={p.id} style={{display:'flex',alignItems:'center',gap:8}}>
                <OVFJAvatar p={p} size={22} />
                <span style={{fontFamily:T.font,fontWeight:T.weightTitle,fontSize:12,color:T.inkSoft,width:78,flexShrink:0,overflow:'hidden',textOverflow:'ellipsis',whiteSpace:'nowrap'}}>{p.name}{isMe?' (Te)':''}</span>""",
    """              <div key={p.id + '#' + ai} style={{display:'flex',alignItems:'center',gap:8}}>
                <div style={{width:22,flexShrink:0}}>{showName && <OVFJAvatar p={p} size={22} />}</div>
                <span style={{fontFamily:T.font,fontWeight:T.weightTitle,fontSize:12,color:T.inkSoft,width:78,flexShrink:0,overflow:'hidden',textOverflow:'ellipsis',whiteSpace:'nowrap'}}>{showName ? (p.name + (isMe?' (Te)':'')) : ''}</span>""",
    'VotingView sor-eleje')

sub("""                ) : null}
              </div>
            );
          })}
        </div>
      ))}
    </div>
  );
}""",
    """                ) : null}
              </div>
            );
          }))}
        </div>
      ))}
    </div>
  );
}""",
    'VotingView sor-vege')

# ══════════════ 3) Kitöltő űrlap ══════════════
sub("""function OVFJWritingForm({ letter, remaining, localAns, setLocalAns, submitted, onSubmit, doneInfo }) {
  const inputRefs = React.useRef([]);
  const [focusIdx, setFocusIdx] = React.useState(-1);
  const doneCount = OVFJ_CATS.filter(c => { const v=(localAns[c.key]||'').trim(); return v.length>0 && ovfjLetterOk(v, letter); }).length;""",
    """function OVFJWritingForm({ letter, remaining, localAns, setLocalAns, submitted, onSubmit, doneInfo, limit }) {
  const inputRefs = React.useRef([]);
  const [focusIdx, setFocusIdx] = React.useState(-1);
  const lim = ovfjLimit(limit);
  const parse = (s) => { const o=[]; String(s||'').split(',').forEach(x=>{const v=x.trim(); if(v) o.push(v);}); return o; };
  // Egy kategória akkor kész, ha van benne legalább egy jó betűs szó.
  const doneCount = OVFJ_CATS.filter(c => parse(localAns[c.key]).some(v => ovfjLetterOk(v, letter))).length;""",
    'WritingForm fejlec')

sub("""          const v = localAns[cat.key]||'';
          const filled = v.trim().length > 0;
          const wrong = filled && !ovfjLetterOk(v, letter);
          const ok = filled && !wrong;""",
    """          const v = localAns[cat.key]||'';
          const words = parse(v);
          const kept = lim ? words.slice(0, lim) : words;
          const goodCount = kept.filter(w => ovfjLetterOk(w, letter)).length;
          const filled = words.length > 0;
          // Több szónál csak akkor pirosodik a mező, ha EGYIK sem használható —
          // különben az első hibás szó az egész sort hibásnak mutatná.
          const wrong = filled && goodCount === 0;
          const ok = goodCount > 0;""",
    'WritingForm sor-allapot')

sub("""                <div style={{fontFamily:T.font,fontWeight:T.weightTitle,fontSize:11.5,color:T.inkSoft,lineHeight:1.1,marginBottom:1}}>{cat.label}</div>""",
    """                <div style={{fontFamily:T.font,fontWeight:T.weightTitle,fontSize:11.5,color:T.inkSoft,lineHeight:1.1,marginBottom:1,display:'flex',alignItems:'center',gap:5}}>
                  <span>{cat.label}</span>
                  {lim !== 1 && <span style={{fontWeight:T.weightTitle,color:goodCount?T.mint:T.inkMute}}>{goodCount}/{lim || '∞'}</span>}
                </div>""",
    'WritingForm cimke')

sub("""                  placeholder={`${letter}...`}
                  style={{width:'100%',boxSizing:'border-box',padding:'1px 0',border:'none',borderBottom:`2px ${active||filled?'solid':'dashed'} ${wrong?T.coral:active||filled?T.mint:T.inkMute+'66'}`,fontFamily:T.font,fontSize:15,fontWeight:T.weightTitle,background:'transparent',color:wrong?T.coral:T.ink,outline:'none',textDecoration:wrong?'line-through':'none'}}
                />""",
    """                  placeholder={lim === 1 ? `${letter}...` : `${letter}..., ${letter}...`}
                  style={{width:'100%',boxSizing:'border-box',padding:'1px 0',border:'none',borderBottom:`2px ${active||filled?'solid':'dashed'} ${wrong?T.coral:active||filled?T.mint:T.inkMute+'66'}`,fontFamily:T.font,fontSize:15,fontWeight:T.weightTitle,background:'transparent',color:wrong?T.coral:T.ink,outline:'none',textDecoration:(lim===1&&wrong)?'line-through':'none'}}
                />
                {/* Amit felismertünk. Enélkül nem derülne ki menet közben, hogy
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
    'WritingForm input')

# ══════════════ 4) Host: állapot, szinkron, pontozás ══════════════
sub("""  const [showQR, setShowQR] = React.useState(false);
  const [, setTick] = React.useState(0);
  const calcRef = React.useRef(false);""",
    """  const [showQR, setShowQR] = React.useState(false);
  const [answerLimit, setAnswerLimit] = React.useState(() => ovfjLimit(gameMeta?.ovfjConfig?.answerLimit));
  const [, setTick] = React.useState(0);
  const calcRef = React.useRef(false);""",
    'host allapot')

sub("""    syncRoom(roomCode, { ovfjTakenIds: [], ovfjState: { sess, phase:'pick', round:1, totalRounds, roundTime, waitFullTime, letter:null, drawTs:null, doneAt:null, hostPid:null } });""",
    """    syncRoom(roomCode, { ovfjTakenIds: [], ovfjState: { sess, phase:'pick', round:1, totalRounds, roundTime, waitFullTime, answerLimit, letter:null, drawTs:null, doneAt:null, hostPid:null } });""",
    'host reset sync')

sub("""    syncRoom(roomCode, { ovfjState: { sess, phase, round, totalRounds, roundTime, waitFullTime, letter, drawTs, doneAt, hostPid, answers, roundScores, cumScores } });
  }, [phase, round, letter, drawTs, doneAt, hostPid, answers, roundScores, cumScores]);""",
    """    syncRoom(roomCode, { ovfjState: { sess, phase, round, totalRounds, roundTime, waitFullTime, answerLimit, letter, drawTs, doneAt, hostPid, answers, roundScores, cumScores } });
  }, [phase, round, letter, drawTs, doneAt, hostPid, answers, roundScores, cumScores, answerLimit]);""",
    'host allapot sync')

sub("""    const validity = ovfjBuildValidity(answers, letter, round);
    const rs = {};
    pl.forEach(p => { rs[p.id] = 0; });
    pl.filter(p => answers[p.id] && answers[p.id].round === round).forEach(p => {
      OVFJ_CATS.forEach(c => {
        const vi = validity(p.id, c.key);
        if (!vi.valid) return;
        const vm = votes[ovfjVoteKey(round, p.id, c.key)] || {};
        const vals = Object.values(vm);
        const yes = vals.filter(Boolean).length, no = vals.length - yes;
        if (yes > no) rs[p.id] += 1;
      });
    });""",
    """    const validity = ovfjBuildValidity(answers, letter, round, answerLimit);
    const rs = {};
    pl.forEach(p => { rs[p.id] = 0; });
    pl.filter(p => answers[p.id] && answers[p.id].round === round).forEach(p => {
      OVFJ_CATS.forEach(c => {
        validity(p.id, c.key).forEach((vi, ai) => {
          if (!vi.valid) return;
          const vm = votes[ovfjVoteKey(round, p.id, c.key, ai)] || {};
          const vals = Object.values(vm);
          const yes = vals.filter(Boolean).length, no = vals.length - yes;
          // Amire SENKI nem szavazott, az elfogadott. Több szónál senki nem tud
          // minden sorra rábökni, és a hallgatás nem elutasítás. Ahol viszont
          // szavaztak, ott a régi szabály él.
          if (vals.length === 0 || yes > no) rs[p.id] += 1;
        });
      });
    });""",
    'pontszamitas')

sub("""      const drinkParts = pl.filter(p => claimedPids.has(p.id))
        .map(p => ({ p, drinks: maxRs - (rs[p.id]||0) }))""",
    """      // Kortyplafon: egy körben legfeljebb annyi, ahány kategória van — ez volt
      // eddig is az elméleti maximum. Enélkül "bármennyi" mellett egy jó és egy
      // gyenge kör között húsz korty is lehetne a különbség.
      const CAP = OVFJ_CATS.length;
      const drinkParts = pl.filter(p => claimedPids.has(p.id))
        .map(p => ({ p, drinks: Math.min(CAP, maxRs - (rs[p.id]||0)) }))""",
    'korty plafon')

sub("""    const validity = ovfjBuildValidity(answers, letter, round);
    const items = [];
    participants.forEach(p => OVFJ_CATS.forEach(c => { if (validity(p.id, c.key).valid) items.push([p.id, c.key]); }));
    if (items.length === 0) return;
    const all = items.every(([pid, ck]) => {
      const vm = votes[ovfjVoteKey(round, pid, ck)] || {};""",
    """    const validity = ovfjBuildValidity(answers, letter, round, answerLimit);
    const items = [];
    participants.forEach(p => OVFJ_CATS.forEach(c => {
      validity(p.id, c.key).forEach((vi, ai) => { if (vi.valid) items.push([p.id, c.key, ai]); });
    }));
    if (items.length === 0) return;
    const all = items.every(([pid, ck, ai]) => {
      const vm = votes[ovfjVoteKey(round, pid, ck, ai)] || {};""",
    'auto-tovabblepes')

# ══════════════ 5) Host nézetek ══════════════
sub("""      <PrimaryButton onClick={startRound}>Kezdés ({pl.filter(p => claimedPids.has(p.id) || p.id === hostPid).length}/{pl.length})</PrimaryButton>""",
    """      <OVFJLimitPicker value={answerLimit} onChange={setAnswerLimit} />
      <PrimaryButton onClick={startRound}>Kezdés ({pl.filter(p => claimedPids.has(p.id) || p.id === hostPid).length}/{pl.length})</PrimaryButton>""",
    'lobby valaszto')

sub("""        onSubmit={hostSubmit}
        doneInfo={`${doneCount}/${expected.length} játékos kész`}""",
    """        onSubmit={hostSubmit}
        limit={answerLimit}
        doneInfo={`${doneCount}/${expected.length} játékos kész`}""",
    'host iras')

sub("""      <OVFJVotingView letter={letter} round={round} players={pl} answers={answers} myPid={hostPid} myVotes={myVotes} onVote={hostVote} tallies={tallies} />""",
    """      <OVFJVotingView letter={letter} round={round} players={pl} answers={answers} myPid={hostPid} myVotes={myVotes} onVote={hostVote} tallies={tallies} limit={answerLimit} />""",
    'host szavazas')

# ══════════════ 6) Vendég nézet ══════════════
sub("""        onSubmit={() => submitAnswers(true)}
        doneInfo={null}""",
    """        onSubmit={() => submitAnswers(true)}
        limit={ovfj.answerLimit}
        doneInfo={null}""",
    'vendeg iras')

sub("""      <OVFJVotingView letter={letter} round={ovfj.round} players={players} answers={answers} myPid={myPid} myVotes={myVotes} onVote={submitVote} tallies={null} />""",
    """      <OVFJVotingView letter={letter} round={ovfj.round} players={players} answers={answers} myPid={myPid} myVotes={myVotes} onVote={submitVote} tallies={null} limit={ovfj.answerLimit} />""",
    'vendeg szavazas')

# ══════════════ verziobump ══════════════
sub("const APP_VERSION = 'v10.183';", "const APP_VERSION = 'v10.184';", 'verzio')

open(P, 'w', encoding='utf-8').write(src)
print('OK — tobb valasz kategoriankent, 1/2/3/barmennyi valaszto a kor elott')
