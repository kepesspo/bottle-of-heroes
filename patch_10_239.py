#!/usr/bin/env python3
# v10.239 — Admin ▸ Rendszer ▸ Partik: egy véletlenül élesben lejátszott parti
#           visszavonása
#
# MIÉRT LEHETSÉGES EGYÁLTALÁN
# A statEvents / gameStatEvents pontosan ugyanazokat a delta-értékeket tárolja,
# amiket a parti alatt hozzáadtunk a stats / game_stats összesítőkhöz
# (incrementStats + logStatEvent egymás mellett fut, lásd a mentő ágakat).
# Ezért egy parti visszavonása nem becslés: levonjuk ugyanazokat a számokat,
# majd töröljük az eseményeket.
#
# AMI NEM ÁLLÍTHATÓ VISSZA
#   bestReactionTime, bestStreak, currentStreak — ezek nem összegek, hanem
#   rekord/sorozat értékek, a korábbi értéküket sehol nem tároljuk. A felület
#   ezt ki is írja, hogy senki ne higgye teljesnek a visszavonást.
#
# PARTI-HATÁROK
# A statEvents a parti VÉGÉN íródik, a gameStatEvents viszont játékonként
# menet közben. Ezért az idővonalat mindkettőből (+ a Beer Pong bajnokságokból)
# rakjuk össze, és 4 óránál nagyobb szünetnél vágunk új partit.
import sys

P = 'app.src.html'
src = open(P, encoding='utf-8').read()

def sub(old, new, what):
    global src
    assert src.count(old) == 1, '%s: %d talalat' % (what, src.count(old))
    src = src.replace(old, new, 1)

COMP = r'''
// ── Admin: Partik — egy parti teljes visszavonása ─────────────────────────────
// Akkor kell, ha valaki véletlenül az ÉLES adatbázisban játszott. A statEvents
// és a gameStatEvents ugyanazokat a deltákat tárolja, amiket az összesítőkhöz
// hozzáadtunk, így a visszavonás pontos: levonjuk és töröljük.
// NEM állítható vissza: bestReactionTime, bestStreak, currentStreak — ezek
// rekord/sorozat értékek, a korábbi értékük sehol nincs eltárolva.
function AdminParties() {
  const GAP = 4 * 3600 * 1000; // ennel nagyobb szunet = uj parti
  const [data, setData] = React.useState(null);
  const [busy, setBusy] = React.useState(null);
  const [confirmKey, setConfirmKey] = React.useState(null);
  const [msg, setMsg] = React.useState(null);

  const load = () => {
    setData(null); setConfirmKey(null);
    Promise.all([
      window.bohColl('statEvents').get().then(s => s.docs.map(d => ({ id:d.id, ...d.data() }))).catch(() => []),
      window.bohColl('gameStatEvents').get().then(s => s.docs.map(d => ({ id:d.id, ...d.data() }))).catch(() => []),
      window.bohColl('bp_tournaments').get().then(s => s.docs.map(d => ({ id:d.id, ...d.data() }))).catch(() => []),
      typeof window.getProfiles === 'function' ? window.getProfiles() : Promise.resolve([]),
    ]).then(([se, ge, bt, profs]) => setData({ se, ge, bt, profs }));
  };
  React.useEffect(load, []);

  // Idovonal MINDHAROM forrasbol: a statEvents a parti vegen keletkezik, a
  // gameStatEvents jatekonkent menet kozben — csak egyutt adnak parti-ablakot.
  const groups = React.useMemo(() => {
    if (!data) return [];
    const items = []
      .concat(data.se.map(x => ({ ts: x.ts || 0, kind: 'se', x })))
      .concat(data.ge.map(x => ({ ts: x.ts || 0, kind: 'ge', x })))
      .concat(data.bt.map(x => ({ ts: x.ts || 0, kind: 'bt', x })))
      .sort((a, b) => a.ts - b.ts);
    const out = [];
    items.forEach(it => {
      const last = out[out.length - 1];
      if (last && it.ts - last.to <= GAP) { last.to = it.ts; last.items.push(it); }
      else out.push({ from: it.ts, to: it.ts, items: [it] });
    });
    return out.map(g => ({
      key: String(g.from),
      from: g.from, to: g.to,
      se: g.items.filter(i => i.kind === 'se').map(i => i.x),
      ge: g.items.filter(i => i.kind === 'ge').map(i => i.x),
      bt: g.items.filter(i => i.kind === 'bt').map(i => i.x),
    })).reverse();
  }, [data]);

  const nameOf = id => (((data && data.profs) || []).find(p => p.id === id) || {}).name || id;
  const fmt = ts => { try { return new Date(ts).toLocaleString('hu-HU', { month:'short', day:'numeric', hour:'2-digit', minute:'2-digit' }); } catch (e) { return String(ts); } };

  const undo = async (g) => {
    setBusy(g.key); setMsg(null); setConfirmKey(null);
    try {
      const FV = firebase.firestore.FieldValue;
      const statsCol = window.bohColl('stats'), gsCol = window.bohColl('game_stats');
      const seCol = window.bohColl('statEvents'), geCol = window.bohColl('gameStatEvents');
      const btCol = window.bohColl('bp_tournaments');

      const perProfile = {};
      g.se.forEach(ev => {
        if (!ev.profileId) return;
        const dst = perProfile[ev.profileId] || (perProfile[ev.profileId] = {});
        Object.keys(ev).forEach(k => {
          if (k === 'id' || k === 'profileId' || k === 'ts') return;
          if (typeof ev[k] === 'number') dst[k] = (dst[k] || 0) + ev[k];
        });
      });
      const perGame = {};
      g.ge.forEach(ev => {
        if (!ev.gameId) return;
        const dst = perGame[ev.gameId] || (perGame[ev.gameId] = { nums:{}, winners:{} });
        Object.keys(ev).forEach(k => {
          if (k === 'id' || k === 'gameId' || k === 'ts' || k === 'winnerProfileId') return;
          if (typeof ev[k] === 'number') dst.nums[k] = (dst.nums[k] || 0) + ev[k];
        });
        if (ev.winnerProfileId) dst.winners[ev.winnerProfileId] = (dst.winners[ev.winnerProfileId] || 0) + 1;
      });

      const ops = [];
      Object.keys(perProfile).forEach(pid => {
        const upd = {};
        Object.keys(perProfile[pid]).forEach(k => { const v = perProfile[pid][k]; if (v) upd[k] = FV.increment(-v); });
        if (Object.keys(upd).length) ops.push({ t:'set', ref: statsCol.doc(pid), data: upd });
      });
      Object.keys(perGame).forEach(gid => {
        const d = perGame[gid], upd = {}, win = {};
        Object.keys(d.nums).forEach(k => { if (d.nums[k]) upd[k] = FV.increment(-d.nums[k]); });
        Object.keys(d.winners).forEach(pid => { if (d.winners[pid]) win[pid] = FV.increment(-d.winners[pid]); });
        if (Object.keys(win).length) upd.winners = win;
        if (Object.keys(upd).length) ops.push({ t:'set', ref: gsCol.doc(gid), data: upd });
      });
      g.se.forEach(ev => ops.push({ t:'del', ref: seCol.doc(ev.id) }));
      g.ge.forEach(ev => ops.push({ t:'del', ref: geCol.doc(ev.id) }));
      g.bt.forEach(ev => ops.push({ t:'del', ref: btCol.doc(ev.id) }));

      // A Firestore batch 500 muveletig birja — bontsuk fel.
      const db2 = firebase.firestore();
      for (let i = 0; i < ops.length; i += 400) {
        const batch = db2.batch();
        ops.slice(i, i + 400).forEach(o => { if (o.t === 'del') batch.delete(o.ref); else batch.set(o.ref, o.data, { merge:true }); });
        await batch.commit();
      }
      setMsg({ ok:true, text:`Visszavonva — ${ops.length} művelet (${g.se.length} stat-esemény, ${g.ge.length} játék-esemény${g.bt.length ? `, ${g.bt.length} bajnokság` : ''}).` });
      load();
    } catch (e) {
      setMsg({ ok:false, text:'Hiba: ' + ((e && e.message) || String(e)) });
    }
    setBusy(null);
  };

  if (data === null) return <div style={{ textAlign:'center', padding:32, color:T.sub, fontFamily:T.font }}>Betöltés…</div>;

  return (
    <div style={{ padding:'0 16px 24px' }}>
      <div style={{ background: window.isTestDb() ? `${T.mint}18` : `${T.coral}18`, borderRadius:14, padding:'12px 14px', marginBottom:14 }}>
        <div style={{ fontFamily:T.font, fontWeight:900, fontSize:13, color: window.isTestDb() ? T.mintDeep : T.coral }}>
          {window.isTestDb() ? 'TESZT adatbázis' : 'ÉLES adatbázis'}
        </div>
        <div style={{ fontFamily:T.font, fontSize:11.5, color:T.sub, marginTop:4, lineHeight:1.5 }}>
          A visszavonás levonja a parti pontjait/kortyait az összesítőkből, és törli az eseményeit.
          Amit NEM tud visszaállítani: legjobb reakcióidő, leghosszabb sorozat, aktuális sorozat —
          ezek rekord-értékek, a korábbi értékük nincs eltárolva.
        </div>
      </div>

      {msg && (
        <div style={{ background: msg.ok ? `${T.mint}18` : `${T.coral}18`, color: msg.ok ? T.mintDeep : T.coral,
                      borderRadius:12, padding:'10px 13px', marginBottom:12, fontFamily:T.font, fontWeight:700, fontSize:12.5 }}>{msg.text}</div>
      )}

      <div style={{ display:'flex', justifyContent:'space-between', alignItems:'center', marginBottom:10 }}>
        <div style={{ fontFamily:T.font, fontSize:11, color:T.sub, fontWeight:700, textTransform:'uppercase', letterSpacing:'0.07em' }}>Partik ({groups.length})</div>
        <button onClick={load} style={{ padding:'6px 12px', borderRadius:10, border:'none', background:T.surface, fontFamily:T.font, fontWeight:700, fontSize:12, color:T.mint, cursor:'pointer', boxShadow:T.shadowPill || T.shadow }}>Frissítés</button>
      </div>

      {groups.length === 0 && (
        <div style={{ textAlign:'center', padding:32, color:T.sub, fontFamily:T.font, fontSize:14 }}>Nincs rögzített parti ebben az adatbázisban.</div>
      )}

      {groups.slice(0, 25).map(g => {
        const perP = {};
        g.se.forEach(ev => {
          if (!ev.profileId) return;
          const d = perP[ev.profileId] || (perP[ev.profileId] = { pts:0, drinks:0 });
          d.pts += ev.totalPoints || 0; d.drinks += ev.totalDrinks || 0;
        });
        const names = Object.keys(perP);
        return (
          <div key={g.key} style={{ background:T.surface, borderRadius:16, padding:'12px 14px', marginBottom:10, boxShadow:T.shadowPill || T.shadow }}>
            <div style={{ display:'flex', alignItems:'flex-start', gap:10 }}>
              <div style={{ flex:1, minWidth:0 }}>
                <div style={{ fontFamily:T.font, fontWeight:900, fontSize:14, color:T.ink }}>{fmt(g.from)}</div>
                <div style={{ fontFamily:T.font, fontSize:11.5, color:T.sub, marginTop:2 }}>
                  {g.from !== g.to ? `${fmt(g.to)}-ig · ` : ''}{g.se.length} stat-esemény · {g.ge.length} játék-esemény{g.bt.length ? ` · ${g.bt.length} bajnokság` : ''}
                </div>
              </div>
              {confirmKey === g.key ? (
                <button disabled={busy === g.key} onClick={() => undo(g)} style={{ flexShrink:0, padding:'8px 12px', borderRadius:10, border:'none', background:T.coral, color:'#fff', fontFamily:T.font, fontWeight:800, fontSize:12, cursor:'pointer', opacity: busy === g.key ? 0.6 : 1 }}>
                  {busy === g.key ? 'Törlés…' : 'Biztos? Visszavonom'}
                </button>
              ) : (
                <button onClick={() => { setConfirmKey(g.key); setMsg(null); }} style={{ flexShrink:0, padding:'8px 12px', borderRadius:10, border:'none', background:T.coralSoft || `${T.coral}22`, color:T.coral, fontFamily:T.font, fontWeight:800, fontSize:12, cursor:'pointer' }}>Visszavonás</button>
              )}
            </div>
            {names.length > 0 && (
              <div style={{ display:'flex', flexWrap:'wrap', gap:6, marginTop:10 }}>
                {names.map(pid => (
                  <span key={pid} style={{ fontFamily:T.font, fontSize:11.5, fontWeight:700, color:T.ink, background:T.bgSoft, borderRadius:999, padding:'4px 10px' }}>
                    {nameOf(pid)} · {perP[pid].pts} pont · {perP[pid].drinks} korty
                  </span>
                ))}
              </div>
            )}
          </div>
        );
      })}
    </div>
  );
}

'''

# ── 1. a komponens beszurasa az AdminScreen ele ──
sub("""// ── AdminScreen ────────────────────────────────────────────────────────────────
function AdminScreen({ go, setTheme, currentTheme }) {""",
    COMP + """// ── AdminScreen ────────────────────────────────────────────────────────────────
function AdminScreen({ go, setTheme, currentTheme }) {""",
    'AdminParties komponens')

# ── 2. uj ful a Rendszer kategoriaban ──
sub("""      ['growth','Növekedés'],['stats','Statisztika'],['seasons','Szezonok'],['zene','Zene'],['rooms','Szobák'],['message','Hirdetmény'],['settings','Beállítások'],""",
    """      ['growth','Növekedés'],['stats','Statisztika'],['partik','Partik'],['seasons','Szezonok'],['zene','Zene'],['rooms','Szobák'],['message','Hirdetmény'],['settings','Beállítások'],""",
    'Partik ful')

sub("""        {tab === 'stats'    && <AdminStats />}""",
    """        {tab === 'stats'    && <AdminStats />}
        {tab === 'partik'   && <AdminParties />}""",
    'Partik tab render')

sub("const APP_VERSION = 'v10.238';", "const APP_VERSION = 'v10.239';", 'verzio')
open(P, 'w', encoding='utf-8').write(src)
print('OK — Admin > Rendszer > Partik: parti visszavonasa')
