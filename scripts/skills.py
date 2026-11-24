#!/usr/bin/env python3
"""Build assets/skills.svg: tech logos grouped by area, one row, labels above.

Icons come from skillicons.dev once, at build time, and are embedded so the
README never depends on that service. Run by hand when the list changes.
"""
import pathlib, re, urllib.request

ROOT = pathlib.Path(__file__).resolve().parent.parent
FONT = "ui-monospace, SFMono-Regular, 'SF Mono', Menlo, Consolas, 'Liberation Mono', monospace"

GROUPS = [
    ("Design", ["figma"]),
    ("Frontend", ["ts", "js", "react", "nextjs", "tailwind", "vite", "vitest", "astro"]),
    ("Native", ["swift", "rust", "tauri", "electron"]),
    ("Backend", ["nodejs", "py", "supabase", "postgres"]),
    ("Infra", ["docker", "vercel", "cloudflare", "githubactions", "bash"]),
]
ICON, GAP, GROUP_GAP, TOP = 40, 6, 28, 24


def icon(name, n):
    req = urllib.request.Request(f"https://skillicons.dev/icons?i={name}&theme=dark", headers={"User-Agent": "curl/8"})
    raw = urllib.request.urlopen(req).read().decode()
    inner = raw[raw.index("<svg", 10): raw.rindex("</g>")].strip()
    # keep ids unique per icon
    ids = set(re.findall(r'id="([^"]+)"', inner))
    for i in ids:
        inner = inner.replace(f'id="{i}"', f'id="{i}_{n}"').replace(f"#{i})", f"#{i}_{n})").replace(f'"#{i}"', f'"#{i}_{n}"')
    return inner


def build():
    parts, x, n = [], 0, 0
    for label, names in GROUPS:
        parts.append(f'  <text x="{x}" y="12" class="mu" font-size="12" letter-spacing="1.5">{label.upper()}</text>')
        for name in names:
            svg = icon(name, n)
            svg = re.sub(r'^<svg ([^>]*?)width="256" height="256"',
                         rf'<svg \1x="{x}" y="{TOP}" width="{ICON}" height="{ICON}"', svg, count=1)
            parts.append("  " + svg)
            x += ICON + GAP
            n += 1
        x += GROUP_GAP - GAP
    W, H = x - GROUP_GAP, TOP + ICON
    alt = "Skills. " + ". ".join(f"{l}: {', '.join(ns)}" for l, ns in GROUPS)
    out = f"""<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" width="{W}" height="{H}" viewBox="0 0 {W} {H}" fill="none" role="img" aria-label="{alt}">
  <title>{alt}</title>
  <style>
    text {{ font-family: {FONT}; }}
    .mu {{ fill: #6B6B66; }}
    @media (prefers-color-scheme: dark) {{ .mu {{ fill: #9C9C96; }} }}
  </style>
{chr(10).join(parts)}
</svg>
"""
    (ROOT / "assets/skills.svg").write_text(out)
    print("ok", W, H)


if __name__ == "__main__":
    build()
