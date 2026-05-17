#!/usr/bin/env python3
"""
Generate the retro SFX bank for Cart Run.

Outputs 22050 Hz / 16-bit / mono WAV files into ../audio/sfx/.
All files are procedurally synthesized — no external samples or
copyrighted material. Each WAV is therefore licensed CC0 by
construction.

These play through the game's audioMaster bitcrush + LPF + comp
chain, so the slightly-clean source ends up sounding like proper
PS1-era PCM playback once the master chain crunches it.
"""

import math
import os
import random
import struct
import wave

SR = 22050
OUT = os.path.join(os.path.dirname(__file__), "..", "audio", "sfx")
os.makedirs(OUT, exist_ok=True)


def write_wav(name, samples):
    path = os.path.join(OUT, name)
    with wave.open(path, "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(SR)
        buf = bytearray()
        for s in samples:
            v = int(max(-1.0, min(1.0, s)) * 32767)
            buf.extend(struct.pack("<h", v))
        w.writeframes(bytes(buf))
    return path


def env_attack_decay(n, attack=0.005, decay=0.12):
    """ADSR-ish envelope as a list of length n."""
    a_n = max(1, int(attack * SR))
    d_n = max(1, int(decay * SR))
    out = [0.0] * n
    for i in range(min(a_n, n)):
        out[i] = i / a_n
    for i in range(a_n, n):
        t = (i - a_n) / d_n
        out[i] = math.exp(-t * 5)
    return out


def square(t, freq):
    return 1.0 if math.sin(2 * math.pi * freq * t) > 0 else -1.0


def saw(t, freq):
    p = (t * freq) % 1.0
    return 2 * p - 1


def sine(t, freq):
    return math.sin(2 * math.pi * freq * t)


def noise():
    return random.uniform(-1, 1)


# --- SFX recipes ---

def sfx_pickup():
    out = []
    notes = [(800, 0.07), (1100, 0.07), (1500, 0.14)]
    for freq, dur in notes:
        n = int(SR * dur)
        env = env_attack_decay(n, 0.002, dur)
        for i in range(n):
            t = i / SR
            out.append(square(t, freq) * env[i] * 0.32)
    return out


def sfx_restock():
    # ascending arpeggio that feels triumphant
    out = []
    notes = [(520, 0.06), (780, 0.06), (1040, 0.06), (1300, 0.18)]
    for freq, dur in notes:
        n = int(SR * dur)
        env = env_attack_decay(n, 0.002, dur)
        for i in range(n):
            t = i / SR
            v = 0.6 * square(t, freq) + 0.3 * sine(t, freq * 2)
            out.append(v * env[i] * 0.34)
    return out


def sfx_crash():
    dur = 0.45
    n = int(SR * dur)
    out = [0.0] * n
    # body: sine pitch drop
    for i in range(n):
        t = i / SR
        # exponential pitch glide 160 → 40
        freq = 160 * math.exp(-t * 4.5) + 40
        out[i] += math.sin(2 * math.pi * freq * t) * math.exp(-t * 4) * 0.55
    # crunch noise burst (first 80ms)
    nb = int(SR * 0.12)
    for i in range(nb):
        out[i] += noise() * (1 - i / nb) * 0.28
    return out


def sfx_bump():
    dur = 0.16
    n = int(SR * dur)
    out = []
    for i in range(n):
        t = i / SR
        freq = 220 * math.exp(-t * 12) + 70
        # triangle
        p = (t * freq) % 1.0
        tri = abs(4 * p - 2) - 1
        env = math.exp(-t * 14)
        out.append(tri * env * 0.4)
    return out


def sfx_clack():
    dur = 0.06
    n = int(SR * dur)
    out = []
    for i in range(n):
        env = math.exp(-i / (SR * 0.012))
        v = noise() * env * 0.45
        out.append(v)
    return out


def sfx_boost():
    dur = 0.5
    n = int(SR * dur)
    out = [0.0] * n
    # bandpass-ish noise sweep via filtering
    fc_start, fc_end = 600, 5500
    # crude one-pole bandpass: keep state hp + lp
    hp = 0.0
    lp = 0.0
    for i in range(n):
        t = i / SR
        x = noise()
        # cutoff ramps
        fc = fc_start * math.exp(math.log(fc_end / fc_start) * (t / dur))
        # lowpass coefficient
        rc = 1.0 / (2 * math.pi * fc)
        alpha = (1.0 / SR) / (rc + 1.0 / SR)
        lp = lp + alpha * (x - lp)
        # highpass: x - prev_lp gives band-emphasis
        bp = x - lp
        env = math.sin(math.pi * (t / dur))  # peak at center
        out[i] += bp * env * 0.55
    # accompanying low whomp sine drop
    for i in range(n):
        t = i / SR
        freq = 90 * math.exp(-t * 3) + 40
        out[i] += math.sin(2 * math.pi * freq * t) * math.exp(-t * 3) * 0.4
    return out


def sfx_beep():
    dur = 0.13
    n = int(SR * dur)
    out = []
    for i in range(n):
        t = i / SR
        env = (1.0 if i < SR * 0.005 else math.exp(-(t - 0.005) * 10))
        out.append(square(t, 880) * env * 0.32)
    return out


def sfx_checkpoint():
    # two-tone bell — short, satisfying
    out = []
    for freq, dur in [(880, 0.16), (1320, 0.36)]:
        n = int(SR * dur)
        for i in range(n):
            t = i / SR
            v = 0.7 * sine(t, freq) + 0.4 * sine(t, freq * 2) + 0.15 * sine(t, freq * 3)
            env = math.exp(-t * 6)
            out.append(v * env * 0.30)
    return out


def sfx_engine_loop():
    """One full loop of low engine drone. The game pitches it via playbackRate."""
    dur = 0.30  # short loop, will be set to .loop=true at runtime
    n = int(SR * dur)
    out = []
    # base saw at ~80Hz with LFO modulation
    base_freq = 80
    for i in range(n):
        t = i / SR
        # mild LFO on pitch
        f = base_freq * (1.0 + 0.04 * math.sin(2 * math.pi * 6 * t))
        v = 0.45 * saw(t, f) + 0.25 * saw(t, f * 2)
        # gentle wobble in amplitude
        amp = 0.65 + 0.1 * math.sin(2 * math.pi * 4 * t)
        out.append(v * amp * 0.4)
    return out


def sfx_warning():
    # short rising alert
    out = []
    for freq, dur in [(420, 0.10), (560, 0.10), (720, 0.14)]:
        n = int(SR * dur)
        env = env_attack_decay(n, 0.002, dur)
        for i in range(n):
            t = i / SR
            out.append(square(t, freq) * env[i] * 0.34)
    return out


def main():
    random.seed(7)
    written = []
    for name, fn in [
        ("pickup.wav",     sfx_pickup),
        ("restock.wav",    sfx_restock),
        ("crash.wav",      sfx_crash),
        ("bump.wav",       sfx_bump),
        ("clack.wav",      sfx_clack),
        ("boost.wav",      sfx_boost),
        ("beep.wav",       sfx_beep),
        ("checkpoint.wav", sfx_checkpoint),
        ("engine.wav",     sfx_engine_loop),
        ("warning.wav",    sfx_warning),
    ]:
        path = write_wav(name, fn())
        size = os.path.getsize(path)
        written.append((name, size))
        print(f"  {name:18s} {size:>8d} bytes")
    total = sum(s for _, s in written)
    print(f"\n{len(written)} files, {total} bytes total.")


if __name__ == "__main__":
    main()
