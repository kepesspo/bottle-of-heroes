# v10.179 — a kabala (Bottle Hero) kivezetese az appbol
#
# 14 megjelenesi hely + a 173 soros beagyazott SVG komponens + a kizarolag hozza
# tartozo CSS. Ahol a kabala volt a doboz vagy a feltetel EGYETLEN tartalma, ott
# az is megy — kulonben ures kifejezes marad, ami nem is fordul le.
#
# Ami MARAD:
#   floatBob   — mas is hasznalja (emoji-diszek a Statisztikan es az observeren)
#   bhConfFall — a nev megteveszto, de ez az eredmeny-modal konfettije
#
# Minden vagas SZO SZERINTI egyezessel megy, sorszam- vagy zarojel-kereses
# nelkul: az elso probalkozasnal egy "az elso }> -ig vagunk" logika atszaladt a
# kovetkezo modalba, es a kozbeeso markupot is elvitte.
import io

P = 'app.src.html'
s = io.open(P, encoding='utf-8').read()
orig = s

def cut(old, new, why):
    global s
    n = s.count(old)
    assert n == 1, '%s: %d talalat (1 kellene)' % (why, n)
    s = s.replace(old, new)

CUTS = [
    # ── ures allapotok / varakozo kepernyok ──
    ("""                  <div style={{ marginBottom:8, display:'flex', justifyContent:'center' }}><BottleHero pose="wait" size={64} /></div>\n""",
     '', 'statisztika ures allapot'),
    ("""        <div style={{ animation:'floatBob 2.4s ease-in-out infinite' }}><BottleHero pose="wait" size={92} /></div>\n        <div style={{ fontFamily:T.font, fontSize:15, color:T.inkSoft }}>Várakozás a házigazdára…</div>""",
     """        <div style={{ fontFamily:T.font, fontSize:15, color:T.inkSoft }}>Várakozás a házigazdára…</div>""",
     'varakozas a hazigazdara'),
    ("""        <div style={{ animation:'floatBob 2.4s ease-in-out infinite' }}><BottleHero pose="wave" size={92} /></div>\n""",
     '', 'Busz lobby'),
    ("""        <div style={{ animation:'floatBob 2.4s ease-in-out infinite' }}><BottleHero pose="wait" size={92} /></div>\n""",
     '', 'Busz varakozo'),
    # ── cimsor melletti kabala: marad a felirat ──
    ("""          <BottleHero pose="deal" size={38} style={{ flexShrink:0 }} />\n""",
     '', 'cimsor'),
    # ── Bingo unneples ──
    ("""            <BottleHero pose="win" size={72} style={{ animation:'floatBob 2.6s ease-in-out infinite' }} />\n""",
     '', 'Bingo unneples'),
    # ── eredmeny-matricak: a kabala volt a wrapper egyetlen tartalma ──
    ("""              {/* Bottle Hero — bal felső sarok matrica, pop-in + lebegés */}
              <div style={{ position:'absolute', top:6, left:8, zIndex:4, pointerEvents:'none', animation:'heroPopIn .55s .15s cubic-bezier(.2,.9,.3,1.35) both' }}>
                <BottleHero pose={isDraw ? 'wait' : (neutral ? (neutralPos?'win':'drink') : (hasWin?'win':'drink'))} size={54} style={{ filter:'drop-shadow(0 4px 10px rgba(0,0,0,0.28))', animation:'floatBob 2.6s .9s ease-in-out infinite' }} />
              </div>
              {split && (
                <div style={{ position:'absolute', bottom:30, right:8, zIndex:4, pointerEvents:'none', animation:'heroPopIn .55s .3s cubic-bezier(.2,.9,.3,1.35) both' }}>
                  <BottleHero pose="drink" size={54} style={{ filter:'drop-shadow(0 4px 10px rgba(0,0,0,0.28))', animation:'floatBob 2.6s 1.2s ease-in-out infinite' }} />
                </div>
              )}
""", '', 'eredmeny-matricak (a {split && (...)} is, mert az is csak ezt tartalmazta)'),
    # ── dobogo-matrica ──
    ("""          {/* Bottle Hero ünnepel a dobogó mellett */}
          <div style={{ position:'absolute', right:-2, top:-6, pointerEvents:'none', zIndex:3, animation:'heroPopIn .55s .9s cubic-bezier(.2,.9,.3,1.35) both' }}>
            <BottleHero pose="win" size={52} style={{ filter:'drop-shadow(0 4px 10px rgba(0,0,0,0.18))', animation:'floatBob 2.6s 1.6s ease-in-out infinite' }} />
          </div>
""", '', 'dobogo-matrica'),
    # ── poharkoszonto modal ikonja: SZO SZERINT, a teljes prop ──
    (""" icon={<BottleHero pose="win" size={68} style={{ filter:'drop-shadow(0 4px 10px rgba(0,0,0,0.18))', animation:'floatBob 2.6s ease-in-out infinite' }} />}""",
     '', 'poharkoszonto modal ikon'),
    # ── onboarding: az elso lepesnek nem volt ikonja (icon:null), ezert allt ott
    #    a kabala. Most o is a tobbi lepes ikon-dobozat kapja. ──
    ("""          {step === 0
            ? <div style={{ display:'flex', justifyContent:'center', marginBottom:14 }}><BottleHero pose="wave" size={86} /></div>
            : <div style={{ display:'flex', justifyContent:'center', marginBottom:16 }}>
                <div style={{ width:72, height:72, borderRadius:24, background:T.mintSoft, display:'grid', placeItems:'center' }}>
                  <BohIcon name={s.icon} size={38} />
                </div>
              </div>}""",
     """          <div style={{ display:'flex', justifyContent:'center', marginBottom:16 }}>
            <div style={{ width:72, height:72, borderRadius:24, background:T.mintSoft, display:'grid', placeItems:'center' }}>
              <BohIcon name={s.icon || 'cheers'} size={38} />
            </div>
          </div>""",
     'onboarding elso lepes'),
    # ── Busz-modal matricaja ──
    ("""        <div style={{ position:'absolute', top:6, left:8, zIndex:2, pointerEvents:'none', animation:'heroPopIn .55s .15s cubic-bezier(.2,.9,.3,1.35) both' }}>
          <BottleHero pose="drink" size={58} style={{ filter:'drop-shadow(0 4px 12px rgba(0,0,0,0.28))', animation:'floatBob 2.6s .9s ease-in-out infinite' }} />
        </div>
""", '', 'Busz-modal matrica'),
    # ── szoba-hiba kepernyo ──
    ("""              <BottleHero pose="wait" size={92} />\n""", '', 'szoba-hiba kepernyo'),
]
for old, new, why in CUTS:
    cut(old, new, why)

# ── szoba-letrehozas: a repulo palack volt a 150 px-es doboz lenyege.
#    A doboz (a benne lebego buborekokkal egyutt) megy, marad a felirat es a
#    harom toltopont. Sorhataron vagunk, mert a belso sorok hosszuak. ──
lines = s.split('\n')
a = next(i for i, l in enumerate(lines) if "maxWidth:420, height:150" in l)
assert 'BottleHero' in lines[a + 3], lines[a + 3][:80]
# A doboz SAJAT zaro sora: azonos behuzas, mint a nyito. A belso burkolok
# zaroi melyebben vannak — az elso probalkozasnal epp egy olyanra futottam.
indent = len(lines[a]) - len(lines[a].lstrip())
b = next(i for i in range(a + 1, a + 20)
         if lines[i].strip() == '</div>' and (len(lines[i]) - len(lines[i].lstrip())) == indent)
seg = lines[a:b + 1]
assert 'BottleHero' in '\n'.join(seg) and 'bhFlyX' in '\n'.join(seg), seg[0][:60]
assert 'fontWeight:T.weightDisplay' not in '\n'.join(seg), 'tul sokat vagnank'
del lines[a:b + 1]
s = '\n'.join(lines)

# ── a komponens ──
a = s.index('function BottleHero({ pose = ')
b = s.index('\n}\n', a) + len('\n}\n')
seg = s[a:b]
assert seg.count('\nfunction ') == 0 and len(seg) > 4000, len(seg)
s = s[:a] + s[b:]

# ── a kizarolag hozza tartozo CSS ──
a = s.index('    @keyframes heroPopIn {')
b = s.index('\n', s.index('    @keyframes bhFlyX{', a)) + 1
seg = s[a:b]
assert '.bh-eye' in seg and 'bhConfFall' not in seg and 'floatBob' not in seg, seg[:80]
s = s[:a] + s[b:]

assert 'BottleHero' not in s and 'heroPopIn' not in s and 'bhFlyX' not in s and '.bh-' not in s
assert 'floatBob' in s and 'bhConfFall' in s, 'ezeknek maradniuk kell'
assert '&& (\n' not in s.replace('&& (\n  ', ''), 'gyanus ures feltetel'

s = s.replace("const APP_VERSION = 'v10.178';", "const APP_VERSION = 'v10.179';", 1)
assert "v10.179" in s and s != orig
io.open(P, 'w', encoding='utf-8').write(s)
print('OK — kabala kivezetve, %d sorral kevesebb' % (orig.count('\n') - s.count('\n')))
