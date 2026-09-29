"""Audit the Curvy Copter cuboctahedron publication without changing tested CAD."""
from pathlib import Path
import ast
import hashlib
import json
import re
from urllib.parse import unquote

ROOT = Path(__file__).resolve().parents[1]
DESIGN = ROOT / 'designs/curvy-copter-cuboctahedron-v3.2'


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    publication = json.loads((DESIGN / 'publication.json').read_text())
    manifest = json.loads((DESIGN / 'manifest.json').read_text())
    geometry = {p.relative_to(DESIGN).as_posix(): digest(p)
                for p in DESIGN.rglob('*') if p.suffix in {'.stl', '.3mf'}}
    assert geometry == publication['delivery_geometry_sha256']
    assert digest(DESIGN / 'manifest.json') == publication['manifest_sha256']
    for part in manifest['parts']:
        assert digest(DESIGN / part['file']) == part['sha256'], part['file']
    puzzle = [r for r in manifest['parts'] if '/puzzle/' in r['file']]
    assert {r['family']: r['quantity'] for r in puzzle} == {'C': 12, 'P': 24, 'K': 8, 'core': 1}
    for group in ['geometry_source_sha256', 'original_report_sha256']:
        for path, expected in publication[group].items():
            assert digest(DESIGN / path) == expected, path
    summary = json.loads((DESIGN / 'reports/summary.json').read_text())
    assert summary['passed'] and summary['normal_turn_checks'] == 12
    feedback = json.loads((DESIGN / 'physical-feedback.json').read_text())
    assert feedback['physically_printed'] and feedback['physically_assembled']
    assert feedback['manifest_sha256'] == publication['manifest_sha256']
    assert feedback['supplied_puzzle_stl_sha256'] == {r['file']: r['sha256'] for r in puzzle}
    assert 'printed and built very well' in feedback['report']
    assert (DESIGN / 'LICENSE').read_bytes() == (ROOT / 'LICENSE').read_bytes()
    for path in (DESIGN / 'source').glob('*.py'):
        ast.parse(path.read_text(), filename=str(path))
    entries = {}
    for line in (DESIGN / 'SHA256SUMS').read_text().splitlines():
        checksum, name = line.split('  ', 1)
        assert digest(DESIGN / name) == checksum, name
        entries[name] = checksum
    actual = {p.relative_to(DESIGN).as_posix() for p in DESIGN.rglob('*')
              if p.is_file() and p.name != 'SHA256SUMS' and '__pycache__' not in p.parts}
    assert actual == set(entries)
    for path in ROOT.rglob('*.md'):
        if any(p.startswith('.') for p in path.relative_to(ROOT).parts):
            continue
        for target in re.findall(r'!?\[[^\]]*\]\(([^)]+)\)', path.read_text()):
            if '://' in target or target.startswith(('#', 'mailto:')):
                continue
            local = unquote(target.split('#')[0])
            assert not local or (path.parent / local).exists(), (path, target)
    print(f'PASS: {len(geometry)} unchanged STL/3MF files, 45 puzzle parts, '
          f'{len(publication["original_report_sha256"])} unchanged reports, '
          f'CAD hashes, feedback, MIT license, local links and {len(entries)} checksums')


if __name__ == '__main__':
    main()
