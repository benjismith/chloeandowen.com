module.exports = function (eleventyConfig) {

  // Photos, thumbnails, album covers and the header wordmark are served
  // verbatim at the same /images/... paths the old PHP site used.
  eleventyConfig.addPassthroughCopy("src/images");

  // The written updates, newest first (the old site ordered them by id).
  eleventyConfig.addCollection("updates", function (collectionApi) {
    return collectionApi.getFilteredByGlob("src/updates/*.html").sort((a, b) => {
      return b.data.legacyId - a.data.legacyId;
    });
  });

  // Split a list into rows of n (thumbnail tables are six across).
  eleventyConfig.addFilter("chunk", function (list, n) {
    const rows = [];
    for (let i = 0; i < list.length; i += n) rows.push(list.slice(i, i + n));
    return rows;
  });

  return {
    dir: {
      input: "src",
      output: "_site",
      includes: "_includes",
      data: "_data"
    },
    templateFormats: ["njk", "html"],
    htmlTemplateEngine: "njk"
  };
};
