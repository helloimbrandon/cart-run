# Audio Sources — Prototype / Temp Use

The shipping game currently uses **zero external audio samples** — every drum, bass, lead, voice formant, engine drone, SFX, and rave vocal hit is generated procedurally with Web Audio. That keeps the project licence-clean by default.

If you decide to drop in real samples (e.g. an actual breakbeat loop, real announcer voice barks, a found vocal stab), use one of the sources below and log it in [`AUDIO_CREDITS.md`](./AUDIO_CREDITS.md) before committing.

## Licence shorthand
- **CC0** — public domain. Best option. No attribution required, commercial OK.
- **CC-BY** — attribution required. Acceptable; record in credits manifest.
- **CC-BY-SA** — share-alike. Avoid unless you're prepared to license your project the same way.
- **CC-BY-NC** — non-commercial only. **Avoid** if this could ever ship as a paid/sponsored project.
- **Custom royalty-free** (Pixabay/Mixkit/Sonniss) — usually commercial-OK, no attribution; still log it.

## Primary sources (recommended)

### CC0-first
- **OpenGameArt.org** — `https://opengameart.org/art-search?keys=&field_art_type_tid%5B%5D=13` (Audio) → filter by licence: **CC0**. Solid for: UI blips, countdown beeps, racing engines, crash impacts, retro game packs.
- **Freesound.org** — `https://freesound.org/search/?f=license%3A%22Creative+Commons+0%22` (CC0 filter). Best general-purpose library; huge. Pre-filter to CC0 to avoid any attribution paperwork. Cycle through "racing", "engine", "whoosh", "impact", "crash", "voice", "countdown".
- **Pixabay Audio** — `https://pixabay.com/sound-effects/` → Pixabay Content License (free commercial, no attribution required). Many engine/UI/voice clips.
- **Mixkit** — `https://mixkit.co/free-sound-effects/` → "Mixkit License" (free, commercial OK, no attribution). UI/whoosh/voice categories are useful.

### Pro packs released free
- **Sonniss "GDC Game Audio Bundle"** — `https://sonniss.com/gameaudiogdc` — multi-gigabyte royalty-free bundles released annually. Commercial OK, no attribution. Best for impact / vehicle / ambient layers.
- **99Sounds.org** — `https://99sounds.org/` — multiple high-quality packs released free; check each pack's licence (most permit commercial use).
- **Soundsnap free packs** — pack-by-pack licences; verify each.

### Procedural / generated (no source files to track at all)
- **jsfxr** (web) — `https://sfxr.me/` — generate retro chip SFX in browser, export WAV. CC0 output by design.
- **ChipTone (SFB Games)** — `https://sfbgames.itch.io/chiptone` — same idea, more knobs.
- **Bfxr** — `https://www.bfxr.net/` — desktop equivalent of jsfxr.
- Use these for: countdown beeps, pickup dings, UI blips, retro crash bursts, alarm tones. Output is uncopyrighted.

### Voice / announcer
- Real announcer voice barks are the hardest CC0 category. Options:
  1. **Freesound CC0 voice search** — `https://freesound.org/search/?q=announcer&f=license%3A%22Creative+Commons+0%22` (also try `shout`, `yeah`, `go`, `race`). Hit rate is low but a few good ones exist.
  2. **OpenGameArt voice/announcer packs** — small but CC0-clean.
  3. **Record your own** — free, you own it. iPhone Voice Memos + processing chain below.
  4. **Online TTS** — for the SNES/Star Fox-style robot voice we already have, the in-browser `speechSynthesis` API is what we're using now and it produces no licence problems.

### Research-only / avoid for shipped audio
- **BBC Sound Effects Archive** — `https://sound-effects.bbcrewind.co.uk/` — licence is **personal/educational only** unless you pay. Useful for reference, not for the final mix.
- **Zapsplat** — free tier requires attribution + has commercial restrictions. Acceptable if you're willing to track + credit, but CC0 sources are cleaner.

### **Do not use**
- Any audio ripped from Star Fox, Sega, Namco, Konami, WipEout, Ridge Racer, Sega Rally, Gran Turismo, Mario Kart, F-Zero, etc.
- Found vocal stabs from copyrighted dance/rave tracks (any famous "YEAH!" / "GO!" sample is almost certainly cleared on the original release and not free to re-use).
- AI-generated voices from services with restricted commercial terms — read each service's TOS.

## Mapping to game needs

| Game need | Best source category | Notes |
|---|---|---|
| Engine drone | Freesound CC0 "car idle" + Sonniss vehicles | Loop a small clean idle, pitch-shift in code with `playbackRate` tied to `truckSpeed` |
| Boost whoosh | Freesound CC0 "whoosh" / jsfxr "powerup" | Layer the existing synthesized whoosh with one short sample |
| Crash thud | Sonniss impacts, Freesound "metal hit" CC0 | One-shot played through `audioMaster` for the bitcrush |
| Cart clack | jsfxr "hit" or short clack from Freesound CC0 | Already synthesized |
| Pickup ding | jsfxr "powerup_pickup" or "blip_select" | Already synthesized |
| Countdown 3-2-1-GO | jsfxr beep + recorded shout | Recorded "GO" routed through master gives the right crunch |
| Checkpoint chime | jsfxr "powerup_two_tone" | Already synthesized |
| Rave vocal hits | Record self / Freesound CC0 shouts | Process through the chain below |
| Music stem replacements | OpenGameArt CC0 game OSTs (search "techno", "rave", "racing") | Most are CC-BY; track each in credits |

## Processing chain — "make any clean sample feel like Sega Genesis / PS1"

The game's master chain already does most of this:

```
your sample → bufferSource
  → bandpass / lowpass (narrow to telephone-range)
  → bitcrusher waveshaper (10-bit)        ← already on audioMaster
  → master lowpass ~10.5kHz                 ← already on audioMaster
  → dynamics compressor                      ← already on audioMaster
  → speakers
```

If you connect a `BufferSource` to `audioMaster` it inherits the lo-fi treatment for free. To go harder per-sample, chain in additionally:

1. **Downsample** — encode source at 22050 Hz or 11025 Hz mono (do offline in Audacity/SoX), or play at lower `playbackRate` and re-record.
2. **Bandpass** — `BiquadFilterNode` of type `bandpass`, 1.2–3.5 kHz, Q = 1.2 — gives the "telephone" / "PCM RAM" sound.
3. **Bitcrush** — already global; for harder crunch you can stack a second `WaveShaperNode` with 6-bit curve.
4. **Slapback delay** — `DelayNode` 60–90ms, gain 0.15. Tiny only.
5. **Pitch variation** — set `bufferSource.playbackRate = rand(0.92, 1.08)` per trigger so each fire varies.
6. **Compression** — already on master.

## Suggested runtime loader

If you want to add a sample-based hit, here's a drop-in helper. Paste somewhere in the audio block of `index.html` and call `loadSample('boost', 'audio/boost.ogg').then(() => playSample('boost'))`.

```js
const _samples = {};
async function loadSample(name, url) {
  if (!audioCtx) await new Promise(r => { const i = setInterval(() => { if (audioCtx) { clearInterval(i); r(); } }, 50); });
  const res = await fetch(url);
  const buf = await res.arrayBuffer();
  _samples[name] = await audioCtx.decodeAudioData(buf);
}
function playSample(name, opts = {}) {
  if (!audioCtx || !_samples[name]) return;
  const src = audioCtx.createBufferSource();
  src.buffer = _samples[name];
  src.playbackRate.value = opts.rate != null ? opts.rate : (0.94 + Math.random() * 0.12);
  // optional extra bandpass for hammered "PCM" texture
  const bp = audioCtx.createBiquadFilter();
  bp.type = 'bandpass';
  bp.frequency.value = opts.bp != null ? opts.bp : 2200;
  bp.Q.value = 1.2;
  const g = audioCtx.createGain();
  g.gain.value = opts.gain != null ? opts.gain : 0.8;
  src.connect(bp); bp.connect(g); g.connect(audioMaster);   // audioMaster does crunch + LPF + comp
  src.start(audioCtx.currentTime);
}
```

Hosting tip for GitHub Pages: drop `*.ogg` files into a `public/audio/` folder in this repo. Pages serves them at `https://helloimbrandon.github.io/cart-run/audio/<file>.ogg`.

## Manifest discipline

Every external sample logs an entry in [`AUDIO_CREDITS.md`](./AUDIO_CREDITS.md) **at the same commit** that adds the file. PR rule of thumb: no new audio files without an updated credits manifest.
