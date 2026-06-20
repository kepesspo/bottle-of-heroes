#!/usr/bin/env python3
"""v9.350 — InstallModal redesign: matches app design language"""

with open('index.html', 'r', encoding='utf-8') as f:
    html = f.read()

old_modal = '''function InstallModal({ onClose }) {
  const isIOS = /iPad|iPhone|iPod/.test(navigator.userAgent) && !window.MSStream;
  const hasNativePrompt = !!window._deferredInstallPrompt;

  const triggerInstall = async () => {
    const prompt = window._deferredInstallPrompt;
    if (!prompt) return;
    prompt.prompt();
    const { outcome } = await prompt.userChoice;
    window._deferredInstallPrompt = null;
    if (outcome === 'accepted') onClose();
  };

  const iosSteps = [
    { icon:'🌐', html:t('iosStep1') },
    { icon:'⬆️', html:t('iosStep2') },
    { icon:'➕', html:t('iosStep3') },
    { icon:'✅', html:t('iosStep4') },
  ];
  const androidSteps = [
    { icon:'⋮', html:t('androidStep1') },
    { icon:'➕', html:t('androidStep2') },
    { icon:'✅', html:t('androidStep3') },
  ];

  return (
    <SheetOverlay onClose={onClose}>
      <div style={{ padding:'4px 20px 32px', display:'flex', flexDirection:'column', gap:18 }}>
        <div style={{ textAlign:'center' }}>
          <div style={{ fontSize:44 }}>📲</div>
          <div style={{ fontFamily:T.font, fontWeight:T.weightDisplay, fontSize:22, color:T.ink, textTransform:'uppercase', letterSpacing:T.letterDisplay, marginTop:6 }}>{t('installTitle')}</div>
          <div style={{ fontFamily:T.font, fontSize:13, color:T.inkSoft, marginTop:4 }}>{t('installSubtitle')}</div>
        </div>

        {hasNativePrompt && (
          <div style={{ display:'flex', flexDirection:'column', gap:10 }}>
            <div style={{ padding:'14px 16px', background:T.surfaceMuted, borderRadius:14, fontFamily:T.font, fontSize:14, color:T.inkSoft, lineHeight:1.6, textAlign:'center' }}>
              {t('installBrowserPrompt')}
            </div>
            <PrimaryButton onClick={triggerInstall}>{t('installNow')}</PrimaryButton>
          </div>
        )}

        {!hasNativePrompt && (
          <div style={{ display:'flex', flexDirection:'column', gap:8 }}>
            {(isIOS ? iosSteps : androidSteps).map((s, i) => (
              <div key={i} style={{ display:'flex', alignItems:'flex-start', gap:14, padding:'12px 14px', background:T.surfaceMuted, borderRadius:14 }}>
                <div style={{ fontSize:22, flexShrink:0, lineHeight:1.4 }}>{s.icon}</div>
                <div style={{ fontFamily:T.font, fontSize:14, color:T.ink, lineHeight:1.55 }} dangerouslySetInnerHTML={{ __html: s.html }} />
              </div>
            ))}
          </div>
        )}

        <button onClick={onClose} style={{ width:'100%', padding:'14px', background:T.surfaceMuted, color:T.inkSoft, border:'none', borderRadius:16, fontFamily:T.font, fontWeight:700, fontSize:15, cursor:'pointer' }}>Bezárás</button>
      </div>
    </SheetOverlay>
  );
}'''

new_modal = '''function InstallModal({ onClose }) {
  const isIOS = /iPad|iPhone|iPod/.test(navigator.userAgent) && !window.MSStream;
  const hasNativePrompt = !!window._deferredInstallPrompt;

  const triggerInstall = async () => {
    const prompt = window._deferredInstallPrompt;
    if (!prompt) return;
    prompt.prompt();
    const { outcome } = await prompt.userChoice;
    window._deferredInstallPrompt = null;
    if (outcome === 'accepted') onClose();
  };

  const iosSteps = [
    { html:t('iosStep1') },
    { html:t('iosStep2') },
    { html:t('iosStep3') },
    { html:t('iosStep4') },
  ];
  const androidSteps = [
    { html:t('androidStep1') },
    { html:t('androidStep2') },
    { html:t('androidStep3') },
  ];

  const steps = isIOS ? iosSteps : androidSteps;

  return (
    <SheetOverlay onClose={onClose}>
      <div style={{ padding:'8px 20px 32px', display:'flex', flexDirection:'column', gap:20 }}>

        {/* Header */}
        <div style={{ display:'flex', flexDirection:'column', alignItems:'center', gap:12, paddingTop:4 }}>
          <div style={{ width:64, height:64, borderRadius:18, background:`linear-gradient(135deg, ${T.mint} 0%, ${T.mintDeep} 100%)`, display:'grid', placeItems:'center', boxShadow:`0 4px 0 ${T.mintDeep}, 0 8px 24px ${T.mint}44` }}>
            <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="#fff" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M12 3v13M8 12l4 4 4-4"/><rect x="3" y="18" width="18" height="3" rx="1.5" fill="#fff" stroke="none"/></svg>
          </div>
          <div style={{ textAlign:'center' }}>
            <div style={{ fontFamily:T.font, fontWeight:T.weightDisplay, fontSize:24, color:T.ink, letterSpacing:T.letterDisplay, lineHeight:1.1 }}>{t('installTitle')}</div>
            <div style={{ fontFamily:T.font, fontSize:13, color:T.inkSoft, marginTop:6, lineHeight:1.5 }}>{t('installSubtitle')}</div>
          </div>
        </div>

        {/* Native prompt */}
        {hasNativePrompt && (
          <div style={{ display:'flex', flexDirection:'column', gap:10 }}>
            <div style={{ padding:'14px 16px', background:T.surfaceMuted, borderRadius:16, fontFamily:T.font, fontSize:14, color:T.inkSoft, lineHeight:1.6, textAlign:'center' }}>
              {t('installBrowserPrompt')}
            </div>
            <PrimaryButton onClick={triggerInstall}>{t('installNow')}</PrimaryButton>
          </div>
        )}

        {/* Manual steps */}
        {!hasNativePrompt && (
          <div style={{ display:'flex', flexDirection:'column', gap:10 }}>
            {steps.map((s, i) => (
              <div key={i} style={{ display:'flex', alignItems:'center', gap:14, padding:'14px 16px', background:T.surfaceMuted, borderRadius:16, boxShadow:T.shadow }}>
                <div style={{ width:32, height:32, borderRadius:10, background:T.mint, display:'grid', placeItems:'center', flexShrink:0, boxShadow:`0 2px 0 ${T.mintDeep}` }}>
                  <span style={{ fontFamily:T.font, fontWeight:900, fontSize:15, color:'#fff', lineHeight:1 }}>{i+1}</span>
                </div>
                <div style={{ fontFamily:T.font, fontSize:14, color:T.ink, lineHeight:1.55, flex:1 }} dangerouslySetInnerHTML={{ __html: s.html }} />
              </div>
            ))}
          </div>
        )}

        {/* Close */}
        <button onClick={onClose} style={{ width:'100%', padding:'15px', background:T.surfaceMuted, color:T.inkSoft, border:'none', borderRadius:18, fontFamily:T.font, fontWeight:700, fontSize:15, cursor:'pointer' }}>Bezárás</button>
      </div>
    </SheetOverlay>
  );
}'''

assert old_modal in html, "FAIL: InstallModal"
html = html.replace(old_modal, new_modal, 1)

html = html.replace("const APP_VERSION = 'v9.349';", "const APP_VERSION = 'v9.350';")

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(html)

print("Done: v9.350 — InstallModal redesigned to match app style")
