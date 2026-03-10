# Quarantine Browser Engine

A browser-based 3D viewer and engine for **Quarantine (1994)** by GameTek / Imagexcel — built entirely from reverse-engineered game data using the original assets and level geometry.

**No Doom. No emulator. No plugins. Pure JavaScript + Three.js.**

> Forked from [diggedypomme/quarantine-modding](https://github.com/diggedypomme/quarantine-modding) which did the foundational reverse engineering of the BLK/MAP/SPR formats. This project takes that work and builds a browser-native engine from it.

---

## Live Demo

Serve the `browser/` directory with any HTTP server:

```bash
cd browser
python3 -m http.server 8765
# open http://localhost:8765/engine.html
```

## What's Working

| Feature | Status |
|---------|--------|
| 5 full levels (KCITY, JCITY, PCITY, SCITY, WCITY) | ✅ |
| Real wall geometry from BLK tile definitions | ✅ |
| Original 64×64 wall textures (SPR files) | ✅ |
| Per-tile floor quads with 64×64 floor textures | ✅ |
| Actual MAP grid placement | ✅ |
| Smart camera spawn (finds street between buildings) | ✅ |
| WASD + mouse look navigation | ✅ |
| Minimap | ✅ |
| Wireframe mode | ✅ |
| Sprite browser (4,168 sprites, 15 categories) | ✅ |
| Interactive fan tribute page | ✅ |
| Sprite billboards (enemies, objects) | 🔜 |
| Collision detection | 🔜 |
| Audio (VOC sound effects) | 🔜 |

## Browser Files

```
browser/
├── engine.html          # Main 3D level viewer (Three.js)
├── tribute.html         # Fan tribute page + sprite browser
├── raycaster.html       # Grid raycaster prototype
├── extract.py           # Asset extraction pipeline
├── parse_blk.py         # BLK tile geometry parser
├── assets/
│   ├── img/             # Full-screen images + floor tiles (320×200 → 64×64 splits)
│   ├── spr/             # 4,207 sprites (palette-matched per area)
│   └── tiles/           # Parsed tile geometry JSON + MAP grids
```

## File Format Reference

### MAP (`*CITY.MAP`)
```
[width: u16le][height: u16le][tiles: u16le × w × h]
```
- `0` = empty road cell
- `1–127` = tile model index (first texture set)
- `128+` = same models, additional texture sets
- Tile model: `(value - 1) % 128` → index into BLK tile array

### BLK (`*CITY.BLK`)
```
[unknown: u16le][num_tiles: u16le]
[num_tiles × tile_header: 8 bytes each]
  → floor_count, wall_count, texture_count, sprite_count (all u16le)
[tile data blocks, variable length, back-to-back]
  → floor_count × 18 raw bytes per floor
  → wall_count  × 18 raw bytes per wall
  → texture_count × 2 bytes (16 variation slots, only first populated)
  → sprite_count × 12 raw bytes per sprite
```

**Wall (18 bytes):**
- `b[0]` = tile_count (number of wall segments)
- `b[2,3]` = east_per_tile (signed: `b[3]==255` → negative)
- `b[4,5]` = south_per_tile (signed)
- `b[6,7]` = height (game units)
- `b[8]+b[9]×256` = start_east, `b[10]+b[11]×256` = start_south
- `b[12,13]` = vertical offset (signed; `offset=20` = floor level)
- `b[15]` = texture_repeat (`255` = one-per-segment, else = single texture)

**Floor (18 bytes):** scale, rotation, height, 4 vertices (scaled ×32 for game units)

**Sprite (12 bytes):** x, y, z position + texture reference

### SPR (sprite files)
```
[count: u8][width_0: u8][height_0: u8]...[raw pixels: count × w × h]
```
Palette comes from companion `*FLOOR.IMG` for that area.

### IMG (full-screen images)
Standard GIF87a with magic bytes replaced: `IMAGEX` → `GIF87a`  
Floor images split into 5×3 grids of 64×64 tiles, lettered `a`–`o`.

## Running the Asset Extractor

You need the original Quarantine game files (freely available at [archive.org](https://archive.org/details/quarantine_202404)):

```bash
cd browser
pip install Pillow tqdm
python3 extract.py --game /path/to/Q/ --out ./assets
python3 parse_blk.py --game /path/to/Q/ --out ./assets/tiles
```

## Credits

- **Format reverse engineering:** [diggedypomme](https://github.com/diggedypomme/quarantine-modding) · [r/QuarantineModding](https://reddit.com/r/QuarantineModding)
- **SPR format:** [colinbourassa/quarantine-decode](https://github.com/colinbourassa/quarantine-decode)
- **Format docs:** [ModdingWiki](https://moddingwiki.shikadi.net/wiki/Quarantine)
- **Quarantine** © 1994 GameTek Inc / Imagexcel Ltd — fan project, not for commercial use
- Game freely available: [archive.org/details/quarantine_202404](https://archive.org/details/quarantine_202404)
