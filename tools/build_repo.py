"""Собирает репозиторий: копирует сайт и делает tilda.html с абсолютными ссылками на картинки."""
import shutil
s=open('site/index.html',encoding='utf-8').read()
shutil.copy('site/index.html','repo/index.html'); shutil.rmtree('repo/assets'); shutil.copytree('site/assets','repo/assets')
base="https://malysh92.github.io/halloween-pumpkin-night/"
pre_css=s[s.index('<style id="pre-css">'):s.index('</style>')+8]
rest=s[s.index('</style>')+8:]
main_style=rest[rest.index('<style>'):rest.index('</style>')+8]
body=s[s.index('<body>')+6:s.rindex('<script>')]
pre_div=body[body.index('<div id="pre"'):]
pre_div=pre_div[:pre_div.index('</div></div></div>')+len('</div></div></div>')]
script=s[s.rindex('<script>'):s.rindex('</script>')+9]
out="<!-- Тыквенная ночь PRO.FINANSY — вставить в Tilda: блок T123 «HTML» (на странице без шапки/подвала) -->\n"+pre_css+"\n"+pre_div+"\n"+main_style+"\n"+body.replace(pre_div,'')+script+"\n"
open('repo/tilda.html','w',encoding='utf-8').write(out.replace('assets/',base+'assets/'))
