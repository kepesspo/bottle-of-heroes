# v10.164 — a lapozas iranya
#
# A kepernyok sorrendje adja az iranyt: elore jobbrol, vissza balrol. Ami
# kimarad a listabol, arra az indexOf -1-et ad — az MINDIG kisebb, tehat a
# kepernyo mindig "vissza"-kent, balrol csuszik be.
#
# Igy jott be balrol a Jatekmenet oldal. De nem csak az: a Naplo, a Jukebox,
# az Esemeny-szerkeszto es az Admin is kimaradt a listabol, tehat azok is
# rosszul lapoztak. Az ismeretlen kepernyo mostantol ELORE szamit — ez a
# biztonsagosabb alapertelmezes, ha kesobb uj kepernyo kerul be.
import io

P = 'app.src.html'
s = io.open(P, encoding='utf-8').read()
orig = s

old = """  const order = ['home','stats','bingo','bar','players','games','play','end','observer'];
  const dir = order.indexOf(screen) >= order.indexOf(prev||'home') ? 1 : -1;"""
new = """  // A sorrend adja a lapozas iranyat: elore jobbrol (slideIn), vissza balrol
  // (slideBack). Ami kimarad, arra az indexOf -1-et adna, es a kepernyo mindig
  // balrol jonne — ezert az ismeretlen kepernyo ELORE szamit, nem vissza.
  const order = ['home','stats','bingo','bar','log','jukebox','create','admin',
                 'players','games','setup','play','end','observer'];
  const posOf = (k) => { const i = order.indexOf(k); return i === -1 ? order.length : i; };
  const dir = posOf(screen) >= posOf(prev || 'home') ? 1 : -1;"""
assert s.count(old) == 1
s = s.replace(old, new)

s = s.replace("const APP_VERSION = 'v10.163';", "const APP_VERSION = 'v10.164';", 1)
assert "v10.164" in s and s != orig
io.open(P, 'w', encoding='utf-8').write(s)
print('OK')
