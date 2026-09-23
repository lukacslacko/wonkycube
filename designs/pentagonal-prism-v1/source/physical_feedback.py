"""Associate physical feedback only with the exact supplied puzzle STLs."""
from pathlib import Path
import hashlib, json

def matching_feedback(destination):
    destination = Path(destination)
    record = Path(__file__).with_name('physical-feedback.json')
    if not record.is_file():
        return None
    data = json.loads(record.read_text())
    expected = data['printed_part_sha256']
    actual = {p.relative_to(destination).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
              for p in (destination / 'stl/puzzle').glob('*.stl')}
    if actual != expected:
        return None
    (destination / 'physical-feedback.json').write_text(record.read_text())
    return data

def feedback_text(destination):
    if matching_feedback(destination):
        return 'On **2026-09-23**, the owner reported that this puzzle **built together very well** and that the **nut-slot sizing is well tuned**. The printed core used the default **5.20 mm terminal seat**. The [physical feedback record](physical-feedback.json) includes the supplied part hashes and the Bambu P1S/PLA settings used. Turning smoothness and long-term wear were not separately assessed in that report.'
    return ('This generated set has not been physically tested. The published design has an owner '
            'report of successful assembly and satisfactory nut-slot fit, but that report is tied '
            'to specific supplied STL hashes and does not validate changed or regenerated meshes.')
