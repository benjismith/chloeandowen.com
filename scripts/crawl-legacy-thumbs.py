import sys, os, json, time, urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed
BASE = "http://chloeandowen.com/images/"
data_dir = sys.argv[1]
crawl = json.load(open(os.path.join(data_dir, "crawl.json")))
albums = json.load(open(sys.argv[2]))
jobs = [("thumbs", p["id"]) for p in crawl["photos"]] + [("albums", a["cover"]) for a in albums]
for sub in ("thumbs", "albums"): os.makedirs(os.path.join(data_dir, sub), exist_ok=True)
def fetch(url, tries=4):
    last = None
    for i in range(tries):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "chloeandowen-archiver/1.0"})
            with urllib.request.urlopen(req, timeout=30) as r: return r.read()
        except Exception as e: last = e; time.sleep(1.5*(i+1))
    raise last
def do(job):
    sub, pid = job
    dst = os.path.join(data_dir, sub, pid + ".jpg")
    if os.path.exists(dst) and os.path.getsize(dst) > 0: return (job, os.path.getsize(dst))
    data = fetch(BASE + sub + "/" + pid + ".jpg")
    open(dst, "wb").write(data); return (job, len(data))
errs, done = [], 0
with ThreadPoolExecutor(max_workers=6) as ex:
    futs = {ex.submit(do, j): j for j in jobs}
    for f in as_completed(futs):
        try: f.result()
        except Exception as e: errs.append((futs[f], repr(e)))
        done += 1
print("done", done, "errors", errs)
