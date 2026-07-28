#!/usr/bin/env python3
# v10.182 — a profilok is kettevalnak, es az eles kap egy masolatot
#
# Ket dolog van benne:
#
# 1) A 'profiles' bekerul a kettevalasztott kollekciok koze. Innentol az
#    elesben torolt szemet-profil nem tunik el a teszt oldalrol, es forditva.
#
# 2) Kozben kiderult, hogy a profil-osszevono admin eszkoz db2.collection('stats')
#    alakban ir — vagyis a v10.180 ota is MINDIG a teszt statisztikaba, barmelyik
#    modban vagyunk. A v10.180 tesztje ezt nem vette eszre, mert csak a
#    db.collection('stats') alakot kereste. Most ez is a coll()-on megy at.
import re, sys

P = 'app.src.html'
src = open(P, encoding='utf-8').read()

# ─── 1) a profilok is kettevalnak ───
OLD_LIST = "var BOH_SPLIT_COLLECTIONS = ['stats', 'statEvents', 'game_stats', 'gameStatEvents', 'usage', 'bp_tournaments'];"
assert src.count(OLD_LIST) == 1, 'lista: %d' % src.count(OLD_LIST)
NEW_LIST = "var BOH_SPLIT_COLLECTIONS = ['stats', 'statEvents', 'game_stats', 'gameStatEvents', 'usage', 'bp_tournaments', 'profiles'];"
src = src.replace(OLD_LIST, NEW_LIST, 1)

# A komment is mondja ki, mi kozos es mi nem — kulonben a lista onmagaban nem
# magyarazza, miert epp ezek.
OLD_NOTE = """  // A statisztika-kollekciók két példányban léteznek. A MOSTANI, prefix nélküli
  // nevek a TESZT-adatot tartják — így a váltáshoz nem kellett egyetlen
  // dokumentumot sem mozgatni. Az éles adat 'live_' prefixű kollekciókba megy,
  // tehát üresen indul."""
assert src.count(OLD_NOTE) == 1, 'komment: %d' % src.count(OLD_NOTE)
NEW_NOTE = """  // A statisztika- és profil-kollekciók két példányban léteznek. A MOSTANI,
  // prefix nélküli nevek a TESZT-adatot tartják — így a váltáshoz nem kellett
  // egyetlen dokumentumot sem mozgatni. Az éles adat 'live_' prefixű
  // kollekciókba megy, tehát üresen indul.
  //
  // Közös marad: config, rooms, barDrinks, tasks, party_templates, seasons —
  // ezek nem az eredményekről szólnak. A szezonok azért maradhatnak közösek,
  // mert csak a dátumokat tárolják; az állás mindig az épp aktív statisztikából
  // számolódik."""
src = src.replace(OLD_NOTE, NEW_NOTE, 1)

# ─── 2) minden hivashely a coll()-on at ───
# A .collection('x') alakot barmilyen valtozon elkapjuk (db, db2, firebase.firestore()),
# nem csak a 'db'-n — pont ez volt a v10.180 vakfoltja.
INSIDE = [   # az init-blokkon BELUL: a helyi coll()
    ("return db.collection('profiles').orderBy('name')",
     "return coll('profiles').orderBy('name')"),
    ("return db.collection('profiles').doc(profileId).set({ drinkLimit: v }, { merge: true })",
     "return coll('profiles').doc(profileId).set({ drinkLimit: v }, { merge: true })"),
    ("var ref = profile.id ? db.collection('profiles').doc(profile.id) : db.collection('profiles').doc();",
     "var ref = profile.id ? coll('profiles').doc(profile.id) : coll('profiles').doc();"),
]
OUTSIDE = [  # az init-blokkon KIVUL: a kitett window.bohColl()
    ("firebase.firestore().collection('profiles').doc(id).delete()",
     "window.bohColl('profiles').doc(id).delete()"),
    ("db2.collection('stats').doc(srcId).get(), db2.collection('stats').doc(dstId).get(),",
     "window.bohColl('stats').doc(srcId).get(), window.bohColl('stats').doc(dstId).get(),"),
    ("db2.collection('profiles').doc(srcId).get(), db2.collection('profiles').doc(dstId).get(),",
     "window.bohColl('profiles').doc(srcId).get(), window.bohColl('profiles').doc(dstId).get(),"),
    ("batch.set(db2.collection('stats').doc(dstId), merged);",
     "batch.set(window.bohColl('stats').doc(dstId), merged);"),
    ("batch.set(db2.collection('profiles').doc(dstId), profPatch, { merge: true });",
     "batch.set(window.bohColl('profiles').doc(dstId), profPatch, { merge: true });"),
    ("batch.delete(db2.collection('profiles').doc(srcId));",
     "batch.delete(window.bohColl('profiles').doc(srcId));"),
    ("batch.delete(db2.collection('stats').doc(srcId));",
     "batch.delete(window.bohColl('stats').doc(srcId));"),
    ("db.collection('profiles').doc(who).set({ email }, { merge: true })",
     "window.bohColl('profiles').doc(who).set({ email }, { merge: true })"),
]
for old, new in INSIDE + OUTSIDE:
    assert src.count(old) == 1, 'hivashely (%d): %s' % (src.count(old), old[:60])
    src = src.replace(old, new, 1)

# ─── 3) egyszeri masolas: a szemelyes adatok atmennek, az eredmenyek nem ───
# Fontos, hogy MEZO-FEHERLISTA legyen, ne a teljes dokumentum: ha kesobb barmi
# eredmeny-jellegu mezo kerul a profilra, az igy nem szivarog at csendben.
ANCHOR = """function AdminProfiles() {"""
assert src.count(ANCHOR) == 1
HELPER = """// Egyszeri átemelés a teszt profilokból az élesbe. Csak a személyes adatok
// mennek át — az eredmények (statisztika, kitüntetések, beerpong-párharcok) a
// stats/ kollekciókban élnek, azok szándékosan nulláról indulnak élesben.
//
// A profil-azonosítók megmaradnak: a közös kollekciók (szobák, bár-értékelések,
// szezonok) ezekre hivatkoznak, új azonosítókkal névtelenné válnának.
const PROFILE_PERSONAL_FIELDS = ['name', 'color', 'nickname', 'phone', 'birthday',
                                 'img', 'avatarId', 'email', 'drinkLimit'];

function AdminProfileCopy({ onDone }) {
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
        let copied = 0, skipped = 0;
        (srcSnap.docs || []).forEach(d => {
          // Ami már megvan élesben, azt nem írjuk felül — különben egy második
          // kattintás visszaállítaná az élesben azóta javított neveket.
          if (have.has(d.id)) { skipped++; return; }
          const s = d.data() || {}, out = {};
          PROFILE_PERSONAL_FIELDS.forEach(k => { if (s[k] !== undefined && s[k] !== null) out[k] = s[k]; });
          if (!out.name) { skipped++; return; }
          batch.set(fdb.collection('live_profiles').doc(d.id), out);
          copied++;
        });
        return (copied ? batch.commit() : Promise.resolve()).then(() => ({ copied, skipped }));
      })
      .then(r => { setResult(r); setBusy(false); onDone && onDone(); })
      .catch(e => { setResult({ err: String(e && e.message || e) }); setBusy(false); });
  };

  return (
    <div style={{ background:T.surface, borderRadius:16, padding:'12px 16px', marginBottom:14, boxShadow:T.shadow }}>
      <div style={{ fontFamily:T.font, fontWeight:900, fontSize:14, color:T.ink }}>Profilok átemelése az élesbe</div>
      <div style={{ fontFamily:T.font, fontSize:12, color:T.inkSoft, marginTop:4, lineHeight:1.5 }}>
        A teszt profilok személyes adatait (név, becenév, szín, avatar, telefon, e-mail,
        születésnap, korty limit) átmásolja az éles adatbázisba, ugyanazokkal az
        azonosítókkal. Az eredmények nem jönnek át — élesben nulláról indul a statisztika.
        Ami élesben már megvan, azt nem írja felül.
      </div>
      <button onClick={run} disabled={busy}
        style={{ marginTop:10, width:'100%', padding:'11px 0', borderRadius:12, border:'none',
                 background: busy ? T.surfaceMuted : T.mint, color: busy ? T.inkSoft : '#fff',
                 fontFamily:T.font, fontWeight:900, fontSize:14, cursor: busy ? 'default' : 'pointer' }}>
        {busy ? 'Másolás…' : 'Átemelés indítása'}
      </button>
      {result && (
        <div style={{ fontFamily:T.font, fontWeight:800, fontSize:12, marginTop:8,
                      color: result.err ? T.coral : T.mint }}>
          {result.err ? ('Nem sikerült: ' + result.err)
            : `${result.copied} profil átemelve${result.skipped ? `, ${result.skipped} kihagyva (már megvolt)` : ''}.`}
        </div>
      )}
    </div>
  );
}

function AdminProfiles() {"""
src = src.replace(ANCHOR, HELPER, 1)

# a kartya bekerul az AdminProfiles tetejere
OLD_TOP = """    <div style={{ padding:'16px' }}>
      {profiles.length >= 2 && <ProfileMergeCard profiles={profiles} onDone={load} />}"""
assert src.count(OLD_TOP) == 1, 'AdminProfiles teteje: %d' % src.count(OLD_TOP)
NEW_TOP = """    <div style={{ padding:'16px' }}>
      <AdminProfileCopy onDone={load} />
      {profiles.length >= 2 && <ProfileMergeCard profiles={profiles} onDone={load} />}"""
src = src.replace(OLD_TOP, NEW_TOP, 1)

# ─── verziobump ───
assert src.count("const APP_VERSION = 'v10.181';") == 1
src = src.replace("const APP_VERSION = 'v10.181';", "const APP_VERSION = 'v10.182';", 1)

open(P, 'w', encoding='utf-8').write(src)
print('OK — profiles kettevalasztva, 11 hivashely atvezetve, atemelo kartya bekerult')
