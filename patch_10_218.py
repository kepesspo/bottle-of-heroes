#!/usr/bin/env python3
# v10.218 — "Hiba bejelentése" atkerul a MENU aljarol a jatek info-modaljaba
#
# Eddig a MENU > Vezerles ful aljan (Kilepes alatt) allt, elszigetelten a
# jatektol amirol szo van. A GameInfoModal (az "i" infogomb tartalma — mind
# a Jatekok listajan, mind a jatek kozbeni fejlecben ugyanez a komponens
# nyilik) mar amugy is a jatek leirasat mutatja, es a BugReportSheet
# placeholdere is arra kerdez, "melyik jatekban" tortent a hiba — logikusabb
# hely a leiras ala tenni, mint egy elszigetelt sor a menu aljan.
import sys

P = 'app.src.html'
src = open(P, encoding='utf-8').read()

def sub(old, new, what):
    global src
    assert src.count(old) == 1, '%s: %d talalat' % (what, src.count(old))
    src = src.replace(old, new, 1)

# ─── 1) ki a MENU aljarol ───
sub("""                  <BohIcon name="exit" size={17} /><span>{t('leave')}</span>
                </button>
                <BugReportEntry T={T} variant="text" />
              </div>{/* end vezérlés */}""",
    """                  <BohIcon name="exit" size={17} /><span>{t('leave')}</span>
                </button>
              </div>{/* end vezérlés */}""",
    'BugReportEntry ki a menubol')

# ─── 2) be a GameInfoModal-ba, a leiras + "Ertem" gomb ala ───
sub("""        {/* Description */}
        <div style={{ padding:'14px 22px calc(22px + env(safe-area-inset-bottom, 0px))' }}>
          <div style={{ fontFamily:T.font, fontSize:14.5, lineHeight:1.75, color:T.ink, fontWeight:500, whiteSpace:'pre-line', marginBottom:18, opacity:0.82 }}>{tg(game,'desc')}</div>
          <PrimaryButton onClick={onClose} big={false}>{'Értem'}</PrimaryButton>
        </div>""",
    """        {/* Description */}
        <div style={{ padding:'14px 22px calc(22px + env(safe-area-inset-bottom, 0px))' }}>
          <div style={{ fontFamily:T.font, fontSize:14.5, lineHeight:1.75, color:T.ink, fontWeight:500, whiteSpace:'pre-line', marginBottom:18, opacity:0.82 }}>{tg(game,'desc')}</div>
          <PrimaryButton onClick={onClose} big={false}>{'Értem'}</PrimaryButton>
          <BugReportEntry T={T} variant="text" />
        </div>""",
    'BugReportEntry be a GameInfoModal-ba')

sub("const APP_VERSION = 'v10.217';", "const APP_VERSION = 'v10.218';", 'verzio')
open(P, 'w', encoding='utf-8').write(src)
print('OK — Hiba bejelentese a jatek-info modalba kerult')
