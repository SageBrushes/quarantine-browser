"""
Quarantine (1994) Asset Extractor
==================================
Extracts all game assets from original Quarantine game files into
web-ready formats for the browser engine.

Requirements:
    pip install Pillow tqdm

Usage:
    python extract.py --game /path/to/quarantine/game/files --out ./assets

Outputs:
    assets/img/     - Full-screen images (GIF→PNG, palette corrected)
    assets/spr/     - Sprites (raw VGA indexed→RGBA PNG, palette matched)
    assets/levels/  - Level geometry JSON (from MAP+BLK files)
    manifest.js     - Sprite/image manifest for browser

Credits:
    - IMG format: moddingwiki.shikadi.net/wiki/Quarantine
    - SPR format: github.com/colinbourassa/quarantine-decode
    - BLK/MAP format: github.com/diggedypomme/quarantine-modding
"""

import os, io, json, struct, argparse
from PIL import Image

# ── Palette offset in IMG files ──────────────────────────────────────────────
PALETTE_OFFSET = 0x0D   # 13 bytes into the IMAGEX header

# ── Per-area palette source IMG ──────────────────────────────────────────────
PALETTE_MAP = {
    'KWALL': 'KFLOOR.IMG', 'KOBJECT': 'KFLOOR.IMG',
    'JWALL': 'JFLOOR.IMG', 'JOBJECT': 'JFLOOR.IMG',
    'PWALL': 'PFLOOR.IMG', 'POBJECT': 'PFLOOR.IMG',
    'SWALL': 'SFLOOR.IMG', 'SOBJECT': 'SFLOOR.IMG',
    'WWALL': 'WFLOOR.IMG', 'WOBJECT': 'WFLOOR.IMG',
    'CAB':   'CAB.IMG',    'WHEEL':   'CAB.IMG',
    'OPTIONC':'OPTION.IMG', 'RICON':  'OPTION.IMG',
}
DEFAULT_PALETTE_IMG = 'FLOOR.IMG'

CATEGORY_MAP = {
    'CAB': 'Taxi', 'WHEEL': 'Taxi',
    'BODA': 'Enemies', 'BOSS': 'Bosses', 'BTANK': 'Bosses',
    'CUBV': 'Bosses', 'BLIM': 'Bosses',
    'PED': 'Pedestrians',
    'EXPLO': 'Explosions', 'FIRE': 'Effects', 'DAMAGE': 'Effects',
    'EFFECTS': 'Effects', 'MFLASH': 'Effects', 'SHAD': 'Effects',
    'PLASMA': 'Weapons', 'MISSILE': 'Weapons', 'MINE': 'Weapons',
    'CANNON': 'Weapons', 'EMISSILE': 'Weapons', 'EMINES': 'Weapons',
    'SPIKE': 'Weapons', 'UZI': 'Weapons',
    'PACK': 'Pickups',
    'WALL': 'Walls', 'JWALL': 'Walls', 'KWALL': 'Walls',
    'PWALL': 'Walls', 'SWALL': 'Walls', 'WWALL': 'Walls',
    'OBJECTS': 'World Objects', 'KOBJECT': 'World Objects',
    'JOBJECT': 'World Objects', 'WOBJECT': 'World Objects',
    'SOBJECT': 'World Objects', 'POBJECT': 'World Objects',
    'CHOP': 'Enemy Vehicles', 'FALC': 'Enemy Vehicles',
    'HOVR': 'Enemy Vehicles', 'MONST': 'Enemy Vehicles',
    'CYCT': 'Enemy Vehicles', 'SPINS': 'Enemy Vehicles',
    'RADAR': 'HUD', 'WRADAR': 'HUD', 'MAPICONS': 'HUD',
    'OPTIONC': 'HUD', 'RICON': 'HUD',
}


def get_category(fname):
    base = fname.split('_')[0].upper()
    for prefix, cat in CATEGORY_MAP.items():
        if base.startswith(prefix):
            return cat
    return 'Misc'


def read_palette(game_dir, img_name):
    path = os.path.join(game_dir, img_name)
    with open(path, 'rb') as f:
        f.seek(PALETTE_OFFSET)
        return f.read(768)


_palette_cache = {}
def get_palette(game_dir, img_name):
    if img_name not in _palette_cache:
        _palette_cache[img_name] = read_palette(game_dir, img_name)
    return _palette_cache[img_name]


def palette_for_spr(game_dir, spr_fname):
    base = spr_fname.split('.')[0].upper()
    for prefix, pal in PALETTE_MAP.items():
        if base.startswith(prefix):
            return get_palette(game_dir, pal)
    return get_palette(game_dir, DEFAULT_PALETTE_IMG)


# ── IMG extraction (IMAGEX → GIF87a patch) ───────────────────────────────────
def extract_imgs(game_dir, out_dir):
    os.makedirs(out_dir, exist_ok=True)
    results = []
    for fname in sorted(os.listdir(game_dir)):
        if not fname.upper().endswith('.IMG'):
            continue
        path = os.path.join(game_dir, fname)
        with open(path, 'rb') as f:
            data = bytearray(f.read())
        data[0:6] = b'GIF87a'
        try:
            Image.MAX_IMAGE_PIXELS = None
            img = Image.open(io.BytesIO(bytes(data)))
            out_path = os.path.join(out_dir, fname.replace('.IMG', '.png').replace('.img', '.png'))
            img.convert('RGB').save(out_path)
            results.append({'file': os.path.basename(out_path), 'w': img.width, 'h': img.height})
        except Exception as e:
            print(f'  SKIP {fname}: {e}')
    print(f'  {len(results)} IMG files extracted')
    return results


# ── SPR extraction ────────────────────────────────────────────────────────────
def extract_sprs(game_dir, out_dir):
    os.makedirs(out_dir, exist_ok=True)
    sprites = []
    for fname in sorted(os.listdir(game_dir)):
        if not fname.upper().endswith('.SPR'):
            continue
        path = os.path.join(game_dir, fname)
        palette = palette_for_spr(game_dir, fname)
        prefix = fname.rsplit('.', 1)[0]
        with open(path, 'rb') as f:
            data = f.read()
        num = data[0]
        dims = [(data[1 + i*2], data[1 + i*2 + 1]) for i in range(num)]
        pos = 1 + num * 2
        for i, (w, h) in enumerate(dims):
            if w < 4 or h < 4:
                continue
            pc = w * h
            if pos + pc > len(data):
                break
            pixels = data[pos:pos+pc]
            pos += pc
            img = Image.new('P', (w, h))
            img.putpalette(palette)
            img.putdata(pixels)
            out_name = f'{prefix}_{i:03d}.png'
            img.convert('RGBA').save(os.path.join(out_dir, out_name))
            sprites.append({
                'file': out_name, 'w': w, 'h': h,
                'cat': get_category(fname),
                'name': prefix,
            })
    print(f'  {len(sprites)} sprites extracted')
    return sprites


# ── MAP parsing ───────────────────────────────────────────────────────────────
def parse_map(game_dir, city):
    path = os.path.join(game_dir, f'{city.upper()}.MAP')
    with open(path, 'rb') as f:
        data = f.read()
    w, h = struct.unpack_from('<HH', data, 0)
    tiles = list(struct.unpack_from(f'<{w*h}H', data, 4))
    return {'w': w, 'h': h, 'tiles': tiles}


# ── Main ──────────────────────────────────────────────────────────────────────
def main():
    parser = argparse.ArgumentParser(description='Quarantine asset extractor')
    parser.add_argument('--game', required=True, help='Path to game files directory')
    parser.add_argument('--out',  required=True, help='Output directory')
    args = parser.parse_args()

    game_dir = args.game
    out_dir  = args.out
    os.makedirs(out_dir, exist_ok=True)

    print('Extracting IMG files...')
    imgs = extract_imgs(game_dir, os.path.join(out_dir, 'img'))

    print('Extracting SPR files...')
    sprites = extract_sprs(game_dir, os.path.join(out_dir, 'spr'))

    print('Parsing level maps...')
    maps = {}
    for city in ['kcity', 'jcity', 'pcity', 'scity', 'wcity', 'city']:
        try:
            maps[city] = parse_map(game_dir, city)
            print(f'  {city}: {maps[city]["w"]}x{maps[city]["h"]}')
        except FileNotFoundError:
            pass

    # Write manifest
    cats = sorted(set(s['cat'] for s in sprites))
    manifest = {
        'sprites': sprites,
        'imgs': imgs,
        'categories': ['All'] + cats,
        'maps': {k: {'w': v['w'], 'h': v['h']} for k, v in maps.items()},
    }
    with open(os.path.join(out_dir, 'manifest.json'), 'w') as f:
        json.dump(manifest, f)

    # Write map data separately (large)
    for city, data in maps.items():
        with open(os.path.join(out_dir, f'map_{city}.json'), 'w') as f:
            json.dump(data, f)

    print(f'\nDone. Output in: {out_dir}')
    print(f'  {len(imgs)} images, {len(sprites)} sprites, {len(maps)} maps')


if __name__ == '__main__':
    main()
