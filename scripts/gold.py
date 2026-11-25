# Updates gold.json with the current price of 1 gram of 24k gold and 1 gram of silver in SAR.
# Sources are tried in order; the file is left untouched if all fail or values look wrong.
import json, urllib.request, datetime, sys
OZ = 31.1034768; SAR = 3.75  # SAR is pegged to USD at 3.75
UA = {'User-Agent': 'Mozilla/5.0 (sukoon-bot; +https://k44vvd.github.io/sukoon/)', 'Accept': 'application/json'}
def get(u):
    with urllib.request.urlopen(urllib.request.Request(u, headers=UA), timeout=25) as r:
        return json.loads(r.read().decode())
def gold_api():
    g = float(get('https://api.gold-api.com/price/XAU')['price']); s = float(get('https://api.gold-api.com/price/XAG')['price'])
    return g * SAR / OZ, s * SAR / OZ, 'gold-api.com'
def goldprice_org():
    it = get('https://data-asg.goldprice.org/dbXRates/SAR')['items'][0]
    return float(it['xauPrice']) / OZ, float(it['xagPrice']) / OZ, 'goldprice.org'
for f in (gold_api, goldprice_org):
    try:
        g, s, src = f()
        if 150 < g < 3000 and 0.5 < s < 60:
            json.dump({'g': round(g, 2), 's': round(s, 3), 't': datetime.datetime.utcnow().strftime('%Y-%m-%dT%H:%MZ'), 'src': src}, open('gold.json', 'w'))
            print('gold', g, 'silver', s, src); sys.exit(0)
        print('rejected', f.__name__, g, s)
    except Exception as e:
        print('fail', f.__name__, e)
sys.exit(0)
