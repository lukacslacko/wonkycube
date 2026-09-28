"""Regenerate in a new build folder after changing geometry or resolution."""
from design import *
import subprocess,sys
if __name__=='__main__':
 relief(raw())
 for script in ['finish.py','export.py','validate.py','render.py','supplements.py','package.py']:
  subprocess.run([sys.executable,str(HERE/script)],check=True)
 print('Generated and checked',DEST,flush=True)
