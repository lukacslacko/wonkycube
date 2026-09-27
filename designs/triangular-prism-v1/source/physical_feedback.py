"""Attach the owner report only to the exact associated supplied STL set."""
from pathlib import Path
import hashlib,json

def feedback_text(destination):
    destination=Path(destination)
    record=Path(__file__).with_name('physical-feedback.json')
    if record.exists():
        data=json.loads(record.read_text())
        actual={p.relative_to(destination).as_posix():hashlib.sha256(p.read_bytes()).hexdigest()
                for p in (destination/'stl/puzzle').glob('*.stl')}
        if actual==data['supplied_puzzle_stl_sha256']:
            (destination/'physical-feedback.json').write_text(record.read_text())
            return 'On **2026-09-27**, the owner reported that this **64 mm non-wavy triangular prism printed, assembled and turns well**. The [physical feedback record](physical-feedback.json) identifies the associated supplied STL files. Exact slicer settings and the chosen optional core were not restated; no endurance or holding-force measurement was reported.'
    return ('This generated STL set has not been physically tested. The published 64 mm '
            'non-wavy design printed, assembled and turns well, but its owner report belongs '
            'to specific supplied file hashes and does not validate changed meshes.')
