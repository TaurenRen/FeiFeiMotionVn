#!/usr/bin/env python3
"""Replace the film's animation <script> with assets/film-script.js.

The film's script is the one part of index.html that gets rewritten over and over (it is the
animation, and `om qa` is what decides whether it is finished). Keeping it in its own file makes the
diff readable and stops a stray edit from taking the om-score block with it. index.html keeps a copy
so the film stays a single open file — this is the copy step.

    python assets/splice_script.py
"""
import pathlib
import re

root = pathlib.Path(__file__).resolve().parent.parent
src = (root / 'assets/film-script.js').read_text(encoding='utf-8')
html_path = root / 'index.html'
html = html_path.read_text(encoding='utf-8')

# the animation script is the last <script> without a src/type, after the om-score block
score_end = re.search(r'<script type="text/vnd\.abc" id="om-score">[\s\S]*?</script>', html)
if not score_end:
    raise SystemExit('no om-score block in index.html')
tail = html[score_end.end():]
m = re.search(r'<script>\n([\s\S]*?)</script>', tail)
if not m:
    raise SystemExit('no animation <script> after the om-score block')
new_tail = tail[:m.start()] + '<script>\n' + src + '</script>' + tail[m.end():]
html_path.write_text(html[:score_end.end()] + new_tail, encoding='utf-8', newline='')
print(f'animation script spliced: {len(src)} bytes')
