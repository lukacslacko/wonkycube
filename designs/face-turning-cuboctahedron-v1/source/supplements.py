"""Part naming, exported-file hashes, source bundle and reproducibility data."""
from hardware import *
import hashlib,shutil
def run():
 meta=json.loads((DEST/'manifest.json').read_text())
 lines=['# Solved neighbors','',
 'T = triangle-face screwed center (8 copies), S = square-face screwed center (6 copies), P = floating petal (24 copies). Every copy within each type is identical. Plate labels identify placement only. All printed copies can be exchanged within their family.','',
 'Each petal spans one triangular facet and one adjacent square facet. Those facets face the corresponding T and S centers. A triangle center has three neighboring petals; a square center has four. Neighbors here share an exterior seam; contact only at a tip is excluded.','',
 '| Piece | Seam neighbors |','|---|---|']
 for row in ROWS:
  sig=set(row['signature']);near=[r['name'] for r in ROWS if len(sig.symmetric_difference(r['signature']))==1]
  assert len(near)=={'T':3,'S':4,'P':2}[row['family']]
  lines.append('| '+row['name']+' | '+', '.join(near)+' |')
 lines+=['','## Axis labels','','Coordinates use the six square-face normals as X/Y/Z. Triangle directions are listed as proportional vectors.','','| Center | Direction | Ordinary turn |','|---|---|---|']
 for row in ROWS[:14]:
  f=row['family'];n=np.array(row['direction'])*(np.sqrt(3) if f=='T' else 1)
  lines.append('| '+row['name']+' | '+', '.join(str(int(round(x))) for x in n)+' | '+('120°' if f=='T' else '90°')+' |')
 (DEST/'NEIGHBORS.md').write_text('\n'.join(lines)+'\n')
 shutil.copy2(CACHE/'rounding.json',DEST/'reports/edge-rounding.json')
 for f in ORBITS:
  for suffix in ['-morphology-trim.json']:
   p=CACHE/(f+suffix)
   if p.exists():shutil.copy2(p,DEST/'reports'/p.name)
  p=CACHE/'ridges-2'/(f+'-tip-trimming.json')
  if p.exists():shutil.copy2(p,DEST/'reports'/p.name)
 report=dict(triangle_half_angle_degrees=float(ANGLES[0]),square_half_angle_degrees=45.,square_face_spacing_mm=64,
  conical_body_gap_mm=BODY_GAP,additional_track_cutter_expansion_mm=TRACK_EXTRA,radial_ridge_radius_mm=2,
  internal_profiles_rho_z_mm={f:profile(f) for f in ['T','S']},core_radius_mm=CORE_R,moving_inner_radius_mm=INNER_R,
  core_bearing_flat_mm=CORE_PAD,bearing_foot_plane_mm=FOOT_PLANE,bearing_foot_radius_mm=FOOT_R,
  triangle_stem_top_mm=SEATS['T'],stem_sweep_radial_clearance_mm=TRACK_EXTRA,
  screw_bore_diameter_mm=3.6,washer_well_diameter_mm=2*WELL_R,washer_seats_mm=SEATS,
  nut_seat_across_flats_mm=NUT_SEAT_AF,nut_entrance_mm=NUT_ENTRY_AF,nut_roof_coordinate_mm=NUT_ROOF)
 (DEST/'reference/design-parameters.json').write_text(json.dumps(report,indent=2)+'\n')
 for p in HERE.iterdir():
  if p.is_file() and (p.suffix in ['.py','.txt','.md','.json'] or p.name=='LICENSE'):shutil.copy2(p,DEST/'source'/p.name)
 license_path=HERE/'LICENSE'
 if license_path.exists():shutil.copy2(license_path,DEST/'LICENSE')
 # The source template previews images one directory above itself.
 (DEST/'README.md').write_text((HERE/'ASSEMBLY.md').read_text().replace('(../images/', '(images/'))
 files=[p for p in sorted(DEST.rglob('*')) if p.is_file() and p.name!='SHA256SUMS.txt']
 (DEST/'SHA256SUMS.txt').write_text(''.join(hashlib.sha256(p.read_bytes()).hexdigest()+'  '+p.relative_to(DEST).as_posix()+'\n' for p in files))
 print('SUPPLEMENTS COMPLETE',flush=True)
if __name__=='__main__':run()
