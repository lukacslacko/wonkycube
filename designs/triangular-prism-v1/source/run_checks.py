"""Run independent delivery audits and preserve separate logs for each."""
from conical_design import *
from concurrent.futures import ThreadPoolExecutor,as_completed
import subprocess,sys
DEST=Path(sys.argv[1]) if len(sys.argv)>1 else WORK/'release'
jobs=[('hardware',['validate_conical.py','hardware']),('structure',['check_structure.py']),('motion',['validate_conical.py','motion']),('assembly',['validate_conical.py','assembly']),('retention',['validate_conical.py','retention']),('printability',['check_printability.py']),('midturn-capture',['check_midturn_capture.py']),('ridge-radii',['check_ridges.py']),('export-fidelity',['check_export_fidelity.py']),('plates',['validate_conical.py','plates'])]
logs=WORK/'logs';logs.mkdir(parents=True,exist_ok=True)
def run(job):
 name,args=job;t=time.time();path=logs/(name+'.log')
 with path.open('w') as log:result=subprocess.run([sys.executable,str(HERE/args[0]),*args[1:],str(DEST)],stdout=log,stderr=subprocess.STDOUT)
 print(('PASS' if result.returncode==0 else 'FAIL'),name,round(time.time()-t,1),'s',flush=True)
 if result.returncode:print('\n'.join(path.read_text().splitlines()[-14:]),flush=True)
 return name,result.returncode
if __name__=='__main__':
 with ThreadPoolExecutor(max_workers=4) as pool:results=list(pool.map(run,jobs))
 (logs/'status.json').write_text(json.dumps(dict(results),indent=2))
 sys.exit(any(code for name,code in results))
