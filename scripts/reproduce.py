"""Build and verify a fresh publication export without overwriting a release."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out', type=Path, default=ROOT / 'build/reproduced')
    args = parser.parse_args()
    out = args.out.resolve()
    if out.exists():
        parser.error(f'Output already exists: {out}; choose a fresh directory.')
    env = os.environ.copy()
    env.setdefault('MPLCONFIGDIR', str(ROOT / '.mpl-cache'))
    base = ROOT / 'cad/baseline'
    steps = [
        ('build_v4p2.py', ['--base', str(base), '--out', str(out)], None, None),
        ('verify_v3.py', ['--out', str(out)], 'verification.json', 'passed'),
        ('verify_v4p2.py', ['--base', str(base), '--out', str(out)], 'ridge_revision_check.json', 'passed'),
        ('verify_radii_v4p2.py', ['--out', str(out)], 'radius_check.json', 'passed'),
        ('check_edge_shapes_v3.py', ['--out', str(out)], 'edge_shape_check.json', 'all_66_pairs_distinct_in_sampled_exterior'),
    ]
    for script, options, report_name, result_key in steps:
        print(f'Running {script}', flush=True)
        subprocess.run([sys.executable, str(ROOT / 'cad' / script), *options], check=True, cwd=ROOT, env=env)
        if report_name:
            report = json.loads((out / 'reference' / report_name).read_text())
            if report.get(result_key) is not True:
                raise RuntimeError(f'{report_name} failed: {report.get("failures", report)}')
    subprocess.run([sys.executable, str(ROOT / 'cad/draw_v4p2.py'), '--base', str(base), '--out', str(out)], check=True, cwd=ROOT, env=env)
    sums = ''.join(f'{hashlib.sha256(p.read_bytes()).hexdigest()}  {p.relative_to(out).as_posix()}\n'
                   for p in sorted(out.rglob('*')) if p.is_file() and p.name != 'SHA256SUMS.txt')
    (out / 'SHA256SUMS.txt').write_text(sums)
    print(f'Build and all checks passed: {out}')


if __name__ == '__main__':
    main()
