from pathlib import Path
import json,math
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import Paragraph
from reportlab.lib.styles import ParagraphStyle
from pypdf import PdfReader
ROOT=Path(__file__).resolve().parents[3];A=ROOT/'docs/solving/triangular-prism/figures';OUT=ROOT/'docs/solving/triangular-prism-solving-guide.pdf'
DATA=json.loads((ROOT/'docs/solving/triangular-prism/algorithms.json').read_text())
for n,f in [('Body','Arial.ttf'),('Bold','Arial Bold.ttf'),('Italic','Arial Italic.ttf')]:pdfmetrics.registerFont(TTFont(n,'/System/Library/Fonts/Supplemental/'+f))
W,H=A4;c=canvas.Canvas(str(OUT),pagesize=A4)
c.setTitle('Wonky triangular prism - full illustrated solving guide')
c.setAuthor('Wonkycube');c.setSubject('Complete shape solution for the 64 mm non-wavy triangular prism; verified algorithms and setup tables.')
ink='#243b49';muted='#536775';paper='#fafaf8';rule='#dce3e5';pal={'C':'#32846a','V':'#377fac','H':'#ae6082','K':'#b77c14'}
checks=[];pg=0

def fill(col):c.setFillColor(colors.HexColor(col))
def text(x,y,s,size=11,font='Body',color=ink):
 fill(color);c.setFont(font,size);c.drawString(x,y,s)
 assert x+pdfmetrics.stringWidth(s,font,size)<W-20,(pg,s)
def centered(x,y,s,size=11,font='Body',color=ink):
 fill(color);c.setFont(font,size);c.drawCentredString(x,y,s)
def para(s,x,top,width,size=10.6,leading=14.5,color=ink):
 st=ParagraphStyle('body',fontName='Body',fontSize=size,leading=leading,textColor=colors.HexColor(color))
 p=Paragraph(s.replace('<b>','<font name="Bold">').replace('</b>','</font>').replace('<i>','<font name="Italic">').replace('</i>','</font>'),st)
 ww,hh=p.wrap(width,H);p.drawOn(c,x,top-hh);checks.append({'page':pg,'top':top,'bottom':top-hh,'text':s[:100]});assert top-hh>48,(pg,s,hh);return hh

def line(x1,y1,x2,y2,col=rule,w=.7):c.setStrokeColor(colors.HexColor(col));c.setLineWidth(w);c.line(x1,y1,x2,y2)
def arrow(x1,y1,x2,y2,col=muted,w=1.3):
 line(x1,y1,x2,y2,col,w);a=math.atan2(y2-y1,x2-x1)
 for d in [-.5,.5]:line(x2-6*math.cos(a+d),y2-6*math.sin(a+d),x2,y2,col,w)
def box(x,y,w,h,col='#edf2f4'):fill(col);c.roundRect(x,y,w,h,7,stroke=0,fill=1)
def page(n,kicker,title,sub):
 global pg;pg=n
 fill(paper);c.rect(0,0,W,H,stroke=0,fill=1)
 text(32,811,kicker,9,'Bold',muted);text(32,779,title,24,'Bold')
 para(sub,32,760,531,10.6,14)
 line(32,43,563,43);text(32,26,'WONKY TRIANGULAR PRISM  |  64 mm non-wavy design  |  October 2026',8,'Body',muted)
 text(538,26,f'{n} / 9',8,'Body',muted)
 c.bookmarkPage(f'page{n}');c.addOutlineEntry(title,f'page{n}',0)
def end():c.showPage()
def pic(name,x,y,w):c.drawImage(str(A/(name+'.png')),x,y,width=w,height=w)
def node(x,y,label,col,r=22):
 fill(col);c.circle(x,y,r,stroke=0,fill=1);centered(x,y-3.5,label,10.5,'Bold','#ffffff')
def cycle(labels,x,y,w=176,h=104,col=None):
 pts=[(x,y),(x+w,y),(x+w/2,y-h)];cc=col or ['#377fac','#ae6082','#b77c14']
 for i in range(3):
  a,b=pts[i],pts[(i+1)%3];v=(b[0]-a[0],b[1]-a[1]);d=math.hypot(*v)
  arrow(a[0]+v[0]*26/d,a[1]+v[1]*26/d,b[0]-v[0]*26/d,b[1]-v[1]*26/d)
 for (xx,yy),lab,color in zip(pts,labels,cc):node(xx,yy,lab,color)
def macro(key,top=716):
 box(32,top-62,531,62)
 text(45,top-22,key+' = '+DATA['macros'][key]['word'],13.2,'Courier-Bold')
 text(45,top-44,key+"' = "+DATA['macros'][key]['inverse'],11.2,'Courier',muted)
def smalltable(headers,rows,x,top,width,cols,rowh=22,fs=10.5,fonts=None):
 box(x,top-rowh,width,rowh,'#e4ecef')
 for xx,head in zip(cols,headers):text(x+xx,top-rowh+7,head,9.5,'Bold')
 for i,row in enumerate(rows):
  yy=top-(i+2)*rowh
  if i%2==0:fill('#eff3f3');c.rect(x,yy,width,rowh,stroke=0,fill=1)
  for j,(xx,v) in enumerate(zip(cols,row)):text(x+xx,yy+7,str(v),fs,(fonts or ['Body']*len(cols))[j])
 return top-(len(rows)+1)*rowh

def setup_table(fam,top):
 rows=[(' > '.join(r['slots']),r['setup'] or '-',r['use'],r['undo'] or '-') for r in DATA['tables'][fam]]
 return smalltable(['Cycle of occupants','Setup S','Use','Undo S'],rows,32,top,531,[10,214,351,399],21,10.2,['Body','Courier','Bold','Courier'])

# 1 - overview
page(1,'FULL SOLUTION GUIDE','Solve the wonky triangular prism','For the successfully printed 64 mm, non-wavy shape mod. Restore the cube shape, including the orientation of every screwed center.')
pic('front',24,447,276);pic('back',295,447,276)
centered(162,451,'Front and above',10,'Bold');centered(433,451,'Back and below',10,'Bold')
para('The colors only distinguish piece families in this guide. Your puzzle can be one color: use its shape and the solved reference views to recognize each piece\'s home.',32,428,531,10.5,14)
for x,f,count,name in [(32,'C','5','screwed centers'),(170,'V','3','vertical petals'),(308,'H','6','horizontal petals'),(446,'K','6','corners')]:
 fill(pal[f]);c.circle(x+6,373,5,stroke=0,fill=1);text(x+18,369,count+' '+name,9.5,'Bold')
text(32,334,'The solving order',17,'Bold')
phases=[('1','Vertical petals','Place all three, then fix any pair of flips.','4'),('2','Screwed centers','Fix the side centers, then the two poles.','4'),('3','Horizontal petals','Use three-cycles; their orientation follows their position.','5-6'),('4','Floating corners','Finish with corner-only three-cycles.','7-8')]
for i,(num,title,desc,pages) in enumerate(phases):
 y=274-51*i;box(32,y,531,45)
 node(54,y+23,num,pal[['V','C','H','K'][i]],13)
 text(79,y+27,title,11.4,'Bold');text(79,y+11,desc,9.8);text(516,y+24,'p. '+pages,9.2,'Bold',muted)
para('<b>Already solved the petals and all five centers?</b> Go straight to page 7. For the full method, first establish the fixed axis names on page 2 and the slot names on page 3.',32,103,531,10.5,14)
end()

# 2 - notation
page(2,'REFERENCE  |  READ THIS FIRST','Five axes, two move sizes','The prism is tilted inside the cube. U and D are the opposing polar screws, not necessarily the top and bottom faces of the solved cube.')
pic('atlas-front',22,437,287)
# Top-view reference schematic: front at bottom, R on the right.
cx,cy=436,582
pF=(cx,cy-86);pBR=(cx+78,cy+45);pBL=(cx-78,cy+45)
for a,b in [(pF,pBR),(pBR,pBL),(pBL,pF)]:line(*a,*b,'#aab9c0',1.3)
node(cx+48,cy-26,'R',pal['C'],22);node(cx-48,cy-26,'L',pal['C'],22);node(cx,cy+62,'B',pal['C'],22);node(cx,cy,'U',pal['C'],19)
centered(cx,cy-112,'FRONT',9,'Bold',muted);centered(cx,cy+99,'Looking down the U axis',10,'Bold')
para('R is the right-front side axis; L is the left-front one; B is behind. D is opposite U. Keep these names fixed even when you change your grip.',323,455,234,10.5,14)
smalltable(['Move','Printed center','Amount'],[('R','C02','180 degrees'),('L','C01','180 degrees'),('B','C03','180 degrees'),('U / U\'','C04','120 degrees CW / CCW'),('D / D\'','C05','120 degrees CW / CCW')],32,384,531,[12,126,275],24,11,['Bold','Body','Body'])
para('<b>Clockwise means looking from outside straight into that axis\'s screw hole.</b> Judge D from underneath. R, L and B are half-turns; either direction has the same final effect. U\' and D\' undo U and D.',32,224,531,11,15)
box(32,112,531,53)
text(45,146,"R U' R U",15,'Courier-Bold');text(196,146,'Read moves from left to right.',11,'Bold')
text(45,126,'Half-turn R; counterclockwise U; half-turn R; clockwise U.',10.5)
para('Turn the entire layer attached to the chosen axis, with every piece it carries. Finish each 180- or 120-degree step before starting the next move. The solved cube outline may disappear during an algorithm.',32,98,531,10.3,14)
end()

# 3 - slot map
page(3,'REFERENCE  |  SOLVED LOCATIONS','Know which piece belongs where','Labels name fixed slots, not pieces traveling with a turn. These are solved views: use the outlines to identify the correct piece and its final orientation.')
pic('atlas-top',24,445,273);pic('atlas-bottom',298,445,273)
centered(160,445,'Looking toward U',10,'Bold');centered(435,445,'Looking toward D from the back',10,'Bold')
text(32,413,'Three vertical petals',13,'Bold',pal['V'])
smalltable(['Slot','Location','Printed part'],[('F','Between L and R','V01'),('BR','Between B and R','V03'),('BL','Between B and L','V02')],32,400,531,[10,106,412],22,10.5,['Bold','Body','Body'])
text(32,291,'Six horizontal petals',13,'Bold',pal['H']);text(310,291,'Six floating corners',13,'Bold',pal['K'])
smalltable(['Slot','Printed part'],[('RU','H03'),('LU','H01'),('BU','H05'),('RD','H04'),('LD','H02'),('BD','H06')],32,278,253,[10,127],21,10.5,['Bold','Body'])
smalltable(['Slot','Printed part'],[('FU','K01'),('BRU','K05'),('BLU','K03'),('FD','K02'),('BRD','K06'),('BLD','K04')],310,278,253,[10,127],21,10.5,['Bold','Body'])
para('<b>RU</b> is between the R and U centers. <b>FU</b> is the front upper corner between L, R and U; <b>BRU</b> is between B, R and U. Replace U with D for the lower layer. There is only one front corner per layer: <b>FU and FD</b>.',32,114,531,10.5,14)
end()

# 4 - early phases
page(4,'PHASES 1 AND 2','Petals first, then the fixed centers','Work on the three blue vertical petals first. Ignore the horizontal petals and corners until later; they are allowed to move throughout this page.')
text(32,713,'1a. Put the vertical petals in their home slots',14,'Bold',pal['V'])
para('Ignore their orientation for now. Each side half-turn swaps one pair. Choose a swap that puts a misplaced petal into its own slot; repeat. At most two swaps are needed.',32,697,531,10.6,14)
smalltable(['Swap these slots','Do'],[('F and BR','R'),('F and BL','L'),('BR and BL','B')],32,643,252,[10,175],22,10.5,['Body','Courier-Bold'])
# Adjacent slot diagram
for a,b in [((392,596),(517,596)),((517,596),(455,545)),((455,545),(392,596))]:line(*a,*b,'#aab9c0',1)
node(392,596,'BL',pal['V'],18);node(517,596,'BR',pal['V'],18);node(455,545,'F',pal['V'],18)
text(32,524,'1b. Flip any two wrongly oriented vertical petals',14,'Bold',pal['V'])
para('Once all three are in place, either none or exactly two need a half-turn in their own slots. Use the matching sequence below; it returns all three to the same slots.',32,507,531,10.6,14)
smalltable(['Flip this pair','Sequence'],[('F and BR','L B L R'),('F and BL','R B R L'),('BR and BL','R L R B')],32,456,531,[10,237],22,11,['Body','Courier-Bold'])
text(32,344,'2a. Orient the three side centers',14,'Bold',pal['C'])
para('With the vertical petals fully solved, either zero or two side centers are half a turn wrong. Repeat the two named side moves three times. The vertical petals return fully solved.',32,327,531,10.6,14)
smalltable(['Wrong side centers','Sequence'],[('R and L','R L R L R L'),('L and B','L B L B L B'),('B and R','B R B R B R')],32,276,531,[10,237],22,11,['Body','Courier-Bold'])
text(32,165,'2b. Orient U and D directly',14,'Bold',pal['C'])
para('Use U or U\' to finish the upper screwed center; use D or D\' to finish the lower one. These moves preserve the solved vertical petals and side centers.',32,148,531,10.6,14)
box(32,64,531,38,'#e5f0eb');text(45,78,'CHECKPOINT: all five centers and all three vertical petals are solved.',10.6,'Bold',pal['C'])
end()

# 5 - H strategy
page(5,'PHASE 3  |  HORIZONTAL PETALS','Solve six petals with a three-cycle','This stage preserves all five screwed centers and all three vertical petals. The floating corners may move; leave them for the last stage.')
macro('M')
pic('H-front',25,418,232);cycle(['RU','LU','RD'],346,601,173,110)
para('<b>M sends RU to LU, LU to RD, and RD to RU.</b> Every other horizontal petal returns to its slot. M\' runs the same cycle backwards.',316,452,246,10.7,14)
text(32,407,'Use a setup to reach any three slots',14,'Bold')
para('Page 6 lists all 20 triples. Find the three slots you want, then do <b>Setup S, Use, Undo S</b>. For the opposite cycle, change M to M\' (or M\' to M) and keep both setup columns unchanged.',32,390,531,10.7,14.5)
text(32,328,'How to choose a useful cycle',13,'Bold')
para('Pick a wrong slot <b>a</b>. The piece in a belongs in <b>b</b>; the piece in b belongs in <b>c</b>. If c is not a, perform <b>a &gt; b &gt; c &gt; a</b>. This puts the first two pieces home. If c is a, leave that swapped pair for now and try another wrong slot. Repeat until only swapped pairs remain, or all six are solved.',32,311,531,10.6,14.5)
box(32,124,531,123,'#f4edf1');text(46,226,'If only two swapped pairs remain',12,'Bold',pal['H'])
para('For <b>a swaps with b</b> and <b>c swaps with d</b>, do these two cycles:<br/><b>a &gt; b &gt; c &gt; a</b>, then <b>a &gt; d &gt; c &gt; a</b>.',46,211,503,10.7,15)
text(46,163,'Example: RU / LU swapped, and RD / LD swapped',10.5,'Bold')
text(46,141,'M   then   L M L',13,'Courier-Bold')
para('A horizontal petal in its correct slot automatically has its correct orientation. <b>There is no separate petal-twisting stage.</b> Stop when all six are flush with the solved centers and vertical petals.',32,104,531,10.5,14)
end()

# 6 - H table
page(6,'PHASE 3  |  COMPLETE SETUP TABLE','Any horizontal-petal three-cycle','An arrow means where the current occupant moves. Every listed cycle closes back to its first slot. A dash means no setup.')
macro('M')
setup_table('H',638)
box(32,111,531,67)
text(45,158,'Example: RU > BU > LD > RU',11,'Bold')
text(45,136,"U D  |  U' R U R  |  D' U'",12,'Courier-Bold')
text(45,120,"Setup U D; use M'; undo with D' U'.",9.8,'Body',muted)
para('<b>Reverse direction:</b> toggle M / M\' only. Always finish the undo column, even if a piece looks solved halfway through. The completed sequence restores every center and vertical petal.',32,96,531,10.2,14)
end()

# 7 - K strategy
page(7,'PHASE 4  |  FLOATING CORNERS','Finish with corner-only cycles','Start here only when all five centers and all nine petals are solved. This ten-move algorithm restores them all, including their orientation.')
macro('N')
pic('K-top',25,411,240);cycle(['FU','BRU','BLU'],345,596,175,110)
para('<b>N sends FU to BRU, BRU to BLU, and BLU to FU.</b> The three lower corners return unchanged. N\' reverses the upper cycle.',316,448,246,10.7,14)
text(32,399,'Position is orientation',14,'Bold',pal['K'])
para('Each corner has only one reachable orientation in a particular slot. Use the solved shapes on page 3 to identify its home; once it is there, it faces the correct way. No final corner-twist algorithm is needed.',32,383,531,10.7,14.5)
text(32,318,'Choose a cycle, then use page 8',13,'Bold')
para('Follow the same method as with horizontal petals: if the piece in a belongs in b, and the piece in b belongs in c, send <b>a &gt; b &gt; c &gt; a</b>. The setup table reaches every triple, including mixed upper and lower corners.',32,301,531,10.6,14.5)
box(32,117,531,123,'#f6f0e3')
text(46,219,'Example: two swapped pairs',12,'Bold',pal['K'])
para('If FU / BRU are swapped and FD / BRD are swapped, do<br/><b>FU &gt; BRU &gt; FD</b>, then <b>FU &gt; BRD &gt; FD</b>.',46,203,503,10.7,15)
text(46,158,"R U' R  |  N  |  R U R",12,'Courier-Bold')
text(46,136,"U R     |  N  |  R U'",12,'Courier-Bold')
para('<b>Finish:</b> every piece now belongs in its own slot and orientation, so the outer surface returns to the solved cube. Keep the original axis names through each setup, algorithm and undo.',32,99,531,10.5,14)
end()

# 8 - K table
page(8,'PHASE 4  |  COMPLETE SETUP TABLE','Any corner three-cycle','Perform Setup S, then the indicated N or N\', then Undo S. Only the three named corners change after the entire sequence.')
macro('N')
setup_table('K',638)
box(32,111,531,67)
text(45,158,'Example: BLU > FD > BRD > BLU',11,'Bold')
text(45,136,"R  |  R D R D' L R U' R U L  |  R",12,'Courier-Bold')
text(45,120,"Setup R; use N'; undo R. Adjacent R R may be omitted.",9.8,'Body',muted)
para('<b>Reverse direction:</b> toggle N / N\' only. The table is exhaustive for any three corners. Repeat cycles until all six corners match the solved outline.',32,96,531,10.2,14)
end()

# 9 - quick reference and robustness
page(9,'QUICK REFERENCE','Checkpoints and troubleshooting','The method solves shape and orientation, not just which family occupies each gap. Use the fixed slot map throughout.')
smalltable(['After this stage','What must be fully solved'],[('Vertical petals','F, BR, BL - both position and orientation'),('Centers','R, L, B, U, D - all five outlines aligned'),('Horizontal petals','RU, LU, BU, RD, LD, BD'),('Corners','FU, BRU, BLU, FD, BRD, BLD')],32,712,531,[10,175],27,10.5,['Bold','Body'])
text(32,550,'The two main algorithms',14,'Bold')
box(32,461,531,73)
text(45,511,'M = '+DATA['macros']['M']['word'],12.5,'Courier-Bold')
text(45,489,'N = '+DATA['macros']['N']['word'],12.5,'Courier-Bold')
text(45,473,'For other slots: Setup, algorithm, undo setup. See pages 6 and 8.',9.6,'Body',muted)
qa=[('Something solved is now wrong.', 'Check that you completed the undo setup and kept the same axis names. U and D are 120-degree moves; the three side moves are 180 degrees.'),('A lower-layer move behaves backwards.', 'D is clockwise when viewed from below, looking into its screw. A view from above reverses the apparent direction.'),('Only one vertical petal seems flipped.', 'With all three vertical petals in their correct slots, flips occur in pairs. Recheck the part identities and which end of each petal belongs up.'),('Only two pieces seem swapped.', 'After the earlier checkpoints, a lone swap of horizontal petals is unreachable. A lone corner swap is also unreachable. Recheck identities and earlier stages; two swapped pairs are handled on pages 5 and 7.'),('A corner seems to need a twist in place.', 'There is no independent corner twist in this mechanism. Recheck its home slot against the solved atlas. The same applies to horizontal petals.')]
y=438
for q,a in qa:
 text(32,y,q,11,'Bold');hh=para(a,32,y-9,531,10.1,13.2);y-=hh+30
line(32,118,563,118)
para('<b>Verification.</b> The guide\'s sequences were checked against the design\'s exact oriented move model: all 96 side-center/vertical-petal states; all 360 permutations in each final phase; and 1,000 random 80-move scrambles solved completely. All 40 setup-table entries were independently checked with the CAD axes and 3D rotation matrices.',32,105,531,9.1,12,muted)
end();c.save()
r=PdfReader(OUT);assert len(r.pages)==9
for i,p in enumerate(r.pages):assert len(p.extract_text())>300,i
(A/'layout-checks.json').write_text(json.dumps({'pages':9,'paragraph_bounds':checks,'validation':DATA['validation']},indent=2))
print(OUT,OUT.stat().st_size,'bytes')
