#!/usr/bin/env python3
"""The three gates a huashu-motion film has to pass before anyone sees it.

    python qc_gate.py <path-to-huashu-motion> <project-dir> [--render]

Gate 1  om doctor   the machine can render at all (Node, FFmpeg, encoders, Chrome)
Gate 2  om check    the film is structurally sound before a single frame is rendered
                    (missing files, layout animations, fonts that are not shipped, text cut off
                    or covered, contrast under 4.5:1, root duration shorter than the timeline)
Gate 3  om qa       the render actually moves: no single-frame pops, no second that is completely
                    still unless it is a reading hold, real cuts, a motion curve

Why a script: every one of these prints ten lines, and it is very easy to read the first two and
start rendering. The gate fails loudly instead. Exit code 0 = passed, 1 = blocked.

The thresholds are the ones `om` itself states in its output (they come from measured launch films),
so this adds no opinion of its own — it only refuses to let a warning scroll past.
"""
import os
import re
import subprocess
import sys
import pathlib

OM = None
PROJECT = None
NODE = os.environ.get('OM_NODE', 'node')   # set OM_NODE if node is not on PATH


def run(args, timeout=900):
    r = subprocess.run([NODE, str(OM), *args], capture_output=True, text=True, timeout=timeout,
                       encoding='utf-8', errors='replace')
    return r.returncode, (r.stdout or '') + (r.stderr or '')


def gate_doctor():
    code, out = run(['doctor'])
    ok = code == 0 and '✓' in out
    fails = [l for l in out.splitlines() if l.strip().startswith('✗')]
    return ok, out.strip(), fails


def gate_check():
    code, out = run(['check', str(PROJECT), '--samples', '6'])
    errors = [l for l in out.splitlines() if '✗ error' in l]
    warns = [l for l in out.splitlines() if l.strip().startswith('! warning')]
    # warnings that are real defects rather than judgement calls
    blocking = [w for w in warns if re.search(r'missing-file|cut-off|stale-sound|low-contrast|layout-motion|font-not-shipped', w)]
    return not errors and not blocking, out.strip(), errors + blocking


def gate_qa():
    code, out = run(['qa', str(PROJECT)])
    body = out.strip()
    pops = 'single-frame pops' in body and '✓ no single-frame pops' not in body
    m = re.search(r'motion per second: ([0-9. ]+)\(contrast', body)
    mean = None
    if m:
        vals = [float(x) for x in m.group(1).split() if x]
        mean = sum(vals) / len(vals) if vals else None
    cuts = re.search(r'(\d+) hard cut\(s\)', body)
    flat_open = 'flat opening' in body
    no_motion = 'barely moves' in body
    still = re.search(r'still for .1 s: ([^\u2014\n]+)', body)
    # A still stretch is NOT a failure: qa itself says "fine for a reading hold or an end card".
    # It is a decision the operator has to make with eyes on the frame, so the gate prints the times
    # and moves on. What does block: pops, a flat first five seconds, and a film that barely moves.
    ok = not pops and not flat_open and not no_motion
    return ok, body, {'pops': pops, 'mean_motion': mean,
                      'cuts': int(cuts.group(1)) if cuts else None,
                      'still': still.group(1).strip() if still else None}


def main():
    global OM, PROJECT
    if len(sys.argv) < 3:
        sys.exit(__doc__)
    root = pathlib.Path(sys.argv[1]).resolve()
    OM = root / 'cli' / 'om.js'
    PROJECT = pathlib.Path(sys.argv[2]).resolve()
    if not OM.exists():
        sys.exit(f'no cli/om.js under {root}')
    if '--render' in sys.argv:
        run(['render', str(PROJECT)], timeout=3600)

    ok1, out1, f1 = gate_doctor()
    print('== GATE 1 · doctor ==')
    print(out1)
    if not ok1:
        print('\nBLOCKED: the machine cannot render. Fix the ✗ lines above.\n')
        return 1

    ok2, out2, f2 = gate_check()
    print('\n== GATE 2 · check ==')
    print(out2)
    if not ok2:
        print('\nBLOCKED: nothing rendered. Fix these first:\n  ' + '\n  '.join(f2) + '\n')
        return 1

    ok3, out3, s3 = gate_qa()
    print('\n== GATE 3 · qa ==')
    print(out3)
    if not ok3:
        print('\nBLOCKED: the render moves less than the tool expects. '
              'A still second is fine only inside a reading hold or an end card.\n')
        return 1

    print(f"\nPASS  cuts={s3['cuts']}  mean motion={s3['mean_motion']:.2f}/s")
    if s3['still']:
        print(f"NOTE  still at {s3['still']}")
        print('      open those seconds yourself: a reading hold or an end card is fine, '
              'a card that simply stopped moving is not.')
    return 0


if __name__ == '__main__':
    sys.exit(main())
