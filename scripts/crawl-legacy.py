#!/usr/bin/env python3
"""Crawl chloeandowen.com: photo detail pages, full images, updates.
Usage: python3 -I crawl.py <crawl_dir_with_photoMenuAll.html_and_updates.html> <out_dir>
"""
import sys, os, re, json, time, html
import urllib.request, urllib.error
from concurrent.futures import ThreadPoolExecutor, as_completed

BASE = "http://chloeandowen.com/"
crawl_dir, out_dir = sys.argv[1], sys.argv[2]
img_dir = os.path.join(out_dir, "images")
page_dir = os.path.join(out_dir, "pages")
os.makedirs(img_dir, exist_ok=True); os.makedirs(page_dir, exist_ok=True)

def fetch(url, tries=4):
    last = None
    for i in range(tries):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "chloeandowen-archiver/1.0"})
            with urllib.request.urlopen(req, timeout=30) as r:
                return r.read()
        except Exception as e:
            last = e; time.sleep(1.5 * (i + 1))
    raise last

# ---- photo ids from the all-photos menu
menu = open(os.path.join(crawl_dir, "photoMenuAll.html"), encoding="latin-1").read()
ids = []
for m in re.finditer(r'photoDetail\.php\?id=([A-Za-z0-9_-]+)', menu):
    if m.group(1) not in ids: ids.append(m.group(1))
print("photo ids:", len(ids), flush=True)

# ---- update ids from the updates list
upd = open(os.path.join(crawl_dir, "updates.html"), encoding="latin-1").read()
updates_meta = []
for m in re.finditer(r'href="update\.php\?id=(\d+)">([^<]*?) - (.*?)</a>', upd):
    updates_meta.append({"id": int(m.group(1)), "dateText": m.group(2).strip(), "title": html.unescape(m.group(3).strip())})
print("updates:", len(updates_meta), flush=True)

DETAIL_RE = re.compile(
    r'<img src="images/([^"]+)">.*?<p class="photoTitle">(.*?)</p>\s*<p class="default">(.*?)</p>', re.S)
PREV_RE = re.compile(r'href="photoDetail\.php\?id=([A-Za-z0-9_-]+)">PREVIOUS PHOTO')
NEXT_RE = re.compile(r'href="photoDetail\.php\?id=([A-Za-z0-9_-]+)">NEXT PHOTO')

def do_photo(pid):
    page_path = os.path.join(page_dir, f"photo-{pid}.html")
    if os.path.exists(page_path):
        raw = open(page_path, "rb").read()
    else:
        raw = fetch(BASE + f"photoDetail.php?id={pid}")
        open(page_path, "wb").write(raw)
    text = raw.decode("latin-1")
    m = DETAIL_RE.search(text)
    if not m:
        return {"id": pid, "error": "no-detail-match"}
    img, title, caption = m.group(1), m.group(2).strip(), m.group(3).strip()
    prev = PREV_RE.search(text); nxt = NEXT_RE.search(text)
    img_path = os.path.join(img_dir, img)
    if not os.path.exists(img_path) or os.path.getsize(img_path) == 0:
        data = fetch(BASE + "images/" + img)
        open(img_path, "wb").write(data)
    return {"id": pid, "image": img, "title": title, "caption": caption,
            "prev": prev.group(1) if prev else None, "next": nxt.group(1) if nxt else None,
            "bytes": os.path.getsize(img_path)}

UPDATE_RE = re.compile(r'<p class="photoTitle">(.*?)</p>\s*<p class="default">(.*?)</p>\s*</div>', re.S)
def do_update(meta):
    uid = meta["id"]
    page_path = os.path.join(page_dir, f"update-{uid}.html")
    if os.path.exists(page_path):
        raw = open(page_path, "rb").read()
    else:
        raw = fetch(BASE + f"update.php?id={uid}")
        open(page_path, "wb").write(raw)
    text = raw.decode("latin-1")
    m = UPDATE_RE.search(text)
    d = dict(meta)
    if m:
        d["pageTitle"] = m.group(1).strip(); d["bodyHtml"] = m.group(2).strip()
    else:
        d["error"] = "no-update-match"
    return d

photos, errors = [], []
with ThreadPoolExecutor(max_workers=6) as ex:
    futs = {ex.submit(do_photo, pid): pid for pid in ids}
    done = 0
    for f in as_completed(futs):
        try:
            r = f.result()
            photos.append(r)
            if "error" in r: errors.append(r)
        except Exception as e:
            errors.append({"id": futs[f], "error": repr(e)})
        done += 1
        if done % 100 == 0: print(f"  photos {done}/{len(ids)}", flush=True)

order = {pid: i for i, pid in enumerate(ids)}
photos.sort(key=lambda p: order[p["id"]])

updates = [do_update(m) for m in updates_meta]

# pagetitle gif
pt = os.path.join(img_dir, "pagetitle.gif")
if not os.path.exists(pt): open(pt, "wb").write(fetch(BASE + "images/pagetitle.gif"))

json.dump({"photos": photos, "updates": updates, "errors": errors}, open(os.path.join(out_dir, "crawl.json"), "w"), indent=1)
print("done. photos:", len(photos), "errors:", len(errors), "updates:", len(updates), flush=True)
for e in errors[:20]: print("  ERR", e)
