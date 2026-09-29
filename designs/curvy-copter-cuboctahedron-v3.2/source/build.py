"""Run in a fresh directory: canonical geometry caches are parameter-specific."""
from design import *
import subprocess,sys
if __name__=='__main__':
 relief(raw())
 for script in ['finish.py','export.py','structure.py','neck_web.py','spherical_report.py','validate.py','retention_v2.py','nominal_capture.py','rocking.py','stress_jumbling.py','render.py','illustrate.py','test_patch.py','package_audit.py','supplements.py']:
  subprocess.run([sys.executable,str(HERE/script)],check=True)
 print('Generated and geometrically checked:',os.environ.get('CUBOCTA_RELEASE',WORK/'release'))
