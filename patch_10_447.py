# v10.447 — Gender Reveal: kompakt szerepválasztó (egy képernyő), és a saját fejlécek
# helyett MINDENHOL a DNR AppBar (a jóváhagyó felületen és a kérdés-szerkesztőn is).
P = 'app.src.html'
s = open(P, encoding='utf-8').read()
def rep(old, new, cnt=1):
    global s
    n = s.count(old); assert n == cnt, (n, old[:120]); s = s.replace(old, new)

rep("const APP_VERSION = 'v10.446'", "const APP_VERSION = 'v10.447'")

# ── 1. a szerepválasztó: egy kártya, három sor ──
a = s.index("""          <div data-reveal-roles style={{ width:'100%', maxWidth:860, display:'grid', gridTemplateColumns:'repeat(auto-fit, minmax(240px, 1fr))', gap:14 }}>""")
b = s.index("""        )}
      </div>
    </div>
  );
}

// Admin → Gender Reveal: belépés""", a)
s = s[:a] + r'''          // v10.447: EGY kártya, három sor (ikon · név + rövid leírás · nyíl) — a régi három
          // nagy kártya telefonon nem fért ki, a Szülők lelógott a képernyőről.
          <div data-reveal-roles style={rvCard({ maxWidth:520 })}>
            {[
              { id:'projector', emoji:'📽️', tone:'info', name:'Vetítő', sub:'A laptop a kivetítőn — képek, üzenetek, kvíz és a leleplezés.' },
              { id:'operator', emoji:'📷', tone:'ok', name:'Operátor', sub:'Képek feltöltése, tippek, a vendégek jóváhagyása.' },
              { id:'trigger', emoji:'👶', tone:'pink', name:'Szülők', sub:'Külön kóddal — leleplezés, Babakvíz, minden beállítás.' },
            ].map((r, i) => (
              <button key={r.id} type="button" data-reveal-role={r.id} onClick={() => { if (r.id === 'projector') revealAudio(); setRole(r.id); }}
                style={{ width:'100%', display:'flex', alignItems:'center', gap:14, padding:'14px 14px 14px 16px', border:'none', borderTop: i ? `1px solid ${T.border}` : 'none', background:'transparent', cursor:'pointer', textAlign:'left', boxSizing:'border-box' }}>
                <span aria-hidden="true" style={{ width:48, height:48, flexShrink:0, borderRadius:14, background:RV_TONES[r.tone][0], display:'grid', placeItems:'center', fontSize:26, lineHeight:1 }}>{r.emoji}</span>
                <span style={{ flex:1, minWidth:0, display:'flex', flexDirection:'column', gap:2 }}>
                  <span style={{ fontFamily:T.font, fontWeight:900, fontSize:17, color:T.ink }}>{r.name}</span>
                  <span style={{ fontFamily:T.font, fontWeight:700, fontSize:13, color:T.inkSoft, lineHeight:1.4 }}>{r.sub}</span>
                </span>
                <span style={{ color:T.inkSoft, display:'flex' }}>{rvIcon('chev', 18)}</span>
              </button>
            ))}
          </div>
''' + s[b:]
rep("""        <img src={REVEAL_LOGO} alt="" style={{ width:120, height:120 }} />
        {!cfg.loaded ? (""", """        <img src={REVEAL_LOGO} alt="" style={{ width:104, height:104 }} />
        {!cfg.loaded ? (""")

# ── 2. a jóváhagyó felület: DNR AppBar ──
rep("""      <div style={{ flexShrink:0, display:'flex', alignItems:'center', gap:8, padding:'calc(8px + env(safe-area-inset-top)) 12px 8px', background:T.surface, borderBottom:`1px solid ${T.border}` }}>
        <button type="button" data-reveal-reviewclose aria-label="Bezárás" onClick={onClose} style={rvBtn('ghost', { width:44, height:44, padding:0, color:T.ink })}>{rvIcon('prev', 22)}</button>
        <div style={{ flex:1, fontFamily:T.font, fontWeight:900, fontSize:19, color:T.ink }}>Jóváhagyás</div>
        {rvPill(n + ' vár', 'pink')}
      </div>""", """      <AppBar title="Jóváhagyás" onBack={onClose} right={<span style={{ paddingRight:6 }}>{rvPill(n + ' vár', 'pink')}</span>} />""")

# ── 3. a kérdés-szerkesztő lap: DNR AppBar ──
rep("""          <div style={{ flexShrink:0, display:'flex', alignItems:'center', gap:8, padding:'calc(10px + env(safe-area-inset-top)) 16px 10px', background:T.surface, borderBottom:`1px solid ${T.border}` }}>
            <div style={{ flex:1, fontFamily:T.font, fontWeight:900, fontSize:18, color:T.ink }}>Babakvíz kérdései</div>
            <button type="button" onClick={() => setEditOpen(false)} style={rvBtn('small')}>Kész</button>
          </div>""", """          <AppBar title="Babakvíz kérdései" onBack={() => setEditOpen(false)} />""")
open(P, 'w', encoding='utf-8').write(s); print('ok')
