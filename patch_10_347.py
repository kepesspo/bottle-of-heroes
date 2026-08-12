# v10.347 - DNR gomb a Szuro mellett, a jatekok kedvenc-soros alakban
#
# Uj, otodik chip a jatekvalaszto szurosoran: „DNR". Megnyomva a lista helyen
# CSAK a DNR exkluziv jatekok allnak, es nem racs-csempekent, hanem a
# KEDVENCEK szeles sorai (`FavTile`) alakjaban.
#
# ⚠️ A SZIN NEM TEMAFUGGO. A kartyan levo „★ DNR EXKLUZIV" szalag mar most is
# fix `#0E0E18` + `#FFD23F` parost visz, es a gomb UGYANAZT jelenti — temabol
# szarmaztatva minden temaban maskepp nezne ki, mint a szalag, amire mutat.
# Ezert lett a ket szin modul-szintu konstans (`DNR_INK` / `DNR_GOLD`), es a
# szalag is innen olvassa. Egy forras, ket felulet.
#
# ⚠️ MELYIK JATEK DNR: EGY forras. Eddig a felteteles kifejezes
# (`g.id === 'busz' || g.dnr`) ket helyen allt volna (Szures + uj gomb) —
# innentol `isDnrGame(g)`. A `busz` azert van azonositoval bedrotozva, mert
# nincs rajta `dnr:true` (CLAUDE.md v10.314).
#
# ⚠️ KOLCSONOS KIZARAS a Szuressel. A Szures lapon MEGMARAD a „DNR Exkluziv"
# sor — az mas dolgot csinal: kategoriakon belul szur, es KOMBINALHATO a
# nehezseggel. Az uj gomb ezzel szemben egy reflektor: mindent elrejt, kiveve a
# DNR jatekokat, es masik alakban mutatja oket. A ketto egyszerre bekapcsolva
# fel-allapot lenne, ezert a gomb kikapcsolja a szuroket, a szuro pedig a gombot.
import io

P = 'app.src.html'
src = io.open(P, encoding='utf-8').read()
orig = src

def sub1(old, new, what):
    global src
    assert src.count(old) == 1, '%s: %d talalat' % (what, src.count(old))
    src = src.replace(old, new)

# ── 1. Modul-szintu konstansok + az EGY forras arrol, mi szamit DNR-nek ──────
sub1(
"""function GamesScreen({ selectedGames, setSelectedGames, gameMeta, setGameMeta, go, players, netReady = true }) {""",
"""// A DNR ket szine. ⚠️ NEM temafuggo, es ez szandekos: a jatekkartyan levo
// „★ DNR EXKLUZIV" szalag mar ezt a parost viszi, a szurosor DNR gombja pedig
// UGYANARRA mutat. Temabol szarmaztatva a gomb es a szalag minden temaban
// elcsuszna egymastol. (Ugyanaz a szabaly, mint a Szures nehezseg-kartyainal
// es a `BOH_TIMER_TONES`-nal: ahol a szin maga a jelentes, ott fix.)
const DNR_INK  = '#0E0E18';
const DNR_GOLD = '#FFD23F';

// ⚠️ EGY forras arrol, melyik jatek DNR exkluziv. A jelolo a `GAMES[]`
// bejegyzesen a `dnr:true` mezo; a `busz` azert log ki, mert azon nincs jelolo,
// azonositoval van bedrotozva (CLAUDE.md v10.314). Ket felulet olvassa: a
// Szures „DNR Exkluziv" sora es a szurosor DNR gombja — ha ket helyen allna a
// felteteles kifejezes, egy uj DNR jatek az egyikbol kimaradna.
function isDnrGame(g) { return !!g && (g.id === 'busz' || !!g.dnr); }

function GamesScreen({ selectedGames, setSelectedGames, gameMeta, setGameMeta, go, players, netReady = true }) {""",
'DNR konstansok + isDnrGame')

# ── 2. DNR mod allapota ─────────────────────────────────────────────────────
sub1(
"""  const [activeFilters, setActiveFilters] = useState([]); // [] = show all
""",
"""  const [activeFilters, setActiveFilters] = useState([]); // [] = show all
  // DNR reflektor-mod: a lista helyen CSAK a DNR exkluziv jatekok allnak,
  // kedvenc-soros (FavTile) alakban. Kolcsonosen kizaro a Szuressel — lasd a
  // `toggleDnrMode` / `toggleFilter` parost.
  const [dnrMode, setDnrMode] = useState(false);
""",
'dnrMode allapot')

# ── 3. Kolcsonos kizaras ────────────────────────────────────────────────────
sub1(
"""  const toggleFilter = f => setActiveFilters(fs => fs.includes(f) ? fs.filter(x=>x!==f) : [...fs, f]);""",
"""  // ⚠️ A ket DNR-belepo kizarja egymast. A Szures „DNR Exkluziv" sora
  // kategorian belul szur es kombinalhato a nehezseggel; a DNR gomb reflektor,
  // ami mindent elrejt. Egyszerre bekapcsolva fel-allapot lenne: szurt lista
  // DNR fejleccel, vagy forditva.
  const toggleFilter = f => { setDnrMode(false); setActiveFilters(fs => fs.includes(f) ? fs.filter(x=>x!==f) : [...fs, f]); };
  const toggleDnrMode = () => { const next = !dnrMode; setDnrMode(next); if (next) setActiveFilters([]); };""",
'kolcsonos kizaras')

# ── 4. A szures DNR aga az EGY forrasbol ────────────────────────────────────
sub1(
"""      f === 'DNR'    ? (g.id === 'busz' || g.dnr) :""",
"""      f === 'DNR'    ? isDnrGame(g) :""",
'gameMatchesFilter DNR ag')

# ── 5. A chip-sor: otodik gomb a Szuro MELLETT ──────────────────────────────
# A negy meglevo oszlop marad `1fr`, a DNR `auto` — pont annyi helyet kap,
# amennyit a felirata ker, es nem szorítja ki a „Veletlen"-t 360 px-en.
sub1(
"""      <div style={{ display:'grid', gridTemplateColumns:'repeat(4,1fr)', gap:8 }}>
        <Chip label={t('allGames')} active={allOn} onClick={selectAll} />
        <Chip label={t('clearGames')} onClick={clearAll} />
        <Chip label={t('randomGames')} onClick={shuffle} tone="purple" icon={Icon.dice('#fff')} />
        <Chip label={hasFilter ? t('filterGames') + ' (' + activeFilters.length + ')' : t('filterGames')} onClick={() => setFilterSheet(true)} tone={hasFilter ? 'filter' : undefined} active={hasFilter} />
      </div>""",
"""      {/* ⚠️ A DNR oszlopa `auto`, nem `1fr`: pontosan annyi helyet kap,
          amennyit a felirata ker. Ot egyenlo oszlopnal 360 px-en a „Veletlen"
          (90 px min-content, kockaikonnal) kiszorult volna a sorbol. */}
      <div style={{ display:'grid', gridTemplateColumns:'repeat(4,1fr) auto', gap:8 }}>
        <Chip label={t('allGames')} active={allOn} onClick={selectAll} />
        <Chip label={t('clearGames')} onClick={clearAll} />
        <Chip label={t('randomGames')} onClick={shuffle} tone="purple" icon={Icon.dice('#fff')} />
        <Chip label={hasFilter ? t('filterGames') + ' (' + activeFilters.length + ')' : t('filterGames')} onClick={() => setFilterSheet(true)} tone={hasFilter ? 'filter' : undefined} active={hasFilter} />
        <Chip label="DNR" tone="dnr" active={dnrMode} onClick={toggleDnrMode} testId="dnr" />
      </div>""",
'chip sor')

# ── 6. A Chip ismeri a DNR hangot ───────────────────────────────────────────
sub1(
"""function Chip({ label, active, onClick, tone, icon, disabled }) {
  const isFilter = tone === 'filter';
  const bg = disabled ? T.surfaceMuted : tone==='purple' ? T.purple : isFilter && active ? T.mint : active ? T.surface : T.surfaceMuted;
  const fg = disabled ? T.inkMute : (tone==='purple' || (isFilter && active)) ? '#fff' : T.ink;
  return (
    <button onClick={disabled ? undefined : onClick} style={{
      minHeight:44, padding:'0 6px', background:bg, color:fg, border:'none',
      borderRadius:14, boxShadow: tone==='purple' ? '0 3px 0 rgba(124,92,196,0.4), 0 6px 16px rgba(124,58,237,0.25)' : isFilter && active ? `0 3px 0 ${T.mint}66, 0 6px 16px ${T.mint}40` : T.shadow,
      fontFamily:T.font, fontWeight:T.weightTitle, fontSize:13,
      display:'flex', alignItems:'center', justifyContent:'center', gap:6,
      cursor: disabled ? 'default' : 'pointer', opacity: disabled ? 0.7 : 1,
    }}>""",
"""function Chip({ label, active, onClick, tone, icon, disabled, testId }) {
  const isFilter = tone === 'filter';
  // ⚠️ A DNR hang szinei FIXEK (`DNR_INK` / `DNR_GOLD`) — ugyanaz a paros, amit
  // a kartyan a „★ DNR EXKLUZIV" szalag visz. Ez a sor egyetlen SOTET chipje,
  // ezert valik el a tobbitol minden temaban. Bekapcsolva megfordul (arany
  // hatteren sotet felirat): igy a be/ki allapot nem csak arnyalatban ter el.
  const isDnr = tone === 'dnr';
  const bg = disabled ? T.surfaceMuted : isDnr ? (active ? DNR_GOLD : DNR_INK) : tone==='purple' ? T.purple : isFilter && active ? T.mint : active ? T.surface : T.surfaceMuted;
  const fg = disabled ? T.inkMute : isDnr ? (active ? DNR_INK : DNR_GOLD) : (tone==='purple' || (isFilter && active)) ? '#fff' : T.ink;
  return (
    <button onClick={disabled ? undefined : onClick} data-chip={testId} aria-pressed={isDnr ? !!active : undefined} style={{
      minHeight:44, padding: isDnr ? '0 11px' : '0 6px', background:bg, color:fg, border: isDnr ? `1.5px solid ${DNR_GOLD}` : 'none',
      borderRadius:14, boxShadow: isDnr ? `0 3px 0 rgba(14,14,24,0.32), 0 6px 16px ${DNR_GOLD}55` : tone==='purple' ? '0 3px 0 rgba(124,92,196,0.4), 0 6px 16px rgba(124,58,237,0.25)' : isFilter && active ? `0 3px 0 ${T.mint}66, 0 6px 16px ${T.mint}40` : T.shadow,
      fontFamily:T.font, fontWeight:T.weightTitle, fontSize: isDnr ? 12.5 : 13,
      letterSpacing: isDnr ? '0.09em' : undefined, whiteSpace: isDnr ? 'nowrap' : undefined,
      display:'flex', alignItems:'center', justifyContent:'center', gap:6,
      cursor: disabled ? 'default' : 'pointer', opacity: disabled ? 0.7 : 1,
    }}>""",
'Chip DNR hang')

# ── 7. A szalag ugyanabbol a ket konstansbol ────────────────────────────────
sub1(
"""          background:'#0E0E18', color:'#FFD23F',
          border:'1.25px solid #FFD23F', borderRadius:999,""",
"""          background:DNR_INK, color:DNR_GOLD,
          border:`1.25px solid ${DNR_GOLD}`, borderRadius:999,""",
'szalag szinei')

# ── 8. DNR modban a tobbi szekcio nem latszik ───────────────────────────────
sub1(
"""        {/* ── Buli-sablonok ── */}
        {(templates.length > 0 || anySelected) && (""",
"""        {/* ── Buli-sablonok ── */}
        {!dnrMode && (templates.length > 0 || anySelected) && (""",
'sablonok elrejtese')

sub1(
"""        {/* ── Kedvencek szekció ── */}
        {!hasFilter && (() => {""",
"""        {/* ── Kedvencek szekció ── */}
        {!hasFilter && !dnrMode && (() => {""",
'kedvencek elrejtese')

# ── 9. A DNR szekcio + a kategoria-szekciok elrejtese ───────────────────────
sub1(
"""        {/* ── Csoportosított játékok ── */}
        {[
          { key:'Egyéni', label:'Egyéni' },""",
"""        {/* ── DNR exkluzív szekció ──
            A jatekok ugyanabban a szeles, kedvenc-soros alakban (`FavTile`)
            allnak, mint a Kedvencek — nem racs-csempekent. A lista a
            `visibleGames`-bol jon, tehat a rejtett es a hamarosan-erkezo
            jatekokra vonatkozo szabalyok automatikusan ervenyesek maradnak. */}
        {dnrMode && (() => {
          const dnrGames = visibleGames.filter(isDnrGame);
          return (
            <div style={{ marginBottom:18 }}>
              <div style={{ display:'flex', alignItems:'center', gap:8, marginBottom:10 }}>
                <span style={{ background:DNR_INK, color:DNR_GOLD, border:`1.25px solid ${DNR_GOLD}`, borderRadius:999, padding:'4px 10px 5px', fontFamily:T.font, fontWeight:900, fontSize:10, letterSpacing:'0.15em', whiteSpace:'nowrap' }}>★ DNR EXKLUZÍV</span>
                <span style={{ flex:1 }} />
                <span style={{ fontFamily:T.font, fontWeight:900, fontSize:11, color:T.inkMute }}>{dnrGames.length} játék</span>
              </div>
              {dnrGames.length === 0 ? (
                <div style={{ fontFamily:T.font, fontSize:12.5, color:T.inkSoft, textAlign:'center', padding:'18px 0' }}>Most nincs elérhető DNR exkluzív játék.</div>
              ) : (
                <div style={{ display:'flex', flexDirection:'column', gap:8 }}>
                  {dnrGames.map(g => {
                    const isSelected = selectedGames.includes(g.id);
                    const locked = isLocked(g.id);
                    const dim = locked || !!g.comingSoon || (anySelected && !isSelected);
                    return (
                      <FavTile key={g.id} g={g} selected={isSelected} dim={dim} locked={locked || !!g.comingSoon}
                        onClick={() => { if (!g.comingSoon) toggle(g.id); }} onInfo={() => setInfo(g.id)}
                        onLongPress={longPressFor(g.id)} />
                    );
                  })}
                </div>
              )}
            </div>
          );
        })()}

        {/* ── Csoportosított játékok ── */}
        {!dnrMode && [
          { key:'Egyéni', label:'Egyéni' },""",
'DNR szekcio + kategoriak elrejtese')

sub1("const APP_VERSION = 'v10.346';", "const APP_VERSION = 'v10.347';", 'verzio')

assert src != orig
io.open(P, 'w', encoding='utf-8').write(src)
print('OK - patch_10_347 alkalmazva')
