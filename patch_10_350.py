# v10.350 - 5 dolog: nyilt licit, latszo kategoria, savos ora, nincs kezi gomb
#
# Negy valtozas, es a masodik megforditja a jatek egyik korabbi szabalyat.
#
# 1. A LICITNEK NINCS FELSO HATARA. Az `OTDOLOG_MAX_BID = 8` megszunt — a licit
#    addig mehet, ameddig akarjak. Ebbol kovetkezik, hogy a jelolo-sor nem
#    lehet tobbe egyetlen `flex` sor: 12 szonal a csempek 20 px szelesek
#    lennenek. Racsba kerul, soronkent legfeljebb HAT jelolovel.
#
# 2. ⚠️ A KATEGORIA MAR A LICIT ALATT LATSZIK. A v10.339 szandekosan satirozta
#    („a licit VAK dontes"), de a tulajdonos dontese az ellenkezo: kategoria
#    nelkul nem lehet ertelmesen licitalni. A satirozott sav es a „Felfed"
#    szohasznalat ezzel egyutt megszunik — a gomb mar csak INDIT.
#
# 3. A licit-lap „<Nev> LICITAL" sora kikerult.
#
# 4. Az ora a KOZOS `BohTimer` `bar` valtozata (30 px, vizszintes) a 160 px-es
#    gyuru helyett. A gyuru 160 px-et vett el a jelolok es a lap elol — a
#    `BohTimer` epp erre keszult (v10.329).
#
# ⚠️ ES A KEZI GOMBOK. A jatek `Paros` (v10.339 ota), a `PlayScreen` pedig a
# Paros jatekokhoz kirakja a „Vesztettem / Nyertem!" gombokat, hacsak az
# azonosito nincs a kizaras-listan. Az `otdolog` az EGYENI listan volt rajta
# (a regi kategoriajabol), a Paroson nem — ezert jottek fel a gombok egy olyan
# jateknal, ami maga konyvel. Ket, egymasnak ellentmondo ut vezetett a ponthoz:
# az ora lejarta utan a jatek MAR eldontotte az eredmenyt.
import io

P = 'app.src.html'
src = io.open(P, encoding='utf-8').read()
orig = src

def sub1(old, new, what):
    global src
    assert src.count(old) == 1, '%s: %d talalat' % (what, src.count(old))
    src = src.replace(old, new)

# ── 1. Nincs felso hatar ────────────────────────────────────────────────────
sub1(
"""const OTDOLOG_MIN_BID = 3, OTDOLOG_MAX_BID = 8, OTDOLOG_DEF_BID = 5;""",
"""// ⚠️ NINCS felso hatar (v10.350): a licit addig mehet, ameddig vallaljak.
// A jelolo-sor ezert RACS, nem egyetlen `flex` sor — soronkent legfeljebb
// `OTDOLOG_COLS` jelolovel, kulonben 12 szonal 20 px szeles csempek lennenek.
const OTDOLOG_MIN_BID = 3, OTDOLOG_DEF_BID = 5, OTDOLOG_COLS = 6;""",
'nincs max licit')

sub1(
"""    const v = Math.max(OTDOLOG_MIN_BID, Math.min(OTDOLOG_MAX_BID, n));""",
"""    const v = Math.max(OTDOLOG_MIN_BID, n);""",
'changeBid clamp')

sub1(
"""              <button onClick={() => changeBid(bid + 1)} disabled={bid >= OTDOLOG_MAX_BID}
                aria-label="Eggyel több"
                style={{ width:48, height:48, borderRadius:'50%', border:'none', background:T.mintSoft, cursor: bid < OTDOLOG_MAX_BID ? 'pointer' : 'default', opacity: bid < OTDOLOG_MAX_BID ? 1 : 0.4, display:'grid', placeItems:'center' }}>""",
"""              <button onClick={() => changeBid(bid + 1)}
                aria-label="Eggyel több"
                style={{ width:48, height:48, borderRadius:'50%', border:'none', background:T.mintSoft, cursor:'pointer', display:'grid', placeItems:'center' }}>""",
'plusz gomb hatar nelkul')

# ── 2. A kategoria mar a licit alatt latszik ────────────────────────────────
sub1(
"""        {phase === 'ready' ? (
          <div style={{ height:34, borderRadius:8, background:'repeating-linear-gradient(-45deg,#e0e4f0,#e0e4f0 4px,#d0d4e4 4px,#d0d4e4 8px)' }}/>
        ) : (
          <div style={{ fontFamily:T.font, fontWeight:T.weightDisplay, fontSize:26, color:T.ink, lineHeight:1.1, animation:'popIn .3s cubic-bezier(.2,.9,.3,1.2)' }}>{cat}</div>
        )}""",
"""        {/* ⚠️ A kategoria MAR A LICIT ALATT latszik (v10.350). A v10.339-ben
            satirozva volt („vak licit"), de kategoria nelkul nem lehet
            ertelmesen vallalni egy szamot. */}
        <div style={{ fontFamily:T.font, fontWeight:T.weightDisplay, fontSize:26, color:T.ink, lineHeight:1.1, animation:'popIn .3s cubic-bezier(.2,.9,.3,1.2)' }}>{cat}</div>""",
'kategoria mindig latszik')

# ── 3. A „<Nev> licital" sor kikerul ───────────────────────────────────────
sub1(
"""          {/* LICIT — a jatek lenyege. A kategoria meg REJTVE van (a satirozott
              sav fent), tehat a licit vak dontes: a kategoriat ismerve mar nem
              lenne tet. */}
          <div style={{ width:'100%', background:T.surface, borderRadius:20, padding:'16px 18px', boxShadow:T.shadow, boxSizing:'border-box' }}>
            <div style={{ fontFamily:T.font, fontSize:11.5, fontWeight:800, color:T.inkMute, textTransform:'uppercase', letterSpacing:'0.12em', textAlign:'center' }}>
              {challenger?.name || 'A kihívó'} licitál
            </div>
            <div style={{ fontFamily:T.font, fontSize:13, color:T.inkSoft, textAlign:'center', marginTop:4, marginBottom:12 }}>
              Hány szót vállalsz?
            </div>""",
"""          {/* LICIT — a jatek lenyege. Ki licital, azt a footer pirulaja mondja
              meg; a lap tetejen ugyanaz a nev feleslegesen ismetlodott. */}
          <div style={{ width:'100%', background:T.surface, borderRadius:20, padding:'16px 18px', boxShadow:T.shadow, boxSizing:'border-box' }}>
            <div style={{ fontFamily:T.font, fontSize:13, color:T.inkSoft, textAlign:'center', marginBottom:12 }}>
              Hány szót vállalsz?
            </div>""",
'licital sor torlese')

# ── 4. Az indito gomb mar nem „felfed" ─────────────────────────────────────
sub1(
"""            <div style={{ fontFamily:T.font, fontWeight:700, fontSize:13, color:'rgba(255,255,255,0.85)' }}>{totalTime}mp · Felfed & Indít</div>""",
"""            <div style={{ fontFamily:T.font, fontWeight:700, fontSize:13, color:'rgba(255,255,255,0.85)' }}>{totalTime}mp · Indítás</div>""",
'indito gomb felirata')

# ── 5. A gyuru helyett a KOZOS BohTimer sav ────────────────────────────────
sub1(
"""      ) : (
        <div style={{ position:'relative', width:160, height:160 }}>
          <svg viewBox="0 0 160 160" style={{ position:'absolute', inset:0, width:'100%', height:'100%', transform:'rotate(-90deg)' }}>
            <circle cx="80" cy="80" r={r} fill="none" stroke={`${T.inkMute}30`} strokeWidth="7" />
            <circle cx="80" cy="80" r={r} fill="none" stroke={timerColor} strokeWidth="7"
              strokeDasharray={circ} strokeDashoffset={+(circ*(1-pct)).toFixed(1)} strokeLinecap="round"
              style={{ transition:'stroke .3s' }} />
          </svg>
          <div style={{ position:'absolute', inset:0, display:'flex', flexDirection:'column', alignItems:'center', justifyContent:'center' }}>
            <div style={{ fontFamily:T.font, fontWeight:T.weightDisplay, fontSize:52, color:T.ink, lineHeight:1 }}>{phase==='done' ? '0' : Math.ceil(timeLeft)}</div>
            <div style={{ fontFamily:T.font, fontSize:12, fontWeight:700, color:T.inkSoft, letterSpacing:'0.07em' }}>MP</div>
          </div>
        </div>
      )}""",
"""      ) : (
        /* A KOZOS visszaszamlalo (v10.329): 30 px, vizszintes. A regi gyuru
           160 px-et vett el a jelolok es a lap elol — pont erre keszult. */
        <BohTimer variant="bar" total={totalTime} left={phase === 'done' ? 0 : timeLeft} />
      )}""",
'BohTimer sav')

# a gyuruhoz tartozo szamitasok mar nem kellenek
sub1(
"""  const checkedCount = checked.filter(Boolean).length;
  const pct = timeLeft / totalTime;
  const r = 72, circ = +(2 * Math.PI * r).toFixed(1);
  const timerColor = pct > 0.5 ? T.mint : pct > 0.2 ? T.yellow : T.coral;
""",
"""  const checkedCount = checked.filter(Boolean).length;
  // A jelolo-sor RACS: soronkent legfeljebb `OTDOLOG_COLS`. Hat folott kisebb
  // csempe, hogy 360 px-en is olvashato maradjon a szam.
  const cols = Math.min(bid, OTDOLOG_COLS);
  const small = cols > 5;
""",
'gyuru szamitasok helyett racs-meret')

# ── 6. A jelolo-sor racs lesz ──────────────────────────────────────────────
sub1(
"""      {phase !== 'ready' && (
        /* Az ot jelolo KITOLTI a sort (flex:1), nem fix 50 px. Igy a szamok
           akkorak lehetnek, hogy futas kozben, feligy odanezve is talalhatoak. */
        <div style={{ display:'flex', gap: bid > 6 ? 6 : 10, width:'100%' }}>
          {checked.map((c, i) => (
            <div key={i} onClick={() => { if (phase === 'done') return; const n=[...checked]; n[i]=!n[i]; setChecked(n); }}
              style={{ flex:1, minWidth:0, height: bid > 6 ? 52 : 64, borderRadius: bid > 6 ? 13 : 16, cursor: phase==='done' ? 'default' : 'pointer', background:c?T.mint:T.surface, opacity: phase==='done' && !c ? 0.45 : 1, display:'grid', placeItems:'center', boxShadow:T.shadow, border:`2px solid ${c?T.mint:'transparent'}`, transition:'all .15s' }}>
              {c ? <span style={{ display:'grid', placeItems:'center' }}>{Icon.check('#fff')}</span>
                 : <span style={{ fontFamily:T.font, fontWeight:800, fontSize: bid > 6 ? 17 : 22, color:T.ink }}>{i+1}</span>}
            </div>
          ))}
        </div>
      )}""",
"""      {phase !== 'ready' && (
        /* A jelolok KITOLTIK a sort (`1fr`), nem fix 50 px — igy a szamok
           akkorak lehetnek, hogy futas kozben, feligy odanezve is talalhatoak.
           ⚠️ RACS, nem egyetlen sor: felso licit-hatar nelkul (v10.350) egy
           12-es vallalas 20 px szeles csempeket adna. */
        <div style={{ display:'grid', gridTemplateColumns:`repeat(${cols},1fr)`, gap: small ? 6 : 10, width:'100%' }}>
          {checked.map((c, i) => (
            <div key={i} onClick={() => { if (phase === 'done') return; const n=[...checked]; n[i]=!n[i]; setChecked(n); }}
              style={{ minWidth:0, height: small ? 52 : 64, borderRadius: small ? 13 : 16, cursor: phase==='done' ? 'default' : 'pointer', background:c?T.mint:T.surface, opacity: phase==='done' && !c ? 0.45 : 1, display:'grid', placeItems:'center', boxShadow:T.shadow, border:`2px solid ${c?T.mint:'transparent'}`, transition:'all .15s' }}>
              {c ? <span style={{ display:'grid', placeItems:'center' }}>{Icon.check('#fff')}</span>
                 : <span style={{ fontFamily:T.font, fontWeight:800, fontSize: small ? 17 : 22, color:T.ink }}>{i+1}</span>}
            </div>
          ))}
        </div>
      )}""",
'jelolo racs')

# ── 7. ⚠️ A kezi „Vesztettem / Nyertem!" gombok kizarasa ───────────────────
sub1(
"""      {currentGame.category === 'Páros' && pairedOpponent && scenario.cta.length > 0 && currentGameId !== 'neugyanazt' && currentGameId !== 'szamsor'""",
"""      {currentGame.category === 'Páros' && pairedOpponent && scenario.cta.length > 0 && currentGameId !== 'otdolog' && currentGameId !== 'neugyanazt' && currentGameId !== 'szamsor'""",
'otdolog kizarasa a Paros gombokbol')

# ── 8. A szovegek kovessek a nyilt, hatartalan licitet ─────────────────────
sub1(
"""  otdolog:   { prompt:'Mondj 5 odaillő szót a megadott időn belül!', cta:[('Nem sikerült'),('Megvan!')] },""",
"""  otdolog:   { prompt:'Licitálj, aztán mondd ki annyi odaillő szót az időn belül!', cta:[('Nem sikerült'),('Megvan!')] },""",
'otdolog prompt')

sub1(
"""desc:'Páros játék. Megjelenik egy kategória, és a soros játékos LICITÁL: megmondja, hány odaillő szót vállal (3–8). Az idő a licithez igazodik.""",
"""desc:'Páros játék. Megjelenik egy kategória, és a soros játékos LICITÁL: megmondja, hány odaillő szót vállal (legalább 3, felső határ nincs). Az idő a licithez igazodik.""",
'otdolog leiras')

sub1("const APP_VERSION = 'v10.349';", "const APP_VERSION = 'v10.350';", 'verzio')

assert src != orig
io.open(P, 'w', encoding='utf-8').write(src)
print('OK - patch_10_350 alkalmazva')
