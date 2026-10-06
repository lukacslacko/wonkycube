"""Regenerate in a new build folder after changing geometry or resolution."""
from design import *
import subprocess,sys
if __name__=='__main__':
 relief(raw())
 for script,args in [('finish.py',[]),('caps.py',['--prepare']),('inlays.py',[]),('caps.py',[]),('export.py',[]),('cap_coupons.py',[]),('validate.py',[]),('spherical_report.py',[]),('validate_inlays.py',[]),('validate_caps.py',[]),('cutting.py',[]),('printable_inlays.py',[]),('validate_rigid_inlays.py',[]),('render.py',[]),('retention_drawing.py',[])]:
  subprocess.run([sys.executable,str(HERE/script)]+args,check=True)
 # ODA is a separately installed converter, never bundled with this design.
 oda=os.environ['ODA_FILE_CONVERTER'];(CACHE/'dwg-output').mkdir(exist_ok=True)
 subprocess.run([oda,str((CACHE/'dwg-source').resolve()),str((CACHE/'dwg-output').resolve()),'ACAD2000','DWG','0','1','*.dxf'],check=True)
 subprocess.run([sys.executable,str(HERE/'cutting.py'),'--verify-dwg'],check=True)
 for script in ['release_audit.py','supplements.py','package.py']:subprocess.run([sys.executable,str(HERE/script)],check=True)
 print('Generated and checked',DEST,flush=True)
