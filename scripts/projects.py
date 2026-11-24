#!/usr/bin/env python3
"""Build the "Contributed to" chips: one SVG per project (avatar + @name), styled
like GitHub's organization chips, linked and with a hover title in the README.
Avatars are embedded as data URIs (an SVG shown via <img> cannot load external images).
Run by hand when the list changes.
"""
import base64, html, pathlib, re, urllib.request

ROOT = pathlib.Path(__file__).resolve().parent.parent
FONT = "ui-monospace, SFMono-Regular, 'SF Mono', Menlo, Consolas, 'Liberation Mono', monospace"

# (GitHub login for the avatar, link, hover text)
PROJECTS = [
    ("futz-pro", "https://github.com/futz-pro", "FutzPro: product design and engineering, web, mobile and API"),
    ("HUMANMADE-DC", "https://github.com/HUMANMADE-DC", "HUMANMADE: content tooling and automation"),
    ("pingdotgg", "https://github.com/pingdotgg/t3code", "T3 Code: contributor"),
    ("HOWMUCH-Time-Cost", "https://github.com/HOWMUCH-Time-Cost/how-much", "How Much: prices as work days"),
    ("vorssaint", "https://github.com/vorssaint/vorssaint-utils", "vorssaint-utils: macOS menu bar toolkit"),
    ("crmne", "https://github.com/crmne/zapfast", "ZapFast: native WhatsApp client in Rust"),
    ("driceroland", "https://github.com/driceroland/Search", "Search: WebKit browser for macOS"),
]
H, AV, CHAR = 40, 24, 8.45  # chip height, avatar size, mono glyph width at 14px


def avatar(login):
    req = urllib.request.Request(f"https://github.com/{login}.png?size=96", headers={"User-Agent": "curl/8"})
    data = urllib.request.urlopen(req).read()
    mime = "image/png" if data[:4] == b"\x89PNG" else "image/jpeg"
    return f"data:{mime};base64,{base64.b64encode(data).decode()}"


def chip(login):
    label = "@" + login
    w = round(12 + AV + 10 + len(label) * CHAR + 14)
    y = (H - AV) / 2
    src = avatar(login)
    return f"""<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" width="{w}" height="{H}" viewBox="0 0 {w} {H}" fill="none" role="img" aria-label="{html.escape(label)}">
  <style>
    text {{ font-family: {FONT}; }}
    .fg {{ fill: #1F2023; }} .bd {{ stroke: #D0D7DE; }}
    @media (prefers-color-scheme: dark) {{ .fg {{ fill: #F6F3EA; }} .bd {{ stroke: #3D444D; }} }}
  </style>
  <rect x="0.5" y="0.5" width="{w-1}" height="{H-1}" rx="8" class="bd"/>
  <clipPath id="av"><rect x="12" y="{y}" width="{AV}" height="{AV}" rx="6"/></clipPath>
  <image x="12" y="{y}" width="{AV}" height="{AV}" clip-path="url(#av)" href="{src}" xlink:href="{src}"/>
  <text x="{12 + AV + 10}" y="{H/2 + 5}" class="fg" font-size="14" font-weight="600">{html.escape(label)}</text>
</svg>
"""


def build():
    out = ROOT / "assets/projects"
    out.mkdir(parents=True, exist_ok=True)
    for old in out.glob("*.svg"):
        old.unlink()
    chips = []
    for login, url, title in PROJECTS:
        (out / f"{login}.svg").write_text(chip(login))
        t = html.escape(title)
        chips.append(f'<a href="{url}" title="{t}"><img src="assets/projects/{login}.svg" height="{H}" alt="@{login}" title="{t}" /></a>')
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
