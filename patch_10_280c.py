#!/usr/bin/env python3
# v10.280c — a megjelolt sor lathatoan is megjelolt legyen
#
# A `T.coral + '16'` (~9% alfa) a barack/meleg temak hattere folott gyakorlatilag
# eltunt: a megjelolt sor ugyanugy nezett ki, mint a tobbi. A visszajelzest csak
# a szam szine es a letiltott `+` adta.
#
# A `T.coralSoft` TEMA-TOKEN, mind a 8 temaban definialva (a sotet temakban
# sotet ertekkel: #301412, #3C1028, #3D1A1A), tehat mindenhol lathato marad,
# es nem kell alfat talalgatni a hatterhez.
#
# A kozos soron keresztul ez a Buntetes-modalra is vonatkozik — ott is hasznos:
# egy pillantasra latszik, kire kerult korty.
import sys

P = 'app.src.html'
src = open(P, encoding='utf-8').read()

def sub(old, new, what):
    global src
    assert src.count(old) == 1, '%s: %d talalat' % (what, src.count(old))
    src = src.replace(old, new, 1)

sub("""                  background: on ? T.coral + '16' : T.surfaceMuted, borderRadius:14, transition:'background .15s' }}>""",
    """                  /* coralSoft, nem alfás coral: a ~9%-os coral a meleg temak
                     hatteren eltunt. A token mind a 8 temaban hangolva van. */
                  background: on ? T.coralSoft : T.surfaceMuted, borderRadius:14, transition:'background .15s' }}>""",
    'kijeloles szine')

open(P, 'w', encoding='utf-8').write(src)
print('OK')
