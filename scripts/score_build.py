#!/usr/bin/env python3
"""Build a bar-accurate ABC score from a compact spec, and refuse to write one that is off.

Why this exists — the trap in huashu-motion's composer mode
-----------------------------------------------------------
`om sound` fits a written score to the picture: every `!mark:name!` has to sound on the timeline
label `scene:name`, so the tempo is bent between marks. A stretch with the wrong number of bars does
not error — it plays that stretch 25 % slower or 50 % faster, and the only warning is one line in the
report you can easily miss.

The unit arithmetic that caused it, measured on this machine (2026-10-24) against
`cli/lib/composer.js` with M:4/4, L:1/8 — one 4/4 bar is **4 units**, and

    bare note = 0.5      X/ = 0.25      X2 = 1      X4 = 2      X8 = 4      z8 = 4 (a bar of rest)

so eight bare notes fill a bar, sixteen `X/` notes do too, and `X8` alone does as well. Reading `z4`
as "a bar of rest" (it is half a bar) is how the first draft of this film's score drifted a bar,
bent the tempo 50 % and ran 8 s past the picture.

So: describe each bar, let the builder sum the units, and make it refuse to write anything that is
not exactly 4 units in every voice.

Usage
-----
    python score_build.py             # writes score.abc next to this file
    python score_build.py --print     # print the ABC without writing
"""
import pathlib
import re
import sys

BARS = 11                 # 11 bars of 4/4 at 100 bpm = 26.4 s, matching the film
UNIT = 4                  # units in one 4/4 bar, as cli/lib/composer.js counts them
BPM = 100
SECONDS_PER_BAR = 60 / BPM * 4

# scene name -> bar index (0-based). Marks are generated from this map, so they cannot drift.
SCENES = {'title': 0, 'claim': 2, 'doctor': 3, 'break': 5, 'numbers': 7, 'end': 9}

VOICES = ['PLK', 'SAW', 'PNO', 'BAS', 'DR']
INST = {
    'PLK': 'inst=synpluck gain=0.5',
    'SAW': 'inst=supersaw gain=0.42',
    'PNO': 'inst=piano',
    'BAS': 'inst=synbass gain=0.8',
    'DR': 'inst=drums kit=pop gain=0.85',
}


def arp(root, fifth):
    """Sixteen `X/` notes: one bar of sixteenth-feel arpeggio."""
    return f'{root}/{fifth}/{root.lower()}/{fifth}/ ' * 4


def pad(*notes):
    """A whole-bar chord."""
    return '[' + ','.join(notes) + ']8'


def pulse(note):
    """Two eighths per beat, eight per bar: the driving bass."""
    return (f'{note}{note} ') * 4


def kit():
    """Kick on every beat."""
    return 'C,,2 C,,2 C,,2 C,,2'


def build():
    spec = {v: [''] * BARS for v in VOICES}

    # PLK — the plucked figure carries every section
    spec['PLK'] = [
        arp('D', 'A'), arp('C', 'G'),                          # 1-2 hook
        'D/A/d/A/ ' * 2 + 'z4',                               # 3 half-time: the floor drops out
        'A/E/a/E/ ' * 4, 'B,/F/b/F/ ' * 4,                     # 4-5 the machine reporting
        'D/A/d/A/ F/A/d/A/ ' * 2, 'C/G/c/G/ D/A/d/A/ ' * 2,    # 6-7 build
        '[Dd]2 [Dd]2 [Dd]2 [Dd]2',                             # 8 drop
        '[Cc]2 [Cc]2 [B,B]2 [A,A]2',                           # 9
        'D/A/d/A/ F/A/d/A/ ' * 2,                              # 10 button
        'D8',                                                  # 11 resolve
    ]
    # SAW — silent under the hook, holds the top of the drop
    spec['SAW'] = [
        '', '',
        pad('D,A,d'),
        pad('D,F,A,'), pad('B,,D,F,'),
        pad('D,F,A,'), pad('B,,D,F,'),
        'z[D,F,A,] ' * 4,
        'z[C,E,G,] ' * 2 + 'z[B,,D,F,] ' + 'z[A,,C,E,] ',
        pad('D,F,A,'), pad('D,A,d'),
    ]
    # PNO — two hits a bar, the weight under the drop
    spec['PNO'] = [
        '[D,,D,]2 z6', '[C,,C,]2 z6',
        '', '', '', '', '',
        '[D,,D,]2 z6', '[C,,C,]2 z6',
        '[D,,D,A,D]2 z6', pad('D,,D,A,D'),
    ]
    # BAS — the pulse
    spec['BAS'] = [
        pulse('D,,'), pulse('C,,'),
        'D,,4 z4',
        pulse('A,,,'), pulse('B,,,'),
        pulse('D,,'), pulse('C,,'),
        'D,,D,D,,D, ' * 2, 'C,,C,C,,C, ' * 2,
        'D,,4 D,,4', 'D,,8',
    ]
    # DR — drums
    spec['DR'] = [
        kit(), kit(),
        'C,,4 z4',
        kit(), kit(),
        kit(), 'C,,/ ' * 16,
        kit(), kit(),
        'C,,4 C,,4', 'C,,4 z4',
    ]

    problems = []
    for v in VOICES:
        for i in range(BARS):
            raw = spec[v][i].strip()
            if not raw:
                continue
            got = units(raw)
            if abs(got - UNIT) > 1e-9:
                problems.append(f'{v} bar {i + 1}: {got:g} units, need {UNIT} - {raw!r}')
    if problems:
        print('\n'.join(problems))
        sys.exit(f'{len(problems)} bar(s) do not add up; nothing written')

    for v in VOICES:
        for i in range(BARS):
            if not spec[v][i].strip():
                spec[v][i] = f'z{UNIT * 2}'   # z8 = a whole-bar rest
    return spec


SLOT = re.compile(r"\[[^\]]*\]\s*[0-9/*]*|[\^_=]*[A-Ga-gz][,']*\s*[0-9/*]*")


def dur(token):
    """The unit value cli/lib/composer.js advances for one token (a whole bar is 4)."""
    body = re.sub(r"^\s*\[[^\]]*\]|^\s*[\^_=]*[A-Ga-gz][,']*", '', token).strip()
    if not body:
        return 0.5                     # a bare note is an eighth
    if body.startswith('/'):
        return 0.5 / (2 ** body.count('/'))
    m = re.fullmatch(r'(\d+)\s*/\s*(\d+)', body)
    if m:                              # X3/2: three halves of the default length
        return 0.5 * int(m.group(1)) / int(m.group(2))
    if body.isdigit():
        return int(body) / 2           # X2 = 1, X4 = 2, X8 = 4
    return 0.5


def units(bar):
    return sum(dur(m.group(0)) for m in SLOT.finditer(bar))


def emit(spec):
    out = [
        '% Generated by assets/score_build.py - edit the spec there, not here.',
        f'% {BARS} bars of 4/4 at {BPM} bpm = {BARS * SECONDS_PER_BAR:.1f} s; every scene cut is a bar line.',
        'X:1',
        'T:Windows Test (tech launch cue: hook -> claim -> ticking doctor -> build -> drop -> button)',
        'M:4/4',
        'L:1/8',
        f'Q:1/4={BPM}',
        'K:Dm',
    ]
    for v in VOICES:
        out.append(f'V:{v} {INST[v]}')
        for i in range(BARS):
            # marks live in the first voice only: one clean beat per scene
            mark = next((f'!mark:{n}! ' for n, b in SCENES.items() if b == i), '') if v == VOICES[0] else ''
            out.append(f'{mark}{spec[v][i]} |'.strip())
    return '\n'.join(out) + '\n'


def main():
    path = pathlib.Path(__file__).resolve().parent / 'score.abc'
    spec = build()
    text = emit(spec)
    if '--print' in sys.argv:
        print(text)
        return
    path.write_text(text, encoding='utf-8', newline='')
    print(f'wrote {path} · {BARS} bars · {BARS * SECONDS_PER_BAR:.1f}s · {len(VOICES)} voices · '
          f'scenes at bars {SCENES}')


if __name__ == '__main__':
    main()
