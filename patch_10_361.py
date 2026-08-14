# v10.361 - Csendes arveres: nincs licit-plafon, es a KOZOS felepitmeny
#
# Harom bejelentes, egy csomagban:
#
# 1. ⚠️ NINCS PLAFON a liciten. Az `ARVERES_MAX_BID = 6` megszunt — a licit addig
#    megy, ameddig vallaljak. Ebbol KOVETKEZIK a fejlec-korong valtozasa:
#    `stake:[0,6]` -> `stake:null`. Egy felso hatar nelkuli ertekre nincs igaz
#    tartomany, amit a korong kiirhatna; a `stake:null` a dokumentalt megoldas
#    a „hatartalan halmozokra" (v10.276), ilyenkor a korong a KORSZAMLALO.
#    Aki visszahozna a tartomanyt, elobb a plafont hozza vissza.
#
# 2. A FEKETE gomb kikerult. Az app sehol nem hasznal tomor sotet gombot —
#    az elsodleges akcio mindenhol a `PrimaryButton` (menta gradiens). Ket
#    helyen allt: „Én vagyok <név>" es a „Licitálás indul".
#
# 3. A nev-CHIPSOR helyett a Loverseny JATEKOS-JELZO SORA. A hat pirula nem
#    mondta meg, hanyadiknal tartunk, es sok jatekosnal ket sorba tort. A
#    Loverseny-fele sor ugyanazt az informaciot viszi, de olvashatoan:
#    avatar + nev + halado pottyok + „N/M".
#    Ugyaninnen jon a LEPTETO alakja is: 52x52-es −/+ es kozottuk a szeles,
#    szinkodolt tet-kartya (zold/sarga/piros).
#
# ⚠️ A HAROM TET-SZIN EGY FORRASBOL jon (`STAKE_TONE_BG`), es a Loverseny is
# atall ra. Ket kezzel irt masolat pontosan az a fajta elcsuszas, amibol a
# korty-sornal negy valtozat lett (v10.291). A Loverseny HIVASA valtozatlan
# (nyers `amount`), tehat ott a rendereles bitre ugyanaz marad.
#
# ⚠️ A ket jatek SZANDEKOSAN mas szamot ad a kartyanak:
#   • Loverseny: NYERS tet (1-6) — a szorzot a lepteto alatti mondat irja ki
#     („6 kortyot (2 × 3)"), ez a v10.299-ben rogzitett dontes;
#   • Arveres:   MAR SZORZOTT szam — itt nincs ilyen mondat, es a felfedesen a
#     `PlayerDrinkRow` is szorzottan mutat. Nyersen hagyva a ket kepernyo
#     mast mondana ugyanarrol a licitrol.
import io

P = 'app.src.html'
src = io.open(P, encoding='utf-8').read()
orig = src

def sub1(old, new, what):
    global src
    assert src.count(old) == 1, '%s: %d talalat' % (what, src.count(old))
    src = src.replace(old, new)

# ── 1. A KOZOS tet-szin ─────────────────────────────────────────────────────
# A `GAMES` tomb ELE nem kell; eleg a ket hasznalati hely ele. Az `ArveresGame`
# jon elobb (~51460), a Loverseny kesobb (~53660).
sub1(
"""const ARVERES_MAX_BID = 6;""",
"""// A tet-kartya harom fokozata. A szinek FIXEK, nem temafuggok: a „zold = keves,
// piros = sok" jelentes nem lehet kek — ugyanaz a szabaly, mint a `BOH_TIMER_TONES`-nal
// es a Szures nehezseg-kartyainal.
//
// ⚠️ EGY FORRAS: a Loverseny tet-kartyaja ES a Csendes arveres leptetoje is ezt
// hivja. Ket kezzel irt masolatbol pontosan az lett a korty-sornal, hogy negy
// valtozat elt egymas mellett, es elcsusztak (v10.291).
//
// A KET HIVAS SZANDEKOSAN MAS SZAMOT ad at: a Loverseny a NYERS tetet (a szorzot
// a lepteto alatti mondat irja ki — v10.299), az arveres a MAR SZORZOTT szamot
// (ott nincs ilyen mondat, es a felfedes `PlayerDrinkRow`-ja is szorzottan mutat).
const STAKE_TONE_BG = (n) => n <= 2 ? '#C9E8D2' : n <= 4 ? '#F5E0AC' : '#F2C4C4';
const STAKE_TONE_INK = '#1A2A4A';""",
'STAKE_TONE_BG bevezetese (es a plafon torlese)')

# A Loverseny atall a kozos forrasra — a HIVAS nyers `amount` marad, tehat a
# rendereles valtozatlan.
sub1(
"""background: amount <= 2 ? '#C9E8D2' : amount <= 4 ? '#F5E0AC' : '#F2C4C4', boxShadow:'0 3px 12px rgba(20,30,50,0.14)'""",
"""background: STAKE_TONE_BG(amount), boxShadow:'0 3px 12px rgba(20,30,50,0.14)'""",
'Loverseny tet-kartya hattere')

sub1(
"""fontSize:28, color: amount <= 2 ? '#1A2A4A' : amount <= 4 ? '#1A2A4A' : '#1A2A4A' }}>{amount}</div>""",
"""fontSize:28, color: STAKE_TONE_INK }}>{amount}</div>""",
'Loverseny tet-kartya tintaja')

# ── 2. GAMES: nincs plafon, tehat nincs tartomany a korongon ────────────────
sub1(
"""  { id:'arveres', stake:[0,6], roundTime:'mid',""",
"""  { id:'arveres', stake:null, roundTime:'mid',""",
'GAMES stake -> null')

sub1(
"""Mindenki TITOKBAN licitál 0–6 kortyot: a telefon körbemegy, és senki nem látja a többiek számát.""",
"""Mindenki TITOKBAN licitál: a telefon körbemegy, és senki nem látja a többiek számát. Felső határ nincs — addig mehet a licit, ameddig vállaljátok.""",
'GAMES leiras')

# ── 3. INTRO: PrimaryButton, es a szoveg sem igerhet plafont ────────────────
sub1(
"""        A telefon körbemegy. Mindenki <strong style={{ color:T.ink }}>titokban</strong> licitál
        0–{ARVERES_MAX_BID * drinkMult} kortyot. A legtöbbet ígérő nyeri a nyereményt — és annyit iszik.
      </div>
      <button onClick={() => { setPhase('bid'); setIdx(0); setOpen(false); setBid(0); }}
        style={bigBtn(T.mint)}>Licitálás indul</button>""",
"""        A telefon körbemegy. Mindenki <strong style={{ color:T.ink }}>titokban</strong> licitál —
        <strong style={{ color:T.ink }}> felső határ nincs</strong>. A legtöbbet ígérő nyeri a
        nyereményt, és annyit is iszik.
      </div>
      <PrimaryButton onClick={() => { setPhase('bid'); setIdx(0); setOpen(false); setBid(0); }}>
        Licitálás indul
      </PrimaryButton>""",
'intro gomb + szoveg')

# ── 4. A BID FAZIS: jelzo-sor, Loverseny-lepteto, PrimaryButton, nincs plafon ─
sub1(
"""  if (phase === 'bid') {
    const cur = pl[idx];
    const step = (d) => setBid(v => Math.max(0, Math.min(ARVERES_MAX_BID, v + d)));
    const done = () => {
      const all = { ...bids, [cur.id]: bid };
      setBids(all);
      if (idx < pl.length - 1) { setIdx(idx + 1); setOpen(false); setBid(0); }
      else { setPhase('reveal'); settle(all); }
    };
    return (
      <div style={wrap}>
        <ArveresDijCard dij={dij} compact />
        <div style={{ width:'100%', background:T.surface, borderRadius:20, padding:'18px 18px 20px',
                      boxShadow:T.shadow, boxSizing:'border-box', textAlign:'center' }}>
          {!open ? (
            <React.Fragment>
              <div style={{ fontFamily:T.font, fontSize:12.5, fontWeight:700, color:T.inkSoft }}>Add át a telefont</div>
              <div style={{ display:'flex', flexDirection:'column', alignItems:'center', gap:8, margin:'14px 0 16px' }}>
                <PlayerAvatar player={cur} size={64} />
                <div style={{ fontFamily:T.font, fontWeight:T.weightDisplay, fontSize:22, color:T.ink }}>{cur?.name}</div>
              </div>
              <button onClick={() => { setOpen(true); setBid(0); }} style={bigBtn(T.ink)}>
                Én vagyok {cur?.name}
              </button>
            </React.Fragment>
          ) : (
            <React.Fragment>
              <div style={{ fontFamily:T.font, fontSize:12.5, fontWeight:700, color:T.inkSoft }}>
                Mennyit ígérsz, <strong style={{ color:T.ink }}>{cur?.name}</strong>?
              </div>
              <div style={{ display:'flex', alignItems:'center', justifyContent:'center', gap:16, margin:'14px 0 10px' }}>
                <button onClick={() => step(-1)} disabled={bid <= 0} aria-label="Egy korttyal kevesebb"
                  style={{ width:48, height:48, borderRadius:'50%', border:'none', background:T.coralSoft,
                           cursor: bid > 0 ? 'pointer' : 'default', opacity: bid > 0 ? 1 : 0.4,
                           display:'grid', placeItems:'center' }}>
                  <BohIcon name="minus" size={22} />
                </button>
                <div style={{ minWidth:92, textAlign:'center' }}>
                  <div style={{ fontFamily:T.font, fontWeight:T.weightDisplay, fontSize:44, color:T.ink, lineHeight:1 }}>{bid * drinkMult}</div>
                  <div style={{ fontFamily:T.font, fontSize:11, fontWeight:700, color:T.inkMute,
                                textTransform:'uppercase', letterSpacing:'0.1em' }}>korty</div>
                </div>
                <button onClick={() => step(1)} disabled={bid >= ARVERES_MAX_BID} aria-label="Egy korttyal több"
                  style={{ width:48, height:48, borderRadius:'50%', border:'none', background:T.mintSoft,
                           cursor: bid < ARVERES_MAX_BID ? 'pointer' : 'default', opacity: bid < ARVERES_MAX_BID ? 1 : 0.4,
                           display:'grid', placeItems:'center' }}>
                  <BohIcon name="plus" size={22} />
                </button>
              </div>
              <div style={{ fontFamily:T.font, fontSize:12, color:T.inkSoft, marginBottom:14 }}>
                Senki ne lássa — utána add tovább a telefont.
              </div>
              <button onClick={done} style={bigBtn(T.mint)}>
                {idx < pl.length - 1 ? 'Kész, jöhet a következő' : 'Kész — felfedés'}
              </button>
            </React.Fragment>
          )}
        </div>
        {/* Haladas: ki adta be mar a licitet. A SZAM sehol nem latszik. */}
        <div style={{ display:'flex', gap:6, flexWrap:'wrap', justifyContent:'center' }}>
          {pl.map((p, i) => (
            <span key={p.id} style={{ padding:'4px 10px', borderRadius:999, fontFamily:T.font, fontSize:11, fontWeight:700,
                                      background: i < idx ? T.mintSoft : i === idx ? T.surfaceMuted : 'transparent',
                                      border: i === idx ? '1.5px solid ' + T.ink + '22' : '1.5px solid transparent',
                                      color: i < idx ? T.mint : T.inkSoft }}>{p.name}</span>
          ))}
        </div>
      </div>
    );""",
"""  if (phase === 'bid') {
    const cur = pl[idx];
    if (!cur) return null;
    // ⚠️ NINCS FELSO HATAR (v10.361) — csak a nulla alja fog. Ha valaha
    // visszajonne a plafon, a `GAMES[].stake`-et is vissza kell allitani
    // tartomanyra, kulonben a fejlec-korong mast igerne, mint a lepteto.
    const step = (d) => setBid(v => Math.max(0, v + d));
    const isLast = idx === pl.length - 1;
    const shownBid = bid * drinkMult;
    const done = () => {
      const all = { ...bids, [cur.id]: bid };
      setBids(all);
      if (!isLast) { setIdx(idx + 1); setOpen(false); setBid(0); }
      else { setPhase('reveal'); settle(all); }
    };
    return (
      <div style={wrap}>
        <ArveresDijCard dij={dij} compact />
        {/* ⚠️ A JATEKOS-JELZO SOR a Loversenybol (v10.361) — avatar + nev +
            halado pottyok + „N/M". A regi nev-chipsor helyett: az nem mondta
            meg, hanyadiknal tartunk, es sok jatekosnal ket sorba tort.
            A pottyok SZAMOT nem arulnak el, csak azt, ki adta mar be. */}
        <div style={{ width:'100%', display:'flex', alignItems:'center', gap:10, background:T.surface,
                      borderRadius:14, padding:'10px 14px', boxShadow:T.shadow, boxSizing:'border-box' }}>
          <PlayerAvatar player={cur} size={36} />
          <div style={{ flex:1, minWidth:0, fontFamily:T.font, fontWeight:T.weightTitle, fontSize:15,
                        color:T.ink, overflow:'hidden', textOverflow:'ellipsis', whiteSpace:'nowrap' }}>{cur.name} licitje</div>
          <div style={{ display:'flex', alignItems:'center', gap:4, flexShrink:0 }}>
            {pl.map((_, i) => <div key={i} style={{ width:8, height:8, borderRadius:'50%',
              background: i < idx ? T.mint : i === idx ? cur.color : T.inkMute+'40' }} />)}
            <div style={{ fontFamily:T.font, fontSize:11, color:T.inkSoft, marginLeft:4 }}>{idx+1}/{pl.length}</div>
          </div>
        </div>
        {!open ? (
          <React.Fragment>
            <div style={{ width:'100%', background:T.surface, borderRadius:20, padding:'18px 18px 22px',
                          boxShadow:T.shadow, boxSizing:'border-box', textAlign:'center' }}>
              <div style={{ fontFamily:T.font, fontSize:12.5, fontWeight:700, color:T.inkSoft }}>Add át a telefont</div>
              <div style={{ display:'flex', flexDirection:'column', alignItems:'center', gap:8, marginTop:14 }}>
                <PlayerAvatar player={cur} size={64} />
                <div style={{ fontFamily:T.font, fontWeight:T.weightDisplay, fontSize:22, color:T.ink }}>{cur.name}</div>
              </div>
            </div>
            <PrimaryButton onClick={() => { setOpen(true); setBid(0); }}>Én vagyok {cur.name}</PrimaryButton>
          </React.Fragment>
        ) : (
          <React.Fragment>
            <div style={{ width:'100%', background:T.surface, borderRadius:20, padding:'18px 18px 20px',
                          boxShadow:T.shadow, boxSizing:'border-box' }}>
              <div style={{ fontFamily:T.font, fontSize:12, fontWeight:700, color:T.inkSoft,
                            textTransform:'uppercase', letterSpacing:'0.1em', marginBottom:10 }}>Hány korty a licited?</div>
              {/* A LEPTETO alakja a Loversenybol: 52x52-es −/+ es kozottuk a
                  szeles, szinkodolt tet-kartya. A `+` SOHA nem tiltott — nincs
                  plafon; a `−` a nullanal all meg. */}
              <div style={{ display:'flex', alignItems:'center', gap:8 }}>
                <button onClick={() => step(-1)} disabled={bid <= 0} aria-label="Egy korttyal kevesebb"
                  style={{ width:52, height:52, border:'none', background:T.surfaceMuted, borderRadius:12,
                           cursor: bid > 0 ? 'pointer' : 'default', display:'grid', placeItems:'center',
                           opacity: bid > 0 ? 1 : 0.6 }}>
                  <BohIcon name="minus" size={22} />
                </button>
                <div style={{ flex:1, borderRadius:20, padding:'12px 16px', background: STAKE_TONE_BG(shownBid),
                              boxShadow:'0 3px 12px rgba(20,30,50,0.14)', display:'flex', alignItems:'center',
                              justifyContent:'center', gap:8 }}>
                  <div style={{ fontFamily:T.font, fontWeight:T.weightDisplay, fontSize:28,
                                color:STAKE_TONE_INK, fontVariantNumeric:'tabular-nums' }}>{shownBid}</div>
                  <BohIcon name="beer" size={20} />
                </div>
                <button onClick={() => step(1)} aria-label="Egy korttyal több"
                  style={{ width:52, height:52, border:'none', background:T.mintSoft, borderRadius:12,
                           cursor:'pointer', display:'grid', placeItems:'center' }}>
                  <BohIcon name="plus" size={22} />
                </button>
              </div>
              <div style={{ fontFamily:T.font, fontSize:12, color:T.inkSoft, textAlign:'center', marginTop:12 }}>
                Senki ne lássa — utána add tovább a telefont.
              </div>
            </div>
            <PrimaryButton onClick={done}>{isLast ? 'Kész — felfedés' : 'Következő →'}</PrimaryButton>
          </React.Fragment>
        )}
      </div>
    );""",
'bid fazis atirasa')

# A `bigBtn` helper igy hivo nelkul maradt — kivezetjuk (v10.340 mintajara:
# halott kod nem marad bent).
sub1(
"""  const bigBtn = (bg) => ({ width:'100%', minHeight:60, borderRadius:16, border:'none', background:bg,
                            color:'#fff', fontFamily:T.font, fontWeight:T.weightTitle, fontSize:16,
                            cursor:'pointer', boxShadow:T.shadow });

""",
"""""",
'bigBtn kivezetese')

sub1("const APP_VERSION = 'v10.360';", "const APP_VERSION = 'v10.361';", 'verzio')

assert 'ARVERES_MAX_BID' not in src, 'maradt ARVERES_MAX_BID hivatkozas'
assert 'bigBtn' not in src, 'maradt bigBtn hivatkozas'
assert src != orig
io.open(P, 'w', encoding='utf-8').write(src)
print('OK - patch_10_361 alkalmazva')
