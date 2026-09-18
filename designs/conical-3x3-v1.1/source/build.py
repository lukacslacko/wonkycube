"""Regenerate and check the complete 70-degree conical 3x3 prototype."""
from pathlib import Path
import argparse,os,subprocess,sys
p=argparse.ArgumentParser();p.add_argument('--build-dir',type=Path,default=Path('conical-build'));p.add_argument('--output',type=Path,default=Path('wonky-conical-3x3-70deg-64mm-v1p1'));a=p.parse_args()
here=Path(__file__).resolve().parent;work=a.build_dir.resolve();out=a.output.resolve();work.mkdir(parents=True,exist_ok=True)
env=os.environ.copy();env.update(CONICAL_BUILD_DIR=str(work),CONICAL_SEGMENTS='192',PYTHONDONTWRITEBYTECODE='1',MPLCONFIGDIR=str(work/'matplotlib'))
def run(script,*args):
 print('Running',script,*map(str,args),flush=True);subprocess.run([sys.executable,str(here/script),*map(str,args)],env=env,check=True)
for script in ['ridge_rounding.py','regularize.py','finish_conical.py','export_conical.py']:run(script)
for mode in ['motion','assembly','hardware','retention','plates']:run('validate_conical.py',mode)
for script in ['check_ridges.py','check_midturn_capture.py','check_printability.py','check_export_fidelity.py','render_conical.py','check_root_web.py']:run(script)
run('package_release.py',work/'release',out)
