# Cart Run

A single-file Three.js arcade game. Shipping truck barrels down a residential street → avenue → downtown, dropping yellow shopping carts out the back. Carts are your clock. Get to the big-box mart before you run out.

## Run it

```bash
cd ~/truck-cart-game
python3 -m http.server 5174
# open http://localhost:5174/
```

(Or any static file server — it's just `index.html` + a CDN-pinned Three.js import map.)

## Controls

- `W` / `↑` — throttle
- `S` / `↓` — brake
- `A`/`←` and `D`/`→` — steer
- `SPACE` — boost (drains the meter; refill with ⬢ pickups on the road)
- `M` — mute audio

## Features

- 3 stages on smooth `CatmullRomCurve3` roads: SUBURB → AVENUE → DOWNTOWN
- Yellow nested cart trail that snakes behind the truck
- Oncoming traffic to dodge; hitting a car loses carts + boost
- Boost meter + on-road glowing boost pickups
- Speed-scaled FOV punch, vignette, screen shake, radial speed lines, manga boost-blast
- 170 BPM lo-fi dark D&B with A → B → C arrangement (groove → melodic breakdown → build), all procedural via Web Audio
- Distant horizon mountains with per-stage palette
- Big-box mart at the end of each stage with a massive parking lot

No build step. Single HTML file. Three.js pulled from `unpkg`.
