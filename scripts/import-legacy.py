#!/usr/bin/env python3
"""One-time import of the legacy PHP site's content into this Eleventy site.

Reads what crawl-legacy.py saved (crawl.json, images/, thumbs/, albums/) plus
the saved photoAlbums.html, and writes -- keeping the original HTML verbatim:

  src/_data/albums.json      album number, cover photo id, description HTML
  src/_data/photos.json      every photo: id, album, frame, title/caption HTML
  src/updates/<id>.html      the eleven written updates (front matter + body)
  src/images/*.jpg           full-size photos (450px)
  src/images/thumbs/*.jpg    90px thumbnails used on album pages
  src/images/albums/*.jpg    200px album covers
  src/images/pagetitle.gif   the header wordmark

Usage: python3 -I scripts/import-legacy.py <crawl_dir> <data_dir> <repo_root>
"""
import sys, os, re, json, html, shutil

crawl_dir, data_dir, root = sys.argv[1:4]
src = os.path.join(root, "src")
for d in ("_data", "updates", "images/thumbs", "images/albums"):
    os.makedirs(os.path.join(src, d), exist_ok=True)

def to_text(s):
    s = re.sub(r'<br\s*/?>', ' ', s or '')
    s = html.unescape(re.sub(r'<[^>]+>', '', s))
    return re.sub(r'\s+', ' ', s).strip()

def check(label, s):
    bad = sorted(set(ch for ch in s if ord(ch) > 127))
    if bad: print(f"  WARNING non-ascii in {label}: {bad!r}")
    if re.search(r'\{[{%#]', s): print(f"  WARNING template syntax in {label}")

def copy(srcp, dstp):
    if os.path.exists(srcp) and os.path.getsize(srcp) > 0 and not os.path.exists(dstp):
        shutil.copyfile(srcp, dstp)

crawl = json.load(open(os.path.join(data_dir, "crawl.json")))

# ---- albums (from the saved photoAlbums.php page) ---------------------
alb_html = open(os.path.join(crawl_dir, "photoAlbums.html"), encoding="latin-1").read()
pat = re.compile(r'href="photoMenu\.php\?album=(\d+)"><img src="images/albums/([^"]+)\.jpg"[^>]*></a></td>\s*'
                 r'<td[^>]*><p class="photoTitle"[^>]*>(.*?)</p><p class="default"[^>]*>(.*?)</p>', re.S)
albums = []
for num, cover, title, desc in pat.findall(alb_html):
    check(f"album {num}", desc)
    albums.append({"number": int(num), "cover": cover,
                   "descriptionHtml": desc.strip(), "descriptionText": to_text(desc)})
    copy(os.path.join(data_dir, "albums", cover + ".jpg"), os.path.join(src, "images", "albums", cover + ".jpg"))
albums.sort(key=lambda a: a["number"])
json.dump(albums, open(os.path.join(src, "_data", "albums.json"), "w"), indent=2)
print("albums:", len(albums))

# ---- photos ------------------------------------------------------------
photos, missing = [], []
for p in crawl["photos"]:
    pid = p["id"]
    full = os.path.join(data_dir, "images", p["image"])
    has_image = os.path.exists(full) and os.path.getsize(full) > 0
    if not has_image: missing.append(pid)
    copy(full, os.path.join(src, "images", pid + ".jpg"))
    copy(os.path.join(data_dir, "thumbs", pid + ".jpg"), os.path.join(src, "images", "thumbs", pid + ".jpg"))
    check(f"photo {pid}", p["title"] + p["caption"])
    photos.append({"id": pid, "album": int(pid[1:3]), "frame": int(pid[4:6]),
                   "titleHtml": p["title"].strip(), "titleText": to_text(p["title"]),
                   "captionHtml": p["caption"].strip(), "hasImage": has_image})
photos.sort(key=lambda p: (p["album"], p["frame"]))
json.dump(photos, open(os.path.join(src, "_data", "photos.json"), "w"), indent=1)
print("photos:", len(photos), "with empty image on the old server:", missing)

# ---- updates -----------------------------------------------------------
for u in crawl["updates"]:
    check(f"update {u['id']}", u["bodyHtml"])
    title = to_text(u["title"]).replace('"', '\\"')
    doc = (f'---\ntitle: "{title}"\ndateText: "{u["dateText"]}"\nlegacyId: {u["id"]}\n---\n'
           f'{u["bodyHtml"].strip()}\n')
    open(os.path.join(src, "updates", f"{u['id']}.html"), "w").write(doc)
print("updates:", len(crawl["updates"]))

copy(os.path.join(data_dir, "images", "pagetitle.gif"), os.path.join(src, "images", "pagetitle.gif"))
