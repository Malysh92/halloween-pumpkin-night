import numpy as np, json
from PIL import Image, ImageFilter

def glow_cut(path, out, width, barrier_t, dil=2, erode=17, anchor=None):
    im=Image.open(path).convert('RGB'); a=np.asarray(im).astype(np.float32)
    m=a.max(axis=2)
    # барьер = яркая рамка; всё, что внутри рамки (недостижимо с краёв), делаем плотным
    bar=Image.fromarray(((m>=barrier_t)*255).astype(np.uint8),'L').filter(ImageFilter.MaxFilter(dil*2+1))
    free=np.asarray(bar)==0
    reg=np.zeros_like(free); reg[0,:]=free[0,:]; reg[-1,:]=free[-1,:]; reg[:,0]=free[:,0]; reg[:,-1]=free[:,-1]
    while True:
        n=reg.copy(); n[1:,:]|=reg[:-1,:]; n[:-1,:]|=reg[1:,:]; n[:,1:]|=reg[:,:-1]; n[:,:-1]|=reg[:,1:]; n&=free
        if (n==reg).all(): break
        reg=n
    solid=~reg                                     # рамка и всё внутри неё
    solid_img=Image.fromarray((solid*255).astype(np.uint8),'L').filter(ImageFilter.MinFilter(erode)).filter(ImageFilter.GaussianBlur(2.0))
    core=np.asarray(solid_img)>200
    solid_a=np.asarray(solid_img).astype(np.float32)
    lum=np.clip(m*1.15,0,255)                      # снаружи: свечение -> прозрачность
    alpha=np.maximum(np.where(solid, 255, 0)*0+solid_a, lum)
    alpha=np.clip(alpha,0,255)
    safe=np.maximum(alpha,1)[...,None]
    rgb=np.where(core[...,None], a, np.clip(a*255.0/safe,0,255))
    res=Image.fromarray(np.dstack([rgb,alpha]).astype(np.uint8),'RGBA')
    bb=res.getchannel('A').point(lambda v:255 if v>8 else 0).getbbox()
    res=res.crop(bb)
    h=round(res.height*width/res.width); res=res.resize((width,h),Image.LANCZOS)
    res.save(out,'WEBP',quality=92,method=6)
    info={'size':res.size,'bbox':bb}
    if anchor:
        info['anchor']=[(anchor[0]-bb[0])/(bb[2]-bb[0]),(anchor[1]-bb[1])/(bb[3]-bb[1])]
    print(out,info); return info

glow_cut('src2/btn.png','site/assets/btn.webp',1200,40,dil=2,erode=17)
glow_cut('src2/wing.png','site/assets/wing.webp',460,35,dil=1,erode=7,anchor=(650,130))
for n in ['btn','wing']:
    im=Image.open(f'site/assets/{n}.webp').convert('RGBA')
    for nm,col in [('dark',(18,26,36,255)),('light',(160,170,185,255))]:
        t=Image.new('RGBA',im.size,col); t.alpha_composite(im); t.convert('RGB').resize((im.width//2,im.height//2)).save(f'tools/chk_{n}_{nm}.png')
