import numpy as np
from PIL import Image, ImageFilter
exec(open('tools/prep2.py').read().split("glow_cut('src2/btn.png'")[0])   # берём glow_cut из прошлого скрипта

def lum_alpha(path, out, width):
    im=Image.open(path).convert('RGB'); a=np.asarray(im).astype(np.float32); m=a.max(axis=2)
    alpha=np.clip(m*1.0,0,255); safe=np.maximum(alpha,1)[...,None]
    rgb=np.clip(a*255.0/safe,0,255)
    img=Image.fromarray(np.dstack([rgb,alpha]).astype(np.uint8),'RGBA')
    img=img.crop(img.getchannel('A').point(lambda v:255 if v>6 else 0).getbbox())
    img=img.resize((width,round(img.height*width/img.width)),Image.LANCZOS)
    img.save(out,'WEBP',quality=92,method=6); print(out,img.size)

def solid_cut(path):
    """Билет на чёрном: всё, что не достижимо с краёв через тёмные пиксели, — плотное."""
    im=Image.open(path).convert('RGB'); a=np.asarray(im).astype(np.float32); m=a.max(axis=2)
    bar=Image.fromarray(((m>=34)*255).astype(np.uint8),'L').filter(ImageFilter.MaxFilter(3))
    free=np.asarray(bar)==0
    reg=np.zeros_like(free); reg[0,:]=free[0,:]; reg[-1,:]=free[-1,:]; reg[:,0]=free[:,0]; reg[:,-1]=free[:,-1]
    while True:
        n=reg.copy(); n[1:,:]|=reg[:-1,:]; n[:-1,:]|=reg[1:,:]; n[:,1:]|=reg[:,:-1]; n[:,:-1]|=reg[:,1:]; n&=free
        if (n==reg).all(): break
        reg=n
    solid=(~reg).astype(np.uint8)*255
    alpha=np.asarray(Image.fromarray(solid,'L').filter(ImageFilter.MinFilter(3)).filter(ImageFilter.GaussianBlur(1.1)))
    return Image.fromarray(np.dstack([a,alpha]).astype(np.uint8),'RGBA')

cov=solid_cut('src3/ticket_cover.png'); opn=solid_cut('src3/ticket_open.png')
bb1=cov.getchannel('A').point(lambda v:255 if v>20 else 0).getbbox(); bb2=opn.getchannel('A').point(lambda v:255 if v>20 else 0).getbbox()
print('bbox',bb1,bb2)
W=1700; H=round((bb1[3]-bb1[1])*W/(bb1[2]-bb1[0]))
for nm,img,bb in [('ticket_cover',cov,bb1),('ticket_open',opn,bb2)]:
    r=img.crop(bb).resize((W,H),Image.LANCZOS); r.save(f'site/assets/{nm}.webp','WEBP',quality=86,method=6); print(nm,r.size)
bg=Image.open('src3/bg2.png').convert('RGB').resize((2560,1440),Image.LANCZOS); bg.save('site/assets/bg2.webp','WEBP',quality=80,method=6)
lum_alpha('src3/title2.png','site/assets/title2.webp',1400)
glow_cut('src3/cta.png','site/assets/cta.webp',1200,40,dil=2,erode=17)
for n in ['ticket_cover','ticket_open','cta']:
    im=Image.open(f'site/assets/{n}.webp').convert('RGBA'); t=Image.new('RGBA',im.size,(120,150,190,255)); t.alpha_composite(im); t.convert('RGB').resize((im.width//2,im.height//2)).save(f'tools/chk_{n}.png')
