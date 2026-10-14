"""Regenerate pocketed STLs and cutting outlines from bundled mesh masters."""
import subprocess,sys,os
from pathlib import Path
HERE=Path(__file__).resolve().parent
steps=['prepare.py','inlays.py','caps.py','export.py','cutting.py','supplements.py','validate.py','retention_v2.py','render.py','check_rounding.py']
for step in steps:
 print('RUN',step,flush=True)
 subprocess.run([sys.executable,str(HERE/step)],check=True,env=os.environ.copy())
print('Build complete. SVG/DXF are ready. Genuine DWG conversion is optional; see BUILD.md.',flush=True)
