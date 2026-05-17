# Audio Credits & Licence Manifest

> **Current state: this project ships with zero external audio samples.** All sound is generated procedurally in the browser via the Web Audio API. No third-party attribution is required.

If/when external samples are added, log them here at the same commit. See [`AUDIO_SOURCES.md`](./AUDIO_SOURCES.md) for vetted sources and the processing chain.

## Manifest format

For each new sample file, add a row:

```
- **File:** public/audio/<filename>.ogg
  **Used for:** <SFX name in code> (e.g. boost whoosh, crash thud, rave "YEAH" hit)
  **Source URL:** <link to original page>
  **Author:** <username / artist name>
  **Licence:** <CC0 / CC-BY-4.0 / Mixkit License / etc.>
  **Attribution required?** <yes / no>
  **Commercial OK?** <yes / no>
  **Processing applied:** <e.g. downsampled to 22050Hz, 6-bit crush, 80ms slapback>
  **Date added:** <YYYY-MM-DD>
  **Notes:** <anything weird about the licence terms>
```

If the licence requires attribution, also mirror the credit line into the in-game results / overlay so it's visible to players (a thin `CREDITS` panel on the title card or end-of-game screen is enough).

## Current samples

### Music
- **File:** `audio/big-stepper.mp3`
  **Used for:** main game music (track 1 of the playlist)
  **Author:** Brandon Foy (project owner)
  **Licence:** owned by author — all rights retained
  **Attribution required?** no (self)
  **Date added:** 2026-05-16

- **File:** `audio/ooiiiii.mp3`
  **Used for:** main game music (track 2 of the playlist; plays when track 1 ends)
  **Author:** Brandon Foy (project owner)
  **Licence:** owned by author
  **Attribution required?** no (self)
  **Date added:** 2026-05-16

### SFX
*(none yet — the `audio/sfx/` folder + the `loadSample()` / `playSample()` runtime helpers in `index.html` are ready for drop-in CC0/CC-BY samples. See [`AUDIO_SOURCES.md`](./AUDIO_SOURCES.md) for vetted sources. All in-game SFX, voice barks, rave vocal hits, and engine drone are still procedurally synthesized by the Web Audio code.)*

## In-game / in-engine procedural sound design

For reference, the procedural elements in `index.html` are:

| Procedural element | What it is | Where in code |
|---|---|---|
| Music track | 132 BPM deep-house, 24-bar A/B/C arrangement, FM bass + FM chord stab + FM bell + sustained pad | `schedSectionA/B/C`, `scheduleBassFM`, `scheduleChordStab`, `scheduleBellLead`, `startPad` |
| Drum kit | Synthesized kick/clap/hat via oscillators + filtered noise bursts | `scheduleKick`, `scheduleClap`, `scheduleHat` |
| Rave vocal hits ("YEAH", "GO", "BOOST" etc.) | Saw oscillator through dual bandpass formant filters with pitch glides — pure synthesis, no vocal samples | `raveVocal`, `raveChop`, `VOCAL_WORDS` |
| Voice barks ("GOOD LUCK", "CHECKPOINT", "BOOST" etc.) | `window.speechSynthesis` via SpeechSynthesisUtterance, browser-supplied voice (no third-party data) | `bark`, `showBark` |
| Engine drone | Sawtooth osc through lowpass, pitch tracks `truckSpeed` | `startEngineSFX`, `updateEngineSFX` |
| Boost whoosh | Bandpass noise sweep + low sine whomp | `sfxBoost` |
| Crash thud | Sine pitch drop + filtered noise burst | `sfxCrash` |
| Cart clack | Short noise pulse, highpassed | `sfxClack` |
| Pickup ding | Three-step square arpeggio | `sfxPickup` |
| Bump tap | Triangle pitch drop | `sfxBump` |
| Convolution reverb tail | Procedurally generated noise impulse, low-passed, ~2.4s tail, used for snares + chord stabs + vocal halo | `audioReverb` setup in `startAudio` |
| Master lo-fi chain | 10-bit `WaveShaperNode` bitcrush → ~10.5 kHz lowpass → dynamics compressor → destination | `makeBitcrusher`, master setup in `startAudio` |

Because everything routes through `audioMaster`, any future sample dropped in via the loader described in `AUDIO_SOURCES.md` will automatically inherit the bitcrush + LPF + compression, so a clean source instantly sounds like PS1/Genesis-era PCM playback.
