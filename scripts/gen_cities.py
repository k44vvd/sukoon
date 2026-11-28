import re, json, math, html, datetime, os
SRC='/home/claude/sukoon/index.html'; OUT='/home/claude/sukoon/mawaqit'; BASE='https://sukoon-app.github.io/sukoon/'
s=open(SRC,encoding='utf-8').read()
cities=json.loads(re.search(r"const CITIES = (\[.*?\]\]);",s).group(1).replace("'",'"'))
wtc_raw=re.search(r"const WTC = \[(.*?)\]\];",s,re.S).group(1)+']'
wtc=[json.loads('['+m.replace("'",'"')+']') for m in re.findall(r"\[('[A-Z]{2}'.*?)\]",wtc_raw)]
SA_SLUG=['jeddah','makkah','madinah','riyadh','dammam','taif','abha','tabuk','khobar','al-ahsa','qatif','jubail','buraydah','unaizah','hail','khamis-mushait','jazan','najran','al-baha','yanbu','sakaka','arar','hafar-al-batin','qurayyat','rabigh','al-kharj','majmaah','bisha']
assert len(SA_SLUG)==len(cities),(len(SA_SLUG),len(cities))
WS={'AE':'abu-dhabi','KW':'kuwait-city','QA':'doha','BH':'manama','OM':'muscat','YE':'sanaa','IQ':'baghdad','SY':'damascus','JO':'amman','LB':'beirut','PS':'jerusalem','EG':'cairo','SD':'khartoum','SO':'mogadishu','DJ':'djibouti','KM':'moroni','LY':'tripoli','TN':'tunis','DZ':'algiers','MA':'rabat','MR':'nouakchott','TR':'ankara','IR':'tehran','AF':'kabul','PK':'islamabad','BD':'dhaka','MV':'male','ID':'jakarta','MY':'kuala-lumpur','BN':'bandar-seri-begawan','AZ':'baku','KZ':'astana','UZ':'tashkent','TM':'ashgabat','TJ':'dushanbe','KG':'bishkek','NG':'abuja','SN':'dakar','ML':'bamako','NE':'niamey','BF':'ouagadougou','TD':'ndjamena','GN':'conakry','GW':'bissau','GM':'banjul','SL':'freetown','CI':'abidjan','BJ':'porto-novo','TG':'lome','CM':'yaounde','GA':'libreville','UG':'kampala','MZ':'maputo','AL':'tirana','GY':'georgetown','SR':'paramaribo'}
MNAME={'UQ':'تقويم أم القرى','EG':'الهيئة المصرية العامة للمساحة','MWL':'رابطة العالم الإسلامي','KR':'جامعة العلوم الإسلامية بكراتشي','AE':'الهيئة العامة للشؤون الإسلامية والأوقاف','KW':'وزارة الأوقاف الكويتية','QA':'وزارة الأوقاف القطرية','SEA':'الجهات الدينية في جنوب شرق آسيا','TR':'رئاسة الشؤون الدينية التركية','IR':'معهد الجيوفيزياء بطهران','MA':'وزارة الأوقاف المغربية','JO':'وزارة الأوقاف الأردنية','TN':'وزارة الشؤون الدينية التونسية','OM':'وزارة الأوقاف العمانية'}
WTM=json.loads(re.search(r"const WTM = (\{.*?\});",s).group(1).replace("'",'"').replace(' UQ:',' "UQ":'))  if False else None
# parse WTM manually
wtm_txt=re.search(r"const WTM = \{(.*?)\};",s).group(1)
WTM={k:json.loads('['+v.replace("'",'"')+']') for k,v in re.findall(r"(\w+): \[([^\]]*)\]",wtm_txt)}
K=(21.4225,39.8262)
def qibla(lat,lng):
    f1,l1,f2,l2=map(math.radians,(lat,lng,*K)); b=math.degrees(math.atan2(math.sin(l2-l1),math.cos(f1)*math.tan(f2)-math.sin(f1)*math.cos(l2-l1)))%360
    d=2*6371*math.asin(math.sqrt(math.sin((f2-f1)/2)**2+math.cos(f1)*math.cos(f2)*math.sin((l2-l1)/2)**2)); return round(b),round(d)
AD=str.maketrans('0123456789','٠١٢٣٤٥٦٧٨٩'); A=lambda x: str(x).translate(AD)
pages=[]
for i,(nm,lat,lng) in enumerate(cities): pages.append(dict(slug=SA_SLUG[i],city=nm,country='السعودية',cc='SA',lat=lat,lng=lng,zone='Asia/Riyadh',m='UQ',h=0,app=f'sa-{i}'))
for c in wtc:
    if c[0]=='SA': continue
    pages.append(dict(slug=WS[c[0]],city=c[2],country=c[1],cc=c[0],lat=c[3],lng=c[4],zone=c[5],m=c[6],h=(c[8] if len(c)>8 else 0),app=c[0]))
flag=lambda cc: ''.join(chr(127397+ord(ch)) for ch in cc)
def links(cur):
    sa=''.join(f'<a href="{p["slug"]}.html"{" aria-current=page" if p is cur else ""}>{html.escape(p["city"])}</a>' for p in pages if p['cc']=='SA')
    wo=''.join(f'<a href="{p["slug"]}.html"{" aria-current=page" if p is cur else ""}>{flag(p["cc"])} {html.escape(p["city"])}</a>' for p in pages if p['cc']!='SA')
    return f'<h2>مواقيت مدن السعودية</h2><nav class="lk">{sa}</nav><h2>مواقيت الدول العربية والإسلامية</h2><nav class="lk">{wo}</nav>'
CSS=open('/home/claude/scripts/city.css',encoding='utf-8').read() if os.path.exists('/home/claude/scripts/city.css') else ''
today=datetime.date.today().isoformat()
for p in pages:
    qb,qd=qibla(p['lat'],p['lng']); M=WTM[p['m']]; mname=MNAME[p['m']]
    place=p['city'] if p['cc']=='SA' else f"{p['city']}، {p['country']}"
    title=f"مواقيت الصلاة في {p['city']} اليوم | أذان الفجر والمغرب{'' if p['cc']=='SA' else ' · '+p['country']} | سدرة"
    desc=f"مواقيت الصلاة في {place} اليوم: الفجر والشروق والظهر والعصر والمغرب والعشاء بالتوقيت المحلي، بطريقة {mname}، مع الصلاة القادمة واتجاه القبلة ({A(qb)}°) وجدول الأسبوع."
    cfg=dict(lat=p['lat'],lng=p['lng'],zone=p['zone'],M=M[:3]+([M[4]] if len(M)>4 else [0]),h=p['h'],uq=p['m']=='UQ',city=p['city'])
    ld={"@context":"https://schema.org","@graph":[{"@type":"WebPage","name":title,"description":desc,"url":f"{BASE}mawaqit/{p['slug']}.html","inLanguage":"ar","isPartOf":{"@type":"WebSite","name":"سدرة","url":BASE}},{"@type":"BreadcrumbList","itemListElement":[{"@type":"ListItem","position":1,"name":"سدرة","item":BASE},{"@type":"ListItem","position":2,"name":"مواقيت الصلاة","item":f"{BASE}mawaqit/"},{"@type":"ListItem","position":3,"name":f"مواقيت الصلاة في {p['city']}"}]}]}
    doc=f'''<!DOCTYPE html><html lang="ar" dir="rtl"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{html.escape(title)}</title><meta name="description" content="{html.escape(desc)}"><link rel="canonical" href="{BASE}mawaqit/{p['slug']}.html">
<meta property="og:title" content="{html.escape(title)}"><meta property="og:description" content="{html.escape(desc)}"><meta property="og:image" content="{BASE}og.jpg"><meta property="og:locale" content="ar_SA"><meta name="theme-color" content="#022b2a">
<link rel="icon" href="../icon-192.png"><link rel="manifest" href="../manifest.json"><script type="application/ld+json">{json.dumps(ld,ensure_ascii=False)}</script><style>{CSS}</style></head><body>
<header><a class="brand" href="../#/home"><img src="../icon-192.png" alt="" width="34" height="34"> سدرة</a><a class="cta" href="../?c={p['app']}#/salah">افتح التطبيق</a></header>
<main><p class="crumb"><a href="../">سدرة</a> › <a href="./">مواقيت الصلاة</a> › {html.escape(p['city'])}</p>
<h1>مواقيت الصلاة في {html.escape(p['city'])} اليوم</h1><p class="sub">{flag(p['cc'])} {html.escape(p['country'])} · <span id="dt"></span></p>
<section class="next" id="next" aria-live="polite"></section>
<section class="grid" id="grid"><noscript>فعّل جافاسكربت لعرض المواقيت.</noscript></section>
<p class="note">المواقيت محسوبة فلكياً لمدينة {html.escape(p['city'])} (خط العرض {A(round(p['lat'],2))}°، خط الطول {A(round(p['lng'],2))}°) بطريقة {mname}{'، والعصر على المذهب الحنفي' if p['h'] else ''}، وبالتوقيت المحلي. قد تختلف دقيقة أو دقيقتين عن أذان بعض المساجد.</p>
<h2>جدول مواقيت الأسبوع في {html.escape(p['city'])}</h2><div class="tw"><table id="wk"><thead><tr><th>اليوم</th><th>الفجر</th><th>الشروق</th><th>الظهر</th><th>العصر</th><th>المغرب</th><th>العشاء</th></tr></thead><tbody></tbody></table></div>
<h2>اتجاه القبلة من {html.escape(p['city'])}</h2><p>اتجاه القبلة من {html.escape(p['city'])} هو <b>{A(qb)}°</b> من الشمال باتجاه عقارب الساعة، والمسافة إلى الكعبة المشرفة في مكة المكرمة تقريباً <b>{A(f"{qd:,}")} كم</b>. افتح البوصلة في سدرة لتحديد القبلة من موقعك بالضبط.</p>
<div class="app"><b>سدرة: رفيقك اليومي</b><p>أذان بأصوات الحرمين، تذكيرات الأذكار والورد والوتر، المصحف كاملاً بالتفسير، والقبلة من موقعك. مجاني وبدون إعلانات.</p><a class="cta" href="../?c={p['app']}#/salah">افتح مواقيت {html.escape(p['city'])} في سدرة</a></div>
{links(p)}
</main><footer><a href="../">سدرة</a> · صدقة جارية · <a href="./">كل المدن</a></footer>
<script>window.CITY_CFG={json.dumps(cfg,ensure_ascii=False)};</script><script src="pt.js"></script></body></html>'''
    open(f"{OUT}/{p['slug']}.html",'w',encoding='utf-8').write(doc)
# index page
idx=f'''<!DOCTYPE html><html lang="ar" dir="rtl"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>مواقيت الصلاة في مدن السعودية والدول العربية والإسلامية | سدرة</title>
<meta name="description" content="مواقيت الصلاة اليوم في {A(len(cities))} مدينة سعودية وعواصم الدول العربية والإسلامية، بالتوقيت المحلي وطريقة الحساب المعتمدة في كل دولة، مع اتجاه القبلة."><link rel="canonical" href="{BASE}mawaqit/"><link rel="icon" href="../icon-192.png"><style>{CSS}</style></head><body>
<header><a class="brand" href="../#/home"><img src="../icon-192.png" alt="" width="34" height="34"> سدرة</a><a class="cta" href="../#/salah">افتح التطبيق</a></header><main><h1>مواقيت الصلاة</h1><p class="sub">اختر مدينتك لمعرفة مواقيت الصلاة اليوم وجدول الأسبوع واتجاه القبلة.</p>{links(None)}</main><footer><a href="../">سدرة</a> · صدقة جارية</footer></body></html>'''
open(f'{OUT}/index.html','w',encoding='utf-8').write(idx)
# sitemap
sm=open('/home/claude/sukoon/sitemap.xml',encoding='utf-8').read()
sm=re.sub(r'\s*<url><loc>[^<]*/mawaqit/[^<]*</loc>.*?</url>','',sm,flags=re.S)
add=''.join(f'\n  <url><loc>{BASE}mawaqit/{u}</loc><lastmod>{today}</lastmod><changefreq>daily</changefreq><priority>{pr}</priority></url>' for u,pr in [('', '0.8')]+[(p['slug']+'.html','0.7') for p in pages])
sm=sm.replace('</urlset>',add+'\n</urlset>')
open('/home/claude/sukoon/sitemap.xml','w',encoding='utf-8').write(sm)
json.dump({p['app']:p['slug'] for p in pages},open(f'{OUT}/_map.json','w'))
print(len(pages),'pages')
