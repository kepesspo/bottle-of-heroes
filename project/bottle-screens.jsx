// bottle-screens.jsx — all screens for the Bottle of Heroes prototype.
// Each screen is themed via the `t` (theme tokens) prop. The same React tree
// runs both variations; visual differences come from the token sheet.

const { useState, useEffect, useRef, useMemo } = React;

// ─── radius scaler ──────────────────────────────────────────
// `r` is a 0..1 tweak; multiply against per-element base radii.
const R = (r, base) => Math.round(base * r);

// ─── shared chrome: top app bar (with optional segmented tab) ──
function AppBar({ t, r, title, onBack, right, sticky = true }) {
  const isB = t.id === 'B';
  return (
    <div style={{
      position: sticky ? 'sticky' : 'relative', top: 0, zIndex: 10,
      background: t.surface,
      borderBottomLeftRadius: R(r, 24), borderBottomRightRadius: R(r, 24),
      boxShadow: isB ? '0 4px 0 #0E0E18' : '0 4px 18px rgba(20,30,50,0.05)',
      border: isB ? '2px solid #0E0E18' : 'none', borderTop: 'none',
      padding: '14px 18px', display: 'flex', alignItems: 'center', gap: 10,
      minHeight: 56
    }}>
      {onBack ?
      <button onClick={onBack} style={{
        width: 38, height: 38, border: 'none', background: 'transparent',
        color: t.ink, cursor: 'pointer', display: 'grid', placeItems: 'center',
        borderRadius: R(r, 12)
      }}>{Icon.back(t.ink)}</button> :
      <div style={{ width: 8 }} />}
      <div style={{
        flex: 1, textAlign: 'center', fontFamily: t.fontDisplay,
        fontWeight: t.weightDisplay, fontSize: isB ? 28 : 20,
        letterSpacing: isB ? '0.04em' : '0.06em',
        textTransform: 'uppercase', color: t.ink
      }}>{title}</div>
      <div style={{ minWidth: 38, display: 'flex', justifyContent: 'flex-end' }}>{right}</div>
    </div>);

}

// Big primary button — fills width, can be disabled.
function PrimaryButton({ t, r, children, onClick, disabled, tone = 'mint', big = true, style }) {
  const isB = t.id === 'B';
  const bg = disabled ? tone === 'mint' ? t.mintSoft : t.coralSoft :
  tone === 'mint' ? t.mint : tone === 'coral' ? t.coral : tone;
  const fg = disabled ? isB ? 'rgba(14,14,24,0.4)' : '#fff' : '#fff';
  return (
    <button onClick={disabled ? undefined : onClick} style={{
      width: '100%', minHeight: big ? 60 : 48, border: isB ? '2px solid #0E0E18' : 'none',
      background: bg, color: fg,
      fontFamily: t.fontDisplay, fontWeight: t.weightTitle,
      fontSize: big ? 20 : 16, letterSpacing: t.letterDisplay,
      borderRadius: R(r, big ? 18 : 12),
      boxShadow: disabled ? 'none' : isB ? '4px 4px 0 #0E0E18' : t.shadow,
      cursor: disabled ? 'default' : 'pointer',
      transition: 'transform .08s, box-shadow .08s',
      padding: '8px 18px',
      whiteSpace: 'nowrap',
      ...style
    }}
    onMouseDown={(e) => {if (!disabled && isB) {e.currentTarget.style.transform = 'translate(2px,2px)';e.currentTarget.style.boxShadow = '2px 2px 0 #0E0E18';}}}
    onMouseUp={(e) => {if (!disabled && isB) {e.currentTarget.style.transform = '';e.currentTarget.style.boxShadow = '4px 4px 0 #0E0E18';}}}
    onMouseLeave={(e) => {if (!disabled && isB) {e.currentTarget.style.transform = '';e.currentTarget.style.boxShadow = '4px 4px 0 #0E0E18';}}}>
      {children}</button>);

}

// Real bottles logo (provided by user). Wrapped so we can pass size + soft drop shadow.
function BottlesIllustration({ t, size = 200 }) {
  return (
    <img src="assets/logo.png" width={size} height={size} alt="Bottle of Heroes"
    style={{
      display: 'block',
      filter: 'drop-shadow(0 6px 14px rgba(20,30,50,0.12))',
      userSelect: 'none', WebkitUserDrag: 'none'
    }} draggable="false" />);

}

// Per-game illustration. Loads the CSV's image_url; falls back to a centered
// emoji on load error or when img is empty (currently just Busz). Always sits
// on a tinted background tile so the bottles-style outline pops.
function GameIcon({ g, size = 64, tone = 'tint' }) {
  // `tone`: 'tint' (light wash of game color) | 'solid' (full color)
  const [failed, setFailed] = React.useState(false);
  const bg = tone === 'solid' ? g.color : `${g.color}26`;
  const showImg = g.img && !failed;
  return (
    <div style={{
      width: size, height: size, position: 'relative', flexShrink: 0,
      background: bg, borderRadius: Math.round(size * 0.22),
      display: 'grid', placeItems: 'center', overflow: 'hidden'
    }}>
      {showImg ?
      <img src={g.img} alt={g.name}
      referrerPolicy="no-referrer"
      onError={() => setFailed(true)}
      style={{
        width: '78%', height: '78%', objectFit: 'contain',
        filter: 'drop-shadow(0 2px 4px rgba(20,30,50,0.12))',
        userSelect: 'none'
      }} draggable="false" /> :

      <span style={{ fontSize: Math.round(size * 0.55), lineHeight: 1, filter: 'drop-shadow(0 2px 4px rgba(20,30,50,0.12))' }}>{g.emoji}</span>
      }
    </div>);

}

// ───────────────────────────────────────────────────────────
// SCREEN: HOME
// ───────────────────────────────────────────────────────────
function HomeScreen({ t, r, go, mode, setMode }) {
  const isB = t.id === 'B';
  return (
    <div style={{
      flex: 1, display: 'flex', flexDirection: 'column',
      padding: '24px 22px 28px', gap: 22,
      background: t.bg
    }}>
      {/* logo + title */}
      <div style={{ flex: 1, display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', gap: 18, paddingTop: 10 }}>
        <BottlesIllustration t={t} size={200} />
        <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 10 }}>
          <div style={{
            fontFamily: t.fontDisplay, fontWeight: t.weightDisplay,
            fontSize: 28, lineHeight: 1,
            letterSpacing: '0.05em',
            color: t.ink, textAlign: 'center', textTransform: 'uppercase'
          }}>Bottle of Heroes</div>
          <div style={{
            display: 'inline-flex', alignItems: 'center', gap: 6,
            padding: '5px 12px',
            background: t.surface,
            borderRadius: R(r, 999),
            boxShadow: t.shadow,
            fontFamily: t.font, fontWeight: 700, fontSize: 11,
            color: t.inkSoft, letterSpacing: '0.08em', textTransform: 'uppercase',
            whiteSpace: 'nowrap'
          }}>
            <span style={{ width: 6, height: 6, borderRadius: '50%', background: t.mint, flexShrink: 0 }} />
            Verzió 3.0 · DNR
          </div>
        </div>
      </div>

      {/* mode segmented */}
      <div style={{
        display: 'flex', padding: 6, background: t.surface,
        borderRadius: R(r, 999),
        border: isB ? '2px solid #0E0E18' : 'none',
        boxShadow: isB ? '4px 4px 0 #0E0E18' : t.shadow
      }}>
        {['Online', 'Offline'].map((m) => {
          const active = mode === m;
          return (
            <button key={m} onClick={() => setMode(m)} style={{
              flex: 1, minHeight: 46, border: 'none', cursor: 'pointer',
              background: active ? t.mint : 'transparent',
              color: active ? '#fff' : t.mint,
              fontFamily: t.fontDisplay, fontWeight: t.weightTitle, fontSize: 16,
              borderRadius: R(r, 999),
              transition: 'all .2s'
            }}>{m}</button>);

        })}
      </div>

      <PrimaryButton t={t} r={r} onClick={() => go('players')} tone="mint">
        Játék
      </PrimaryButton>

      <PrimaryButton t={t} r={r} onClick={() => go('observer')} tone="coral">
        Megfigyelő
      </PrimaryButton>
    </div>);

}

// ───────────────────────────────────────────────────────────
// SCREEN: PLAYERS — add / remove / pick color
// ───────────────────────────────────────────────────────────
function PlayersScreen({ t, r, players, setPlayers, go }) {
  const isB = t.id === 'B';
  const [editing, setEditing] = useState(null); // playerId or 'new'

  const addPlayer = () => {
    const used = new Set(players.map((p) => p.color));
    const color = PLAYER_COLORS.find((c) => !used.has(c)) || PLAYER_COLORS[0];
    const np = { id: 'p' + Date.now(), name: '', color, drinks: 0, points: 0 };
    setPlayers([...players, np]);
    setEditing(np.id);
  };
  const removePlayer = (id) => setPlayers(players.filter((p) => p.id !== id));
  const updatePlayer = (id, patch) => setPlayers(players.map((p) => p.id === id ? { ...p, ...patch } : p));

  return (
    <div style={{ flex: 1, display: 'flex', flexDirection: 'column', background: t.bg }}>
      <AppBar t={t} r={r} title={`Játékosok (${players.length})`} onBack={() => go('home')}
      right={
      <div style={{ display: 'flex', gap: 6, padding: 4, background: t.mintSoft, borderRadius: R(r, 999) }}>
            <div style={{ width: 34, height: 34, borderRadius: R(r, 999), background: t.mint, display: 'grid', placeItems: 'center', color: '#fff' }}>{Icon.users('#fff')}</div>
            <div style={{ width: 34, height: 34, display: 'grid', placeItems: 'center', color: t.mintDeep }}>{Icon.controller(t.mintDeep)}</div>
          </div>
      } />
      

      <div style={{ flex: 1, padding: '20px 18px 20px', overflowY: 'auto' }}>
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr', gap: 12 }}>
          {players.map((p) =>
          <PlayerCard key={p.id} t={t} r={r} p={p}
          onEdit={() => setEditing(p.id)}
          onRemove={() => removePlayer(p.id)} />

          )}
          {/* add slot */}
          <button onClick={addPlayer} style={{
            aspectRatio: '1 / 1.18', minHeight: 120,
            border: isB ? '2.5px dashed #0E0E18' : `2.5px dashed ${t.mint}`,
            borderRadius: R(r, 18), background: t.surfaceMuted,
            display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center',
            gap: 8, cursor: 'pointer', color: t.mint, padding: 6
          }}>
            <div style={{ width: 44, height: 44, borderRadius: R(r, 999), border: `2.5px solid ${t.mint}`, display: 'grid', placeItems: 'center' }}>{Icon.plus(t.mint)}</div>
            <div style={{ fontFamily: t.fontDisplay, fontWeight: t.weightTitle, fontSize: 13, color: t.mint, textAlign: 'center' }}>
              {players.length + 1}. Játékos
            </div>
          </button>
        </div>

        {players.length < 2 &&
        <div style={{
          marginTop: 18, padding: '14px 16px', background: t.coralSoft,
          border: isB ? '2px solid #0E0E18' : 'none',
          borderRadius: R(r, 14),
          fontFamily: t.font, fontSize: 13, color: t.ink, fontWeight: 600
        }}>Legalább 2 játékos kell. Adj hozzá még valakit!</div>
        }
      </div>

      <BottomBar t={t} r={r}>
        <PrimaryButton t={t} r={r} disabled={players.length < 2} onClick={() => go('games')}>
          Tovább a játékokhoz
        </PrimaryButton>
      </BottomBar>

      {editing &&
      <PlayerEditSheet t={t} r={r}
      player={players.find((p) => p.id === editing)}
      onClose={() => setEditing(null)}
      onChange={(patch) => updatePlayer(editing, patch)}
      usedColors={new Set(players.filter((p) => p.id !== editing).map((p) => p.color))} />

      }
    </div>);

}

function PlayerCard({ t, r, p, onEdit, onRemove }) {
  const isB = t.id === 'B';
  return (
    <div style={{
      position: 'relative', background: t.surface,
      borderRadius: R(r, 18), padding: '14px 8px 12px',
      border: isB ? '2px solid #0E0E18' : 'none',
      boxShadow: isB ? '3px 3px 0 #0E0E18' : t.shadow,
      display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 6,
      cursor: 'pointer', height: "110px"
    }} onClick={onEdit}>
      <button onClick={(e) => {e.stopPropagation();onRemove();}} style={{
        position: 'absolute', top: -6, right: -6, width: 24, height: 24,
        borderRadius: '50%', background: t.surface, color: t.inkSoft,
        border: isB ? '2px solid #0E0E18' : '1.5px solid rgba(20,30,50,0.12)',
        boxShadow: isB ? '2px 2px 0 #0E0E18' : '0 1px 3px rgba(0,0,0,0.1)',
        cursor: 'pointer', display: 'grid', placeItems: 'center', padding: 0
      }}>{Icon.close(t.inkSoft)}</button>
      <div style={{
        width: 56, height: 56, borderRadius: '50%', background: p.color,
        display: 'grid', placeItems: 'center',
        border: isB ? '2px solid #0E0E18' : 'none'
      }}>{Icon.user('#fff')}</div>
      <div style={{
        fontFamily: t.fontDisplay, fontWeight: t.weightTitle, fontSize: 14,
        color: t.ink, textAlign: 'center',
        whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis', maxWidth: '100%'
      }}>{p.name || 'Új játékos'}</div>
      <div style={{ width: 22, height: 2, background: p.color, borderRadius: 1, opacity: 0.5 }} />
    </div>);

}

function PlayerEditSheet({ t, r, player, onClose, onChange, usedColors }) {
  const isB = t.id === 'B';
  return (
    <SheetOverlay t={t} r={r} onClose={onClose}>
      <div style={{ padding: '6px 22px 22px', display: 'flex', flexDirection: 'column', gap: 16 }}>
        <div style={{ textAlign: 'center', fontFamily: t.fontDisplay, fontWeight: t.weightDisplay, fontSize: 22, color: t.ink, textTransform: 'uppercase', letterSpacing: t.letterDisplay }}>Játékos</div>
        <div style={{ display: 'flex', justifyContent: 'center' }}>
          <div style={{ width: 86, height: 86, borderRadius: '50%', background: player.color, display: 'grid', placeItems: 'center', border: isB ? '2.5px solid #0E0E18' : 'none' }}>
            <svg width="48" height="48" viewBox="0 0 24 24" fill="none">
              <circle cx="12" cy="8" r="3.5" stroke="#fff" strokeWidth="2" />
              <path d="M5 20c1.5-3.5 4-5 7-5s5.5 1.5 7 5" stroke="#fff" strokeWidth="2" strokeLinecap="round" />
            </svg>
          </div>
        </div>
        <input autoFocus value={player.name} onChange={(e) => onChange({ name: e.target.value.slice(0, 14) })}
        placeholder="Név…"
        style={{
          width: '100%', boxSizing: 'border-box',
          background: t.bgSoft, border: isB ? '2px solid #0E0E18' : 'none',
          borderRadius: R(r, 14), padding: '14px 18px',
          fontFamily: t.fontDisplay, fontWeight: t.weightTitle, fontSize: 18,
          color: t.ink, textAlign: 'center', outline: 'none'
        }} />
        <div>
          <div style={{ fontFamily: t.font, fontSize: 12, fontWeight: 700, color: t.inkSoft, marginBottom: 10, textTransform: 'uppercase', letterSpacing: '0.06em' }}>Szín</div>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(5, 1fr)', gap: 10 }}>
            {PLAYER_COLORS.map((c) => {
              const used = usedColors.has(c) && c !== player.color;
              const active = c === player.color;
              return (
                <button key={c} disabled={used} onClick={() => onChange({ color: c })} style={{
                  aspectRatio: '1 / 1', borderRadius: '50%', background: c,
                  border: active ? isB ? '3px solid #0E0E18' : `3px solid ${t.ink}` : isB ? '2px solid #0E0E18' : '2px solid transparent',
                  cursor: used ? 'default' : 'pointer',
                  opacity: used ? 0.25 : 1,
                  transform: active ? 'scale(1.08)' : 'scale(1)',
                  transition: 'transform .15s',
                  boxShadow: active && isB ? '3px 3px 0 #0E0E18' : 'none'
                }} />);

            })}
          </div>
        </div>
        <PrimaryButton t={t} r={r} onClick={onClose} disabled={!player.name.trim()}>Mehet</PrimaryButton>
      </div>
    </SheetOverlay>);

}

// ───────────────────────────────────────────────────────────
// SCREEN: GAMES picker
// ───────────────────────────────────────────────────────────
function GamesScreen({ t, r, selectedGames, setSelectedGames, gameMeta, setGameMeta, go, tileStyle = 1, dimMode = 'fade', buszBadge = 'corner' }) {
  const isB = t.id === 'B';
  const [info, setInfo] = useState(null); // game id
  const [sheet, setSheet] = useState(false);

  const allOn = selectedGames.length === GAMES.length;
  const anySelected = selectedGames.length > 0;
  // Busz is an exclusive (full-app) game — when it's picked, nothing else can
  // run alongside it; when anything else is picked, Busz is blocked.
  const buszSelected = selectedGames.includes('busz');
  const otherSelected = selectedGames.some((id) => id !== 'busz');
  const isLocked = (id) => id === 'busz' ? otherSelected : buszSelected;

  const toggle = (id) => {
    // Locked tiles ignore taps — except the Busz lock collapse, where tapping
    // Busz while others are picked should NOT silently swap; user must clear first.
    if (isLocked(id)) return;
    setSelectedGames(
      selectedGames.includes(id) ? selectedGames.filter((x) => x !== id) : [...selectedGames, id]
    );
  };
  const selectAll = () => setSelectedGames(GAMES.filter((g) => g.id !== 'busz').map((g) => g.id));
  const clearAll = () => setSelectedGames([]);
  const shuffle = () => {
    // Random shuffle never includes Busz (it's exclusive)
    const pool = GAMES.filter((g) => g.id !== 'busz');
    const shuffled = [...pool].sort(() => Math.random() - 0.5);
    const n = 4 + Math.floor(Math.random() * 4);
    setSelectedGames(shuffled.slice(0, n).map((g) => g.id));
  };

  return (
    <div style={{ flex: 1, display: 'flex', flexDirection: 'column', background: t.bg }}>
      <AppBar t={t} r={r} title="Játékok" onBack={() => go('players')}
      right={
      <div style={{ display: 'flex', gap: 6, padding: 4, background: t.mintSoft, borderRadius: R(r, 999) }}>
            <div style={{ width: 34, height: 34, display: 'grid', placeItems: 'center', color: t.mintDeep }}>{Icon.users(t.mintDeep)}</div>
            <div style={{ width: 34, height: 34, borderRadius: R(r, 999), background: t.mint, display: 'grid', placeItems: 'center' }}>{Icon.controller('#fff')}</div>
          </div>
      } />
      

      {/* filter chips */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: 8, padding: '14px 18px 8px' }}>
        <Chip t={t} r={r} label="Összes" active={allOn} onClick={selectAll} />
        <Chip t={t} r={r} label="Törlés" onClick={clearAll} />
        <Chip t={t} r={r} label="Véletlen" onClick={shuffle} tone="purple" icon={Icon.dice('#fff')} />
        <Chip t={t} r={r} label="+ Saját" disabled tone="muted" />
      </div>

      {/* games grid — scrollable; extra top room so the info-button overhang
                doesn't kiss the filter chips above; bottom clears the absolute BottomBar. */}
      <div style={{ flex: 1, minHeight: 0, overflowY: 'auto', padding: '14px 18px 96px' }}>
        <div style={{
          display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: 12
        }}>
          {GAMES.map((g) => {
            const isSelected = selectedGames.includes(g.id);
            const locked = isLocked(g.id);
            // Treat "locked because of exclusive Busz rule" the same way visually
            // as the soft-dim treatment, so the selection still pops.
            const dim = locked || anySelected && !isSelected;
            return (
              <GameTile key={g.id} t={t} r={r} g={g} tileStyle={tileStyle}
              selected={isSelected} dim={dim} dimMode={dimMode}
              locked={locked} lockReason={g.id === 'busz' ? 'others' : 'busz'}
              buszBadge={buszBadge}
              onClick={() => toggle(g.id)}
              onInfo={() => setInfo(g.id)} />);


          })}
        </div>
      </div>

      <BottomBar t={t} r={r} anchored extra={
      <button onClick={() => setSheet(true)} aria-label="Beállítások" style={{
        width: 56, height: 60, minHeight: 60, flexShrink: 0,
        background: t.surfaceMuted, border: 'none',
        borderRadius: R(r, 16),
        color: t.ink, cursor: 'pointer',
        display: 'grid', placeItems: 'center',
        boxShadow: t.shadow
      }}>{Icon.settings(t.ink)}</button>
      }>
        <PrimaryButton t={t} r={r} disabled={selectedGames.length < 1} onClick={() => go('play')}>
          Játék indítása! ({selectedGames.length})
        </PrimaryButton>
      </BottomBar>

      {sheet &&
      <SheetOverlay t={t} r={r} onClose={() => setSheet(false)}>
          <GameSettingsContent t={t} r={r} meta={gameMeta} setMeta={setGameMeta} onDone={() => setSheet(false)} canStart={selectedGames.length >= 1} go={go} />
        </SheetOverlay>
      }
      {info &&
      <GameInfoModal t={t} r={r} game={GAMES.find((g) => g.id === info)} onClose={() => setInfo(null)} />
      }
    </div>);

}

function Chip({ t, r, label, active, onClick, tone, icon, disabled }) {
  const isB = t.id === 'B';
  const bg = disabled ? t.surfaceMuted : tone === 'purple' ? t.purple : active ? t.surface : t.surfaceMuted;
  const fg = disabled ? t.inkMute : tone === 'purple' ? '#fff' : t.ink;
  return (
    <button onClick={disabled ? undefined : onClick} style={{
      minHeight: 44, padding: '0 6px',
      background: bg, color: fg,
      border: isB ? '2px solid #0E0E18' : 'none',
      borderRadius: R(r, 14),
      boxShadow: isB ? disabled ? 'none' : '3px 3px 0 #0E0E18' : tone === 'purple' ? '0 4px 14px rgba(124,58,237,0.3)' : 'none',
      fontFamily: t.fontDisplay, fontWeight: t.weightTitle, fontSize: 13,
      display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 6,
      cursor: disabled ? 'default' : 'pointer', opacity: disabled ? 0.7 : 1
    }}>
      {icon && <span style={{ display: 'flex' }}>{icon}</span>}
      {label}
    </button>);

}

// Returns CSS for the "dim" treatment applied to unselected cards once
// anything is selected. Multiple modes so we can compare which reads best.
const DIM_STYLES = {
  none: { filter: 'none', opacity: 1 },
  fade: { filter: 'none', opacity: 0.4 },
  gray: { filter: 'grayscale(0.8) brightness(0.96)', opacity: 0.7 },
  recede: { filter: 'none', opacity: 0.55, transform: 'scale(0.94)' },
  blur: { filter: 'blur(0.7px) saturate(0.65)', opacity: 0.65 }
};
function dimStyle(mode, dim) {
  if (!dim) return { filter: 'none', opacity: 1, transform: 'scale(1)' };
  return { ...DIM_STYLES.none, ...(DIM_STYLES[mode] || DIM_STYLES.fade) };
}

function GameTile({ t, r, g, selected, dim, dimMode, locked, lockReason, buszBadge, onClick, onInfo, tileStyle = 1 }) {
  const props = { t, r, g, selected, dim, dimMode, locked, lockReason, buszBadge, onClick, onInfo };
  if (tileStyle === 2) return <GameTileV2 {...props} />;
  if (tileStyle === 3) return <GameTileV3 {...props} />;
  return <GameTileV1 {...props} />;
}

// V1 — Player-card style: white card, image inside a tinted circle, name
// always visible below, color stripe underline. Fixed 122px height so the
// whole grid stays perfectly uniform regardless of name length or selection.
function GameTileV1({ t, r, g, selected, dim, dimMode, locked, lockReason, buszBadge, onClick, onInfo }) {
  const isB = t.id === 'B';
  const diff = DIFFICULTY_META[g.difficulty];
  const selColor = diff.tone;
  const ds = dimStyle(dimMode, dim);
  return (
    <div onClick={onClick} style={{
      position: 'relative', cursor: locked ? 'not-allowed' : 'pointer',
      minWidth: 0, boxSizing: 'border-box',
      background: t.surface, borderRadius: R(r, 18),
      border: isB ? '2px solid #0E0E18' : 'none',
      boxShadow: isB ?
      '3px 3px 0 #0E0E18' :
      selected ? `inset 0 0 0 3px ${selColor}, 0 8px 22px ${selColor}55` : t.shadow,
      padding: '10px 6px 8px',
      display: 'flex', flexDirection: 'column', alignItems: 'center',
      justifyContent: 'flex-start', gap: 6,
      ...ds,
      transition: 'box-shadow .2s, filter .25s, opacity .25s, transform .25s', height: "125px", width: "110px"
    }}>
      <div style={{
        width: 54, height: 54, borderRadius: '50%', background: `${g.color}26`,
        border: isB ? '2px solid #0E0E18' : 'none',
        display: 'grid', placeItems: 'center', padding: 7, flexShrink: 0, overflow: 'hidden'
      }}>
        <GameImg g={g} size="full" />
      </div>
      <div style={{
        fontFamily: t.fontDisplay, fontWeight: t.weightTitle, fontSize: 12,
        color: t.ink, textAlign: 'center', lineHeight: 1.15,
        whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis', maxWidth: '100%'
      }}>{g.name}</div>
      <div style={{ width: 22, height: 3, borderRadius: 2, background: g.color, opacity: 0.85 }} />
      <TileDiffDot tone={diff.tone} />
      <TileInfoBtn t={t} r={r} onInfo={onInfo} />
      {g.id === 'busz' && <BuszBadge t={t} r={r} variant={buszBadge} />}
      {locked && <LockOverlay t={t} r={r} reason={lockReason} />}
    </div>);

}

// V2 — Poszter (fixed height for grid uniformity)
function GameTileV2({ t, r, g, selected, dim, dimMode, locked, lockReason, buszBadge, onClick, onInfo }) {
  const isB = t.id === 'B';
  const diff = DIFFICULTY_META[g.difficulty];
  const selColor = diff.tone;
  const ds = dimStyle(dimMode, dim);
  return (
    <div onClick={onClick} style={{
      position: 'relative', cursor: locked ? 'not-allowed' : 'pointer',
      height: 122, minWidth: 0, boxSizing: 'border-box',
      background: t.surface, borderRadius: R(r, 16),
      border: isB ? '2px solid #0E0E18' : 'none',
      boxShadow: isB ?
      '3px 3px 0 #0E0E18' :
      selected ? `inset 0 0 0 3px ${selColor}, 0 8px 22px ${selColor}55` : t.shadow,
      overflow: 'hidden',
      ...ds,
      transition: 'box-shadow .2s, filter .25s, opacity .25s, transform .25s',
      display: 'flex', flexDirection: 'column'
    }}>
      <div style={{
        flex: 1, background: `${g.color}1F`,
        display: 'grid', placeItems: 'center', padding: 12, minHeight: 0
      }}>
        <GameImg g={g} size="full" />
      </div>
      <div style={{
        padding: '6px 6px 8px', background: g.color, color: '#fff',
        display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 2,
        textShadow: '0 1px 0 rgba(0,0,0,0.08)'
      }}>
        <div style={{
          fontFamily: t.fontDisplay, fontWeight: t.weightTitle, fontSize: 12,
          textAlign: 'center', lineHeight: 1.1,
          whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis', maxWidth: '100%'
        }}>{g.name}</div>
      </div>
      <TileDiffDot tone={diff.tone} />
      <TileInfoBtn t={t} r={r} onInfo={onInfo} />
      {g.id === 'busz' && <BuszBadge t={t} r={r} variant={buszBadge} />}
      {locked && <LockOverlay t={t} r={r} reason={lockReason} />}
    </div>);

}

// V3 — Címke (fixed height)
function GameTileV3({ t, r, g, selected, dim, dimMode, locked, lockReason, buszBadge, onClick, onInfo }) {
  const isB = t.id === 'B';
  const diff = DIFFICULTY_META[g.difficulty];
  const selColor = diff.tone;
  const ds = dimStyle(dimMode, dim);
  return (
    <div onClick={onClick} style={{
      position: 'relative', cursor: locked ? 'not-allowed' : 'pointer',
      height: 122, minWidth: 0, boxSizing: 'border-box',
      background: t.surface, borderRadius: R(r, 16),
      border: isB ? '2px solid #0E0E18' : 'none',
      boxShadow: isB ?
      '3px 3px 0 #0E0E18' :
      selected ? `inset 0 0 0 3px ${selColor}, 0 8px 22px ${selColor}55` : t.shadow,
      padding: 6,
      display: 'flex', flexDirection: 'column', gap: 4,
      ...ds,
      transition: 'box-shadow .2s, filter .25s, opacity .25s, transform .25s'
    }}>
      <div style={{
        flex: 1, borderRadius: R(r, 12),
        background: `${g.color}1F`,
        display: 'grid', placeItems: 'center', padding: 10, minHeight: 0
      }}>
        <GameImg g={g} size="full" />
      </div>
      <div style={{
        padding: '2px 4px 4px',
        fontFamily: t.fontDisplay, fontWeight: t.weightTitle, fontSize: 12,
        color: t.ink, textAlign: 'center', lineHeight: 1.1,
        whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis'
      }}>{g.name}</div>
      <TileDiffDot tone={diff.tone} />
      <TileInfoBtn t={t} r={r} onInfo={onInfo} />
      {g.id === 'busz' && <BuszBadge t={t} r={r} variant={buszBadge} />}
      {locked && <LockOverlay t={t} r={r} reason={lockReason} />}
    </div>);

}

// shared corners
function TileDiffDot({ tone }) {
  return (
    <div style={{
      position: 'absolute', top: 8, left: 8,
      width: 9, height: 9, borderRadius: '50%',
      background: tone, boxShadow: '0 0 0 1.5px rgba(255,255,255,0.95)',
      zIndex: 2
    }} />);

}

// "DNR Exkluzív" marker for the Busz tile. Multiple placement variants so
// we can find one that doesn't collide with the info button, name, etc.
function BuszBadge({ t, r, variant = 'corner' }) {
  // Variant SICKER — original bottom-hanging black+gold pill, slightly rotated.
  // Smaller than the first take so it doesn't crowd the tile.
  if (variant === 'sticker') {
    return (
      <div style={{
        position: 'absolute', bottom: -5, left: '50%',
        transform: 'translateX(-50%) rotate(-3deg)',
        padding: '1px 8px 2px',
        background: '#0E0E18', color: '#FFD23F',
        border: '1.25px solid #FFD23F',
        borderRadius: 999,
        fontFamily: '"Nunito", sans-serif', fontWeight: 900, fontSize: 7.5,
        letterSpacing: '0.15em',
        boxShadow: '0 1.5px 4px rgba(14,14,24,0.3), 0 0 0 1.5px rgba(255,210,63,0.18)',
        zIndex: 3, whiteSpace: 'nowrap', pointerEvents: 'none'
      }}>★ DNR EXKLUZÍV</div>);

  }
  // Variant A — corner stripe banner (top-right, replaces info button area
  // for Busz; info button is repositioned inside the tile when this is on).
  if (variant === 'corner') {
    return (
      <div style={{
        position: 'absolute', top: 0, right: 0, zIndex: 3,
        background: '#0E0E18', color: '#FFD23F',
        padding: '2px 8px 3px 10px',
        borderTopRightRadius: R(r, 18), borderBottomLeftRadius: R(r, 10),
        fontFamily: '"Nunito", sans-serif', fontWeight: 900, fontSize: 8.5,
        letterSpacing: '0.16em',
        pointerEvents: 'none', whiteSpace: 'nowrap'
      }}>★ DNR</div>);

  }
  // Variant B — ribbon along the bottom edge (inside the card, not hanging)
  if (variant === 'ribbon') {
    return (
      <div style={{
        position: 'absolute', left: 6, right: 6, bottom: 4, zIndex: 3,
        background: '#0E0E18', color: '#FFD23F',
        padding: '2px 0 3px',
        borderRadius: 3,
        fontFamily: '"Nunito", sans-serif', fontWeight: 900, fontSize: 8,
        letterSpacing: '0.22em', textAlign: 'center',
        pointerEvents: 'none', whiteSpace: 'nowrap',
        boxShadow: '0 1px 2px rgba(14,14,24,0.25)'
      }}>★ DNR EXKLUZÍV</div>);

  }
  // Variant C — small star chip above the name (centered under the avatar)
  if (variant === 'chip') {
    return (
      <div style={{
        position: 'absolute', top: 6, left: '50%',
        transform: 'translateX(-50%)', zIndex: 3,
        background: '#FFD23F', color: '#0E0E18',
        padding: '1px 7px 2px',
        borderRadius: 999,
        fontFamily: '"Nunito", sans-serif', fontWeight: 900, fontSize: 8,
        letterSpacing: '0.16em',
        boxShadow: '0 1px 3px rgba(14,14,24,0.25)',
        pointerEvents: 'none', whiteSpace: 'nowrap'
      }}>★ DNR</div>);

  }
  // Variant D — gold dot in the difficulty-dot position (replaces diff color
  // with a "premium" gold star indicator); also tints the name pill
  if (variant === 'dot') {
    return (
      <div style={{
        position: 'absolute', top: 5, left: 5, zIndex: 3,
        width: 18, height: 18, borderRadius: '50%',
        background: '#FFD23F', color: '#0E0E18',
        display: 'grid', placeItems: 'center',
        boxShadow: '0 0 0 2px #0E0E18, 0 2px 4px rgba(14,14,24,0.3)',
        pointerEvents: 'none'
      }}>
        <svg width="10" height="10" viewBox="0 0 24 24" fill="#0E0E18">
          <path d="M12 2l2.9 6.9L22 10l-5.5 4.8L18.2 22 12 18l-6.2 4 1.7-7.2L2 10l7.1-1.1L12 2z" />
        </svg>
      </div>);

  }
  // Variant E — "frame": a full second outline in gold around the whole tile
  if (variant === 'frame') {
    return (
      <React.Fragment>
        <div style={{
          position: 'absolute', inset: -3, zIndex: 0,
          borderRadius: R(r, 21),
          background: 'linear-gradient(135deg, #FFD23F 0%, #F4A04A 100%)',
          boxShadow: '0 6px 16px rgba(244,160,74,0.35)',
          pointerEvents: 'none'
        }} />
        <div style={{
          position: 'absolute', top: 6, right: 6, zIndex: 3,
          padding: '2px 7px 3px',
          background: '#0E0E18', color: '#FFD23F',
          borderRadius: 999,
          fontFamily: '"Nunito", sans-serif', fontWeight: 900, fontSize: 8,
          letterSpacing: '0.16em',
          pointerEvents: 'none', whiteSpace: 'nowrap'
        }}>★ DNR</div>
      </React.Fragment>);

  }
  return null;
}

// Tile-wide locked overlay — shown when a game can't be selected because
// Busz is exclusive. Cosmetic only; the tile already swallows clicks.
function LockOverlay({ t, r, reason }) {
  return (
    <div style={{
      position: 'absolute', inset: 0, zIndex: 2,
      borderRadius: 'inherit',
      pointerEvents: 'none',
      display: 'flex', alignItems: 'flex-end', justifyContent: 'flex-start',
      padding: 6
    }}>
      <div title={reason === 'busz' ? 'Busz exkluzív játék' : 'Busz mellett nem indítható'}
      style={{
        width: 22, height: 22, borderRadius: '50%',
        background: 'rgba(14,14,24,0.7)', color: '#fff',
        display: 'grid', placeItems: 'center',
        boxShadow: '0 2px 4px rgba(0,0,0,0.2)'
      }}>
        <svg width="11" height="11" viewBox="0 0 24 24" fill="none">
          <rect x="5" y="11" width="14" height="9" rx="2" stroke="#fff" strokeWidth="2.2" />
          <path d="M8 11V8a4 4 0 018 0v3" stroke="#fff" strokeWidth="2.2" strokeLinecap="round" />
        </svg>
      </div>
    </div>);

}
function TileInfoBtn({ t, r, onInfo }) {
  const isB = t.id === 'B';
  return (
    <button onClick={(e) => {e.stopPropagation();onInfo();}} style={{
      position: 'absolute', top: -8, right: -8, width: 30, height: 30, zIndex: 2,
      borderRadius: '50%', background: t.surface,
      border: isB ? '2px solid #0E0E18' : 'none',
      boxShadow: isB ? '2px 2px 0 #0E0E18' : '0 2px 6px rgba(0,0,0,0.12), 0 0 0 1px rgba(20,30,50,0.04)',
      cursor: 'pointer', display: 'grid', placeItems: 'center', padding: 0,
      color: t.inkSoft
    }}>
      <svg width="18" height="18" viewBox="0 0 24 24" fill="none">
        <circle cx="12" cy="12" r="9" stroke={t.inkSoft} strokeWidth="2" />
        <path d="M12 11v6M12 8v.01" stroke={t.inkSoft} strokeWidth="2.5" strokeLinecap="round" />
      </svg>
    </button>);

}
function TileCheck({ t, r, tone }) {
  return (
    <div style={{
      position: 'absolute', bottom: 6, right: 6,
      width: 20, height: 20, borderRadius: '50%',
      background: tone, color: '#fff',
      display: 'grid', placeItems: 'center', zIndex: 2,
      boxShadow: '0 2px 4px rgba(0,0,0,0.15)',
      animation: 'popIn .25s cubic-bezier(.2,.9,.3,1.4)'
    }}>
      <svg width="12" height="12" viewBox="0 0 24 24" fill="none">
        <path d="M5 12l5 5L20 7" stroke="#fff" strokeWidth="3.5" strokeLinecap="round" strokeLinejoin="round" />
      </svg>
    </div>);

}

// Variant of GameIcon used inside the tile — fills available square w/o its own bg.
function GameImg({ g, size = 'full', selected }) {
  const [failed, setFailed] = React.useState(false);
  const showImg = g.img && !failed;
  const style = size === 'full' ?
  { width: '100%', height: '100%', objectFit: 'contain' } :
  { width: size, height: size, objectFit: 'contain' };
  return showImg ?
  <img src={g.img} alt={g.name} referrerPolicy="no-referrer"
  onError={() => setFailed(true)}
  style={{ ...style, filter: selected ? 'drop-shadow(0 2px 0 rgba(0,0,0,0.2))' : 'drop-shadow(0 2px 4px rgba(20,30,50,0.08))', userSelect: 'none' }} draggable="false" /> :

  <span style={{ fontSize: size === 'full' ? 44 : Math.round(size * 0.6), lineHeight: 1, filter: selected ? 'drop-shadow(0 2px 0 rgba(0,0,0,0.2))' : 'none' }}>{g.emoji}</span>;

}

function GameInfoModal({ t, r, game, onClose }) {
  const isB = t.id === 'B';
  const diff = DIFFICULTY_META[game.difficulty];
  const cat = CATEGORY_META[game.category];
  return (
    <div onClick={onClose} style={{
      position: 'absolute', inset: 0, background: 'rgba(14,14,24,0.5)',
      zIndex: 50, display: 'flex', alignItems: 'center', justifyContent: 'center',
      padding: 22, animation: 'fadeIn .2s'
    }}>
      <div onClick={(e) => e.stopPropagation()} style={{
        background: t.surface, borderRadius: R(r, 22), padding: '22px 22px 20px',
        width: '100%', maxWidth: 340, maxHeight: '90%', overflowY: 'auto',
        border: isB ? '2.5px solid #0E0E18' : 'none',
        boxShadow: isB ? '5px 5px 0 #0E0E18' : '0 20px 60px rgba(0,0,0,0.25)',
        animation: 'popIn .25s cubic-bezier(.2,.9,.3,1.4)'
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 14, marginBottom: 14 }}>
          <div style={{
            width: 76, height: 76, borderRadius: R(r, 18),
            background: `${game.color}26`,
            border: isB ? '2px solid #0E0E18' : 'none',
            display: 'grid', placeItems: 'center', padding: 8,
            flexShrink: 0
          }}>
            <GameImg g={game} size="full" />
          </div>
          <div style={{ minWidth: 0 }}>
            <div style={{ fontFamily: t.fontDisplay, fontWeight: t.weightDisplay, fontSize: 22, color: t.ink, textTransform: 'uppercase', letterSpacing: t.letterDisplay, lineHeight: 1.05 }}>{game.name}</div>
            <div style={{ display: 'flex', gap: 6, marginTop: 8, flexWrap: 'wrap' }}>
              <Tag t={t} r={r} tone={diff.tone}>{diff.label}</Tag>
              <Tag t={t} r={r} tone={t.inkSoft} subtle>{cat.icon} {cat.label}</Tag>
            </div>
          </div>
        </div>
        <div style={{
          fontFamily: t.font, fontSize: 13.5, lineHeight: 1.55, color: t.inkSoft,
          marginBottom: 18, fontWeight: 500, whiteSpace: 'pre-line'
        }}>{game.desc}</div>
        <PrimaryButton t={t} r={r} onClick={onClose} big={false}>Értem</PrimaryButton>
      </div>
    </div>);

}

function Tag({ t, r, tone, subtle, children }) {
  return (
    <span style={{
      display: 'inline-flex', alignItems: 'center', gap: 4,
      padding: '3px 9px', borderRadius: R(r, 999),
      background: subtle ? 'rgba(20,30,50,0.06)' : `${tone}22`,
      color: subtle ? t.inkSoft : tone,
      fontFamily: t.fontDisplay, fontWeight: t.weightTitle, fontSize: 11,
      letterSpacing: '0.04em', textTransform: 'uppercase'
    }}>{children}</span>);

}

function GameSettingsContent({ t, r, meta, setMeta, onDone, go }) {
  const isB = t.id === 'B';
  const modes = [
  { id: 'points', label: 'Pontgyűjtés' },
  { id: 'bonus', label: 'Bonus Képernyő' },
  { id: 'random', label: 'Random Pictogram' },
  { id: 'group', label: 'Csoportos Ivás' }];

  const diffs = [
  { id: 'easy', label: 'Könnyű' },
  { id: 'mid', label: 'Közepes' },
  { id: 'hard', label: 'Nehéz' }];

  const toggleMode = (id) => setMeta({ ...meta, modes: meta.modes.includes(id) ? meta.modes.filter((x) => x !== id) : [...meta.modes, id] });
  return (
    <div style={{ padding: '6px 22px 22px', display: 'flex', flexDirection: 'column', gap: 18 }}>
      <div style={{ textAlign: 'center', fontFamily: t.fontDisplay, fontWeight: t.weightDisplay, fontSize: 22, color: t.ink, textTransform: 'uppercase', letterSpacing: t.letterDisplay }}>Játékmenet</div>
      <div style={{ display: 'flex', flexDirection: 'column', gap: 4 }}>
        {modes.map((m) => {
          const on = meta.modes.includes(m.id);
          return (
            <button key={m.id} onClick={() => toggleMode(m.id)} style={{
              padding: '14px 4px', border: 'none', background: 'transparent',
              display: 'flex', alignItems: 'center', justifyContent: 'space-between',
              cursor: 'pointer', borderBottom: `1px solid ${isB ? 'rgba(14,14,24,0.08)' : 'rgba(20,30,50,0.06)'}`
            }}>
              <span style={{ fontFamily: t.fontDisplay, fontWeight: t.weightTitle, fontSize: 16, color: t.ink }}>{m.label}</span>
              <div style={{
                width: 26, height: 26, borderRadius: '50%',
                border: on ? `2.5px solid ${t.mint}` : `2px solid ${t.inkMute}`,
                background: on ? t.mint : 'transparent',
                display: 'grid', placeItems: 'center'
              }}>{on && Icon.check('#fff')}</div>
            </button>);

        })}
      </div>
      <div>
        <div style={{ fontFamily: t.fontDisplay, fontWeight: t.weightDisplay, fontSize: 16, color: t.ink, textTransform: 'uppercase', letterSpacing: t.letterDisplay, marginBottom: 10, textAlign: 'center' }}>Nehézségi Szint</div>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: 8 }}>
          {diffs.map((d) => {
            const on = meta.difficulty === d.id;
            return (
              <button key={d.id} onClick={() => setMeta({ ...meta, difficulty: d.id })} style={{
                minHeight: 46, border: isB ? '2px solid #0E0E18' : 'none',
                background: on ? t.mint : t.mintSoft, color: on ? '#fff' : t.mintDeep,
                fontFamily: t.fontDisplay, fontWeight: t.weightTitle, fontSize: 14,
                borderRadius: R(r, 12),
                boxShadow: on && isB ? '3px 3px 0 #0E0E18' : 'none',
                cursor: 'pointer'
              }}>{d.label}</button>);

          })}
        </div>
      </div>
      <PrimaryButton t={t} r={r} onClick={() => {onDone();go('play');}}>Tovább</PrimaryButton>
    </div>);

}

// ───────────────────────────────────────────────────────────
// Bottom bar — by default a flex-tail card. With `anchored`, becomes
// absolute-positioned to the parent's bottom edge so it stays docked even
// while content above scrolls. `extra` slot drops a sibling control beside
// the primary action (e.g. a small settings gear).
// ───────────────────────────────────────────────────────────
function BottomBar({ t, r, children, pull, anchored, extra }) {
  const isB = t.id === 'B';
  const positioning = anchored ?
  { position: 'absolute', left: 0, right: 0, bottom: 0, zIndex: 5 } :
  { flexShrink: 0 };
  return (
    <div style={{
      ...positioning,
      background: t.surface,
      // No top rounding — bar is flush with the bottom edge of the device,
      // a tidy thick rail rather than a floating card. (User feedback)
      padding: pull ? '4px 16px 14px' : '14px 16px 14px',
      boxShadow: isB ? '0 -4px 0 #0E0E18, 0 -16px 32px rgba(20,30,50,0.06)' :
      '0 -2px 0 rgba(20,30,50,0.04), 0 -14px 32px rgba(20,30,50,0.12)',
      border: isB ? '2px solid #0E0E18' : 'none', borderBottom: 'none'
    }}>
      {pull &&
      <button onClick={pull} style={{
        width: '100%', height: 22, border: 'none', background: 'transparent',
        display: 'flex', alignItems: 'center', justifyContent: 'center', cursor: 'pointer'
      }}>
          <div style={{ width: 44, height: 5, borderRadius: 3, background: t.inkMute, opacity: 0.35 }} />
        </button>
      }
      <div style={{ display: 'flex', gap: 10, alignItems: 'stretch' }}>
        {extra}
        <div style={{ flex: 1, minWidth: 0 }}>{children}</div>
      </div>
    </div>);

}

function SheetOverlay({ t, r, onClose, children }) {
  const isB = t.id === 'B';
  return (
    <div onClick={onClose} style={{
      position: 'absolute', inset: 0, background: 'rgba(14,14,24,0.45)',
      zIndex: 40, display: 'flex', alignItems: 'flex-end',
      animation: 'fadeIn .2s'
    }}>
      <div onClick={(e) => e.stopPropagation()} style={{
        width: '100%', background: t.surface,
        borderTopLeftRadius: R(r, 28), borderTopRightRadius: R(r, 28),
        border: isB ? '2.5px solid #0E0E18' : 'none', borderBottom: 'none',
        boxShadow: isB ? '0 -4px 0 #0E0E18' : '0 -10px 40px rgba(0,0,0,0.2)',
        animation: 'slideUp .3s cubic-bezier(.2,.9,.3,1)',
        maxHeight: '85%', overflowY: 'auto'
      }}>
        <div style={{ display: 'flex', justifyContent: 'center', padding: '10px 0 6px' }}>
          <div style={{ width: 44, height: 5, borderRadius: 3, background: t.inkMute, opacity: 0.35 }} />
        </div>
        {children}
      </div>
    </div>);

}

Object.assign(window, { HomeScreen, PlayersScreen, GamesScreen, GameInfoModal, AppBar, PrimaryButton, BottomBar, SheetOverlay, BottlesIllustration, GameImg, R });