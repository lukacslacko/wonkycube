"""Package the audited v4.3 delivery; never rebuild or alter the source meshes."""
import argparse
import hashlib
from pathlib import Path
import tempfile
import shutil
import zipfile

from audit_compact_release import DESIGN, audit


def archive(source, target, root):
    # Stable file order and timestamps make publication archives reproducible.
    with zipfile.ZipFile(target, 'w', zipfile.ZIP_DEFLATED, compresslevel=6) as z:
        for path in sorted(p for p in source.rglob('*') if p.is_file()):
            info = zipfile.ZipInfo(str(Path(root) / path.relative_to(source)), (2026, 1, 1, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o100644 << 16
            z.writestr(info, path.read_bytes())
    with zipfile.ZipFile(target) as z:
        assert z.testzip() is None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--out', type=Path, required=True)
    out = ap.parse_args().out.resolve()
    audit()
    out.mkdir(parents=True, exist_ok=True)
    full = out / 'wonkycube-v4.3-64mm-full.zip'
    edges = out / 'wonkycube-v4.3-64mm-edges-radial-down.zip'
    sums = out / 'wonkycube-v4.3-SHA256SUMS.txt'
    for path in (full, edges, sums):
        if path.exists():
            raise SystemExit(f'Preserving existing file: {path}')
    archive(DESIGN, full, 'wonkycube-v4.3-64mm')
    with tempfile.TemporaryDirectory() as tmp:
        stage = Path(tmp)
        for path in (DESIGN / 'stl/puzzle').glob('E*.stl'):
            shutil.copy2(path, stage / path.name)
        for name in ('LICENSE', 'NEIGHBORS.md'):
            shutil.copy2(DESIGN / name, stage / name)
        (stage / 'README.txt').write_text(
            'Wonkycube v4.3: twelve compact 64 mm edges, radial inward down (-Z).\n'
            'Millimetres, 100% scale. Keep the supplied print orientation.\n'
            'For the compact v4.3 only; these do not fit the 80 mm versions.\n'
            'The full release supplies the core, corners, CAD, assembly and validation.\n'
            'Known core issue: locknuts can spin. A tighter terminal nut seat is\n'
            'documented as a future core-only change, not implemented in this release.\n'
            'https://github.com/lukacslacko/wonkycube/releases/tag/v4.3\n')
        files = sorted(stage.iterdir())
        (stage / 'SHA256SUMS').write_text(''.join(
            hashlib.sha256(p.read_bytes()).hexdigest() + '  ' + p.name + '\n' for p in files))
        archive(stage, edges, 'wonkycube-v4.3-64mm-edges-radial-down')
    sums.write_text(''.join(hashlib.sha256(p.read_bytes()).hexdigest() + '  ' + p.name + '\n'
                            for p in (full, edges)))
    print(sums.read_text(), end='')


if __name__ == '__main__':
    main()
