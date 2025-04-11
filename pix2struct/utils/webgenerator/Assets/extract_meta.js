// $(document).ready(function() {
//     //Meta extraction
//     window.layout = $('meta[name=wg-layout]').attr("content");
//     window.palette = $('meta[name=wg-palette]').attr("content");
//   });

document.addEventListener("DOMContentLoaded", function() {
  const layoutMeta = document.querySelector('meta[name=wg-layout]');
  const paletteMeta = document.querySelector('meta[name=wg-palette]');

  window.layout = layoutMeta ? layoutMeta.getAttribute("content") : null;
  window.palette = paletteMeta ? paletteMeta.getAttribute("content") : null;
});

