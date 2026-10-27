// Joins albums.json and photos.json: each album gets its photos (in frame
// order), and each photo gets the ids of the previous and next photo in the
// site-wide sequence, which is what the old photoDetail page linked to.
const albums = require("./albums.json");
const photos = require("./photos.json");

module.exports = function () {
  const byNumber = new Map(albums.map((a) => [a.number, { ...a, photos: [] }]));
  for (const p of photos) byNumber.get(p.album).photos.push(p);

  const sequence = photos.map((p, i) => ({
    ...p,
    prev: i > 0 ? photos[i - 1].id : null,
    next: i < photos.length - 1 ? photos[i + 1].id : null,
  }));

  // Ids of every photo that has an image, for the random photo on the home page.
  const ids = photos.filter((p) => p.hasImage).map((p) => p.id).join(",");

  return { albums: [...byNumber.values()], photos: sequence, ids };
};
