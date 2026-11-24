#!/usr/bin/env python3
"""Build the "Contributed to" chips: one SVG per project (logo + project name), styled
like GitHub's organization chips, linked and with a hover title in the README.
Avatars are embedded as data URIs (an SVG shown via <img> cannot load external images).
Run by hand when the list changes.
"""
import base64, html, pathlib, re, urllib.request

ROOT = pathlib.Path(__file__).resolve().parent.parent
FONT = "ui-monospace, SFMono-Regular, 'SF Mono', Menlo, Consolas, 'Liberation Mono', monospace"

# (file id, project name, logo source, link, hover text)
# Logo source: "gh:<login>" = GitHub avatar (org avatars are the project brand),
# a URL = the project's own icon, None = a neutral glyph (no logo published).
# Ordered biggest first: public projects by GitHub stars, then private orgs.
PROJECTS = [
    ("t3code", "T3 Code", "https://t3.codes/apple-touch-icon.png", "https://github.com/pingdotgg/t3code",
     "T3 Code by Ping: contributor"),
    ("vorssaint-utils", "Vorssaint Utils", "https://vorssaint.com/icon-192.png",
     "https://github.com/vorssaint/vorssaint-utils", "Vorssaint Utils: macOS menu bar toolkit"),
    ("zapfast", "ZapFast", "https://zapfast.rocks/assets/images/logo.svg", "https://github.com/crmne/zapfast",
     "ZapFast: native WhatsApp client in Rust"),
    ("search", "Search", None, "https://github.com/driceroland/Search", "Search: WebKit browser for macOS"),
    ("futzpro", "FutzPro", "gh:futz-pro", "https://github.com/futz-pro",
     "FutzPro: product design and engineering, web, mobile and API"),
    ("humanmade", "HUMANMADE", "gh:HUMANMADE-DC", "https://github.com/HUMANMADE-DC",
     "HUMANMADE: content tooling and automation"),
    ("howmuch", "How Much", "gh:HOWMUCH-Time-Cost", "https://github.com/HOWMUCH-Time-Cost/how-much",
     "How Much: prices as work days"),
]
H, AV, CHAR, FS = 28, 16, 7.25, 12  # chip height, logo size, mono glyph width at FS px, font size


def fetch(url):
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req) as r:
        return r.read(), r.headers.get_content_type()


def logo(src):
    if src.startswith("gh:"):
        src = f"https://github.com/{src[3:]}.png?size=64"
    data, mime = fetch(src)
    if data[:4] == b"\x89PNG":
        mime = "image/png"
    elif data[:3] == b"\xff\xd8\xff":
        mime = "image/jpeg"
    elif b"<svg" in data[:500]:
        mime = "image/svg+xml"
    return f"data:{mime};base64,{base64.b64encode(data).decode()}"


GLYPH = ('<rect x="{x}" y="{y}" width="{s}" height="{s}" rx="4" class="gl"/>'
         '<circle cx="{cx}" cy="{cy}" r="3.6" stroke-width="1.6" class="gs"/>'
         '<path d="M{lx1} {ly1}L{lx2} {ly2}" stroke-width="1.6" stroke-linecap="round" class="gs"/>')


def chip(name, src):
    w = round(8 + AV + 7 + len(name) * CHAR + 10)
    y = (H - AV) / 2
    if src:
        href = logo(src)
        mark = (f'<clipPath id="av"><rect x="8" y="{y}" width="{AV}" height="{AV}" rx="4"/></clipPath>'
                f'<image x="8" y="{y}" width="{AV}" height="{AV}" clip-path="url(#av)" href="{href}" xlink:href="{href}"/>')
    else:
        mark = GLYPH.format(x=8, y=y, s=AV, cx=8 + 7, cy=y + 7, lx1=8 + 9.6, ly1=y + 9.6, lx2=8 + 12, ly2=y + 12)
    return f"""<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" width="{w}" height="{H}" viewBox="0 0 {w} {H}" fill="none" role="img" aria-label="{html.escape(name)}">
  <style>
    text {{ font-family: {FONT}; }}
    .fg {{ fill: #1F2023; }} .bd {{ stroke: #D0D7DE; }} .gl {{ fill: #EAEEF2; }} .gs {{ stroke: #57606A; }}
    @media (prefers-color-scheme: dark) {{ .fg {{ fill: #F6F3EA; }} .bd {{ stroke: #3D444D; }} .gl {{ fill: #262C36; }} .gs {{ stroke: #C9D1D9; }} }}
  </style>
  <rect x="0.5" y="0.5" width="{w-1}" height="{H-1}" rx="6" class="bd"/>
  {mark}
  <text x="{8 + AV + 7}" y="{H/2 + 4}" class="fg" font-size="{FS}" font-weight="500">{html.escape(name)}</text>
</svg>
"""


def build():
    out = ROOT / "assets/projects"
    out.mkdir(parents=True, exist_ok=True)
    for old in out.glob("*.svg"):
        old.unlink()
    chips = []
    for fid, name, src, url, title in PROJECTS:
        (out / f"{fid}.svg").write_text(chip(name, src))
        t = html.escape(title)
        chips.append(f'<a href="{url}" title="{t}"><img src="assets/projects/{fid}.svg" height="{H}" alt="{html.escape(name)}" title="{t}" /></a>')
    block = "<!-- projects:start -->\n<p>\n" + "\n".join(chips) + "\n</p>\n<!-- projects:end -->"
    readme = ROOT / "README.md"
    text = readme.read_text()
    if "<!-- projects:start -->" in text:
        text = re.sub(r"<!-- projects:start -->.*?<!-- projects:end -->", lambda m: block, text, flags=re.S)
    else:
        text = text.rstrip() + "\n\n### Contributed to\n\n" + block + "\n"
    readme.write_text(text)
    print("ok", len(chips))


if __name__ == "__main__":
    build()
