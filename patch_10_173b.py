# v10.173 (b) — a kapcsolo az OVFJ beallito lapjan
import io

P = 'app.src.html'
s = io.open(P, encoding='utf-8').read()
orig = s

old = """            })}
          </div>
        </div>
      </div>
    </SheetOverlay>
  );
}

// ═══════════════ ORSZÁG-VÁROS — közös segédek ═══════════════"""
assert s.count(old) == 1
s = s.replace(old, """            })}
          </div>
        </div>
        <div style={{ padding:'13px 0', borderTop:`1px solid ${T.surfaceMuted}`, display:'flex', alignItems:'center', gap:12 }}>
          <div style={{ flex:1, minWidth:0 }}>
            <div style={{ fontFamily:T.font, fontWeight:800, fontSize:15, color: roundTime == null ? T.inkMute : T.ink }}>
              Várjuk meg a kör végét
            </div>
            <div style={{ fontFamily:T.font, fontSize:11, color:T.inkSoft, marginTop:1, lineHeight:1.5 }}>
              {roundTime == null
                ? 'Idő nélküli körnél nem választható — ilyenkor a 10 mp az egyetlen, ami lezárja a kört.'
                : (config.waitFullTime
                    ? 'A kör ideje mindig végig lejár, akkor is ha valaki hamarabb végez.'
                    : 'Ha valaki kész, a többieknek 10 mp marad.')}
            </div>
          </div>
          <Toggle on={roundTime != null && !!config.waitFullTime}
            onChange={() => { if (roundTime != null) setConfig(c => ({ ...c, waitFullTime: !c.waitFullTime })); }} />
        </div>
      </div>
    </SheetOverlay>
  );
}

// ═══════════════ ORSZÁG-VÁROS — közös segédek ═══════════════""")

s = s.replace("const APP_VERSION = 'v10.172';", "const APP_VERSION = 'v10.173';", 1)
assert "v10.173" in s and s != orig
io.open(P, 'w', encoding='utf-8').write(s)
print('OK')
