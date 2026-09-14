"""Compare actual rounded edge exterior profiles in both physical mounting orientations."""
from mechanism_v3 import *
from optimize_rotation import samples,flip
import time,argparse

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--out',type=Path,default=Path(__file__).resolve().parents[1]/'outputs'/'rotated-redi-80mm-v3')
    start=time.time();out=ap.parse_args().out/'reference'
    data=json.loads((out/'design.json').read_text());frames=np.array(data['rotation']['edge_frames'])
    u=samples(15);z=np.load(out/'assembly_meshes.npz');profiles=[]
    for i,Q in enumerate(frames):
        name=f'E{i+1:02}';m=trimesh.Trimesh(z[name+'_v'],z[name+'_f'],process=False)
        dirs=np.concatenate((u,u@flip.T))@Q.T
        locations,index,_=m.ray.intersects_location(np.zeros_like(dirs),dirs,multiple_hits=True)
        h=np.full(len(dirs),np.nan)
        for ray in np.unique(index):h[ray]=np.max(np.linalg.norm(locations[index==ray],axis=1))
        profiles.append(h.reshape(2,-1));print(name,'directions',len(u),'missed',np.isnan(h).sum(),flush=True)
    h=np.array(profiles);valid=np.isfinite(h).all(axis=(0,1));h=h[:,:,valid]
    pairs=[]
    for i,j in itertools.combinations(range(12),2):
        rms=np.sqrt(np.mean((h[i,0]-h[j])**2,axis=1))
        pairs.append({'edges':[i+1,j+1],'minimum_RMS_mm':float(rms.min())})
    report={'samples_per_edge_orientation':len(u),'common_valid_directions':int(valid.sum()),'proper_mounting_orientations_per_pair':2,
        'minimum_pair_RMS_mm':min(p['minimum_RMS_mm'] for p in pairs),'all_66_pairs_distinct_in_sampled_exterior':all(p['minimum_RMS_mm']>.1 for p in pairs),
        'scope':'Actual rounded exported assembly meshes. Equal-solid-angle radial samples in both proper self-isometries of the common attachment lens; reflections are excluded. Rotation retained from the original search, not reoptimized for this revision. A distinction test, not a proof of global optimality or of every forced insertion attempt.',
        'pairs':pairs,'seconds':time.time()-start}
    (out/'edge_shape_check.json').write_text(json.dumps(report,indent=2));print('DONE',report['minimum_pair_RMS_mm'],flush=True)

if __name__=='__main__':main()
