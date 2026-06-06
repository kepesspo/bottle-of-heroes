#!/usr/bin/env python3
"""v8.44: Lóverseny — hanghatás javítva (AudioContext resume + erősebb hang)"""

with open('index.html', 'r', encoding='utf-8') as f:
    content = f.read()

OLD_SOUND = """const playRaceSound = () => {
    try {
      const ctx = new (window.AudioContext || window.webkitAudioContext)();
      const dur = 1.8;
      // Crowd cheer: multiple oscillators at varying freqs + white noise burst
      [220,330,440,550,660].forEach((freq, i) => {
        const osc = ctx.createOscillator();
        const gain = ctx.createGain();
        osc.type = 'sawtooth';
        osc.frequency.setValueAtTime(freq + Math.random()*80, ctx.currentTime);
        osc.frequency.exponentialRampToValueAtTime(freq*1.4, ctx.currentTime + dur);
        gain.gain.setValueAtTime(0, ctx.currentTime + i*0.05);
        gain.gain.linearRampToValueAtTime(0.06, ctx.currentTime + i*0.05 + 0.1);
        gain.gain.exponentialRampToValueAtTime(0.001, ctx.currentTime + dur);
        osc.connect(gain); gain.connect(ctx.destination);
        osc.start(ctx.currentTime + i*0.05); osc.stop(ctx.currentTime + dur);
      });
      // Trumpet fanfare: simple melody
      const fanfareNotes = [[659,0],[784,0.15],[880,0.3],[1047,0.45],[880,0.6],[1047,0.75]];
      fanfareNotes.forEach(([freq, t]) => {
        const osc = ctx.createOscillator();
        const gain = ctx.createGain();
        osc.type = 'square';
        osc.frequency.value = freq;
        gain.gain.setValueAtTime(0, ctx.currentTime + t);
        gain.gain.linearRampToValueAtTime(0.12, ctx.currentTime + t + 0.04);
        gain.gain.exponentialRampToValueAtTime(0.001, ctx.currentTime + t + 0.14);
        osc.connect(gain); gain.connect(ctx.destination);
        osc.start(ctx.currentTime + t); osc.stop(ctx.currentTime + t + 0.15);
      });
    } catch(e) {}
  };"""

NEW_SOUND = """const playRaceSound = () => {
    try {
      const ctx = new (window.AudioContext || window.webkitAudioContext)();
      const play = () => {
        const t = ctx.currentTime;
        // Kürtfanfár — erős, tiszta hangok
        const fanfare = [[523,0,0.25],[659,0.25,0.25],[784,0.5,0.25],[1047,0.75,0.5],[784,1.25,0.2],[1047,1.45,0.6]];
        fanfare.forEach(([freq, start, dur]) => {
          const osc = ctx.createOscillator();
          const gain = ctx.createGain();
          osc.type = 'sawtooth';
          osc.frequency.value = freq;
          gain.gain.setValueAtTime(0, t + start);
          gain.gain.linearRampToValueAtTime(0.35, t + start + 0.03);
          gain.gain.setValueAtTime(0.35, t + start + dur - 0.05);
          gain.gain.linearRampToValueAtTime(0, t + start + dur);
          osc.connect(gain); gain.connect(ctx.destination);
          osc.start(t + start); osc.stop(t + start + dur + 0.05);
        });
        // Tömeg zaj — fehér zaj burst
        const bufSize = ctx.sampleRate * 2;
        const buf = ctx.createBuffer(1, bufSize, ctx.sampleRate);
        const data = buf.getChannelData(0);
        for (let i = 0; i < bufSize; i++) data[i] = (Math.random() * 2 - 1);
        const noise = ctx.createBufferSource();
        const noiseGain = ctx.createGain();
        const filter = ctx.createBiquadFilter();
        filter.type = 'bandpass'; filter.frequency.value = 800; filter.Q.value = 0.5;
        noise.buffer = buf;
        noiseGain.gain.setValueAtTime(0, t);
        noiseGain.gain.linearRampToValueAtTime(0.18, t + 0.1);
        noiseGain.gain.setValueAtTime(0.18, t + 1.5);
        noiseGain.gain.linearRampToValueAtTime(0, t + 2.0);
        noise.connect(filter); filter.connect(noiseGain); noiseGain.connect(ctx.destination);
        noise.start(t); noise.stop(t + 2.1);
      };
      if (ctx.state === 'suspended') { ctx.resume().then(play); } else { play(); }
    } catch(e) {}
  };"""

assert OLD_SOUND in content, "playRaceSound not found"
content = content.replace(OLD_SOUND, NEW_SOUND, 1)
print("✓ playRaceSound újraírva")

OLD_VER = "const APP_VERSION = 'v8.43';"
NEW_VER = "const APP_VERSION = 'v8.44';"
assert OLD_VER in content
content = content.replace(OLD_VER, NEW_VER, 1)

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(content)
print("✓ v8.44 saved")
