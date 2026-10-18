from pathlib import Path
from PIL import Image,ImageDraw
pages=sorted(Path('docs/qa').glob('page-*.png'))
thumbs=[]
for path in pages:
 im=Image.open(path).convert('RGB');im.thumbnail((310,445))
 tile=Image.new('RGB',(330,475),'#dedede');tile.paste(im,((330-im.width)//2,20));ImageDraw.Draw(tile).text((14,455),path.stem,fill='black');thumbs.append(tile)
for part in range((len(thumbs)+4)//5):
 subset=thumbs[part*5:part*5+5];canvas=Image.new('RGB',(330*len(subset),475),'white')
 for i,tile in enumerate(subset):canvas.paste(tile,(i*330,0))
 canvas.save(f'docs/qa/contact-sheet-{part+1}.png')
print('Rendered pages',len(pages))
