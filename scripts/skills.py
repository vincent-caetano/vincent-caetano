#!/usr/bin/env python3
"""Build the README skills grid: one column per area, one logo file each (hover shows the name).

Icons come from skillicons.dev once, at build time, and are embedded so the
README never depends on that service. Run by hand when the list changes.
"""
import html, pathlib, re, urllib.request

ROOT = pathlib.Path(__file__).resolve().parent.parent

GROUPS = [
    ("Product & design", ["figma", "framer", "webflow", "miro", "linear", "notion",
                          "posthog", "googleanalytics", "hotjar", "umami", "chatwoot"]),
    ("Frontend", ["ts", "js", "react", "nextjs", "tailwind", "vite", "vitest", "astro"]),
    ("Native", ["apple", "swift", "xcode", "expo", "rust", "tauri", "electron"]),
    ("Backend", ["nodejs", "py", "graphql", "supabase", "postgres", "neon", "redis",
                 "firebase", "stripe", "resend", "ffmpeg"]),
    ("Infra", ["linux", "nginx", "docker", "aws", "vercel", "cloudflare", "githubactions",
               "tailscale", "sentry", "grafana"]),
    ("AI & tools", ["claude", "claudecode", "codex", "raycast", "git", "npm", "bash"]),
]
NAMES = {
    "figma": "Figma", "framer": "Framer", "webflow": "Webflow", "miro": "Miro", "linear": "Linear",
    "notion": "Notion", "posthog": "PostHog", "googleanalytics": "Google Analytics", "hotjar": "Hotjar",
    "umami": "Umami", "chatwoot": "Chatwoot", "ts": "TypeScript", "js": "JavaScript", "react": "React",
    "nextjs": "Next.js", "tailwind": "Tailwind CSS", "vite": "Vite", "vitest": "Vitest", "astro": "Astro",
    "apple": "SwiftUI", "swift": "Swift", "xcode": "Xcode", "expo": "Expo / React Native", "rust": "Rust",
    "tauri": "Tauri", "electron": "Electron", "nodejs": "Node.js", "py": "Python", "graphql": "GraphQL",
    "supabase": "Supabase", "postgres": "PostgreSQL", "neon": "Neon", "redis": "Redis",
    "firebase": "Firebase", "stripe": "Stripe", "resend": "Resend", "ffmpeg": "FFmpeg", "linux": "Linux",
    "nginx": "Nginx", "docker": "Docker", "aws": "AWS", "vercel": "Vercel", "cloudflare": "Cloudflare",
    "githubactions": "GitHub Actions", "tailscale": "Tailscale", "sentry": "Sentry", "grafana": "Grafana",
    "claude": "Claude API", "claudecode": "Claude Code", "codex": "Codex", "raycast": "Raycast",
    "git": "Git", "npm": "npm", "bash": "Bash",
}

# Not in skillicons: logo drawn on a matching tile. Value: (colour, source).
# Near-black brands use warm white so they show on the dark tile (Miro: its yellow).
W_ = "#F6F3EA"
SI = "https://cdn.jsdelivr.net/npm/simple-icons@16.38.1/icons/{}.svg"
LH = "https://cdn.jsdelivr.net/npm/@lobehub/icons-static-svg@1.106.0/icons/{}.svg"
SIMPLE = {
    "linear": ("#5E6AD2", SI), "posthog": (W_, SI), "googleanalytics": ("#E37400", SI),
    "neon": ("#34D59A", SI), "resend": (W_, SI), "tailscale": (W_, SI), "framer": (W_, SI),
    "miro": ("#FFD02F", SI), "hotjar": ("#FF3C00", SI), "stripe": ("#635BFF", SI),
    "expo": (W_, SI), "umami": (W_, SI), "chatwoot": ("#1F93FF", SI),
    "xcode": ("#147EFB", SI), "ffmpeg": ("#2FB344", SI), "raycast": ("#FF6363", SI),
    "claude": ("#D97757", LH), "claudecode": ("#D97757", LH), "codex": (W_, LH),
}
COLUMN = 846  # GitHub profile README content width on desktop, px
CELL_ICON, PER_ROW, SLOT_GAP, COL_GAP = 32, 3, 6, 24  # README grid: logo px, logos per column line, gaps
FONT = "ui-monospace, SFMono-Regular, 'SF Mono', Menlo, Consolas, 'Liberation Mono', monospace"


def simple_tile(name):
    colour, src = SIMPLE[name]
    req = urllib.request.Request(src.format(name), headers={"User-Agent": "curl/8"})
    raw = urllib.request.urlopen(req).read().decode()
    inner = re.sub(r"<title>.*?</title>", "", raw[raw.index(">") + 1: raw.rindex("</svg>")])
    return ('<svg xmlns="http://www.w3.org/2000/svg" width="256" height="256" fill="none" viewBox="0 0 256 256">'
            '<rect width="256" height="256" fill="#242938" rx="60"/>'
            f'<g transform="translate(56 56) scale(6)" fill="{colour}" fill-rule="evenodd">{inner}</g></svg>')


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
    # Each logo is its own file so it can carry a hover title on GitHub
    # (an SVG shown through <img> ignores titles inside it).
    icons = ROOT / "assets/icons"
    icons.mkdir(parents=True, exist_ok=True)
    for old in icons.glob("*.svg"):
        old.unlink()
    n = 0
    for _, names in GROUPS:
        for name in names:
            svg = icon(name, n)
            if "xmlns:xlink" not in svg and "xlink:" in svg:
                svg = svg.replace("<svg ", '<svg xmlns:xlink="http://www.w3.org/1999/xlink" ', 1)
            # Built-in size = README size, for viewers that ignore % widths (e.g. T3's preview).
            svg = re.sub(r'^<svg ([^>]*?)width="256" height="256"', rf'<svg \1width="{CELL_ICON}" height="{CELL_ICON}"', svg, count=1)
            if "viewBox" not in svg.split(">", 1)[0]:
                svg = svg.replace("<svg ", '<svg viewBox="0 0 256 256" ', 1)
            (icons / f"{name}.svg").write_text(svg + "\n")
            n += 1
    write_readme()
    print("ok", n)


def write_readme():
    """Skills grid without a table (GitHub tables always get borders and a fill):
    one header image with the area labels, then lines of logos where invisible
    spacer images hold every column in place. Each logo keeps a hover title."""
    import hashlib
    cols = len(GROUPS)
    col_w = PER_ROW * CELL_ICON + (PER_ROW - 1) * SLOT_GAP
    total_w = cols * col_w + (cols - 1) * COL_GAP

    labels = "".join(
        f'<text x="{c * (col_w + COL_GAP)}" y="11" class="mu" font-size="10.5" letter-spacing="0.6">{html.escape(l.upper())}</text>'
        for c, (l, _) in enumerate(GROUPS))
    head = (f'<svg xmlns="http://www.w3.org/2000/svg" width="{total_w}" height="16" viewBox="0 0 {total_w} 16" '
            f'fill="none" role="img" aria-label="Skill areas"><style>text {{ font-family: {FONT}; }} '
            '.mu { fill: #6B6B66; } @media (prefers-color-scheme: dark) { .mu { fill: #9C9C96; } }</style>'
            f'{labels}</svg>\n')
    v = hashlib.sha1(head.encode()).hexdigest()[:8]
    for old in (ROOT / "assets").glob("skills-head*.svg"):
        old.unlink()
    (ROOT / f"assets/skills-head-{v}.svg").write_text(head)
    # Spacers carry their real size too, so the fallback layout keeps the columns.
    for w in {SLOT_GAP, COL_GAP, CELL_ICON}:
        (ROOT / f"assets/icons/_{w}.svg").write_text(
            f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{CELL_ICON}" viewBox="0 0 {w} {CELL_ICON}"/>\n')

    # Widths as % of the README column so the grid fills it like the stats card.
    # Scaled to 99.4% so sub-pixel rounding never pushes the last logo to a new line.
    def pct(px):
        return f"{px / total_w * 99.4:.3f}%"

    # Fixed heights reserve each line before the images load (no layout shift).
    # Sized for GitHub's desktop README column; SVGs keep their ratio when narrower.
    row_h = round(COLUMN * 0.994 * CELL_ICON / total_w)
    head_h = round(COLUMN * 0.994 * 16 / total_w)

    def gap(w):
        return f'<img src="assets/icons/_{w}.svg" width="{pct(w)}" height="{row_h}" alt="" />'

    def img(n):
        t = html.escape(NAMES[n])
        return f'<img src="assets/icons/{n}.svg" width="{pct(CELL_ICON)}" height="{row_h}" alt="{t}" title="{t}" />'

    rows = max(-(-len(ns) // PER_ROW) for _, ns in GROUPS)
    lines = []
    for r in range(rows):
        parts = []
        for c, (_, ns) in enumerate(GROUPS):
            if c:
                parts.append(gap(COL_GAP))
            for k in range(PER_ROW):
                if k:
                    parts.append(gap(SLOT_GAP))
                i = r * PER_ROW + k
                parts.append(img(ns[i]) if i < len(ns) else gap(CELL_ICON))
        lines.append("".join(parts))

    line = " · ".join(f"<b>{html.escape(l)}</b> {html.escape(', '.join(NAMES[n] for n in ns))}" for l, ns in GROUPS)
    block = (f'<!-- skills:start -->\n<p><img src="assets/skills-head-{v}.svg" width="99.4%" height="{head_h}" alt="" /><br />\n'
             + "<br />\n".join(lines) + "</p>\n\n"
             f"<p><sub>{line}</sub></p>\n<!-- skills:end -->")
    readme = ROOT / "README.md"
    text = re.sub(r"<!-- skills:start -->.*?<!-- skills:end -->", lambda m: block, readme.read_text(), flags=re.S)
    readme.write_text(text)


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
