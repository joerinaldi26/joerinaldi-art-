# joerinaldi.art

Joe Rinaldi's illustration portfolio. A plain static site: HTML, one CSS file, one small JavaScript file for the full-size viewer. No framework and no build step on the server.

```
content.json        all the words: series titles, decks, piece titles, Etsy links, lead pieces
build.py            turns content.json into the HTML in site/
site/               the website itself (this is what gets deployed)
  index.html          homepage
  <series>/index.html one page per series, at the same addresses as the old Squarespace site
  assets/             site.css, viewer.js
  fonts/              Big Shoulders Display, Libre Franklin, Libre Caslon Text (open licenses included)
  img/<series>/       NN-800.webp, NN-1600.webp, NN-full.webp for every piece
  img/cast/           cut-out characters for the homepage lineup
  _redirects          /about and /contact point to the About section
tools/images.py     converts new or higher-resolution originals into the three web sizes
```

## Editing

1. Change words in `content.json` (titles, captions, Etsy links, the About text, which piece leads each series).
   Hide a piece with `"hidden": true`. Pick a series' "Leading Off" piece with `lead.index`.
2. Rebuild: `python3 build.py` (Python 3.12 or newer, no packages needed).
3. Commit and push. Cloudflare redeploys automatically.

## Adding or replacing art

1. Drop originals in `originals/<series>/<NN>.png` (NN matches the piece number in content.json).
   For a new piece, add an entry to that series' `pieces` list first.
2. `pip install pillow` then `python3 tools/images.py`, then `python3 build.py`.

The Star Wars chases currently come from Squarespace, which caps images at 2500px wide.
Put the full-size originals in `originals/star-wars-chase/01.png` through `06.png` and run the
two commands above; the viewer will then show them at full detail.

## Deploying on Cloudflare

1. Push this folder to a GitHub repo.
2. Cloudflare dashboard: Workers & Pages, Create, Pages, Connect to Git, pick the repo.
3. Build settings: framework preset **None**, build command **empty**, build output directory **site**.
4. Deploy. Check the preview at the `*.pages.dev` address.
5. Custom domains: add `joerinaldi.art` (and `www.joerinaldi.art`). Follow Cloudflare's DNS
   instructions at the domain's registrar. Keep Squarespace running until the new site loads
   at joerinaldi.art, then cancel the Squarespace site plan (keep the domain registration unless
   you move it).

Pieces that open in the horizontal viewer are any piece more than 2.2 times wider than tall.
