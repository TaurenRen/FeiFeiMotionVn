#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Push this repo to GitHub through the Git Data API.

Why not `git push`: on this machine git's HTTPS path is blocked (connection reset / 502 through the
local proxy) while api.github.com answers fine. So the push is one commit built from the API:
blobs -> tree -> commit -> ref. Binary evidence (mp4, gif, png) goes through the blobs endpoint as
base64 instead of being skipped.

    python scripts/sync_github.py                 # message generated
    python scripts/sync_github.py -m "add xxx"    # explicit message

Requires `gh auth status` to be logged in and the repo to exist.
"""
import base64
import datetime
import json
import os
import subprocess
import sys

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

GH = os.environ.get('GH_BIN', r'D:/WorkBuddy/.workbuddy/binaries/tools/bin/gh.exe')
OWNER = 'TaurenRen'
NAME = 'huashu-motion-win32'
REPO = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
TMP = os.path.join(REPO, '.sync-tmp')


def gh(args, inp_path=None, allow_fail=False):
    cmd = [GH, 'api'] + args
    if inp_path:
        cmd += ['--input', '-']
        with open(inp_path, 'rb') as fh:
            r = subprocess.run(cmd, stdin=fh, capture_output=True, text=True, encoding='utf-8')
    else:
        r = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8')
    if r.returncode != 0 and not allow_fail:
        print('FAIL:', ' '.join(args))
        print((r.stdout or '')[:1200], (r.stderr or '')[:600])
        sys.exit(1)
    try:
        return json.loads(r.stdout) if r.stdout.strip() else {}
    except Exception:
        return {}


def blob(path, data):
    """A tree entry for one file: inline text, or a base64 blob when it is not UTF-8."""
    try:
        return {'path': path, 'mode': '100644', 'type': 'blob', 'content': data.decode('utf-8')}
    except UnicodeDecodeError:
        p = os.path.join(TMP, 'blob.json')
        with open(p, 'w', encoding='utf-8') as fh:
            json.dump({'content': base64.b64encode(data).decode('ascii'), 'encoding': 'base64'}, fh)
        r = gh(['-X', 'POST', 'repos/%s/%s/git/blobs' % (OWNER, NAME)], inp_path=p)
        print('  blob %-42s %6.1f KB' % (path, len(data) / 1024))
        return {'path': path, 'mode': '100644', 'type': 'blob', 'sha': r['sha']}


def main():
    os.makedirs(TMP, exist_ok=True)
    msg = None
    if '-m' in sys.argv:
        msg = sys.argv[sys.argv.index('-m') + 1]
    if not msg:
        msg = 'sync %s' % datetime.datetime.now().strftime('%Y-%m-%d %H:%M')

    info = gh(['repos/%s/%s' % (OWNER, NAME)])
    branch = info.get('default_branch', 'main')

    # A brand new repo has no commit, and the blobs endpoint answers 409 "Git Repository is empty"
    # until one exists. So make the branch first, then build the real tree on top of it.
    head = gh(['repos/%s/%s/git/refs/heads/%s' % (OWNER, NAME, branch)], allow_fail=True)
    if not head.get('object'):
        init_path = os.path.join(TMP, 'init.json')
        with open(init_path, 'w', encoding='utf-8') as fh:
            json.dump({'message': 'init', 'content': base64.b64encode(b'# init\n').decode('ascii')}, fh)
        r0 = subprocess.run([GH, 'api', '-X', 'PUT', 'repos/%s/%s/contents/README.md' % (OWNER, NAME),
                             '--input', '-'], stdin=open(init_path, 'rb'), capture_output=True)
        print('init branch:', 'ok' if r0.returncode == 0 else r0.stderr.decode('utf-8', 'replace')[:200])
        head = gh(['repos/%s/%s/git/refs/heads/%s' % (OWNER, NAME, branch)], allow_fail=True)
    parents = [head['object']['sha']] if head.get('object') else []

    files = subprocess.run(['git', 'ls-files'], cwd=REPO, capture_output=True, text=True).stdout.split()
    if not files:
        sys.exit('git ls-files is empty — git add the files first')

    tree = []
    for f in files:
        with open(os.path.join(REPO, f.replace('/', os.sep)), 'rb') as fh:
            tree.append(blob(f, fh.read()))
    print('files =', len(tree))

    tree_path = os.path.join(TMP, 'tree.json')
    with open(tree_path, 'w', encoding='utf-8') as fh:
        json.dump({'tree': tree}, fh, ensure_ascii=False)

    t = gh(['-X', 'POST', 'repos/%s/%s/git/trees' % (OWNER, NAME)], inp_path=tree_path)
    print('tree   =', t.get('sha'))

    commit_path = os.path.join(TMP, 'commit.json')
    with open(commit_path, 'w', encoding='utf-8') as fh:
        json.dump({'message': msg, 'tree': t['sha'], 'parents': parents}, fh, ensure_ascii=False)
    c = gh(['-X', 'POST', 'repos/%s/%s/git/commits' % (OWNER, NAME)], inp_path=commit_path)
    print('commit =', c.get('sha'))

    ref_path = os.path.join(TMP, 'ref.json')
    with open(ref_path, 'w', encoding='utf-8') as fh:
        json.dump({'sha': c['sha'], 'force': True}, fh)
    gh(['-X', 'PATCH', 'repos/%s/%s/git/refs/heads/%s' % (OWNER, NAME, branch)], inp_path=ref_path)

    print('DONE -> https://github.com/%s/%s' % (OWNER, NAME))


if __name__ == '__main__':
    main()
