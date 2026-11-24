#!/usr/bin/env python3
"""Generate the profile stats card (assets/stats.svg).

Uses the gh CLI (GH_TOKEN). With a token that can read private repos, private
work is counted too; with the default Actions token only public data is.
No third-party services, no dependencies.
"""
import json, subprocess, collections, datetime, pathlib, html

ROOT = pathlib.Path(__file__).resolve().parent.parent
BG, FG, MUTED, LINE = "#18191B", "#F6F3EA", "#B9B9B2", "#2A2B2E"
ORANGE, LILAC, GREEN = "#FF9866", "#BBB3EC", "#C6D7AC"
FONT = "-apple-system, BlinkMacSystemFont, 'Segoe UI', Helvetica, Arial, sans-serif"
LOGIN = "vincent-caetano"

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


def frame(w, h, body, title):
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" fill="none" role="img" aria-label="{esc(title)}">
  <title>{esc(title)}</title>
  <defs>
    <pattern id="dots" width="24" height="24" patternUnits="userSpaceOnUse"><circle cx="2" cy="2" r="1" fill="#FFFFFF" opacity="0.06"/></pattern>
    <clipPath id="c"><rect width="{w}" height="{h}" rx="24"/></clipPath>
  </defs>
  <g clip-path="url(#c)" font-family="{FONT}">
    <rect width="{w}" height="{h}" fill="{BG}"/>
    <rect width="{w}" height="{h}" fill="url(#dots)"/>
{body}
  </g>
</svg>
"""


def label(x, y, text):
    return f'    <text x="{x}" y="{y}" fill="{MUTED}" font-size="13" letter-spacing="2.6">{esc(text.upper())}</text>\n'


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
    W, H = 1200, 300
    b = label(56, 52, "Last 12 months")
    tiles = [
        (fmt(cal["totalContributions"]), "contributions", ORANGE),
        (f"{active}", "active days", LILAC),
        (f"{cur}", "day streak" if cur == best else f"day streak · best {best}", GREEN),
        (f'{u["repositories"]["totalCount"]}', "repositories", FG),
    ]
    for i, (v, k, c) in enumerate(tiles):
        x = 56 + i * 220
        b += f'    <text x="{x}" y="112" fill="{FG}" font-size="46" font-weight="700" letter-spacing="-1.5">{esc(v)}</text>\n'
        b += f'    <circle cx="{x+4}" cy="133" r="4" fill="{c}"/>\n'
        b += f'    <text x="{x+15}" y="138" fill="{MUTED}" font-size="15">{esc(k)}</text>\n'
    # heatmap
    mx = max([d["contributionCount"] for d in days] + [1])
    levels = [LINE, "#4A3A33", "#8A5A43", "#C7764F", ORANGE]
    cell, gap, x0, y0 = 12, 4, 56, 168
    for wi, w in enumerate(weeks):
        for d in w["contributionDays"]:
            n = d["contributionCount"]
            row = (datetime.date.fromisoformat(d["date"]).weekday() + 1) % 7  # Sun first
            lvl = 0 if n == 0 else min(4, 1 + int(3 * (n / mx) ** 0.5 + 0.5))
            b += (f'    <rect x="{x0 + wi*(cell+gap)}" y="{y0 + row*(cell+gap)}" width="{cell}" height="{cell}" '
                  f'rx="3" fill="{levels[lvl]}"><title>{n} on {d["date"]}</title></rect>\n')
    # languages, right column
    top = languages(u)
    total = sum(n for _, n in top) or 1
    palette = [ORANGE, LILAC, GREEN, FG, "#8C8C86", "#5E5E5A"]
    lx = 56 + 53 * (cell + gap) + 44
    b += label(lx, 52, "Languages")
    bw = W - 56 - lx
    b += f'    <clipPath id="bar"><rect x="{lx}" y="98" width="{bw}" height="10" rx="5"/></clipPath>\n    <g clip-path="url(#bar)">\n'
    cx = lx
    for i, (name, n) in enumerate(top):
        wpx = bw * n / total
        b += f'      <rect x="{cx:.1f}" y="98" width="{wpx:.1f}" height="10" fill="{palette[i]}"/>\n'
        cx += wpx
    b += "    </g>\n"
    for i, (name, n) in enumerate(top):
        y = 172 + i * 19
        b += f'    <circle cx="{lx+4}" cy="{y-5}" r="4" fill="{palette[i]}"/>\n'
        b += f'    <text x="{lx+15}" y="{y}" fill="{FG}" font-size="14">{esc(name)}</text>\n'
        b += f'    <text x="{W-56}" y="{y}" fill="{MUTED}" font-size="14" text-anchor="end">{round(100*n/total)}%</text>\n'
    return frame(W, H, b, f"GitHub activity: {cal['totalContributions']} contributions in the last year; languages " + ", ".join(n for n, _ in top))


if __name__ == "__main__":
    u = fetch()
    (ROOT / "assets/stats.svg").write_text(stats_svg(u))
    print("ok")
