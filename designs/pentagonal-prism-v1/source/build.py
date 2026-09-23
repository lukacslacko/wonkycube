"""Generate the seven-axis geometry; checkpoints live in CONICAL_BUILD_DIR/cache."""
from conical_design import *
from ridge_rounding import rounded_cells
import subprocess,sys
if __name__=='__main__':
 t=time.time()
 cells=raw_cells();cells=build_relief(cells);cells=round_inner_cells(cells);rounded_cells(cells)
 for script in ['regularize.py','finish_conical.py']:
  subprocess.run([sys.executable,str(HERE/script)],check=True)
 print('BUILD COMPLETE',time.time()-t,flush=True)
