#!/usr/bin/env python3
"""Put assets/score.abc into index.html as the om-score the CLI reads.

`om sound` only looks at <script type="text/vnd.abc" id="om-score"> inside the composition, so the
score exists twice while it is being written: the .abc file is what a person edits, this keeps the
copy in index.html in step. Run it after every change to the score.
"""
import io, re, sys, pathlib

root = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else '.')
abc = (root / 'assets/score.abc').read_text(encoding='utf-8')
html_path = root / 'index.html'
html = html_path.read_text(encoding='utf-8')
block = '<script type="text/vnd.abc" id="om-score">\n' + abc + '</script>'
new, n = re.subn(r'<script type="text/vnd\.abc" id="om-score">[\s\S]*?</script>', lambda m: block, html)
if n == 0:
    sys.exit('index.html has no om-score block — add one first')
html_path.write_text(new, encoding='utf-8', newline='')
print(f'om-score updated: {len(abc)} bytes, {abc.count(chr(10))} lines')
