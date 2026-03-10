"""
Quarantine BLK Parser
======================
Parses *CITY.BLK files into structured JSON tile geometry for the browser engine.

Format credit: github.com/diggedypomme/quarantine-modding

BLK Structure:
  [u16le: unknown] [u16le: num_tiles=128]
  [num_tiles × 8 bytes: tile headers (floor_count, wall_count, texture_count, sprite_count)]
  [variable tile data blocks, back-to-back]
    Each tile block:
      floor_count × 18 bytes  (9 × u16le per floor)
      wall_count  × 18 bytes  (9 × u16le per wall)
      texture data            (4 loops of floor+wall texture refs)
      sprite_count × 12 bytes (6 × u16le per sprite)

Usage:
  python parse_blk.py --game /path/to/Q/ --out ./assets
"""

import os, sys, json, struct, argparse

AREA_CONFIG = {
    'kcity': {'blk': 'KCITY.BLK', 'walls': 'kwall', 'floors': 'kfloor', 'objects': 'kobjects'},
    'jcity': {'blk': 'JCITY.BLK', 'walls': 'jwall', 'floors': 'jfloor', 'objects': 'jobjects'},
    'pcity': {'blk': 'PCITY.BLK', 'walls': 'pwall', 'floors': 'pfloor', 'objects': 'pobject'},
    'scity': {'blk': 'SCITY.BLK', 'walls': 'swall', 'floors': 'sfloor', 'objects': 'sobject'},
    'wcity': {'blk': 'WCITY.BLK', 'walls': 'wwall', 'floors': 'wfloor', 'objects': 'wobjects'},
    'city':  {'blk': 'CITY.BLK',  'walls': 'wall',  'floors': 'floor',  'objects': 'objects'},
}


def signed16(lo, hi):
    """Read a potentially-negative 16-bit value stored as (value, sign_byte)."""
    return (lo - 256) if hi == 255 else lo


def parse_wall(b):
    """Parse 18 raw bytes into a wall definition."""
    # b[0]       = tile_count
    # b[2],b[3]  = east_per_tile (signed: b[3]==255 means negative)
    # b[4],b[5]  = south_per_tile (signed)
    # b[6],b[7]  = height (b[7]==255 means add 256)
    # b[8]+b[9]*256  = start_east
    # b[10]+b[11]*256 = start_south
    # b[12],b[13]= offset_v (signed)
    # b[15]      = 255 → not repeating, else repeating
    tile_count     = b[0]
    east_per_tile  = signed16(b[2], b[3])
    south_per_tile = signed16(b[4], b[5])
    height         = b[6] + 256 if b[7] == 255 else b[6]
    start_east     = b[8]  + b[9]  * 256
    start_south    = b[10] + b[11] * 256
    offset_v       = signed16(b[12], b[13])
    texture_repeat = (b[15] != 255)

    return {
        'tile_count':     tile_count,
        'start_east':     start_east,
        'start_south':    start_south,
        'end_east':       start_east  + east_per_tile  * tile_count,
        'end_south':      start_south + south_per_tile * tile_count,
        'height':         height,
        'offset_v':       offset_v,
        'texture_repeat': texture_repeat,
        'textures':       [],
    }


def parse_floor(b):
    """Parse 18 raw bytes into a floor definition."""
    # Vertices at byte offsets 6,7 / 9,10 / 12,13 / 15,16
    return {
        'scale':    b[0],
        'rotation': b[2],
        'height':   b[3],
        'vertices': [
            {'x': b[6],  'y': b[7]},
            {'x': b[9],  'y': b[10]},
            {'x': b[12], 'y': b[13]},
            {'x': b[15], 'y': b[16]},
        ],
        'textures': [],
    }


def parse_sprite(b, objects_prefix):
    """Parse 12 raw bytes into a sprite placement."""
    z = (256 - b[4]) if b[5] > 0 else b[4]
    sprite_num = b[8]
    img = f'{objects_prefix}_{sprite_num}.png'
    if 'pobject' in objects_prefix:
        img = f'{objects_prefix}{b[6] + 1}_{sprite_num}.png'
    return {
        'x':   b[0] + b[1] * 256,
        'y':   b[2] + b[3] * 256,
        'z':   z,
        'img': img,
    }


def number_to_letter(n):
    return chr(97 + n) if 0 <= n < 26 else '?'


def parse_blk(game_dir, city):
    cfg = AREA_CONFIG[city]
    blk_path = os.path.join(game_dir, cfg['blk'])

    with open(blk_path, 'rb') as f:
        raw = f.read()

    dec = list(raw)  # flat byte array
    pos = 0

    # ── Header ──────────────────────────────────────────────────────────
    _unknown   = dec[0] + dec[1] * 256;  pos += 2
    num_tiles  = dec[2] + dec[3] * 256;  pos += 2

    # ── Per-tile counts ──────────────────────────────────────────────────
    tile_headers = []
    for _ in range(num_tiles):
        fc = dec[pos] + dec[pos+1] * 256
        wc = dec[pos+2] + dec[pos+3] * 256
        tc = dec[pos+4] + dec[pos+5] * 256   # texture_count (padding)
        sc = dec[pos+6] + dec[pos+7] * 256
        tile_headers.append({'fc': fc, 'wc': wc, 'tc': tc, 'sc': sc})
        pos += 8

    # ── Tile data blocks ─────────────────────────────────────────────────
    # Each element is u16le → stride = 2 bytes
    tiles = []
    for hdr in tile_headers:
        fc, wc, tc, sc = hdr['fc'], hdr['wc'], hdr['tc'], hdr['sc']

        # Parse floors (18 raw bytes each)
        floors = []
        for _ in range(fc):
            floors.append(parse_floor(dec[pos:pos+18]))
            pos += 18

        # Parse walls (18 raw bytes each)
        walls = []
        for _ in range(wc):
            walls.append(parse_wall(dec[pos:pos+18]))
            pos += 18

        # Texture data: 4 loops of (fc floor refs + variable wall refs)
        tex_start = pos
        for loop in range(4):
            # Floor textures (1 ref each)
            for fi in range(fc):
                lo, hi = dec[pos], dec[pos+1]
                floors[fi]['textures'].append(
                    f'{cfg["floors"]}_{number_to_letter(hi)}.gif'
                )
                pos += 2

            # Wall textures (tile_count refs, or 1 if texture_repeat)
            for wi in range(wc):
                n = 1 if walls[wi]['texture_repeat'] else walls[wi]['tile_count']
                wall_tex = []
                for _ in range(n):
                    lo, hi = dec[pos], dec[pos+1]
                    wall_tex.append(f'{cfg["walls"]}{lo + 1}_{hi}.png')
                    pos += 2
                walls[wi]['textures'].append(wall_tex)

        # Sprites (12 raw bytes each)
        sprites = []
        for _ in range(sc):
            sprites.append(parse_sprite(dec[pos:pos+12], cfg['objects']))
            pos += 12

        tiles.append({'floors': floors, 'walls': walls, 'sprites': sprites})

    return {
        'city':      city,
        'num_tiles': num_tiles,
        'tile_size': 512,   # each tile occupies 512×512 world units
        'tiles':     tiles,
    }


def main():
    parser = argparse.ArgumentParser(description='Parse Quarantine BLK files to JSON')
    parser.add_argument('--game', required=True, help='Path to game files directory')
    parser.add_argument('--out',  required=True, help='Output directory for JSON files')
    args = parser.parse_args()

    os.makedirs(args.out, exist_ok=True)

    for city in AREA_CONFIG:
        blk_path = os.path.join(args.game, AREA_CONFIG[city]['blk'])
        if not os.path.exists(blk_path):
            print(f'  SKIP {city}: {AREA_CONFIG[city]["blk"]} not found')
            continue
        try:
            print(f'Parsing {city}...')
            data = parse_blk(args.game, city)
            out_path = os.path.join(args.out, f'tiles_{city}.json')
            with open(out_path, 'w') as f:
                json.dump(data, f)
            sz = os.path.getsize(out_path) // 1024
            print(f'  {city}: {data["num_tiles"]} tiles → {out_path} ({sz}KB)')
        except Exception as e:
            print(f'  ERROR {city}: {e}')
            import traceback; traceback.print_exc()


if __name__ == '__main__':
    main()
