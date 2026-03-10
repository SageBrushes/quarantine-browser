# Quarantine Browser Engine

> **Fork of [diggedypomme/quarantine-modding](https://github.com/diggedypomme/quarantine-modding)** — a browser-native 3D reimplementation of Quarantine (1994). No Doom. No emulator. Pure JavaScript.

## What's here

| Path | Description |
|------|-------------|
| `browser/tribute.html` | Interactive fan tribute + sprite browser (4,168 sprites) |
| `browser/raycaster.html` | 3D viewer prototype with real textures + actual level maps |
| `browser/extract.py` | Asset pipeline: IMG→PNG, SPR→RGBA PNG, MAP→JSON |
| `fullscript/` | Original BLK/MAP parser from diggedypomme (preserved) |

## Quick start

**Extract assets** (needs original Quarantine game files):
```bash
cd browser
pip install Pillow tqdm
python extract.py --game /path/to/Q/ --out ./assets
```

**Run locally:**
```bash
# Just open in browser — no server needed
open browser/tribute.html
open browser/raycaster.html
```

## File Format Reference

| Format | Structure |
|--------|-----------|
| `.MAP` | `[width: u16le][height: u16le][tiles: u16le * w * h]` — tile 0=empty, 1–127=model index |
| `.BLK` | 128 tile models, each with floor/wall/sprite definitions. Walls have real x/y endpoints within a 512×512 unit cell |
| `.SPR` | `[count: u8][w: u8][h: u8]... [raw pixels]` — palette-indexed, palette from area's `*FLOOR.IMG` |
| `.IMG` | GIF87a with magic bytes replaced (`IMAGEX` → `GIF87a`) |

All format research by [diggedypomme](https://github.com/diggedypomme/quarantine-modding) and [colinbourassa](https://github.com/colinbourassa/quarantine-decode).

## Engine Roadmap

- [x] Asset extraction (IMG + SPR, palette-matched)
- [x] Sprite browser (4,168 sprites, 15 categories)
- [x] Fan tribute page
- [x] Grid raycaster prototype (real 64×64 textures, actual MAP data)
- [ ] BLK parser → proper wall geometry JSON
- [ ] Three.js renderer with real wall positions + heights
- [ ] Sprite billboards (enemies, objects, pedestrians)
- [ ] All 5 levels (KCITY, JCITY, PCITY, SCITY, WCITY)
- [ ] Collision + movement

## Credits

- Reverse engineering: [diggedypomme](https://github.com/diggedypomme/quarantine-modding)
- SPR format: [colinbourassa](https://github.com/colinbourassa/quarantine-decode)
- Format docs: [ModdingWiki](https://moddingwiki.shikadi.net/wiki/Quarantine)
- Quarantine © 1994 GameTek / Imagexcel — fan project, not for commercial use
