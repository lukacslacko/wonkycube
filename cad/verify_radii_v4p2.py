"""Check actual print-STL transverse arc radii along both ridges of every edge."""
from mechanism_v4p2 import *
import argparse,time

def front(polys,z):
    ys=[]
    for p in polys:
        a=p;b=np.roll(p,-1,axis=0);dz=b[:,1]-a[:,1]
        ok=(abs(dz)>1e-10)&(np.minimum(a[:,1],b[:,1])-1e-8<=z)&(np.maximum(a[:,1],b[:,1])+1e-8>=z)
        ys.extend((a[ok,0]+(z-a[ok,1])*(b[ok,0]-a[ok,0])/dz[ok]).tolist())
    if not ys:raise ValueError('missing front boundary')
    return min(ys)

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--out',type=Path,required=True);args=ap.parse_args();out=args.out;t=time.time()
    meta=json.loads((out/'reference/design.json').read_text());rows=json.loads((out/'reference/ridge_sections.json').read_text())
    xs=np.array([r['x_mm'] for r in rows]);cys=np.array([r['circle_center_y_mm'] for r in rows]);angles=np.array([r['half_arc_angle_rad'] for r in rows])
    records={r['name']:r for r in meta['parts']};report=[];fail=[]
    F=np.array([[0,1,0],[0,0,1],[1,0,0]]);swap=np.array([[0,1,0],[1,0,0],[0,0,-1]])
    stations=np.r_[np.arange(24.5,34.01,.125),35.5,37.5,40]
    for change in meta['radial_ridge_changes']:
        name=change['name'];Q=np.array(change['cutter_rotation']);T=np.array(records[name]['mechanism_to_print_matrix_3x4'])
        m=trimesh.load(out/'parts'/f'{name}.stl',force='mesh',process=True)
        m.vertices=((m.vertices-T[:,3])@T[:,:3])@Q
        s=from_mesh(m)
        for label,R in [('+X',np.eye(3)),('+Y',swap)]:
            local=xform(s,F@R)
            for x in stations:
                cy=float(np.interp(x,xs,cys));angle=float(np.interp(x,xs,angles));polys=local.slice(x).to_polygons()
                zs=3*np.sin(np.linspace(-.8*angle,.8*angle,41));ys=np.array([front(polys,z) for z in zs])
                radius_errors=abs(np.hypot(ys-cy,zs)-3)
                A=np.column_stack((ys,zs,np.ones_like(zs)));coeff=np.linalg.lstsq(A,-(ys*ys+zs*zs),rcond=None)[0]
                fitted_radius=float(np.sqrt(max(0,(coeff[0]**2+coeff[1]**2)/4-coeff[2])))
                row={'edge':name,'ridge':label,'station_mm':x,'fitted_radius_mm':fitted_radius,'max_error_from_nominal_circle_mm':float(radius_errors.max())}
                row['passed']=bool(abs(fitted_radius-3)<.06 and radius_errors.max()<.015)
                if not row['passed']:fail.append(f'{name} {label} x={x}')
                report.append(row)
        print(name,'radius range',min(r['fitted_radius_mm'] for r in report if r['edge']==name),max(r['fitted_radius_mm'] for r in report if r['edge']==name),flush=True)
    result={'scope':'Actual delivered print STLs, transformed back into assembly coordinates. Eighty sections on each of two ridges per edge cover the inner track every 0.125 mm from 24.5 through 34 mm, plus outer stations at 35.5, 37.5 and 40 mm. Each fit uses 41 points from the central 80% of the exposed rounding arc.',
        'nominal_radius_mm':3,'radius_taper':False,'sections':report,'passed':not fail,'failures':fail,'seconds':time.time()-t}
    (out/'reference/radius_check.json').write_text(json.dumps(result,indent=2))
    print('DONE',result['passed'],fail,flush=True)

if __name__=='__main__':main()
