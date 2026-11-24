#!/usr/bin/env python3
"""Build assets/skills.svg: tech logos grouped by area, one row, labels above.

Icons come from skillicons.dev once, at build time, and are embedded so the
README never depends on that service. Run by hand when the list changes.
"""
import html, pathlib, re, urllib.request

ROOT = pathlib.Path(__file__).resolve().parent.parent
FONT = "ui-monospace, SFMono-Regular, 'SF Mono', Menlo, Consolas, 'Liberation Mono', monospace"

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
ICON, GAP, COL_GAP, TOP, W = 36, 6, 20, 26, 1094
INSET = 8  # same safe margin as the stats card


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
    # One column per area, equal widths; icons wrap inside their column.
    cols = len(GROUPS)
    col_w = (W - COL_GAP * (cols - 1)) / cols
    per_row = max(1, int((col_w + GAP) // (ICON + GAP)))
    parts, n, H = [], 0, 0
    for c, (label, names) in enumerate(GROUPS):
        x0 = c * (col_w + COL_GAP)
        parts.append(f'  <text x="{x0:.0f}" y="12" class="mu" font-size="12" letter-spacing="1.5">{html.escape(label.upper())}</text>')
        for i, name in enumerate(names):
            x = x0 + (i % per_row) * (ICON + GAP)
            y = TOP + (i // per_row) * (ICON + GAP)
            svg = re.sub(r'^<svg ([^>]*?)width="256" height="256"',
                         rf'<svg \1x="{x:.0f}" y="{y}" width="{ICON}" height="{ICON}"', icon(name, n), count=1)
            parts.append("  " + svg)
            H = max(H, y + ICON)
            n += 1
    alt = html.escape("Skills. " + ". ".join(f"{l}: {', '.join(NAMES[n] for n in ns)}" for l, ns in GROUPS))
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
    footnote()
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


def footnote():
    """Plain-text list under the logos, for readers, scrapers and search engines."""
    line = " · ".join(f"<b>{html.escape(l)}</b> {html.escape(', '.join(NAMES[n] for n in ns))}" for l, ns in GROUPS)
    block = f"<!-- skills:start -->\n<p><sub>{line}</sub></p>\n<!-- skills:end -->"
    readme = ROOT / "README.md"
    text = readme.read_text()
    if "<!-- skills:start -->" in text:
        text = re.sub(r"<!-- skills:start -->.*?<!-- skills:end -->", lambda m: block, text, flags=re.S)
    else:
        text = re.sub(r'(<img src="assets/skills-[^>]*/>)', lambda m: m.group(1) + "\n\n" + block, text)
    readme.write_text(text)


if __name__ == "__main__":
    build()
