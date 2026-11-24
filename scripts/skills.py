#!/usr/bin/env python3
"""Build assets/skills.svg: tech logos grouped by area, one row, labels above.

Icons come from skillicons.dev once, at build time, and are embedded so the
README never depends on that service. Run by hand when the list changes.
"""
import pathlib, re, urllib.request

ROOT = pathlib.Path(__file__).resolve().parent.parent
FONT = "ui-monospace, SFMono-Regular, 'SF Mono', Menlo, Consolas, 'Liberation Mono', monospace"

GROUPS = [
    ("Design", ["figma", "framer", "webflow", "miro"]),
    ("Product", ["linear", "notion", "posthog", "googleanalytics", "hotjar", "umami", "chatwoot"]),
    ("Frontend", ["ts", "js", "react", "nextjs", "tailwind", "vite", "vitest", "astro"]),
    ("Native", ["swift", "expo", "rust", "tauri", "electron"]),
    ("Backend", ["nodejs", "py", "supabase", "postgres", "neon", "stripe", "resend"]),
    ("Infra", ["docker", "vercel", "cloudflare", "githubactions", "tailscale", "sentry", "grafana", "bash"]),
]
# Not in skillicons: drawn from Simple Icons (pinned) on a matching tile.
# Value is the logo colour; near-black brands use warm white (Miro: its yellow).
SIMPLE = {"linear": "#5E6AD2", "posthog": "#F6F3EA", "googleanalytics": "#E37400",
          "neon": "#34D59A", "resend": "#F6F3EA", "tailscale": "#F6F3EA",
          "framer": "#F6F3EA", "miro": "#FFD02F", "hotjar": "#FF3C00", "stripe": "#635BFF",
          "expo": "#F6F3EA", "umami": "#F6F3EA", "chatwoot": "#1F93FF"}
SIMPLE_URL = "https://cdn.jsdelivr.net/npm/simple-icons@16.38.1/icons/{}.svg"
ICON, GAP, COL_GAP, TOP, W = 36, 6, 20, 26, 1094
INSET = 8  # same safe margin as the stats card


def simple_tile(name):
    req = urllib.request.Request(SIMPLE_URL.format(name), headers={"User-Agent": "curl/8"})
    path = re.search(r'<path d="([^"]+)"', urllib.request.urlopen(req).read().decode()).group(1)
    return ('<svg xmlns="http://www.w3.org/2000/svg" width="256" height="256" fill="none" viewBox="0 0 256 256">'
            '<rect width="256" height="256" fill="#242938" rx="60"/>'
            f'<path transform="translate(56 56) scale(6)" fill="{SIMPLE[name]}" d="{path}"/></svg>')


def icon(name, n):
    if name in SIMPLE:
        return simple_tile(name)
    req = urllib.request.Request(f"https://skillicons.dev/icons?i={name}&theme=dark", headers={"User-Agent": "curl/8"})
    raw = urllib.request.urlopen(req).read().decode()
    inner = raw[raw.index("<svg", 10): raw.rindex("</g>")].strip()
    # keep ids unique per icon
    ids = set(re.findall(r'id="([^"]+)"', inner))
    for i in ids:
        inner = inner.replace(f'id="{i}"', f'id="{i}_{n}"').replace(f"#{i})", f"#{i}_{n})").replace(f'"#{i}"', f'"#{i}_{n}"')
    return inner


def build():
    # One column per area, equal widths; icons wrap inside their column.
    cols = len(GROUPS)
    col_w = (W - COL_GAP * (cols - 1)) / cols
    per_row = max(1, int((col_w + GAP) // (ICON + GAP)))
    parts, n, H = [], 0, 0
    for c, (label, names) in enumerate(GROUPS):
        x0 = c * (col_w + COL_GAP)
        parts.append(f'  <text x="{x0:.0f}" y="12" class="mu" font-size="12" letter-spacing="1.5">{label.upper()}</text>')
        for i, name in enumerate(names):
            x = x0 + (i % per_row) * (ICON + GAP)
            y = TOP + (i // per_row) * (ICON + GAP)
            svg = re.sub(r'^<svg ([^>]*?)width="256" height="256"',
                         rf'<svg \1x="{x:.0f}" y="{y}" width="{ICON}" height="{ICON}"', icon(name, n), count=1)
            parts.append("  " + svg)
            H = max(H, y + ICON)
            n += 1
    alt = "Skills. " + ". ".join(f"{l}: {', '.join(ns)}" for l, ns in GROUPS)
    out = f"""<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" width="{W+2*INSET}" height="{H+2*INSET}" viewBox="0 0 {W+2*INSET} {H+2*INSET}" fill="none" role="img" aria-label="{alt}">
  <title>{alt}</title>
  <style>
    text {{ font-family: {FONT}; }}
    .mu {{ fill: #6B6B66; }}
    @media (prefers-color-scheme: dark) {{ .mu {{ fill: #9C9C96; }} }}
  </style>
<g transform="translate({INSET} {INSET})">
{chr(10).join(parts)}
</g>
</svg>
"""
    publish("skills", out)
    print("ok", W, H, per_row)


def publish(name, svg):
    """Write assets/<name>-<hash>.svg, drop older copies, point README at it.
    A new file name per version is the only cache-bust that survives GitHub's
    redirect to raw.githubusercontent.com (it drops query strings)."""
    import hashlib, re
    v = hashlib.sha1(svg.encode()).hexdigest()[:8]
    for old in (ROOT / "assets").glob(f"{name}*.svg"):
        old.unlink()
    (ROOT / f"assets/{name}-{v}.svg").write_text(svg)
    readme = ROOT / "README.md"
    readme.write_text(re.sub(rf'assets/{name}[^"]*\.svg[^"]*"', f'assets/{name}-{v}.svg"', readme.read_text()))


if __name__ == "__main__":
    build()
