"""Rebuild to a fresh folder, leaving the supplied release untouched."""
from pathlib import Path
import argparse,os,sys,subprocess,shutil
HERE=Path(__file__).resolve().parent
ap=argparse.ArgumentParser()
ap.add_argument('--out',type=Path,default=HERE.parent.parent/'rebuilt-redi-v4p3')
ap.add_argument('--from-masters',action='store_true',help='Reuse supplied final canonical internal meshes')
ap.add_argument('--validate',action='store_true')
args=ap.parse_args();build=args.out.resolve()
if build.exists():raise SystemExit('Choose a new output directory; existing output is preserved.')
build.mkdir(parents=True);os.environ['REDI_BUILD_DIR']=str(build)
import redi_design as d
if args.from_masters:
 d.OUT.mkdir(parents=True)
 for path in (HERE/'masters').glob('*'):shutil.copy(path,d.OUT/path.name)
 for name,s in d.raw_cells().items():d.save(s,d.OUT/'raw'/(name+'.npz'))
else:d.build_canonical()
def run(script,*extra):subprocess.run([sys.executable,str(HERE/script),*map(str,extra)],check=True)
run('finish_redi.py');run('export_redi.py',build/'release')
if args.validate:
 for mode in ['hardware','assembly','retention','motion','plates']:run('validate_redi.py',mode,build/'release')
 run('check_ridges_and_shapes.py',build/'release')
run('render_redi.py',build/'release')
print('Rebuilt print geometry:',build/'release')
