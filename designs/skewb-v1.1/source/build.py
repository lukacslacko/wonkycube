"""Regenerate geometry, export, validate, render and package the Skewb."""
from pathlib import Path
import argparse,os,subprocess,sys
p=argparse.ArgumentParser();p.add_argument('--build-dir',type=Path,default=Path('skewb-build'));p.add_argument('--output',type=Path,default=Path('wonky-skewb-64mm-v1p1'));a=p.parse_args()
here=Path(__file__).resolve().parent;work=a.build_dir.resolve();out=a.output.resolve();work.mkdir(parents=True,exist_ok=True)
env=os.environ.copy();env.update(SKEWB_BUILD_DIR=str(work),SKEWB_SEGMENTS='192',PYTHONDONTWRITEBYTECODE='1',MPLCONFIGDIR=str(work/'matplotlib'))
def run(script,*args):
 print('\nRunning',script,*map(str,args),flush=True);subprocess.run([sys.executable,str(here/script),*map(str,args)],env=env,check=True)
run('ridge_rounding.py');run('finish_skewb.py');run('export_skewb.py')
for mode in ['motion','assembly','hardware','retention','plates']:run('validate_skewb.py',mode)
run('check_ridges_shapes.py');run('check_export_surface.py');run('check_tip_revision.py');run('render_skewb.py');run('render_tip_comparison.py');run('package_release.py',work/'release',out)
