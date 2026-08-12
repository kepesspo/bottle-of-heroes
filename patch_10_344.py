# v10.344 - A profil-statisztika lap tul nagyban jott fel
#
# A bejelentes: „ha a statisztika oldalon ranyomok egy profilra, akkor tul nagyban
# jelenik meg". A kartya a kepernyo tetejetol az aljaig ert.
#
# ⚠️ AZ OK: az `ActionModal` kartyajanak NINCS magassag-korlatja es nincs
# gorgetese. Rovid modalnal (egy mondat + ket gomb) ez sosem latszott, a
# `QuickStatsModal` viszont egy TELJES profil-statisztikat tesz bele (csempek,
# XP-sav, kituntetesek, pont-grafikon, teljesitmeny) — a kartya egyszeruen
# addig nott, amig el nem fogyott a kepernyo.
#
# Ket kovetkezmenye volt, es a masodik a sulyosabb:
#   1. a lap ugy nezett ki, mint egy kepernyo, nem mint egy kartya;
#   2. ami nem fert ki, az LEVAGODOTT — a „TELJESITMENY" blokk alja egyszeruen
#      nem volt elerheto, mert a kartyan nem volt gorgetes.
#
# A javitas a KOZOS `ActionModal`-ban van, tehat minden hosszu modal orokli:
# a kartya legfeljebb 620 px (es sosem magasabb a rendelkezesre allo helynel),
# a FEJ es a GOMBSOR a helyen marad, a tartalom pedig gorgetheto.
import io

P = 'app.src.html'
src = io.open(P, encoding='utf-8').read()
orig = src

def sub1(old, new, what):
    global src
    assert src.count(old) == 1, '%s: %d talalat' % (what, src.count(old))
    src = src.replace(old, new)

# --- a kartya: magassag-korlat + gorgetheto torzs ---------------------------
sub1(
"""      <div onClick={e => e.stopPropagation()} style={{ background:T.surface, borderRadius:28, padding: wide ? '26px 18px 20px' : '26px 24px 22px', width:'100%', maxWidth: wide ? 440 : 360, display:'flex', flexDirection:'column', alignItems:'center', gap:12, boxShadow:'0 24px 64px rgba(0,0,0,0.3)', animation:'popIn .3s cubic-bezier(.2,.9,.3,1.3)' }}>
        {icon}
        {kicker && <div style={{ fontFamily:T.font, fontWeight:900, fontSize:12, color: kickerColor || T.coral, textTransform:'uppercase', letterSpacing:'0.14em' }}>{kicker}</div>}
        <div style={{ width:'100%', fontFamily:T.font, fontWeight:800, fontSize:18, color:T.ink, textAlign:'center', lineHeight:1.38 }}>{children}</div>
        <div style={{ display:'flex', gap:10, width:'100%', marginTop:6 }}>""",
"""      {/* ⚠️ A kartyanak KELL magassag-korlat es gorgetes. Nelkule a hosszu
          tartalom (pl. a profil-statisztika: csempek, XP-sav, kituntetesek,
          grafikon) a kepernyo tetejetol az aljaig nyujtotta a lapot, es ami
          nem fert ki, az LEVAGODOTT — gorgetni sem lehetett hozza.
          A `min(100%, 620px)` ket dolgot ad: sosem lóg tul a rendelkezesre allo
          helyen, es hosszu tartalomnal is KARTYANAK latszik, nem kepernyonek. */}
      <div onClick={e => e.stopPropagation()} style={{ background:T.surface, borderRadius:28, padding: wide ? '26px 18px 20px' : '26px 24px 22px', width:'100%', maxWidth: wide ? 440 : 360, maxHeight:'min(100%, 620px)', boxSizing:'border-box', overflow:'hidden', display:'flex', flexDirection:'column', alignItems:'center', gap:12, boxShadow:'0 24px 64px rgba(0,0,0,0.3)', animation:'popIn .3s cubic-bezier(.2,.9,.3,1.3)' }}>
        {icon && <div style={{ flexShrink:0 }}>{icon}</div>}
        {kicker && <div style={{ flexShrink:0, fontFamily:T.font, fontWeight:900, fontSize:12, color: kickerColor || T.coral, textTransform:'uppercase', letterSpacing:'0.14em' }}>{kicker}</div>}
        {/* `flex:0 1 auto` + `minHeight:0`: rovid modalnal a termeszetes magassag
            marad, es CSAK akkor gorget, ha tenyleg nem fer ki. */}
        <div style={{ width:'100%', flex:'0 1 auto', minHeight:0, overflowY:'auto', WebkitOverflowScrolling:'touch', fontFamily:T.font, fontWeight:800, fontSize:18, color:T.ink, textAlign:'center', lineHeight:1.38 }}>{children}</div>
        <div style={{ flexShrink:0, display:'flex', gap:10, width:'100%', marginTop:6 }}>""",
'ActionModal kartya')

sub1("const APP_VERSION = 'v10.343';", "const APP_VERSION = 'v10.344';", 'verzio')

assert src != orig
io.open(P, 'w', encoding='utf-8').write(src)
print('OK - patch_10_344 alkalmazva')
