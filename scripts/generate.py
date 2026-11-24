#!/usr/bin/env python3
"""Generate the profile stats card (assets/stats.svg).

Uses the gh CLI (GH_TOKEN). With a token that can read private repos, private
work is counted too; with the default Actions token only public data is.
Transparent background; colours follow the viewer's light/dark theme.
No third-party services, no dependencies.
"""
import json, subprocess, collections, datetime, pathlib, html

ROOT = pathlib.Path(__file__).resolve().parent.parent
FONT = "ui-monospace, SFMono-Regular, 'SF Mono', Menlo, Consolas, 'Liberation Mono', monospace"
LOGIN = "vincent-caetano"

# Theme-aware palette: light values first, dark overrides in the media query.
CSS = """
  text { font-family: %s; }
  .fg { fill: #1F2023; } .mu { fill: #6B6B66; } .ln { fill: #E7E5DF; }
  .o { fill: #F07A3E; } .l { fill: #8E83D8; } .g { fill: #8DAA62; } .k { fill: #1F2023; } .k2 { fill: #8C8C86; } .k3 { fill: #B5B5AF; }
  .h1 { fill: #FBD9C6; } .h2 { fill: #F7B693; } .h3 { fill: #F39561; } .h4 { fill: #E8692B; }
  @media (prefers-color-scheme: dark) {
    .fg { fill: #F6F3EA; } .mu { fill: #9C9C96; } .ln { fill: #2A2B2E; }
    .o { fill: #FF9866; } .l { fill: #BBB3EC; } .g { fill: #C6D7AC; } .k { fill: #F6F3EA; } .k2 { fill: #8C8C86; } .k3 { fill: #5E5E5A; }
    .h1 { fill: #4A3A33; } .h2 { fill: #8A5A43; } .h3 { fill: #C7764F; } .h4 { fill: #FF9866; }
  }
""" % FONT

Q = """query($login:String!){ user(login:$login){
  repositories(ownerAffiliations:OWNER, isFork:false, first:100){ totalCount
    nodes{ name languages(first:10, orderBy:{field:SIZE, direction:DESC}){ totalSize edges{ size node{ name } } } } }
  contributionsCollection{ restrictedContributionsCount
    contributionCalendar{ totalContributions weeks{ contributionDays{ date contributionCount } } } } } }"""


def fetch():
    out = subprocess.check_output(["gh", "api", "graphql", "-f", f"query={Q}", "-f", f"login={LOGIN}"])
    return json.loads(out)["data"]["user"]


def esc(s):
    return html.escape(str(s), quote=True)


def label(x, y, text):
    return f'  <text x="{x}" y="{y}" class="mu" font-size="12" letter-spacing="1.5">{esc(text.upper())}</text>\n'


def streaks(days):
    best = run = 0
    for d in days:
        run = run + 1 if d["contributionCount"] else 0
        best = max(best, run)
    cur = 0
    for i, d in enumerate(reversed(days)):
        if d["contributionCount"]:
            cur += 1
        elif i == 0:  # today not counted yet
            continue
        else:
            break
    return cur, best


def fmt(n):
    return f"{n/1000:.1f}k".replace(".0k", "k") if n >= 10000 else f"{n:,}"


def languages(u):
    # Repos by language (a language counts if it is >=15% of a repo's code),
    # so generated landing-page HTML does not drown out real work.
    skip = {"HTML", "CSS", "Shell", "Makefile", "Dockerfile", "Batchfile", "MDX", "Nunjucks", "mcfunction"}
    cnt = collections.Counter()
    for r in u["repositories"]["nodes"]:
        code = [e for e in r["languages"]["edges"] if e["node"]["name"] not in skip]
        tot = sum(e["size"] for e in code) or 1
        for e in code:
            if e["size"] / tot >= 0.15:
                cnt[e["node"]["name"]] += 1
    return cnt.most_common(6)


def stats_svg(u):
    cal = u["contributionsCollection"]["contributionCalendar"]
    weeks = cal["weeks"][-53:]
    days = [d for w in weeks for d in w["contributionDays"]]
    cur, best = streaks(days)
    active = sum(1 for d in days if d["contributionCount"])

    cell, gap = 12, 4
    hm_w = 53 * (cell + gap) - gap          # 844
    lx = hm_w + 48                          # languages column
    W, H = lx + 200, 228

    b = label(0, 12, "Last 12 months")
    tiles = [
        (fmt(cal["totalContributions"]), "contributions", "o"),
        (f"{active}", "active days", "l"),
        (f"{cur}", "day streak" if cur == best else f"streak · best {best}", "g"),
        (f'{u["repositories"]["totalCount"]}', "repositories", "k"),
    ]
    for i, (v, k, c) in enumerate(tiles):
        x = i * 216
        b += f'  <text x="{x}" y="66" class="fg" font-size="42" font-weight="700" letter-spacing="-2">{esc(v)}</text>\n'
        b += f'  <circle cx="{x+4}" cy="87" r="4" class="{c}"/>\n'
        b += f'  <text x="{x+14}" y="92" class="mu" font-size="14">{esc(k)}</text>\n'

    # heatmap
    mx = max([d["contributionCount"] for d in days] + [1])
    y0 = 120
    for wi, w in enumerate(weeks):
        for d in w["contributionDays"]:
            n = d["contributionCount"]
            row = (datetime.date.fromisoformat(d["date"]).weekday() + 1) % 7  # Sun first
            lvl = 0 if n == 0 else min(4, 1 + int(3 * (n / mx) ** 0.5 + 0.5))
            cls = "ln" if lvl == 0 else f"h{lvl}"
            b += (f'  <rect x="{wi*(cell+gap)}" y="{y0 + row*(cell+gap)}" width="{cell}" height="{cell}" '
                  f'rx="3" class="{cls}"><title>{n} on {d["date"]}</title></rect>\n')

    # languages
    top = languages(u)
    total = sum(n for _, n in top) or 1
    classes = ["o", "l", "g", "k", "k2", "k3"]
    bw = W - lx
    b += label(lx, 12, "Languages")
    b += f'  <clipPath id="bar"><rect x="{lx}" y="56" width="{bw}" height="10" rx="5"/></clipPath>\n  <g clip-path="url(#bar)">\n'
    cx = lx
    for i, (name, n) in enumerate(top):
        wpx = bw * n / total
        b += f'    <rect x="{cx:.1f}" y="56" width="{wpx + 0.5:.1f}" height="10" class="{classes[i]}"/>\n'
        cx += wpx
    b += "  </g>\n"
    for i, (name, n) in enumerate(top):
        y = 130 + i * 19
        b += f'  <circle cx="{lx+4}" cy="{y-4}" r="4" class="{classes[i]}"/>\n'
        b += f'  <text x="{lx+14}" y="{y}" class="fg" font-size="13">{esc(name)}</text>\n'
        b += f'  <text x="{W}" y="{y}" class="mu" font-size="13" text-anchor="end">{round(100*n/total)}%</text>\n'

    title = (f"GitHub activity: {cal['totalContributions']} contributions in the last year; "
             "languages " + ", ".join(n for n, _ in top))
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" fill="none" role="img" aria-label="{esc(title)}">
  <title>{esc(title)}</title>
  <style>{CSS}</style>
{b}</svg>
"""


if __name__ == "__main__":
    u = fetch()
    svg = stats_svg(u)
    (ROOT / "assets/stats.svg").write_text(svg)
    # Cache-bust: browsers keep raw images ~5 min, so tag the link with a content hash.
    import hashlib, re
    v = hashlib.sha1(svg.encode()).hexdigest()[:8]
    readme = ROOT / "README.md"
    readme.write_text(re.sub(r'assets/stats\.svg(\?v=\w+)?"', f'assets/stats.svg?v={v}"', readme.read_text()))
    print("ok")
