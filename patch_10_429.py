# v10.429 — Imposztor: az imposztorok száma beállítható (Auto / 1 / 2 / 3).
f = 'app.src.html'; s = open(f, encoding='utf8').read()
def rep(old, new, cnt=1):
    global s
    assert s.count(old) == cnt, (s.count(old), old[:90])
    s = s.replace(old, new)

rep("function ImposztorHint({ hint }) {", """// Hány imposztor legyen (v10.429). `cfg.count`: 'auto' (alap — 5 főtől 2, alatta 1) vagy
// 1/2/3. Mindig marad legalább KÉT nem-imposztor, különben nincs kit kiszavazni.
function imposztorCount(cfg, n) {
  const c = cfg && cfg.count;
  const want = (typeof c === 'number' && c > 0) ? c : (n >= 5 ? 2 : 1);
  return Math.max(1, Math.min(want, n - 2));
}

function ImposztorHint({ hint }) {""")
rep("    const numImpostors = players.length >= 5 ? 2 : 1;",
    "    const numImpostors = imposztorCount(gameMeta && gameMeta.imposztorConfig, players.length);")
rep("  }, [gameIdx, players.length]);\n\n  // A felfedés/szavazás sorrendje",
    "  }, [gameIdx, players.length, gameMeta && gameMeta.imposztorConfig && gameMeta.imposztorConfig.count]);\n\n  // A felfedés/szavazás sorrendje")
rep("impostorIndices.length === 2 ? 'szavazhattok az egyik imposztorra' : 'szavazhattok'",
    "impostorIndices.length > 1 ? 'szavazhattok az egyik imposztorra' : 'szavazhattok'")
rep("Az Imposztor{impostors.length === 2 ? 'ok' : ''}", "Az Imposztor{impostors.length > 1 ? 'ok' : ''}")
rep("""function ImposztorConfigSheet({ config, setConfig, onClose }) {
  return (""", """function ImposztorConfigSheet({ config, setConfig, onClose, playerCount }) {
  const n = playerCount || 0;
  const cnt = typeof config.count === 'number' ? config.count : 'auto';
  const eff = n ? imposztorCount(config, n) : null;
  return (""")
rep("""        value={config.mode === 'undercover' ? 'undercover' : 'classic'} onPick={v => setConfig(c => ({ ...c, mode: v }))} />
      {config.mode !== 'undercover' && (""", """        value={config.mode === 'undercover' ? 'undercover' : 'classic'} onPick={v => setConfig(c => ({ ...c, mode: v }))} />
      <CfgRow label="Imposztorok száma"
        hint={(cnt === 'auto' ? 'Automatikus: 5 játékostól 2, alatta 1' : 'Mindig marad legalább 2 nem-imposztor')
              + (eff != null ? ` · most ${n} főre: ${eff} imposztor` : '')}
        options={[{ v:'auto', l:'Auto' }, { v:1, l:'1' }, { v:2, l:'2' }, { v:3, l:'3' }]}
        value={cnt} onPick={v => setConfig(c => ({ ...c, count: v }))} />
      {config.mode !== 'undercover' && (""")
rep("const APP_VERSION = 'v10.428';", "const APP_VERSION = 'v10.429';")
open(f, 'w', encoding='utf8').write(s)
print('ok')
