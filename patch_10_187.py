#!/usr/bin/env python3
# v10.187 — az átemelés kihagyott profilokat
#
# Miert: a Jatekosok kepernyo indulaskor beirja a 12 elore beallitott profilt a
# Firestore-ba (window.saveProfile), az pedig v10.182 ota az EPP AKTIV
# adatbazisba ir. Aki eles modban ranyitott a Jatekosok oldalra, annal a 12
# profil letrejott az elesben — a hardkodolt alapertekekkel. Az atemeles utana
# "mar megvolt"-kent kihagyta oket, tehat a becenev, avatar, telefon, e-mail,
# szuletesnap es korty limit sosem jott at.
#
# Harom javitas:
#   1) az atemeles a HIANYZO mezoket potolja a meglevo profilokon is (a mar
#      kitoltott ertekekhez tovabbra sem nyul);
#   2) szerverrol olvas, nem a helyi gyorsitotarbol — az hianyos is lehet;
#   3) 500-as kotegre bontva ir (a Firestore ennyit enged egy kotegben).
#
# Es mostantol a kartya MEGMUTATJA, mi hianyzik: mennyi van a ket oldalon, es
# nevszerint melyik profil nincs meg elesben.
import sys

P = 'app.src.html'
src = open(P, encoding='utf-8').read()

def sub(old, new, what):
    global src
    assert src.count(old) == 1, '%s: %d talalat' % (what, src.count(old))
    src = src.replace(old, new, 1)

OLD = """function AdminProfileCopy({ onDone }) {
  const [busy, setBusy] = React.useState(false);
  const [result, setResult] = React.useState(null);

  const run = () => {
    if (busy || typeof firebase === 'undefined') return;
    setBusy(true); setResult(null);
    const fdb = firebase.firestore();
    Promise.all([fdb.collection('profiles').get(), fdb.collection('live_profiles').get()])
      .then(([srcSnap, dstSnap]) => {
        const have = new Set((dstSnap.docs || []).map(d => d.id));
        const batch = fdb.batch();
        let copied = 0, existed = 0, unnamed = 0;
        (srcSnap.docs || []).forEach(d => {
          // Ami már megvan élesben, azt nem írjuk felül — különben egy második
          // kattintás visszaállítaná az élesben azóta javított neveket.
          if (have.has(d.id)) { existed++; return; }
          const s = d.data() || {}, out = {};
          PROFILE_PERSONAL_FIELDS.forEach(k => { if (s[k] !== undefined && s[k] !== null) out[k] = s[k]; });
          if (!out.name) { unnamed++; return; }
          batch.set(fdb.collection('live_profiles').doc(d.id), out);
          copied++;
        });
        return (copied ? batch.commit() : Promise.resolve()).then(() => ({ copied, existed, unnamed }));
      })
      .then(r => { setResult(r); setBusy(false); onDone && onDone(); })
      .catch(e => { setResult({ err: String(e && e.message || e) }); setBusy(false); });
  };
"""

NEW = """// Mindig a szerverről olvas: a helyi gyorsítótár hiányos lehet (élesben lehet,
// hogy ez az eszköz sosem látta a teljes listát), és abból csendben kimaradna
// pár profil.
function ovfjFreshGet(col) {
  return col.get({ source: 'server' }).catch(() => col.get());
}
// A Firestore egy kötegben 500 írást enged.
function bohCommitInChunks(fdb, ops) {
  const chunks = [];
  for (let i = 0; i < ops.length; i += 400) chunks.push(ops.slice(i, i + 400));
  return chunks.reduce((chain, ch) => chain.then(() => {
    const batch = fdb.batch();
    ch.forEach(([id, data]) => batch.set(fdb.collection('live_profiles').doc(id), data, { merge: true }));
    return batch.commit();
  }), Promise.resolve());
}
// Mit kell átvinni, és mi van már meg. Külön függvény, hogy a kártya
// megnyitáskor is meg tudja mutatni — ne kelljen megnyomni ahhoz, hogy lásd.
function bohProfileDiff(srcSnap, dstSnap) {
  const dst = {};
  (dstSnap.docs || []).forEach(d => { dst[d.id] = d.data() || {}; });
  const has = (o, k) => o && o[k] !== undefined && o[k] !== null && o[k] !== '';
  const ops = [], newNames = [], filledNames = [];
  let same = 0, unnamed = 0;
  (srcSnap.docs || []).forEach(d => {
    const s = d.data() || {};
    if (!has(s, 'name')) { unnamed++; return; }
    const cur = dst[d.id];
    const out = {};
    // Amit élesben már kitöltöttek, ahhoz nem nyúlunk — csak a hiányzót pótoljuk.
    PROFILE_PERSONAL_FIELDS.forEach(k => { if (has(s, k) && !has(cur, k)) out[k] = s[k]; });
    if (!cur) { newNames.push(s.name); ops.push([d.id, out]); return; }
    if (Object.keys(out).length) { filledNames.push(s.name); ops.push([d.id, out]); return; }
    same++;
  });
  return { ops, newNames, filledNames, same, unnamed,
           srcCount: (srcSnap.docs || []).length, dstCount: (dstSnap.docs || []).length };
}

function AdminProfileCopy({ onDone }) {
  const [busy, setBusy] = React.useState(false);
  const [result, setResult] = React.useState(null);
  const [diff, setDiff] = React.useState(null);

  const load = React.useCallback(() => {
    if (typeof firebase === 'undefined') return Promise.resolve(null);
    const fdb = firebase.firestore();
    return Promise.all([ovfjFreshGet(fdb.collection('profiles')), ovfjFreshGet(fdb.collection('live_profiles'))])
      .then(([a, b]) => { const d = bohProfileDiff(a, b); setDiff(d); return d; })
      .catch(() => null);
  }, []);
  React.useEffect(() => { load(); }, [load]);

  const run = () => {
    if (busy || typeof firebase === 'undefined') return;
    setBusy(true); setResult(null);
    const fdb = firebase.firestore();
    Promise.all([ovfjFreshGet(fdb.collection('profiles')), ovfjFreshGet(fdb.collection('live_profiles'))])
      .then(([srcSnap, dstSnap]) => {
        const d = bohProfileDiff(srcSnap, dstSnap);
        return bohCommitInChunks(fdb, d.ops).then(() => d);
      })
      .then(r => { setResult(r); setBusy(false); onDone && onDone(); return load(); })
      .catch(e => { setResult({ err: String(e && e.message || e) }); setBusy(false); });
  };
"""
sub(OLD, NEW, 'AdminProfileCopy fej')

# ─── A kartya szovege + a diff kiirasa ───
OLD_UI = """      <div style={{ fontFamily:T.font, fontSize:12, color:T.inkSoft, marginTop:4, lineHeight:1.5 }}>
        A teszt profilok személyes adatait (név, becenév, szín, avatar, telefon, e-mail,
        születésnap, korty limit) átmásolja az éles adatbázisba, ugyanazokkal az
        azonosítókkal. Az eredmények nem jönnek át — élesben nulláról indul a statisztika.
        Ami élesben már megvan, azt nem írja felül.
      </div>"""
NEW_UI = """      <div style={{ fontFamily:T.font, fontSize:12, color:T.inkSoft, marginTop:4, lineHeight:1.5 }}>
        A teszt profilok személyes adatait (név, becenév, szín, avatar, telefon, e-mail,
        születésnap, korty limit) átemeli az éles adatbázisba, ugyanazokkal az
        azonosítókkal. Az eredmények nem jönnek át — élesben nulláról indul a statisztika.
        A már kitöltött éles mezőket nem írja felül, csak a hiányzókat pótolja.
      </div>
      {diff && (
        <div style={{ marginTop:8, display:'flex', flexDirection:'column', gap:6 }}>
          <div style={{ display:'flex', gap:8 }}>
            {[{ l:'Teszt', n:diff.srcCount }, { l:'Éles', n:diff.dstCount }].map(x => (
              <div key={x.l} style={{ flex:1, background:T.bg, borderRadius:11, padding:'7px 10px' }}>
                <div style={{ fontFamily:T.font, fontSize:10, fontWeight:800, color:T.inkSoft, textTransform:'uppercase', letterSpacing:'0.08em' }}>{x.l}</div>
                <div style={{ fontFamily:T.font, fontSize:17, fontWeight:900, color:T.ink, fontVariantNumeric:'tabular-nums' }}>{x.n}</div>
              </div>
            ))}
          </div>
          {/* Ez a lényeg: névszerint megmondja, mi nincs meg élesben. */}
          {diff.newNames.length > 0 && (
            <div style={{ fontFamily:T.font, fontSize:11.5, color:T.coral, lineHeight:1.5 }}>
              Élesben még nincs meg ({diff.newNames.length}): {diff.newNames.join(', ')}
            </div>
          )}
          {diff.filledNames.length > 0 && (
            <div style={{ fontFamily:T.font, fontSize:11.5, color:T.inkSoft, lineHeight:1.5 }}>
              Hiányos adattal van fenn ({diff.filledNames.length}): {diff.filledNames.join(', ')}
            </div>
          )}
          {diff.newNames.length === 0 && diff.filledNames.length === 0 && (
            <div style={{ fontFamily:T.font, fontSize:11.5, fontWeight:800, color:T.mint }}>
              Minden teszt profil fent van élesben, hiánytalanul.
            </div>
          )}
          {diff.unnamed > 0 && (
            <div style={{ fontFamily:T.font, fontSize:11, color:T.inkMute }}>
              {diff.unnamed} névtelen rekord kimarad.
            </div>
          )}
        </div>
      )}"""
sub(OLD_UI, NEW_UI, 'kartya szoveg')

OLD_RES = """            : `${result.copied} profil átemelve`
              + (result.existed ? `, ${result.existed} már megvolt` : '')
              + (result.unnamed ? `, ${result.unnamed} névtelen kihagyva` : '') + '.'}"""
NEW_RES = """            : `${result.newNames.length} új profil`
              + (result.filledNames.length ? `, ${result.filledNames.length} kiegészítve` : '')
              + (result.same ? `, ${result.same} változatlan` : '')
              + (result.unnamed ? `, ${result.unnamed} névtelen kihagyva` : '') + '.'}"""
sub(OLD_RES, NEW_RES, 'eredmeny szoveg')

# ─── Verziobump ───
sub("const APP_VERSION = 'v10.186';", "const APP_VERSION = 'v10.187';", 'verzio')

open(P, 'w', encoding='utf-8').write(src)
print('OK — hianyzo mezok potlasa, szerverrol olvasas, kotegeles, es lathato kulonbseg')
