"""Audit the published triangular-prism files without rerunning unchanged CAD."""
from pathlib import Path
import ast
import hashlib
import json
import re
from urllib.parse import unquote

ROOT = Path(__file__).resolve().parents[1]
DESIGN = ROOT / 'designs/triangular-prism-v1'


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    publication = json.loads((DESIGN / 'publication.json').read_text())
    manifest = json.loads((DESIGN / 'manifest.json').read_text())
    expected = publication['delivery_geometry_sha256']
    actual = {p.relative_to(DESIGN).as_posix(): digest(p)
              for p in DESIGN.rglob('*') if p.suffix in {'.stl', '.3mf'}}
    assert actual == expected, 'A supplied STL or 3MF has changed'
    manifest_hash = digest(DESIGN / 'manifest.json')
    assert manifest_hash == publication['manifest_sha256']
    for part in manifest['parts']:
        assert digest(DESIGN / part['file']) == part['sha256'], part['file']
    for name in ['motion', 'assembly', 'hardware', 'retention', 'plates', 'structure',
                 'midturn-capture', 'corner-capture', 'printability', 'ridge-radii', 'export-fidelity', 'summary']:
        report = json.loads((DESIGN / 'reports' / (name + '.json')).read_text())
        assert report['manifest_sha256'] == manifest_hash, name
        assert report.get('passed', report.get('_completion', {}).get('passed', False)), name
    feedback = json.loads((DESIGN / 'physical-feedback.json').read_text())
    printed = {p.relative_to(DESIGN).as_posix(): digest(p)
               for p in (DESIGN / 'stl/puzzle').glob('*.stl')}
    assert len(printed) == 21 and printed == feedback['supplied_puzzle_stl_sha256']
    assert feedback['physically_printed'] and feedback['reported_date'] == '2026-09-27'
    for name,expected_hash in publication['geometry_source_sha256'].items():
        assert digest(DESIGN/name)==expected_hash, name
    assert digest(DESIGN / 'physical-feedback.json') == digest(DESIGN / 'source/physical-feedback.json')
    assert (DESIGN / 'LICENSE').read_bytes() == (ROOT / 'LICENSE').read_bytes()
    for path in (DESIGN / 'source').glob('*.py'):
        ast.parse(path.read_text(), filename=str(path))
    for path in ROOT.rglob('*.md'):
        if any(p.startswith('.') for p in path.relative_to(ROOT).parts):
            continue
        for target in re.findall(r'!?\[[^\]]*\]\(([^)]+)\)', path.read_text()):
            if '://' in target or target.startswith(('#', 'mailto:')):
                continue
            local = unquote(target.split('#')[0])
            assert not local or (path.parent / local).exists(), (path, target)
    checksums = DESIGN / 'SHA256SUMS.txt'
    entries = {}
    for line in checksums.read_text().splitlines():
        checksum, name = line.split('  ', 1)
        assert digest(DESIGN / name) == checksum, name
        entries[name] = checksum
    files = {p.relative_to(DESIGN).as_posix() for p in DESIGN.rglob('*')
             if p.is_file() and p != checksums and '__pycache__' not in p.parts}
    assert files == set(entries), 'Checksum file list differs'
    print(f'PASS: {len(actual)} unchanged STL/3MF files, 21 supplied puzzle parts, '
          f'12 passing reports, source syntax, local links and {len(entries)} checksums')


if __name__ == '__main__':
    main()
