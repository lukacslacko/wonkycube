"""Render the three published puzzles from their unmodified, assembled STL meshes."""
from pathlib import Path
import hashlib
import json
import sys

import numpy as np
import trimesh
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'designs/conical-3x3-v1.1/source'))
import mesh_render as renderer

DESIGNS = [
    ('redi-v4.3', 'Redi', 'Corner turns · 20 moving pieces',
     {'C': '#a68bcc', 'E': '#e9ba58'}),
    ('skewb-v1.1', 'Skewb', 'Deep diagonal cuts · 14 moving pieces',
     {'C': '#a68bcc', 'F': '#e9ba58', 'K': '#65b7b2'}),
    ('conical-3x3-v1.1', 'Conical 3×3', '70° curved cuts · 26 moving pieces',
     {'C': '#86bea6', 'E': '#7bb2d7', 'K': '#e9c96d'}),
]


def font(size, bold=False):
    from matplotlib.font_manager import findfont
    return ImageFont.truetype(findfont('DejaVu Sans' + (':weight=bold' if bold else '')), size)


def main():
    # Match camera and scale so the common 64 mm exterior can be compared directly.
    tile = 900
    page = Image.new('RGB', (3 * tile, 1110), '#fafaf8')
    draw = ImageDraw.Draw(page)
    provenance = []
    for column, (folder, title, subtitle, colors) in enumerate(DESIGNS):
        root = ROOT / 'designs' / folder
        manifest = json.loads((root / 'manifest.json').read_text())
        rotation = np.array(json.loads((root / 'source/chosen_rotation.json').read_text())['cube_to_mechanism_matrix'])
        objects = []
        for row in manifest['parts']:
            if not row['file'].startswith('stl/puzzle/'):
                continue
            path = root / row['file']
            digest = hashlib.sha256(path.read_bytes()).hexdigest()
            assert digest == row['sha256'], path
            mesh = trimesh.load(path, force='mesh', process=False)
            transform = np.array(row['mechanism_to_print'])
            mesh.vertices = (mesh.vertices - transform[:, 3]) @ transform[:, :3]
            key = folder + '/' + row['name']
            renderer.meshes[key] = mesh
            color = colors.get(row['name'][0], '#818d98')
            objects.append((key, rotation.T, np.zeros(3), color))
            provenance.append({'file': path.relative_to(ROOT).as_posix(), 'sha256': digest})
        image = renderer.render(objects, size=tile * 2, extent=53, elev=27, az=-55)
        image = image.resize((tile, tile), Image.Resampling.LANCZOS)
        page.paste(image, (column * tile, 0))
        center = column * tile + tile / 2
        draw.text((center, 910), title, font=font(44, True), anchor='mt', fill='#273847')
        draw.text((center, 979), subtitle, font=font(26), anchor='mt', fill='#53616a')
        print('Rendered', title, flush=True)
    draw.text((1350, 1070), 'Three 64 mm cubes · the same rotated exterior · actual printable geometry',
              font=font(25), anchor='mt', fill='#53616a')
    destination = ROOT / 'docs/images/three-cubes.png'
    page.save(destination, optimize=True)
    destination.with_suffix('.json').write_text(json.dumps({
        'camera': {'elevation_deg': 27, 'azimuth_deg': -55, 'half_extent_mm': 53},
        'geometry': 'Unmodified delivered STL meshes; colors distinguish piece families for illustration.',
        'parts': provenance,
    }, indent=2) + '\n')
    print(destination, flush=True)


if __name__ == '__main__':
    main()
