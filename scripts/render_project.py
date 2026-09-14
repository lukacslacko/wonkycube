"""Render actual released meshes for the project README."""
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'cad'))
from mechanism_v3 import *
from build_v4 import load_parts
import mesh_render as renderer
from PIL import Image,ImageDraw,ImageFont
from matplotlib.font_manager import findfont

def main():
    parts=load_parts(ROOT/'models/current');renderer.meshes={k:mesh(v) for k,v in parts.items()}
    page=Image.new('RGB',(1680,1050),'#fafaf8');d=ImageDraw.Draw(page)
    normal=findfont('DejaVu Sans');bold=findfont('DejaVu Sans:weight=bold')
    def text(xy,s,size=24,heavy=False,color='#244a3e'):
        d.text(xy,s,font=ImageFont.truetype(bold if heavy else normal,size),fill=color)
    text((55,30),'WONKYCUBE',46,True)
    text((57,99),'A rotated exterior. A corner-turning mechanism. Twelve distinct edges.',25)
    names=['core']+[f'C{i:02}' for i in range(1,9)]+[f'E{i:02}' for i in range(1,13)]
    R=np.array(json.loads((ROOT/'cad/chosen_rotation.json').read_text())['cube_to_mechanism_matrix'])
    colors=['#80ad9b','#a6c4b4','#d3b681','#b0bac3','#b9c58c','#d0ad96']
    for mode in [0,1]:
        objects=[]
        for name in names:
            color='#929d9b' if name=='core' else ('#ded6c5' if name.startswith('C') else colors[(int(name[1:])-1)%6])
            shift=np.zeros(3)
            if mode==1:
                if name=='C08':shift=AXES[7]*37
                if name=='E12':shift=np.array([1,1,0])*18
            objects.append((name,R.T if mode==0 else np.eye(3),shift,color))
        im=renderer.render(objects,size=810,extent=73 if mode==0 else 88,elev=28 if mode==0 else 25,az=45)
        page.paste(im,(30+810*mode,158))
    text((65,174),'Solved exterior',26,True)
    text((890,174),'Mechanism revealed',26,True)
    text((65,927),'80 mm cube • face planes rotated relative to the axes',22)
    text((890,927),'C08 and E12 displaced to show the interior',22)
    text((57,996),'Actual v4.2.1 meshes · colors identify pieces for illustration · MIT licensed',20,color='#61716a')
    page.save(ROOT/'docs/images/wonkycube.png')

if __name__=='__main__':main()
