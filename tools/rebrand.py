#!/usr/bin/env python3
"""One-time rebrand sweep: huashu -> feifei across the vendored engine.

Kept in the repo because a fork's provenance should be reproducible: run it on a fresh checkout of
the upstream engine and you get the same tree this repository ships. It only rewrites text files and
renames one directory; it never touches binary media.

    python tools/rebrand.py <engine-dir> [--dry]

What it does
------------
1. text replacements, longest first so `HUASHU-MOTION` does not get half-eaten by `huashu`
2. renames skills/huashu-motion -> skills/feifei-motion
3. drops the upstream's own author page and English README (the project has its own now)
4. prints a per-file count so the run is auditable

The original MIT copyright notice is NOT removed: it lives in NOTICE at the repository root, which is
what the licence asks for. Product naming is ours; provenance stays on the record.
"""
import os
import pathlib
import sys

TEXT_EXT = {'.js', '.mjs', '.cjs', '.json', '.md', '.html', '.css', '.txt', '.py', '.abc', '.ps1', '.sh'}
SKIP_DIRS = {'.git', '.om', 'out', 'node_modules', '.sync-tmp'}

REPLACEMENTS = [
    ('HUASHU-MOTION', 'FEIFEI-MOTION'),
    ('Huashu-Motion', 'FeiFeiMotionVn'),
    ('Huashu Motion', 'FeiFeiMotionVn'),
    ('huashu-motion', 'feifei-motion'),
    ('huashu_motion', 'feifei_motion'),
    ('huashu design', 'feifei design'),
    ('HUASHU DESIGN', 'FEIFEI DESIGN'),
    ('Huashu Design', 'FeiFei Design'),
    ('huashu-design', 'feifei-design'),
    ('Huashu', 'FeiFei'),
    ('HUASHU', 'FEIFEI'),
    ('huashu', 'feifei'),
    ('花叔', 'FeiFei'),
]

DROP = [
    'README.en.md',
    'skills/feifei-motion/references/about-author.md',
]


def sweep(root, dry=False):
    total_files = 0
    total_hits = 0
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
        for name in filenames:
            p = pathlib.Path(dirpath) / name
            if p.suffix.lower() not in TEXT_EXT:
                continue
            try:
                s = p.read_text(encoding='utf-8')
            except (UnicodeDecodeError, OSError):
                continue
            hits = 0
            out = s
            for a, b in REPLACEMENTS:
                if a in out:
                    hits += out.count(a)
                    out = out.replace(a, b)
            if hits:
                total_files += 1
                total_hits += hits
                print('%5d  %s' % (hits, p.relative_to(root).as_posix()))
                if not dry:
                    p.write_text(out, encoding='utf-8', newline='')
    return total_files, total_hits


def main():
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    root = pathlib.Path(sys.argv[1]).resolve()
    dry = '--dry' in sys.argv
    if not (root / 'cli' / 'om.js').exists():
        sys.exit(f'{root} does not look like an engine checkout')

    # the directory has to move before the sweep so any path inside a file points at the new name
    old = root / 'skills' / 'huashu-motion'
    new = root / 'skills' / 'feifei-motion'
    if old.exists() and not dry:
        old.rename(new)
        print('renamed skills/huashu-motion -> skills/feifei-motion')

    files, hits = sweep(root, dry)
    print(f'\n{files} files, {hits} replacements' + (' (dry run)' if dry else ''))

    for rel in DROP:
        p = root / rel
        if p.exists():
            if not dry:
                p.unlink()
            print('dropped', rel)


if __name__ == '__main__':
    main()
