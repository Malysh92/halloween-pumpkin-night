"""Сборка репозитория.
 python3 tools/build_repo.py            -> копирует сайт (index.html, assets) в repo/
 python3 tools/build_repo.py <sha>      -> + tilda.html: картинки с CDN Тильды (tools/tilda_urls.json),
                                           запасные адреса — jsDelivr (по sha) и GitHub Pages; шрифты и музыка на jsDelivr."""
import shutil, sys, re, json, os
s=open('site/index.html',encoding='utf-8').read()
shutil.copy('site/index.html','repo/index.html'); shutil.rmtree('repo/assets'); shutil.copytree('site/assets','repo/assets')
if len(sys.argv)>1:
    sha=sys.argv[1]; tilda=json.load(open('tools/tilda_urls.json'))
    J="https://cdn.jsdelivr.net/gh/Malysh92/halloween-pumpkin-night@%s/assets/"%sha
    P="https://malysh92.github.io/halloween-pumpkin-night/assets/"
    pre_css=s[s.index('<style id="pre-css">'):s.index('</style>')+8]
    rest=s[s.index('</style>')+8:]
    main_style=rest[rest.index('<style>'):rest.index('</style>')+8]
    body=s[s.index('<body>')+6:s.rindex('<script>')]
    pre_div=body[body.index('<div id="pre"'):]
    pre_div=pre_div[:pre_div.index('</div></div></div>')+len('</div></div></div>')]
    script=s[s.rindex('<script>'):s.rindex('</script>')+9]
    out="<!-- Тыквенная ночь PRO.FINANSY — вставить в Tilda: блок T123 «HTML» (на странице без шапки/подвала) -->\n"+pre_css+"\n"+pre_div+"\n"+main_style+"\n"+body.replace(pre_div,'')+script+"\n"
    # Manrope уже подключён в настройках сайта Тильды
    out="\n".join(l for l in out.split("\n") if not (l.startswith("@font-face") and "font-family:'Manrope'" in l))
    # шрифты: jsDelivr + запасной
    out=re.sub(r"src:url\(assets/fonts/([^)]+)\) format\('woff2'\)", lambda m:"src:url(%sfonts/%s) format('woff2'), url(%sfonts/%s) format('woff2')"%(J,m.group(1),P,m.group(1)), out)
    # цепочки адресов для каждого файла из assets
    names=[]
    for root,_,files in os.walk('site/assets'):
        for f in files:
            if f.endswith(('.webp','.svg','.mp3','.woff2')): names.append(os.path.relpath(os.path.join(root,f),'site/assets'))
    chains=[]; primary={}
    for n in sorted(names):
        ch=([tilda[n]] if n in tilda else [])+[J+n,P+n]
        chains.append(ch); primary[n]=ch[0]
    out=out.replace('const ASSET_PRIMARY = {};','const ASSET_PRIMARY = %s;'%json.dumps(primary,ensure_ascii=False,separators=(',',':')))
    out=out.replace('const ASSET_CHAINS = [];','const ASSET_CHAINS = %s;'%json.dumps(chains,ensure_ascii=False,separators=(',',':')))
    # все оставшиеся относительные ссылки assets/... -> основной адрес
    def sub(m):
        n=m.group(1); return primary.get(n, J+n)
    out=re.sub(r'(?<![/\w.-])assets/([\w./-]+?\.(?:webp|svg|mp3|woff2))', sub, out)
    open('repo/tilda.html','w',encoding='utf-8').write(out)
    print('tilda.html', len(out),'байт; относительных ссылок осталось:', len(re.findall(r'(?<![/\w.-])assets/',out)))
