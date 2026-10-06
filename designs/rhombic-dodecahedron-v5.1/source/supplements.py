"""Part naming, exported-file hashes, source bundle and reproducibility data."""
from hardware import *
import hashlib,shutil
def run():
 meta=json.loads((DEST/'manifest.json').read_text())
 lines=['# Solved neighbors','',
 'T = threefold screwed center (8 copies), S = fourfold screwed center (6 copies), P = floating petal (24 copies). Every plastic copy within a type is identical; colored inlays identify the solved placement.','',
 'Each petal borders one T and one S center and straddles two rhombic faces. A T center has three neighboring petals; an S center has four. Neighbors here share an exterior seam; contact only at a tip is excluded.','',
 '| Piece | Seam neighbors |','|---|---|']
 for row in ROWS:
  sig=set(row['signature']);near=[r['name'] for r in ROWS if len(sig.symmetric_difference(r['signature']))==1]
  assert len(near)=={'T':3,'S':4,'P':2}[row['family']]
  lines.append('| '+row['name']+' | '+', '.join(near)+' |')
 lines+=['','## Axis labels','','Coordinates use the six fourfold vertices as X/Y/Z. Threefold directions are listed as proportional vectors.','','| Center | Direction | Ordinary turn |','|---|---|---|']
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
 report=dict(threefold_half_angle_degrees=float(ANGLES[0]),fourfold_half_angle_degrees=45.,opposite_face_spacing_mm=2*FACE_HEIGHT,opposite_fourfold_vertex_spacing_mm=2*VERTEX_RADIUS,
  conical_body_gap_mm=BODY_GAP,additional_track_cutter_expansion_mm=TRACK_EXTRA,radial_ridge_radius_mm=2,
  internal_profiles_rho_z_mm={f:profile(f) for f in ['T','S']},core_radius_mm=CORE_R,moving_inner_radius_mm=INNER_R,
  core_bearing_flat_mm=CORE_PAD,bearing_foot_plane_mm=FOOT_PLANE,bearing_foot_radius_mm=FOOT_R,
  triangle_stem_top_mm=SEATS['T'],stem_sweep_radial_clearance_mm=TRACK_EXTRA,
  screw_bore_diameter_mm=3.6,washer_well_diameter_mm=2*WELL_R,washer_seats_mm=SEATS,
  nut_seat_across_flats_mm=NUT_SEAT_AF,nut_entrance_mm=NUT_ENTRY_AF,nut_roof_coordinate_mm=NUT_ROOF)
 report['retention']=dict(type='concentric spherical shells',center=[0,0,0],shoulder_radius_mm=SHOULDER_R,outer_return_radius_mm=COLLAR_OUTER_R,neck_half_angles_degrees=NECK_ANGLES,bearing_clearance_per_face_mm=BODY_GAP+TRACK_EXTRA,radial_flange_thickness_mm=COLLAR_OUTER_R-SHOULDER_R-2*(BODY_GAP/2+TRACK_EXTRA),radial_groove_width_mm=COLLAR_OUTER_R-SHOULDER_R+BODY_GAP,flange_end_outline_radius_mm=FLANGE_OUTLINE_RADIUS,assembly_relief=False)
 report['inlays']=dict(thickness_mm=2,depth_mm=2.1,minimum_between_pockets_mm=1.6,nominal_rim_mm=1,minimum_floor_web_mm=1.2,minimum_lateral_web_mm=.775,nominal_foam_compression_per_side_mm=.04,total_inlays=96)
 report['printable_inlays']=meta.get('printable_inlays')
 report['plugs']=json.loads((CACHE/'caps.json').read_text())
 report['opposite_threefold_vertex_spacing_mm']=2*FACE_HEIGHT*np.sqrt(1.5)
 (DEST/'reference/design-parameters.json').write_text(json.dumps(report,indent=2)+'\n')
 for f in ['T','S']:shutil.copy2(CACHE/f'flange-rounding-{f}.json',DEST/'reports'/f'flange-rounding-{f}.json')
 for p in HERE.iterdir():
  if p.is_file() and (p.suffix in ['.py','.txt','.md','.json'] or p.name=='LICENSE'):shutil.copy2(p,DEST/'source'/p.name)
 for name in ['physical-feedback.json','VALIDATION.md']:
  if (HERE/name).exists():
   text=(HERE/name).read_text().replace('(../physical-feedback.json)', '(physical-feedback.json)')
   (DEST/name).write_text(text)
 license_path=HERE/'LICENSE'
 if license_path.exists():shutil.copy2(license_path,DEST/'LICENSE')
 # The source template previews images one directory above itself.
 (DEST/'README.md').write_text((HERE/'ASSEMBLY.md').read_text().replace('(../images/', '(images/').replace('(../physical-feedback.json)', '(physical-feedback.json)').replace('(../VALIDATION.md)', '(VALIDATION.md)'))
 files=[p for p in sorted(DEST.rglob('*')) if p.is_file() and p.name!='SHA256SUMS.txt']
 (DEST/'SHA256SUMS.txt').write_text(''.join(hashlib.sha256(p.read_bytes()).hexdigest()+'  '+p.relative_to(DEST).as_posix()+'\n' for p in files))
 print('SUPPLEMENTS COMPLETE',flush=True)
if __name__=='__main__':run()
