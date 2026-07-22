/**
 * DNR Tippbajnokság — automatikus BL (Bajnokok Ligája) mérkőzés-feltöltő
 * (Google Apps Script; a meglévő "DNR Tipp mail" projekthez add hozzá új fájlként)
 *
 * Mit csinál naponta:
 *  - Lekéri a ±néhány napos BL-meccseket a football-data.org ingyenes API-jából
 *  - Az ÚJ meccseket hozzáadja a tippbajnoksághoz (kezdési idő + kieséses jelölés)
 *  - A BEFEJEZETT meccseknél beírja a végeredményt → a pontok maguktól számolódnak
 *  - A kézzel felvett meccseket és a már beírt eredményeket NEM bántja
 *
 * ── EGYSZERI BEÁLLÍTÁS ──
 * 1) Ingyenes API-token: menj a https://www.football-data.org/client/register oldalra,
 *    regisztrálj, és másold ki a kapott API tokent. Illeszd be lent a FD_TOKEN-be.
 * 2) Illeszd be ezt a fájlt a meglévő Apps Script projektbe (Fájl → + → Szkript, pl. "fixtures").
 * 3) Mentés (Ctrl+S).
 * 4) Futtasd le egyszer kézzel: fent a függvény-legördülőnél válaszd a `fillClFixtures`-t,
 *    majd „Futtatás". Engedélyezd a hozzáférést (Speciális → Ugrás… → Engedélyezés).
 *    Ellenőrizd az appban: Tipp bajnokság → megjelentek a meccsek.
 * 5) Napi automatika: bal oldalt az órák ikon (Aktivátorok / Triggers) → „Aktivátor hozzáadása":
 *      - Futtatandó függvény: fillClFixtures
 *      - Esemény forrása: Idő szerint
 *      - Idő alapú aktivátor: Napi időzítő
 *      - Napszak: pl. 06:00–07:00
 *    → Mentés. Ettől kezdve minden nap magától frissül.
 */

// ── BEÁLLÍTÁSOK ──
var FD_TOKEN     = 'IDE_ILLESZD_A_FOOTBALL_DATA_TOKENT';
var COMPETITION  = 'CL';                 // Bajnokok Ligája. (Pl. 'EC' = Eb, 'WC' = Vb, 'PL' = Premier League)
var PAST_DAYS    = 2;                    // ennyi napra visszamenőleg tölti a végeredményeket
var AHEAD_DAYS   = 3;                    // ennyi napra előre veszi fel a meccseket
var TIMEZONE     = 'Europe/Budapest';    // a kezdési időt ebben az időzónában írja
var FIRESTORE_PROJECT = 'bottle-of-heroes';
var FIRESTORE_KEY     = 'AIzaSyCH6yb3vQOLqw5eeZR566qf7KJ-JMwAQiY';

function fillClFixtures() {
  var today = new Date();
  var from = new Date(today.getTime() - PAST_DAYS * 864e5);
  var to   = new Date(today.getTime() + AHEAD_DAYS * 864e5);
  var d = function (x) { return Utilities.formatDate(x, 'GMT', 'yyyy-MM-dd'); };

  // 1) Meccsek lekérése
  var url = 'https://api.football-data.org/v4/competitions/' + COMPETITION +
            '/matches?dateFrom=' + d(from) + '&dateTo=' + d(to);
  var res = UrlFetchApp.fetch(url, { headers: { 'X-Auth-Token': FD_TOKEN }, muteHttpExceptions: true });
  if (res.getResponseCode() !== 200) {
    Logger.log('football-data hiba: ' + res.getResponseCode() + ' ' + res.getContentText());
    return;
  }
  var api = JSON.parse(res.getContentText());
  var apiMatches = api.matches || [];

  // 2) Jelenlegi config beolvasása
  var docUrl = 'https://firestore.googleapis.com/v1/projects/' + FIRESTORE_PROJECT +
               '/databases/(default)/documents/config/bingoConfig?key=' + FIRESTORE_KEY;
  var getRes = UrlFetchApp.fetch(docUrl, { muteHttpExceptions: true });
  var exists = getRes.getResponseCode() === 200;
  var doc = exists ? JSON.parse(getRes.getContentText()) : { fields: {} };
  var existing = fsDecodeArray((doc.fields || {}).matches);

  // meglévők id szerint
  var byId = {};
  existing.forEach(function (m) { if (m && m.id) byId[m.id] = m; });

  // 3) API meccsek beolvasztása
  apiMatches.forEach(function (f) {
    var id = 'cl_' + f.id;
    var home = (f.homeTeam && (f.homeTeam.shortName || f.homeTeam.name)) || 'TBD';
    var away = (f.awayTeam && (f.awayTeam.shortName || f.awayTeam.name)) || 'TBD';
    var kickoff = f.utcDate ? Utilities.formatDate(new Date(f.utcDate), TIMEZONE, "yyyy-MM-dd'T'HH:mm") : '';
    var stage = f.stage || '';
    var knockout = (stage !== 'GROUP_STAGE' && stage !== 'LEAGUE_STAGE' && stage !== '');
    var finished = f.status === 'FINISHED';
    var ft = (f.score && f.score.fullTime) || {};

    var prev = byId[id] || {};
    var hs = prev.hs != null ? prev.hs : null;
    var as = prev.as != null ? prev.as : null;
    if (finished && ft.home != null && ft.away != null) { hs = ft.home; as = ft.away; } // hivatalos végeredmény

    byId[id] = {
      id: id,
      home: (home || '').substring(0, 24),
      away: (away || '').substring(0, 24),
      kickoff: kickoff || prev.kickoff || '',
      knockout: !!knockout,
      hs: hs,
      as: as
    };
  });

  // 4) Rendezés kezdési idő szerint
  var merged = Object.keys(byId).map(function (k) { return byId[k]; })
    .sort(function (a, b) { return (a.kickoff || '').localeCompare(b.kickoff || ''); });

  // 5) Visszaírás — csak a matches mezőt (a többi beállítás érintetlen);
  //    ha a doksi még nem létezik, létrehozzuk értelmes alapokkal.
  var fields = { matches: fsEncode(merged) };
  var maskFields = ['matches'];
  if (!exists) {
    fields.enabled = fsEncode(true);
    fields.mode = fsEncode('tipp');
    fields.tippTitle = fsEncode('BL Tippbajnokság');
    maskFields.push('enabled', 'mode', 'tippTitle');
  }
  var mask = maskFields.map(function (f) { return 'updateMask.fieldPaths=' + f; }).join('&');
  var patchUrl = docUrl.replace('?key=', '?' + mask + '&key=');
  var patchRes = UrlFetchApp.fetch(patchUrl, {
    method: 'patch',
    contentType: 'application/json',
    payload: JSON.stringify({ fields: fields }),
    muteHttpExceptions: true
  });
  Logger.log('Firestore PATCH: ' + patchRes.getResponseCode() + ' | meccsek: ' + merged.length +
             ' (' + apiMatches.length + ' az API-ból)');
}

// ── Firestore REST kódolás/dekódolás ──
function fsEncode(v) {
  if (v === null || v === undefined) return { nullValue: null };
  if (typeof v === 'boolean') return { booleanValue: v };
  if (typeof v === 'number') return Number.isInteger(v) ? { integerValue: String(v) } : { doubleValue: v };
  if (typeof v === 'string') return { stringValue: v };
  if (Array.isArray(v)) return { arrayValue: { values: v.map(fsEncode) } };
  if (typeof v === 'object') {
    var f = {};
    Object.keys(v).forEach(function (k) { f[k] = fsEncode(v[k]); });
    return { mapValue: { fields: f } };
  }
  return { stringValue: String(v) };
}
function fsDecode(val) {
  if (!val) return null;
  if ('nullValue' in val) return null;
  if ('booleanValue' in val) return val.booleanValue;
  if ('integerValue' in val) return parseInt(val.integerValue, 10);
  if ('doubleValue' in val) return val.doubleValue;
  if ('stringValue' in val) return val.stringValue;
  if ('arrayValue' in val) return ((val.arrayValue && val.arrayValue.values) || []).map(fsDecode);
  if ('mapValue' in val) {
    var o = {}, f = (val.mapValue && val.mapValue.fields) || {};
    Object.keys(f).forEach(function (k) { o[k] = fsDecode(f[k]); });
    return o;
  }
  return null;
}
function fsDecodeArray(val) {
  var a = fsDecode(val);
  return Array.isArray(a) ? a : [];
}
