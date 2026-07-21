/**
 * DNR Tippbajnokság — e-mail kód küldő (Google Apps Script webapp)
 *
 * Ez a script fogadja az appból érkező kéréseket, és a saját (DNR) Gmail-fiókodból
 * kiküldi a játékosnak a személyes tipp-kódját.
 *
 * ── TELEPÍTÉS (egyszer, a dnrgroupbp@gmail.com fiókkal bejelentkezve) ──
 * 1. Nyisd meg: https://script.google.com  →  „Új projekt”
 * 2. Töröld a mintakódot, másold be EZT a teljes fájlt, mentsd (Ctrl+S).
 * 3. Jobb fent: „Telepítés” → „Új telepítés”.
 * 4. A fogaskerék (Típus kiválasztása) → „Webalkalmazás”.
 * 5. Beállítások:
 *      - Leírás: DNR Tipp mail
 *      - Végrehajtás mint: Én (dnrgroupbp@gmail.com)
 *      - Hozzáféréssel rendelkezik: Bárki
 * 6. „Telepítés” → engedélyezd a hozzáférést (Speciális → Ugrás a projektre → Engedélyezés).
 * 7. Másold ki a „Webalkalmazás URL”-t (…/exec végű) és illeszd be az appban:
 *    Admin → Bingó fül → Tipp bajnokság → E-mailes kódvédelem BE → „E-mail küldő URL” mező.
 *
 * Ha később módosítod a kódot: „Telepítés” → „Telepítések kezelése” → ceruza →
 * Verzió: „Új verzió” → Telepítés (az URL ugyanaz marad).
 */

function doPost(e) {
  try {
    var d = JSON.parse(e.postData.contents);
    var to    = (d.to || '').trim();
    var name  = (d.name || '').trim();
    var code  = (d.code || '').trim();
    var title = (d.title || 'Tippbajnokság').trim();

    if (!to || !code) {
      return _json({ ok: false, error: 'missing to/code' });
    }

    var subject = title + ' — a személyes tipp-kódod';
    var greeting = name ? ('Szia ' + name + '!') : 'Szia!';

    var html =
      '<div style="font-family:Arial,Helvetica,sans-serif;max-width:460px;margin:0 auto;color:#1A2A4A">' +
        '<div style="background:#2FA35F;color:#fff;border-radius:16px 16px 0 0;padding:20px 24px">' +
          '<div style="font-size:13px;letter-spacing:.12em;text-transform:uppercase;opacity:.85">DNR Games</div>' +
          '<div style="font-size:22px;font-weight:900;margin-top:2px">' + _esc(title) + ' 🎯</div>' +
        '</div>' +
        '<div style="background:#F7F7F4;border-radius:0 0 16px 16px;padding:24px">' +
          '<p style="font-size:15px;margin:0 0 14px">' + _esc(greeting) + '</p>' +
          '<p style="font-size:14px;margin:0 0 10px">A tippjeidet ezzel a személyes kóddal tudod szerkeszteni az appban:</p>' +
          '<div style="text-align:center;margin:18px 0">' +
            '<span style="display:inline-block;background:#1A2A4A;color:#fff;font-size:30px;font-weight:900;letter-spacing:.28em;padding:14px 26px;border-radius:12px">' + _esc(code) + '</span>' +
          '</div>' +
          '<p style="font-size:13px;color:#5A6478;margin:0 0 4px">A folyamat: nyisd meg a Tippbajnokságot, válaszd ki magad, írd be ezt a kódot — és kész, tippelhetsz!</p>' +
          '<p style="font-size:13px;color:#5A6478;margin:14px 0 0">Jó tippelést! 🍻<br>DNR Games</p>' +
        '</div>' +
      '</div>';

    var plain = greeting + '\n\nA(z) "' + title + '" tippbajnoksághoz a személyes kódod:\n\n    ' +
                code + '\n\nEzzel a kóddal tudod szerkeszteni a tippjeidet az appban.\n\nJó tippelést!\nDNR Games';

    GmailApp.sendEmail(to, subject, plain, { htmlBody: html, name: 'DNR Games' });
    return _json({ ok: true });
  } catch (err) {
    return _json({ ok: false, error: String(err) });
  }
}

// Böngészőből megnyitva egy egyszerű állapot-jelzés
function doGet() {
  return _json({ ok: true, service: 'DNR Tipp mail', ts: new Date().toISOString() });
}

function _json(obj) {
  return ContentService
    .createTextOutput(JSON.stringify(obj))
    .setMimeType(ContentService.MimeType.JSON);
}

function _esc(s) {
  return String(s).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
}
