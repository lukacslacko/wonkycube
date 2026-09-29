"""Nominal, foot-only radial probes with all supporting parts seated."""
from retention_v2 import *
def run():
 cells,_=load_parts();out=[]
 for family,support in [('P','C'),('K','P')]:
  r=canonical(family);s=retaining_foot(cells[r['name']]);n=np.array(r['direction']);fixed=union([v for name,v in cells.items() if name[0]==support]);cc=curve(s,n,fixed,np.arange(0,6.001,.05));rec=dict(family=family,support=support,support_lift_mm=0,foot_only=True,**summary(cc),curve=cc);print({k:v for k,v in rec.items() if k!='curve'},flush=True);out.append(rec)
 (DEST/'reports/nominal-foot-capture.json').write_text(json.dumps(out,indent=2)+'\n')
if __name__=='__main__':run()
