import numpy as np
from PIL import Image, ImageDraw, ImageFilter
S='src/'; O='site/assets/'

def lum_alpha(path, out, width, boost=1.0):
    """Свечение на чёрном -> прозрачный PNG/WebP: альфа = яркость, цвет раскрашен обратно."""
    im=Image.open(path).convert('RGB'); a=np.asarray(im).astype(np.float32)
    m=a.max(axis=2)
    alpha=np.clip(m*boost,0,255)
    safe=np.maximum(alpha,1)[...,None]
    rgb=np.clip(a*255.0/safe,0,255)
    res=np.dstack([rgb,alpha]).astype(np.uint8)
    img=Image.fromarray(res,'RGBA')
    bb=img.getchannel('A').point(lambda v:255 if v>6 else 0).getbbox()
    img=img.crop(bb)
    h=round(img.height*width/img.width); img=img.resize((width,h),Image.LANCZOS)
    img.save(out,'WEBP',quality=92,method=6); print(out,img.size,bb)
    return bb

def cut_bg(path, out, width, is_bg, feather=1.2, crop=True):
    im=Image.open(path).convert('RGB'); a=np.asarray(im)
    cand=is_bg(a).astype(np.uint8)*255
    c=cand>0
    reg=np.zeros_like(c); reg[0,:]=c[0,:]; reg[-1,:]=c[-1,:]; reg[:,0]=c[:,0]; reg[:,-1]=c[:,-1]
    while True:
        n=reg.copy()
        n[1:,:]|=reg[:-1,:]; n[:-1,:]|=reg[1:,:]; n[:,1:]|=reg[:,:-1]; n[:,:-1]|=reg[:,1:]
        n&=c
        if (n==reg).all(): break
        reg=n
    bgreg=reg
    alpha=Image.fromarray(np.where(bgreg,0,255).astype(np.uint8),'L')
    alpha=alpha.filter(ImageFilter.GaussianBlur(feather))
    rgba=np.dstack([a,np.asarray(alpha)]); img=Image.fromarray(rgba,'RGBA')
    if crop:
        bb=img.getchannel('A').point(lambda v:255 if v>10 else 0).getbbox(); img=img.crop(bb)
    hh=round(img.height*width/img.width); img=img.resize((width,hh),Image.LANCZOS)
    img.save(out,'WEBP',quality=90,method=6); print(out,img.size)
    return img

# фон
bg=Image.open(S+'bg1.png').convert('RGB').resize((2560,1440),Image.LANCZOS)
bg.save(O+'bg1.webp','WEBP',quality=84,method=6); print('bg',bg.size)
# заголовок и тыква счётчика (свечение на чёрном)
lum_alpha(S+'title.png',O+'title.webp',1400)
lum_alpha(S+'counter_full.png',O+'counter_full.webp',260)
# тыква для окон
cut_bg(S+'pumpkin_win.png',O+'pumpkin.webp',480,lambda a:a.max(axis=2)<24)
# паук: берём тело с короткой ниткой, нитку дальше тянет код
sp=Image.open(S+'spider.png').convert('RGB'); a=np.asarray(sp)
tmp='tools/spider_body.png'
sp.crop((0,1850,sp.width,3150)).save(tmp)
cut_bg(tmp,O+'spider.webp',280,lambda a:a.min(axis=2)>238,feather=0.8)

# горящее окно: берём стекло левого окна
w=np.asarray(Image.open(S+'window.png').convert('RGBA')).astype(int)
r,g,b,al=w[...,0],w[...,1],w[...,2],w[...,3]
amber=(al>200)&(r>110)&(r>b*1.7)
xs=np.where(amber[:, :700].any(axis=0))[0]; ys=np.where(amber[:, :700].any(axis=1))[0]
print('glass bbox',xs.min(),xs.max(),ys.min(),ys.max())
