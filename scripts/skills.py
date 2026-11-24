#!/usr/bin/env python3
"""Build the README skills table: one column per area, one logo file each (hover shows the name).

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
CELL_ICON, PER_ROW = 32, 3  # README table: logo size, logos per line in a cell


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
            (icons / f"{name}.svg").write_text(svg + "\n")
            n += 1
    write_readme()
    print("ok", n)


def write_readme():
    """Skills table (one column per area, hover names) plus a plain-text line."""
    head = "".join(f"<th><sub>{html.escape(l.upper())}</sub></th>" for l, _ in GROUPS)
    # GitHub sizes tables to max-content, so break rows by hand to stay in width.
    def img(n):
        t = html.escape(NAMES[n])
        return f'<img src="assets/icons/{n}.svg" width="{CELL_ICON}" height="{CELL_ICON}" alt="{t}" title="{t}" />'
    cells = "".join(
        '<td valign="top">' + "<br />".join(
            " ".join(img(n) for n in ns[i:i + PER_ROW]) for i in range(0, len(ns), PER_ROW)) + "</td>"
        for _, ns in GROUPS)
    line = " · ".join(f"<b>{html.escape(l)}</b> {html.escape(', '.join(NAMES[n] for n in ns))}" for l, ns in GROUPS)
    block = (f"<!-- skills:start -->\n<table>\n<tr>{head}</tr>\n<tr>{cells}</tr>\n</table>\n\n"
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
