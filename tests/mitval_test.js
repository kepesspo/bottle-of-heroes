// v10.312 — a „Mit választanál?" kérdésbank
//
// A lista 15-ről 100-ra nőtt. A játék `gameIdx % hossz` szerint lapoz, tehát
// 15 kérdésnél egy hosszabb esten belül ismétlődött — ezért a DARABSZÁM maga is
// ellenőrzött érték, nem csak a mezők megléte.
//
// Böngésző nélkül fut: a tömb sima objektum-literál, a forrásból kiolvasva
// kiértékelhető. Így a teljes bank átnézése másodperc, nem perc.
const fs = require('fs');
const path = require('path');
const SRC = path.join(__dirname, '..', 'app.src.html');

let fail = 0;
const ok = (label, cond, extra) => {
  console.log((cond ? '  OK   ' : '  HIBA ') + label + (extra !== undefined ? '  → ' + extra : ''));
  if (!cond) fail++;
};

const src = fs.readFileSync(SRC, 'utf8');
const m = src.match(/const MIT_VALASZTANAL = \[([\s\S]*?)\n\];/);
if (!m) { console.error('CRASH: nem találom a MIT_VALASZTANAL tömböt'); process.exit(1); }
const Q = eval('[' + m[1] + ']');

console.log('\n===== A KÉRDÉSBANK =====');
ok('pontosan 100 kérdés', Q.length === 100, Q.length + ' db');

const hianyos = Q.filter(q => !q.a || !q.b || typeof q.statsA !== 'number');
ok('mindegyiknek van A, B és statsA mezője', hianyos.length === 0,
   hianyos.length ? hianyos.map(q => q.a || '(nincs A)').join(' · ') : '—');

console.log('\n===== A KÉT EMOJI =====');
// A kör-jelvény emojija a lap fő megkülönböztetője. Fél párral az egyik
// oldalon a betű (A/B) jelenne meg jelvényként, a másikon kép — a két lap
// elcsúszna. Ezért MINDKÉT oldalra kell jel.
const felPar = Q.filter(q => !q.ea || !q.eb);
ok('mindkét oldalon van emoji', felPar.length === 0,
   felPar.length ? felPar.map(q => q.a).join(' · ') : '—');

const azonos = Q.filter(q => q.ea && q.ea === q.eb);
ok('a páron belül a két emoji különbözik', azonos.length === 0,
   azonos.length ? azonos.map(q => q.a + ' / ' + q.b).join(' · ') : '—');

console.log('\n===== A TÖBBSÉGI OLDAL =====');
// A `majorityA = statsA >= 50`, és a felfedés „a többséggel értettél egyet" /
// „kisebbségben voltál" mondattal zár. 50-nél a többség érzésre is döntetlen,
// tehát a mondat állítana valamit, ami nem igaz. 0 és 100 ugyanígy hazudna:
// azt ígérné, hogy SENKI nem választja az egyik oldalt.
const otven = Q.filter(q => q.statsA === 50);
ok('egyik kérdés sem áll pontosan 50-en', otven.length === 0,
   otven.length ? otven.map(q => q.a).join(' · ') : '—');

const tartomany = Q.filter(q => q.statsA < 1 || q.statsA > 99);
ok('minden statsA az 1–99 tartományban van', tartomany.length === 0,
   tartomany.length ? tartomany.map(q => q.a + ':' + q.statsA).join(' · ') : '—');

// Mindkét oldalnak kell nyerő kérdés is: ha minden statsA 50 fölött lenne, a
// „B" választása SOHA nem érne pontot, és a játék egy kör után kiadná magát.
const aTobbseg = Q.filter(q => q.statsA >= 50).length;
ok('mindkét oldal lehet többségi', aTobbseg > 0 && aTobbseg < Q.length,
   aTobbseg + ' kérdésnél az A, ' + (Q.length - aTobbseg) + '-nél a B');

console.log('\n===== ISMÉTLŐDÉS =====');
const parok = Q.map(q => q.a + ' | ' + q.b);
const dup = parok.filter((x, i) => parok.indexOf(x) !== i);
ok('nincs két azonos kérdés', dup.length === 0, dup.join(' · ') || '—');

// Ugyanaz a mondat a másik oldalon is ismétlődés — a játékos ugyanazt a
// dilemmát kapná meg, csak A/B cserével.
const oldalak = Q.flatMap(q => [q.a.trim().toLowerCase(), q.b.trim().toLowerCase()]);
const dupOldal = [...new Set(oldalak.filter((x, i) => oldalak.indexOf(x) !== i))];
ok('nincs két azonos opció-szöveg', dupOldal.length === 0, dupOldal.join(' · ') || '—');

console.log('\n===== HOSSZ =====');
// A kártya 118 px magas, a szöveg a 74 px-es jelvény mellett fut. Kb. 60
// karakter fölött 360 px-es kijelzőn négy sorba törik, és kilóg a lapból.
const hosszu = Q.flatMap(q => [q.a, q.b]).filter(x => x.length > 60);
ok('egyik opció sem hosszabb 60 karakternél', hosszu.length === 0,
   hosszu.length ? hosszu.map(x => x.length + ': ' + x).join(' · ')
                 : 'leghosszabb ' + Math.max(...Q.flatMap(q => [q.a.length, q.b.length])) + ' karakter');

console.log(fail ? '\n❌ ' + fail + ' ELLENORZES BUKOTT' : '\n✅ MINDEN ELLENORZES RENDBEN');
process.exit(fail ? 1 : 0);
