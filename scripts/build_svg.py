#!/usr/bin/env python3
"""Build profile-dark.svg / profile-light.svg (neofetch-style profile card).

Layout + static content live here; scripts/update_stats.py only patches the
value <tspan>s (id="...") afterwards. Re-run this script when the ASCII art
or the info block changes, then run update_stats.py to fill in live values.
"""

from html import escape
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ART = (ROOT / "ascii" / "carlo.txt").read_text().rstrip("\n").split("\n")

FONT = "'SFMono-Regular',Consolas,'Liberation Mono',Menlo,monospace"
FONT_SIZE = 10
LINE_HEIGHT = 13
ART_X = 24
INFO_X = 400
TOP = 30
WIDTH = 790

THEMES = {
    "dark": {
        "bg": "#0d1117",
        "border": "#30363d",
        "text": "#c9d1d9",
        "art": "#c9d1d9",
        "key": "#ffa657",
        "head": "#58a6ff",
        "dim": "#8b949e",
    },
    "light": {
        "bg": "#ffffff",
        "border": "#d0d7de",
        "text": "#24292f",
        "art": "#2a2f37",
        "key": "#953800",
        "head": "#0969da",
        "dim": "#57606a",
    },
}

RULE = "─" * 44

# Each line is a list of segments: (style, text[, tspan-id]).
# Styles: head | dim | key | text. Values patched by update_stats.py get ids.
LINES = [
    [("head", "Carlo van Driesten")],
    [("dim", RULE)],
    [("key", "Role ........ "), ("text", "Systems Architect, Virtual Test & Validation")],
    [("key", "Host ........ "), ("text", "BMW Group | vDL Digital Ventures GmbH")],
    [("key", "Uptime ...... "), ("text", "—", "uptime")],
    [("key", "Focus ....... "), ("text", "Agentic AI, Data Spaces, Simulation")],
    [],
    [("key", "Lang.Code ... "), ("text", "Python, TypeScript")],
    [("key", "Lang.Data ... "), ("text", "OWL/RDF, LinkML, SHACL, JSON-LD")],
    [("key", "Standards ... "), ("text", "ASAM OSI (CCB) | ASAM OpenX | ISO 3450x")],
    [("key", "Web3 ........ "), ("text", "TZIP | CAIP")],
    [("key", "Projects .... "), ("text", "Lichtblick | ENVITED-X | Haven")],
    [],
    [("head", "Contact")],
    [("dim", RULE)],
    [("key", "Email ....... "), ("text", "github.com.charity937@passmail.com")],
    [("key", "Web ......... "), ("text", "vdl.digital | reachhaven.com")],
    [("key", "LinkedIn .... "), ("text", "in/carlo-van-driesten")],
    [],
    [("head", "GitHub Stats")],
    [("dim", RULE)],
    [("key", "Repos ....... "), ("text", "—", "repos"), ("dim", " public · contributed to "), ("text", "—", "contrib")],
    [("key", "Commits ..... "), ("text", "—", "commits")],
    [("key", "PRs ......... "), ("text", "—", "prs"), ("dim", " · reviews "), ("text", "—", "reviews")],
    [("key", "Issues ...... "), ("text", "—", "issues")],
    [("key", "Stars ....... "), ("text", "—", "stars"), ("dim", " · followers "), ("text", "—", "followers")],
    [],
    [("dim", "updated "), ("dim", "—", "updated"), ("dim", " · github.com/jdsika/jdsika")],
]

HEIGHT = TOP + max(len(ART), len(LINES)) * LINE_HEIGHT + 22


def render(theme: dict) -> str:
    out = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{WIDTH}" height="{HEIGHT}" '
        f'viewBox="0 0 {WIDTH} {HEIGHT}" role="img" '
        'aria-label="Carlo van Driesten — GitHub profile card">',
        f'<rect x="0.5" y="0.5" width="{WIDTH - 1}" height="{HEIGHT - 1}" rx="6" '
        f'fill="{theme["bg"]}" stroke="{theme["border"]}"/>',
        f'<g font-family="{FONT}" font-size="{FONT_SIZE}" xml:space="preserve">',
    ]

    for i, line in enumerate(ART):
        y = TOP + i * LINE_HEIGHT
        # Non-breaking spaces: SVG renderers collapse leading ASCII spaces
        # even with xml:space="preserve", which would shear the portrait.
        art_line = escape(line).replace(" ", " ")
        out.append(f'<text x="{ART_X}" y="{y}" fill="{theme["art"]}">{art_line}</text>')

    for i, segments in enumerate(LINES):
        if not segments:
            continue
        y = TOP + i * LINE_HEIGHT
        spans = []
        for segment in segments:
            style, value = segment[0], segment[1]
            span_id = f' id="{segment[2]}"' if len(segment) > 2 else ""
            weight = ' font-weight="bold"' if style == "head" else ""
            spans.append(
                f'<tspan{span_id} fill="{theme[style]}"{weight}>{escape(value)}</tspan>'
            )
        out.append(f'<text x="{INFO_X}" y="{y}">{"".join(spans)}</text>')

    out.append("</g></svg>")
    return "\n".join(out) + "\n"


for name, theme in THEMES.items():
    path = ROOT / f"profile-{name}.svg"
    path.write_text(render(theme))
    print(f"wrote {path}")
