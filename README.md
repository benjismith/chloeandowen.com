# chloeandowen.com

A static rebuild of the 2002–2006 family photo site, which used to run as a
PHP script on a DigitalOcean droplet. The look and markup are kept as they
were; only the URLs changed from query strings to paths, and the
"add caption" button was dropped because there is no server any more.

Built with [Eleventy](https://www.11ty.dev/) and deployed to GitHub Pages by
`.github/workflows/deploy.yml` on every push to `main`.

## Layout

| Old URL                      | New URL              | Template                 |
| ---------------------------- | -------------------- | ------------------------ |
| `index.php`                  | `/`                  | `src/index.njk`          |
| `updates.php`                | `/updates/`          | `src/updates/index.njk`  |
| `update.php?id=12`           | `/updates/12/`       | `src/updates/12.html`    |
| `photoAlbums.php`            | `/albums/`           | `src/albums/index.njk`   |
| `photoMenu.php?album=55`     | `/albums/55/`        | `src/albums/album.njk`   |
| `photoMenu.php`              | `/photos/`           | `src/photos/index.njk`   |
| `photoDetail.php?id=R55-09`  | `/photos/R55-09/`    | `src/photos/photo.njk`   |

`src/404.njk` redirects the old `.php` URLs to their new paths, so old
bookmarks and links in emails still work.

Content lives in `src/_data/albums.json` (55 albums), `src/_data/photos.json`
(1452 photos: id, album, title, caption) and `src/updates/*.html` (11 written
updates). `src/_data/gallery.js` joins albums and photos and adds previous/next
links. Images are in `src/images/` (full size), `src/images/thumbs/` (90px) and
`src/images/albums/` (200px covers), copied through unchanged.

`scripts/` holds the one-off crawler and importer that pulled everything off
the old server.

## Working on it

```
npm install
npm run dev      # serves http://localhost:8080 and rebuilds on change
npm run build    # writes _site/
```
