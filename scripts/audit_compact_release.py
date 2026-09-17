"""Audit the compact publication without rebuilding its checked geometry."""
import ast
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DESIGN = ROOT / 'designs/redi-v4.3'


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def audit():
    entries = {}
    for line in (DESIGN / 'SHA256SUMS').read_text().splitlines():
        sha, name = line.split('  ', 1)
        assert name not in entries, f'Duplicate checksum: {name}'
        entries[name] = sha
        assert digest(DESIGN / name) == sha, f'Checksum mismatch: {name}'
    actual = {p.relative_to(DESIGN).as_posix() for p in DESIGN.rglob('*')
              if p.is_file() and p.name != 'SHA256SUMS'}
    assert actual == set(entries), actual.symmetric_difference(entries)

    provenance = json.loads((DESIGN / 'publication.json').read_text())
    assert provenance['geometry_changed'] is False
    for name, sha in provenance['unchanged_files_sha256'].items():
        assert digest(DESIGN / name) == sha, f'Changed delivery file: {name}'
    for pattern in ('*.stl', '*.3mf', '*.npz'):
        for path in DESIGN.rglob(pattern):
            assert path.relative_to(DESIGN).as_posix() in provenance['unchanged_files_sha256']

    manifest = json.loads((DESIGN / 'manifest.json').read_text())
    assert manifest['version'] == 'v4.3' and manifest['cube_side_mm'] == 64
    assert len(manifest['parts']) == 28 and len(manifest['plates']) == 7
    puzzle = {p.stem for p in (DESIGN / 'stl/puzzle').glob('*.stl')}
    assert puzzle == {'core'} | {f'C{i:02}' for i in range(1, 9)} | {f'E{i:02}' for i in range(1, 13)}
    for row in manifest['parts']:
        assert digest(DESIGN / row['file']) == row['sha256']
        assert row['watertight'] and row['components'] == 1 and row['solid_volume_mm3'] > 0
        if row['role'] == 'edge':
            assert row['print_orientation'] == 'inward-radial-down-v1'
            assert max(abs(a - b) for a, b in zip(row['inward_direction_in_print_coordinates'], [0, 0, -1])) < 1e-10

    names = ('motion', 'assembly', 'hardware', 'retention', 'plates', 'ridge-radii', 'edge-shapes')
    for name in names:
        report = json.loads((DESIGN / 'reports' / f'{name}.json').read_text())
        assert report.get('_completion', {}).get('passed', report.get('passed', False)), name
        if name == 'plates':
            for row in report['plates']:
                assert digest(DESIGN / row['file']) == row['sha256']
    orientation = json.loads((DESIGN / 'reports/edge-print-orientation.json').read_text())
    assert len(orientation['edges']) == 12
    by_name = {row['name']: row for row in manifest['parts']}
    for row in orientation['edges']:
        assert row['new_sha256'] == by_name[row['name']]['sha256']
        assert row['watertight'] and row['components'] == 1
        assert abs(row['minimum_z_mm']) < 1e-5
    for path in (DESIGN / 'source').glob('*.py'):
        ast.parse(path.read_text(), filename=str(path))
    print(f'PASS compact: {len(entries)} hashed files; 28 STLs, 7 plates; delivery geometry unchanged; reports, orientation and source syntax valid')


if __name__ == '__main__':
    audit()
