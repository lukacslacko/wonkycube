"""Check shipped file hashes, reports and local Markdown links using stdlib."""
import hashlib
import json
from pathlib import Path
import re
from urllib.parse import unquote

ROOT = Path(__file__).resolve().parents[1]
MODEL = ROOT / 'models/current'


def main():
    failures = []
    manifest = MODEL / 'SHA256SUMS.txt'
    entries = {}
    for line in manifest.read_text().splitlines():
        digest, name = line.split('  ', 1)
        path = MODEL / name
        entries[name] = digest
        if not path.is_file() or hashlib.sha256(path.read_bytes()).hexdigest() != digest:
            failures.append(f'Changed or missing release file: {name}')
    actual = {p.relative_to(MODEL).as_posix() for p in MODEL.rglob('*') if p.is_file() and p != manifest}
    if actual != set(entries):
        failures.append(f'Manifest file set differs: {actual.symmetric_difference(entries)}')
    for name, key in [('verification.json', 'passed'), ('ridge_revision_check.json', 'passed'),
                      ('radius_check.json', 'passed'), ('edge_shape_check.json', 'all_66_pairs_distinct_in_sampled_exterior')]:
        report = json.loads((MODEL / 'reference' / name).read_text())
        if report.get(key) is not True:
            failures.append(f'Failed report: {name}')
    if len(list((MODEL / 'parts').glob('*.stl'))) != 21:
        failures.append('Expected 21 puzzle STLs')
    if len(list((MODEL / 'calibration').glob('*.stl'))) != 7:
        failures.append('Expected seven fixture/jig STLs')
    for path in ROOT.rglob('*.md'):
        if any(part.startswith('.') for part in path.relative_to(ROOT).parts):
            continue
        for target in re.findall(r'!?\[[^\]]*\]\(([^)]+)\)', path.read_text()):
            if '://' in target or target.startswith(('#', 'mailto:')):
                continue
            local = unquote(target.split('#')[0])
            if local and not (path.parent / local).exists():
                failures.append(f'Broken local link: {path.relative_to(ROOT)} -> {target}')
    if failures:
        raise SystemExit('\n'.join(failures))
    print(f'PASS: {len(entries)} released files, four reports, 28 STLs and local document links')


if __name__ == '__main__':
    main()
