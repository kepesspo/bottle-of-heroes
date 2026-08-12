# v10.334 — Idoparbaj: sajat telefonrol is jatszhato
#
# A PROBLEMA: ha a host egy laptop, a jatekot senki nem tudja jatszani — a
# stoppert a host kepernyojen kellett inditani/megallitani.
#
# ⚠️ A DONTO KULONBSEG a Tapperhez kepest: ott a telefon csak a NYOMVA-TARTAS
# tenyet kuldi, es a hoston fut az ora. Itt a MERT IDO maga a jatek, 0,1 mp
# felbontassal — egy 100–300 ms-os halozati korido inditasnal ES megallitasnal
# is torzitana, vagyis a jatek merhetetlen lenne. Ezert a stopper a TELEFONON
# fut helyben, es csak a KESZ EREDMENY megy fel a szobaba.
#
# Ugyanezert a telefon a sajat HELYI allapotabol rajzol (`localRun`), nem a
# szoba fazisabol: kulonben az „Indit" utan a „Stop" gomb csak a pillanatkep
# visszaeresekor jelenne meg, es a jatekos nem tudna idoben megallitani.
# (Ugyanaz a lecke, mint a Blackjack optimista visszhangjanal — v10.331.)
import io

P = 'app.src.html'
src = io.open(P, encoding='utf-8').read()
orig = src

def sub1(old, new, what):
    global src
    assert src.count(old) == 1, f'{what}: {src.count(old)} talalat'
    src = src.replace(old, new)

# ── 1. a CEL-LAP kozos komponensbe (host + telefon ugyanazt rajzolja) ─────────
TARGET_JSX = """      <div style={{ position:'relative', background:T.mint, borderRadius:20, padding:'20px 24px 18px', width:'100%', textAlign:'center', boxSizing:'border-box', overflow:'hidden', boxShadow:T.shadow }}>
        <svg viewBox="0 0 200 120" preserveAspectRatio="none" style={{ position:'absolute', inset:0, width:'100%', height:'100%', pointerEvents:'none', opacity:0.16 }}>
          <circle cx="100" cy="60" r="34" fill="none" stroke="#fff" strokeWidth="1.4"/>
          <circle cx="100" cy="60" r="52" fill="none" stroke="#fff" strokeWidth="1.4"/>
          <circle cx="100" cy="60" r="70" fill="none" stroke="#fff" strokeWidth="1.4"/>
        </svg>
        <div style={{ position:'relative' }}>
          <div style={{ display:'grid', placeItems:'center', marginBottom:2 }}>
            <svg width="22" height="22" viewBox="0 0 24 24" fill="none">
              <circle cx="12" cy="12" r="8.5" stroke="rgba(255,255,255,0.75)" strokeWidth="1.8"/>
              <circle cx="12" cy="12" r="3.6" stroke="rgba(255,255,255,0.75)" strokeWidth="1.8"/>
              <path d="M12 1.8v3.2M12 19v3.2M1.8 12h3.2M19 12h3.2" stroke="rgba(255,255,255,0.75)" strokeWidth="1.8" strokeLinecap="round"/>
            </svg>
          </div>
          <div style={{ fontFamily:T.font, fontSize:10, fontWeight:700, color:'rgba(255,255,255,0.62)', textTransform:'uppercase', letterSpacing:'0.12em', marginBottom:6 }}>CÉL IDŐ</div>
          <div style={{ fontFamily:'monospace', fontWeight:900, fontSize:52, color:'#fff', lineHeight:1 }}>{tgt.toFixed(1)}<span style={{ fontFamily:T.font, fontSize:22, fontWeight:700, marginLeft:4, color:'rgba(255,255,255,0.75)' }}>mp</span></div>
          <div style={{ display:'flex', justifyContent:'center', marginTop:12 }}>
            <div style={{ padding:'6px 16px', borderRadius:999, background:'rgba(255,255,255,0.18)', fontFamily:T.font, fontWeight:700, fontSize:13, color:'#fff' }}>Minél közelebb, annál jobb!</div>
          </div>
        </div>
      </div>"""

# a jatekbol kiszedjuk, es a modul-szintu komponensre csereljuk
OLD_BLOCK = """      {/* Cel ido. A lap MENTA (T.mint), nem T.ink: a fekete tabla ugy nezett
          ki, mint egy hibauzenet-sav, holott ez a jatek celja. A halvany
          koncentrikus korok es a celtabla-ikon mondjak meg, mire celzunk. */}
""" + TARGET_JSX + "\n"
sub1(OLD_BLOCK, "      <IdoparbajTargetCard tgt={tgt} />\n", 'cel-lap kiemelese')

# a komponens az IdoparbajBigBtn ELE kerul (modul-szint, nem torzs — lasd a
# lenti figyelmeztetest az ujramountolasrol)
TARGET_COMP = """// A CEL-LAP: a host tablaja ES a telefon UGYANEZT rajzolja. Ket masolat
// elcsuszna egymastol — ugyanaz a szabaly, ami a korty-sornal negy valtozatot
// szult (lasd CLAUDE.md „Ki igyon?").
// A lap MENTA (T.mint), nem T.ink: a fekete tabla ugy nezett ki, mint egy
// hibauzenet-sav, holott ez a jatek celja.
function IdoparbajTargetCard({ tgt }) {
  return (
""" + TARGET_JSX.replace('\n      ', '\n    ').replace('      <div style={{ position:\'relative\', background:T.mint', '    <div style={{ position:\'relative\', background:T.mint') + """
  );
}

"""
sub1("function IdoparbajBigBtn({ label, sub, onClick, color }) {",
     TARGET_COMP + "function IdoparbajBigBtn({ label, sub, onClick, color }) {",
     'IdoparbajTargetCard beszurasa')

# ── 2. a JATEK: szoba-szinkron + tavoli bemenet ──────────────────────────────
OLD_HEAD = """function IdoparbajGame({ gameIdx, challenger, opponent, onAdvance, onResult }) {
  const target = React.useRef(+(5 + Math.random() * 25).toFixed(1));
  const [phase, setPhase] = React.useState('idle'); // 'idle'|'p1running'|'p1done'|'p2running'|'result'
  const [t1, setT1] = React.useState(null);
  const [t2, setT2] = React.useState(null);
  const startRef = React.useRef(null);
  const advRef = React.useRef(false);

  React.useEffect(() => { target.current = +(5 + Math.random() * 25).toFixed(1); setPhase('idle'); setT1(null); setT2(null); advRef.current = false; }, [gameIdx]);

  const tgt = target.current;

  const startP1 = () => { startRef.current = Date.now(); setPhase('p1running'); };
  const stopP1  = () => { setT1(+((Date.now() - startRef.current) / 1000).toFixed(1)); setPhase('p1done'); };
  const startP2 = () => { startRef.current = Date.now(); setPhase('p2running'); };
  const stopP2  = () => {
    const tv = +((Date.now() - startRef.current) / 1000).toFixed(1);
    setT2(tv);
    setPhase('result');
    if (!advRef.current) {
      advRef.current = true;
      const d1 = Math.abs(t1 - tgt), d2 = Math.abs(tv - tgt);
      const p1wins = d1 <= d2;
      const loser = p1wins ? opponent : challenger;
      const winner = p1wins ? challenger : opponent;
      setTimeout(() => {
        onResult && onResult({ winners:[winner].filter(Boolean), losers:[loser].filter(Boolean), drinks:1, winNote:'+1 pont' });
        // a győztes pontja is menjen át, ne csak a vesztes kortya
        onAdvance && onAdvance(loser ? { [loser.id]: 1 } : {}, winner ? { [winner.id]: 1 } : {});
      }, 400);
    }
  };
"""

NEW_HEAD = """function IdoparbajGame({ gameIdx, challenger, opponent, onAdvance, onResult, roomCode }) {
  const target = React.useRef(+(5 + Math.random() * 25).toFixed(1));
  const [phase, setPhase] = React.useState('idle'); // 'idle'|'p1running'|'p1done'|'p2running'|'result'
  const [t1, setT1] = React.useState(null);
  const [t2, setT2] = React.useState(null);
  const startRef = React.useRef(null);
  const advRef = React.useRef(false);
  // A tavoli bemenet a LEGUTOLSO pillanatkepbol jon, tehat a fazist es az elso
  // idot REF-bol kell olvasni: a feliratkozas closure-je kulonben a mountoláskori
  // erteket latna, es a masodik jatekos ideje az elso melle szamolna.
  const phaseRef = React.useRef('idle');
  const t1Ref = React.useRef(null);
  // pid -> utoljara feldolgozott jelolo. Enelkul ugyanaz a bemenet a kovetkezo
  // pillanatkepnel ujra lefutna, sot a kor visszaertekor magatol elsulne
  // (ugyanaz a csapda, amit a Kisebb/Nagyobb `kisebbGuess.ts`-e old meg).
  const seenTokRef = React.useRef({});

  React.useEffect(() => {
    target.current = +(5 + Math.random() * 25).toFixed(1);
    setPhase('idle'); setT1(null); setT2(null);
    phaseRef.current = 'idle'; t1Ref.current = null;
    advRef.current = false; seenTokRef.current = {};
    // A regi bemenetet TOROLNI kell, kulonben az uj kor az elozo kor
    // megallitasaval indulna.
    if (roomCode && typeof syncRoom === 'function') syncRoom(roomCode, { idoInput: null });
  }, [gameIdx]);

  const tgt = target.current;

  // A PAROST es a FAZIST a host kuldi le — az a hiteles forras. (Az ellenfelet
  // a PlayScreen VELETLENSZERUEN sorsolja, tehat a telefon nem tudja kitalalni;
  // ugyanaz a hiba, ami a Tappert „csak a host kepernyon" mukodove tette.)
  React.useEffect(() => {
    if (!roomCode || typeof syncRoom !== 'function') return;
    syncRoom(roomCode, { idoState: {
      gameIdx, target: tgt, phase, t1, t2,
      p1: challenger ? { id:challenger.id, name:challenger.name } : null,
      p2: opponent   ? { id:opponent.id,   name:opponent.name   } : null,
    } });
  }, [roomCode, gameIdx, phase, t1, t2]);

  const commitT1 = (tv) => { t1Ref.current = tv; setT1(tv); phaseRef.current = 'p1done'; setPhase('p1done'); };
  const commitT2 = (tv) => {
    setT2(tv);
    phaseRef.current = 'result'; setPhase('result');
    if (!advRef.current) {
      advRef.current = true;
      const d1 = Math.abs(t1Ref.current - tgt), d2 = Math.abs(tv - tgt);
      const p1wins = d1 <= d2;
      const loser = p1wins ? opponent : challenger;
      const winner = p1wins ? challenger : opponent;
      setTimeout(() => {
        onResult && onResult({ winners:[winner].filter(Boolean), losers:[loser].filter(Boolean), drinks:1, winNote:'+1 pont' });
        // a győztes pontja is menjen át, ne csak a vesztes kortya
        onAdvance && onAdvance(loser ? { [loser.id]: 1 } : {}, winner ? { [winner.id]: 1 } : {});
      }, 400);
    }
  };

  // A telefonok bemenete. A KESZ IDO jon fel (`t`), nem inditas/megallitas
  // idobelyeg: a stopper a telefonon fut, tehat a halozati korido nem torzitja.
  React.useEffect(() => {
    if (!roomCode || typeof subscribeRoom !== 'function') return;
    const unsub = subscribeRoom(roomCode, data => {
      const inp = data && data.idoInput; if (!inp) return;
      [[challenger, 1], [opponent, 2]].forEach(([p, n]) => {
        const e = p && inp[p.id];
        if (!e || !e.tok || seenTokRef.current[p.id] === e.tok) return;
        seenTokRef.current[p.id] = e.tok;
        const ph = phaseRef.current;
        if (e.st === 'running') {
          if (n === 1 && ph === 'idle')   { phaseRef.current = 'p1running'; setPhase('p1running'); }
          if (n === 2 && ph === 'p1done') { phaseRef.current = 'p2running'; setPhase('p2running'); }
        } else if (e.st === 'done' && typeof e.t === 'number') {
          if (n === 1 && (ph === 'idle'   || ph === 'p1running')) commitT1(e.t);
          if (n === 2 && (ph === 'p1done' || ph === 'p2running')) commitT2(e.t);
        }
      });
    });
    return () => unsub && unsub();
  }, [roomCode, gameIdx, challenger, opponent]);

  const startP1 = () => { startRef.current = Date.now(); phaseRef.current = 'p1running'; setPhase('p1running'); };
  const stopP1  = () => commitT1(+((Date.now() - startRef.current) / 1000).toFixed(1));
  const startP2 = () => { startRef.current = Date.now(); phaseRef.current = 'p2running'; setPhase('p2running'); };
  const stopP2  = () => commitT2(+((Date.now() - startRef.current) / 1000).toFixed(1));
"""
sub1(OLD_HEAD, NEW_HEAD, 'IdoparbajGame fej')

# a host also savja mondja meg, hogy telefonrol is megy
sub1("""      {phase==='idle'     && <IdoparbajBigBtn label={`▶ ${challenger?.name} indul`} sub="Nyomd meg az időzítő indításához" onClick={startP1} color={T.mint} />}""",
     """      {phase==='idle'     && <IdoparbajBigBtn label={`▶ ${challenger?.name} indul`} sub={roomCode ? 'Innen vagy a saját telefonjáról' : 'Nyomd meg az időzítő indításához'} onClick={startP1} color={T.mint} />}""",
     'p1 gomb felirata')
sub1("""      {phase==='p1done'   && <IdoparbajBigBtn label={`▶ ${opponent?.name} indul`} sub="Nyomd meg az időzítő indításához" onClick={startP2} color={T.mint} />}""",
     """      {phase==='p1done'   && <IdoparbajBigBtn label={`▶ ${opponent?.name} indul`} sub={roomCode ? 'Innen vagy a saját telefonjáról' : 'Nyomd meg az időzítő indításához'} onClick={startP2} color={T.mint} />}""",
     'p2 gomb felirata')

# ── 3. GameContent: a roomCode lemegy a jatekhoz ─────────────────────────────
sub1("""  if (gameId === 'idopárbaj') return <IdoparbajGame key={gameIdx} gameIdx={gameIdx} challenger={challenger} opponent={opponent} onAdvance={onAdvance} onResult={onResult} />;""",
     """  if (gameId === 'idopárbaj') return <IdoparbajGame key={gameIdx} gameIdx={gameIdx} challenger={challenger} opponent={opponent} onAdvance={onAdvance} onResult={onResult} roomCode={roomCode} />;""",
     'GameContent roomCode')

# ── 4. a TELEFONOS nezet ─────────────────────────────────────────────────────
OBS = '''function IdoparbajObserverView({ code, room, observerName }) {
  const st = room.idoState || null;
  const gameIdx = st ? st.gameIdx : (room.gameIdx || 0);
  // A parost a HOST kuldi le; a teljes jatekos-objektumot (avatar, szin) a
  // szoba `players` tombjebol vesszuk hozza.
  const byId = (x) => (x && (room.players || []).find(p => p.id === x.id)) || x || null;
  const challenger = byId(st && st.p1);
  const opponent   = byId(st && st.p2);
  const pair = [challenger, opponent].filter(Boolean);

  const [selId, setSelId] = React.useState(() => (pair.find(p => p && p.name === observerName) || {}).id || null);
  const me = pair.find(p => p && p.id === selId) || null;
  const isP1 = !!(me && challenger && me.id === challenger.id);

  const phase = (st && st.phase) || 'idle';
  const tgt = st && typeof st.target === 'number' ? st.target : null;
  const t1 = st ? st.t1 : null, t2 = st ? st.t2 : null;
  const myTime = isP1 ? t1 : t2;

  // ⚠️ A gomb a HELYI allapotbol rajzol, nem a szoba fazisabol. Ha a szobara
  // varnank, az „Indit" utan a „Stop" csak a pillanatkep visszaeresekor
  // (100–300 ms) jelenne meg — pont a meres elejet vesztenenk el.
  const [localRun, setLocalRun] = React.useState(false);
  const startRef = React.useRef(null);
  React.useEffect(() => { setLocalRun(false); startRef.current = null; }, [gameIdx]);

  const myTurn = !!me && (isP1 ? (phase === 'idle' || phase === 'p1running')
                              : (phase === 'p1done' || phase === 'p2running'));

  const write = (payload) => {
    if (!me || typeof db === 'undefined') return;
    const tok = Date.now().toString(36) + Math.random().toString(36).slice(2, 6);
    db.collection('rooms').doc(code).update({ ['idoInput.' + me.id]: { ...payload, tok } }).catch(() => {});
  };
  const start = () => { if (localRun) return; startRef.current = Date.now(); setLocalRun(true); write({ st:'running' }); };
  const stop  = () => {
    if (!localRun || !startRef.current) return;
    // A MERT IDO megy fel, nem idobelyeg — a stopper vegig ezen a keszuleken
    // futott, tehat a halozat nem szol bele.
    const tv = +((Date.now() - startRef.current) / 1000).toFixed(1);
    setLocalRun(false);
    write({ st:'done', t: tv });
  };

  const d1 = (t1 !== null && t1 !== undefined && tgt !== null) ? Math.abs(t1 - tgt) : null;
  const d2 = (t2 !== null && t2 !== undefined && tgt !== null) ? Math.abs(t2 - tgt) : null;
  const p1wins = phase === 'result' ? (d1 <= d2) : null;

  return (
    <div style={{ flex:1, display:'flex', flexDirection:'column', alignItems:'center', gap:14, background:T.bg, padding:'18px 16px', overflow:'auto' }}>
      <div style={{ fontFamily:T.font, fontWeight:900, fontSize:13, color:T.inkMute, textTransform:'uppercase', letterSpacing:'0.1em' }}>⏱️ Időpárbaj · {code}</div>

      {!st ? (
        <div style={{ marginTop:40, fontFamily:T.font, fontSize:14, color:T.inkMute }}>Várakozás a játékra…</div>
      ) : !me ? (
        /* Ugyanaz az avataros valaszto, mint a Tapper/Kisebb observerén. */
        <div style={{ display:'flex', flexDirection:'column', alignItems:'center', gap:18, width:'100%', maxWidth:320, marginTop:24 }}>
          <div style={{ width:76, height:76, borderRadius:999, background:T.surface, display:'grid', placeItems:'center', boxShadow:T.shadowLift || T.shadow }}>
            <div style={{ transform:'scale(1.5)', display:'grid', placeItems:'center' }}>{Icon.users(T.mint)}</div>
          </div>
          <div style={{ textAlign:'center' }}>
            <div style={{ fontFamily:T.font, fontWeight:900, fontSize:21, color:T.ink, marginBottom:4 }}>Ki vagy?</div>
            <div style={{ fontFamily:T.font, fontSize:13.5, color:T.inkSoft }}>Válaszd ki magad — a stoppert a saját telefonodon nyomod.</div>
          </div>
          <div style={{ display:'flex', flexDirection:'column', gap:8, width:'100%' }}>
            {pair.map(p => (
              <button key={p.id} onClick={() => setSelId(p.id)}
                style={{ width:'100%', display:'flex', alignItems:'center', gap:12, padding:'10px 14px', borderRadius:16,
                         border:'none', background:T.surface, boxShadow:T.shadow, cursor:'pointer', textAlign:'left', touchAction:'manipulation' }}>
                <PlayerAvatar player={p} size={40} />
                <span style={{ flex:1, minWidth:0, fontFamily:T.font, fontWeight:800, fontSize:16, color:T.ink, overflow:'hidden', textOverflow:'ellipsis', whiteSpace:'nowrap' }}>{p.name}</span>
                <span style={{ fontFamily:T.font, fontWeight:900, fontSize:16, color:T.inkMute }}>›</span>
              </button>
            ))}
            {pair.length === 0 && (
              <div style={{ textAlign:'center', fontFamily:T.font, fontSize:13, color:T.inkMute }}>Várakozás a párosításra…</div>
            )}
          </div>
        </div>
      ) : (
        <React.Fragment>
          {tgt !== null && <IdoparbajTargetCard tgt={tgt} />}

          <div style={{ display:'flex', gap:10, width:'100%' }}>
            <IdoparbajPlayerCard p={challenger} time={t1 === undefined ? null : t1} diff={d1} tgt={tgt || 0}
              isWinner={phase==='result'&&p1wins===true} isLoser={phase==='result'&&p1wins===false}
              isUp={phase==='idle'||phase==='p1running'} />
            <IdoparbajPlayerCard p={opponent} time={t2 === undefined ? null : t2} diff={d2} tgt={tgt || 0}
              isWinner={phase==='result'&&p1wins===false} isLoser={phase==='result'&&p1wins===true}
              isUp={phase==='p1done'||phase==='p2running'} />
          </div>

          {localRun ? (
            <div style={{ width:'100%', display:'flex', flexDirection:'column', alignItems:'center', gap:12 }}>
              <div style={{ fontFamily:T.font, fontSize:14, color:T.inkSoft, fontWeight:600 }}>Mérés fut… állítsd meg időben!</div>
              <IdoparbajBigBtn label="⏹ Stop!" onClick={stop} color={T.coral} />
            </div>
          ) : (myTime !== null && myTime !== undefined) ? (
            <div style={{ fontFamily:T.font, fontSize:14, color:T.inkSoft, fontWeight:600, marginTop:8, textAlign:'center' }}>
              {phase === 'result' ? 'Kész — nézd az eredményt!' : 'Megvan az időd. Most a másik játékos jön.'}
            </div>
          ) : myTurn ? (
            <IdoparbajBigBtn label="▶ Indítás" sub="Te következel — nyomd meg, aztán állítsd meg" onClick={start} color={T.mint} />
          ) : (
            <div style={{ fontFamily:T.font, fontSize:14, color:T.inkSoft, fontWeight:600, marginTop:8, textAlign:'center' }}>
              {(isP1 ? opponent : challenger)?.name || 'A másik játékos'} következik — várj a sorodra.
            </div>
          )}

          <button onClick={() => setSelId(null)} style={{ marginTop:4, padding:'8px 20px', borderRadius:12, border:'none', background:'rgba(20,30,50,0.08)', fontFamily:T.font, fontWeight:700, fontSize:13, color:T.inkSoft, cursor:'pointer' }}>Mégsem</button>
        </React.Fragment>
      )}
    </div>
  );
}

'''
sub1("function TapperObserverView({ code, room, observerName }) {",
     OBS + "function TapperObserverView({ code, room, observerName }) {",
     'IdoparbajObserverView beszurasa')

# ── 5. az observer-valto ─────────────────────────────────────────────────────
sub1("""  if (_ovCurG === 'tapper') return <TapperObserverView code={code} room={room} observerName={observerName} />;""",
     """  if (_ovCurG === 'tapper') return <TapperObserverView code={code} room={room} observerName={observerName} />;
  if (_ovCurG === 'idopárbaj') return <IdoparbajObserverView code={code} room={room} observerName={observerName} />;""",
     'observer valto')

# ── 6. verziobump ────────────────────────────────────────────────────────────
sub1("const APP_VERSION = 'v10.333';", "const APP_VERSION = 'v10.334';", 'verzio')

assert src != orig
io.open(P, 'w', encoding='utf-8').write(src)
print('OK — patch_10_334 alkalmazva')
