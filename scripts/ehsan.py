# Fetches live numbers for featured Ehsan cases and writes ehsan.json (run by GitHub Actions).
import json, re, urllib.request, datetime
CASES = {"P84148": "https://ehsan.sa/projects/0/83149"}
out = {"updated": datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds"), "cases": {}}
try:
    old = json.load(open("ehsan.json", encoding="utf-8"))
except Exception:
    old = {"cases": {}}
num = lambda s: int(re.sub(r"[^\d]", "", s))
for no, url in CASES.items():
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126 Safari/537.36", "Accept-Language": "ar"})
        h = urllib.request.urlopen(req, timeout=40).read().decode("utf-8", "ignore")
        got = re.search(r"تم جمع[\s\S]{0,300}?([\d][\d,]*)", h)
        left = re.search(r"المبلغ المتبقي[\s\S]{0,300}?([\d][\d,]*)", h)
        if not (got and left):
            raise ValueError("numbers not found")
        out["cases"][no] = {"got": num(got.group(1)), "left": num(left.group(1)), "asof": out["updated"]}
        print(no, out["cases"][no])
    except Exception as e:
        print(no, "FAILED:", e)
        if no in old.get("cases", {}):
            out["cases"][no] = old["cases"][no]
if not out["cases"]:
    raise SystemExit(1)
json.dump(out, open("ehsan.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
