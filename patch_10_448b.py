# v10.448 (2. rész) — a Leleplezés fül gombjai is a fix alsó DOKKBA kerülnek, a fül-sáv
# fölé (a görgő terület alja iOS PWA-ban nem megbízható — a gyökér magassága változó).
P = 'app.src.html'
s = open(P, encoding='utf-8').read()
def rep(old, new, cnt=1):
    global s
    n = s.count(old); assert n == cnt, (n, old[:120]); s = s.replace(old, new)

# a dokk: felső „rés" (slot) a fül saját gombjainak + a fül-sáv
rep("""function RevealParentTabs({ tab, onTab }) {
  return ReactDOM.createPortal(
    <nav aria-label="Szülők fülek" data-reveal-ptabs style={{ position:'fixed', left:0, right:0, bottom:'calc(-1 * env(safe-area-inset-bottom) - 80px)', zIndex:60,
      display:'grid', gridTemplateColumns:'repeat(4, minmax(0, 1fr))', background:T.surface, boxShadow:'0 -4px 18px rgba(20,30,50,0.08)',
      borderTopLeftRadius:20, borderTopRightRadius:20, padding:'4px 6px calc(env(safe-area-inset-bottom) + 108px)', boxSizing:'border-box' }}>""",
"""// A dokk felső része (`dockRef` → slot) a fülök SAJÁT alsó gombjainak helye (a Leleplezés
// fül oda portáloz). z-index 6600: a modalok (9998) és a kérdés-szerkesztő lap (7000) alatt.
function RevealParentTabs({ tab, onTab, dockRef }) {
  return ReactDOM.createPortal(
    <div data-reveal-pdock style={{ position:'fixed', left:0, right:0, bottom:'calc(-1 * env(safe-area-inset-bottom) - 80px)', zIndex:6600,
      background:T.surface, boxShadow:'0 -4px 18px rgba(20,30,50,0.10)', borderTopLeftRadius:20, borderTopRightRadius:20,
      padding:'0 0 calc(env(safe-area-inset-bottom) + 108px)', boxSizing:'border-box' }}>
    <div ref={dockRef} data-reveal-pdockslot />
    <nav aria-label="Szülők fülek" data-reveal-ptabs style={{ display:'grid', gridTemplateColumns:'repeat(4, minmax(0, 1fr))', padding:'4px 6px 0', maxWidth:560, margin:'0 auto' }}>""")
rep("""          <span style={{ width:52, height:30, borderRadius:999, display:'grid', placeItems:'center', background: on ? (T.mintSoft || T.bgSoft) : 'transparent' }}>{rvIcon(ic, 20)}</span>{label}</button>); })}
    </nav>, document.body
  );
}""", """          <span style={{ width:52, height:30, borderRadius:999, display:'grid', placeItems:'center', background: on ? (T.mintSoft || T.bgSoft) : 'transparent' }}>{rvIcon(ic, 20)}</span>{label}</button>); })}
    </nav>
    </div>, document.body
  );
}""")
# a Leleplezés fül: a gombok a dokkba
rep("function RevealParentRevealTab() {", "function RevealParentRevealTab({ dock }) {")
rep("""      <div style={{ flex:1, minHeight:4 }} />
      <div data-reveal-firepanel data-armed={armed ? '1' : '0'} style={{ display:'flex', flexDirection:'column', gap:8, flexShrink:0 }}>""",
    """      {(() => { const actions = (
      <div data-reveal-firepanel data-armed={armed ? '1' : '0'} style={{ display:'flex', flexDirection:'column', gap:8, padding:'12px 16px 6px', maxWidth:520, margin:'0 auto', boxSizing:'border-box', borderBottom:`1px solid ${T.border}` }}>""")
rep("""        {msg && <div data-reveal-firemsg role="status" style={{ textAlign:'center', fontFamily:T.font, fontWeight:800, fontSize:13, color:'#1F6B50' }}>{msg}</div>}
      </div>
      {ask && (""", """        {msg && <div data-reveal-firemsg role="status" style={{ textAlign:'center', fontFamily:T.font, fontWeight:800, fontSize:13, color:'#1F6B50' }}>{msg}</div>}
      </div>);
      return dock ? ReactDOM.createPortal(actions, dock) : actions; })()}
      {ask && (""")
# a Szülők képernyő: dokk-állapot, és a görgő terület alja a dokk magasságával
rep("""  const [tab, setTab] = React.useState('reveal');
  const sec = secret.v || {};
  const tryCode""", """  const [tab, setTab] = React.useState('reveal');
  const [dock, setDock] = React.useState(null);
  const sec = secret.v || {};
  const tryCode""")
rep("""padding:'2px 16px calc(env(safe-area-inset-bottom) + 100px)', boxSizing:'border-box', WebkitOverflowScrolling:'touch' }}>""",
    """padding:`2px 16px calc(env(safe-area-inset-bottom) + ${tab === 'reveal' ? 220 : 100}px)`, boxSizing:'border-box', WebkitOverflowScrolling:'touch' }}>""")
rep("""          {tab === 'reveal' && <RevealParentRevealTab />}""", """          {tab === 'reveal' && <RevealParentRevealTab dock={dock} />}""")
rep("""      <RevealParentTabs tab={tab} onTab={setTab} />""", """      <RevealParentTabs tab={tab} onTab={setTab} dockRef={setDock} />""")
open(P, 'w', encoding='utf-8').write(s); print('ok')
