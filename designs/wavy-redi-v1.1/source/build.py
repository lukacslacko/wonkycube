"""Rebuild the design and validate the actual exported files."""
from pathlib import Path
import argparse,os,subprocess,sys
HERE=Path(__file__).resolve().parent
p=argparse.ArgumentParser();p.add_argument('--work',type=Path,default=HERE.parent/'build');p.add_argument('--output',type=Path,default=HERE.parent/'rebuilt');args=p.parse_args()
work=args.work.resolve();dest=args.output.resolve();work.mkdir(parents=True,exist_ok=True);dest.mkdir(parents=True,exist_ok=True)
env=os.environ.copy();env['WAVY_BUILD_DIR']=str(work);env['WAVY_SEG']='240';env['MPLCONFIGDIR']=str(work/'matplotlib-cache')
def run(script,*args):subprocess.run([sys.executable,str(HERE/script),*map(str,args)],cwd=HERE,env=env,check=True)
run('redi_design.py');run('round_ridges.py');run('finish_parts.py');run('export_parts.py',dest)
for mode in ['motion','assembly','retention','hardware','strength','ridges','plates','exterior']:run('validate_parts.py',mode,dest)
run('render_parts.py',dest);run('render_profile.py',dest);run('write_docs.py',dest);run('summarize_validation.py',dest)
print('Complete:',dest)
