#!/usr/bin/env python3

import calendar
import datetime as dt
import html
import json
import os
import urllib.error
import urllib.parse
import urllib.request


USER_NAME = os.environ.get("USER_NAME", "senior-13j")
TOKEN = os.environ.get("ACCESS_TOKEN") or os.environ.get("GITHUB_TOKEN") or ""
LINKEDIN = "https://www.linkedin.com/in/%E2%98%95-arkadii-kotliarov-781aaa19a/"
PROFILE_URL = f"https://github.com/{USER_NAME}/{USER_NAME}"
HOST = "Senior Frontend React & Web Engineer | React, Next.js, TypeScript, AI, Realtime UX | DevOps"
AVAILABILITY = "open to frontend and full-stack roles, learning DevOps to future transition"
HOST_LINE_1 = "Senior Frontend React & Web Engineer | React, Next.js,"
HOST_LINE_2 = HOST.removeprefix(f"{HOST_LINE_1} ")
LINKEDIN_LINE_1 = "https://www.linkedin.com/in/"
LINKEDIN_LINE_2 = LINKEDIN.removeprefix(LINKEDIN_LINE_1)
AVAILABILITY_LINE_1 = "open to frontend and full-stack roles,"
AVAILABILITY_LINE_2 = AVAILABILITY.removeprefix(f"{AVAILABILITY_LINE_1} ")
SVG_WIDTH = 1120
SVG_HEIGHT = 550
RIGHT_X = 390

ASCII_ART = [
    "        .-==++++++++++++==-.        ",
    "     .-+####################+-.     ",
    "    +##########################+    ",
    "   *###########********#########*   ",
    "  *########*=-::::::::-=*########*  ",
    " +#######=:.            .:=#######+ ",
    ".######-.    .-======-.    -######.",
    "+#####:    .+##########+.    :####+",
    "#####=    -####*+==+*####-    =####",
    "#####:   .###+:      :+###.   :####",
    "####*    +##=  .--  --. =##+   *###",
    "####*    ##+    <>  <>   +##   *###",
    "####*    +##.      __    .##+  *###",
    "+####.   :##+    ----   +##:  .###+",
    ".####=    +##*=.      .=*##+   =###.",
    " +####+    =###*=-::-=*###=   +### ",
    "  *####*.   :=*########*=:  .*###  ",
    "   *####=.     .::::.     .=####   ",
    "    +#####*=-.        .-=*####+    ",
    "     =##########****#########=     ",
    "    .+##########****#########+.    ",
    "   .##########+:    :+#########.   ",
    "   +#########-        -########+   ",
    "  :#########+          +########:  ",
    "  +########=            =########+ ",
]


THEMES = {
    "dark_mode.svg": {
        "bg": "#161b22",
        "fg": "#c9d1d9",
        "key": "#ffa657",
        "value": "#a5d6ff",
        "comment": "#616e7f",
        "add": "#3fb950",
        "del": "#f85149",
    },
    "light_mode.svg": {
        "bg": "#f6f8fa",
        "fg": "#24292f",
        "key": "#953800",
        "value": "#0a3069",
        "comment": "#c2cfde",
        "add": "#1a7f37",
        "del": "#cf222e",
    },
}


def api_get(url, accept="application/vnd.github+json"):
    headers = {
        "Accept": accept,
        "X-GitHub-Api-Version": "2022-11-28",
        "User-Agent": f"{USER_NAME}-profile-readme",
    }
    if TOKEN:
        headers["Authorization"] = f"Bearer {TOKEN}"
    request = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(request, timeout=30) as response:
        return json.loads(response.read().decode("utf-8"))


def github_user():
    return api_get(f"https://api.github.com/users/{USER_NAME}")


def github_repos():
    repos = []
    page = 1
    while True:
        url = f"https://api.github.com/users/{USER_NAME}/repos?per_page=100&page={page}&sort=updated"
        chunk = api_get(url)
        if not chunk:
            return repos
        repos.extend(chunk)
        page += 1


def commit_count():
    query = urllib.parse.quote(f"author:{USER_NAME}")
    url = f"https://api.github.com/search/commits?q={query}"
    try:
        data = api_get(url, "application/vnd.github.cloak-preview+json")
        return data.get("total_count", 0)
    except (urllib.error.HTTPError, urllib.error.URLError, TimeoutError):
        return 0


def language_bytes(repos):
    totals = {}
    for repo in repos:
        if repo.get("fork"):
            continue
        try:
            langs = api_get(repo["languages_url"])
        except (urllib.error.HTTPError, urllib.error.URLError, TimeoutError):
            continue
        for lang, size in langs.items():
            totals[lang] = totals.get(lang, 0) + int(size)
    return totals


def account_age(created_at):
    start = dt.datetime.fromisoformat(created_at.replace("Z", "+00:00")).date()
    today = dt.datetime.now(dt.timezone.utc).date()
    years = today.year - start.year
    months = today.month - start.month
    days = today.day - start.day
    if days < 0:
        months -= 1
        previous_month = today.month - 1 or 12
        previous_year = today.year if today.month > 1 else today.year - 1
        days += calendar.monthrange(previous_year, previous_month)[1]
    if months < 0:
        years -= 1
        months += 12
    return f"{years}y {months}m {days}d"


def human_number(value):
    return f"{int(value):,}"


def human_bytes(value):
    value = float(value)
    for unit in ("B", "KB", "MB", "GB"):
        if value < 1024 or unit == "GB":
            return f"{value:.1f} {unit}" if unit != "B" else f"{int(value)} B"
        value /= 1024
    return f"{value:.1f} GB"


def dot_fill(label, value, width=35):
    used = len(label) + len(str(value)) + 2
    dots = max(2, width - used)
    return " " + ("." * dots) + " "


def tspan(text, cls=None, x=None, y=None):
    attrs = []
    if x is not None:
        attrs.append(f'x="{x}"')
    if y is not None:
        attrs.append(f'y="{y}"')
    if cls:
        attrs.append(f'class="{cls}"')
    attr_text = " " + " ".join(attrs) if attrs else ""
    return f"<tspan{attr_text}>{html.escape(str(text))}</tspan>"


def data_line(y, label, value, prefix=". ", value_cls="value"):
    return (
        tspan(prefix, "cc", RIGHT_X, y)
        + tspan(label, "key")
        + ":"
        + tspan(dot_fill(label, value), "cc")
        + tspan(value, value_cls)
    )


def data_line_plain(y, label, value, prefix=". ", value_cls="value"):
    return (
        tspan(prefix, "cc", RIGHT_X, y)
        + tspan(label, "key")
        + ": "
        + tspan(value, value_cls)
    )


def continuation_line(y, label, value, prefix=". ", value_cls="value"):
    return (
        tspan(prefix, "cc", RIGHT_X, y)
        + tspan(" " * (len(label) + 2), "cc")
        + tspan(value, value_cls)
    )


def section_line(y, label):
    return tspan(f"- {label}", None, RIGHT_X, y) + " " + "-" * 68


def render_svg(filename, stats):
    theme = THEMES[filename]
    top_langs = stats["top_langs"]
    first_lang = top_langs[0] if top_langs else ("TypeScript", 0)
    other_bytes = max(0, stats["code_bytes"] - first_lang[1])

    rows = [
        (30, section_line(30, f"arkadii@{USER_NAME}")),
        (50, data_line(50, "OS", "Arch Linux, Hyprland, Web")),
        (70, data_line(70, "Uptime", stats["account_age"])),
        (90, data_line_plain(90, "Host", HOST_LINE_1)),
        (110, continuation_line(110, "Host", HOST_LINE_2)),
        (130, data_line(130, "Kernel", "React, Next.js, TypeScript, AI SDK")),
        (150, data_line(150, "IDE", "Cursor, VS Code, Codex CLI")),
        (170, tspan(". ", "cc", RIGHT_X, 170)),
        (190, data_line(190, "Languages.Programming", "TypeScript, JavaScript, Python")),
        (210, data_line(210, "Languages.Computer", "HTML, CSS, JSON, YAML, SQL")),
        (230, data_line(230, "Languages.Real", "English, Russian")),
        (250, tspan(". ", "cc", RIGHT_X, 250)),
        (270, data_line(270, "Focus.Frontend", "React, Next.js, realtime UX")),
        (290, data_line(290, "Focus.Delivery", "CI/CD, Docker, QA, mentoring")),
        (310, section_line(310, "Contact")),
        (330, data_line_plain(330, "LinkedIn", LINKEDIN_LINE_1)),
        (350, continuation_line(350, "LinkedIn", LINKEDIN_LINE_2)),
        (370, data_line(370, "GitHub", f"github.com/{USER_NAME}")),
        (390, data_line(390, "Location", "Belgrade, Serbia")),
        (410, data_line_plain(410, "Availability", AVAILABILITY_LINE_1)),
        (430, continuation_line(430, "Availability", AVAILABILITY_LINE_2)),
        (450, data_line(450, "Profile", "React, Next.js, TypeScript, AI UX")),
        (470, section_line(470, "GitHub Stats")),
        (
            490,
            tspan(". ", "cc", RIGHT_X, 490)
            + tspan("Repos", "key")
            + ":"
            + tspan(dot_fill("Repos", stats["public_repos"], 12), "cc")
            + tspan(human_number(stats["public_repos"]), "value")
            + " {"
            + tspan("Original", "key")
            + ": "
            + tspan(human_number(stats["original_repos"]), "value")
            + "} | "
            + tspan("Stars", "key")
            + ":"
            + tspan(dot_fill("Stars", stats["stars"], 14), "cc")
            + tspan(human_number(stats["stars"]), "value")
        ),
        (
            510,
            tspan(". ", "cc", RIGHT_X, 510)
            + tspan("Commits", "key")
            + ":"
            + tspan(dot_fill("Commits", stats["commits"], 18), "cc")
            + tspan(human_number(stats["commits"]), "value")
            + " | "
            + tspan("Followers", "key")
            + ":"
            + tspan(dot_fill("Followers", stats["followers"], 12), "cc")
            + tspan(human_number(stats["followers"]), "value")
        ),
        (
            530,
            tspan(". ", "cc", RIGHT_X, 530)
            + tspan("Code Footprint", "key")
            + ":"
            + tspan(dot_fill("Code Footprint", human_bytes(stats["code_bytes"]), 24), "cc")
            + tspan(human_bytes(stats["code_bytes"]), "value")
            + " ( "
            + tspan(f"{first_lang[0]} {human_bytes(first_lang[1])}", "addColor")
            + ", "
            + tspan(f"Other {human_bytes(other_bytes)}", "delColor")
            + " )"
        ),
    ]

    ascii_lines = "\n".join(
        tspan(line[:48], x=15, y=30 + i * 20) for i, line in enumerate(ASCII_ART)
    )
    data_lines = "\n".join(line for _, line in rows)

    svg = f"""<?xml version='1.0' encoding='UTF-8'?>
<svg xmlns="http://www.w3.org/2000/svg" font-family="ConsolasFallback,Consolas,monospace" width="{SVG_WIDTH}px" height="{SVG_HEIGHT}px" font-size="16px" xml:space="preserve">
<style>
@font-face {{
src: local('Consolas'), local('Consolas Bold');
font-family: 'ConsolasFallback';
font-display: swap;
-webkit-size-adjust: 109%;
size-adjust: 109%;
}}
.key {{fill: {theme["key"]};}}
.value {{fill: {theme["value"]};}}
.addColor {{fill: {theme["add"]};}}
.delColor {{fill: {theme["del"]};}}
.cc {{fill: {theme["comment"]};}}
text, tspan {{white-space: pre;}}
</style>
<rect width="{SVG_WIDTH}px" height="{SVG_HEIGHT}px" fill="{theme["bg"]}" rx="15"/>
<text x="15" y="30" fill="{theme["fg"]}" class="ascii">
{ascii_lines}
</text>
<text x="{RIGHT_X}" y="30" fill="{theme["fg"]}">
{data_lines}
</text>
</svg>
"""
    with open(filename, "w", encoding="utf-8") as file:
        file.write(svg)


def write_readme():
    readme = f"""<a href="{PROFILE_URL}">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="https://raw.githubusercontent.com/{USER_NAME}/{USER_NAME}/main/dark_mode.svg">
    <img alt="Arkadii Kotliarov's GitHub Profile README" src="https://raw.githubusercontent.com/{USER_NAME}/{USER_NAME}/main/light_mode.svg">
  </picture>
</a>
"""
    with open("README.md", "w", encoding="utf-8") as file:
        file.write(readme)


def build_stats():
    user = github_user()
    repos = github_repos()
    originals = [repo for repo in repos if not repo.get("fork")]
    languages = language_bytes(repos)
    top_langs = sorted(languages.items(), key=lambda item: item[1], reverse=True)
    return {
        "account_age": account_age(user["created_at"]),
        "public_repos": user.get("public_repos", len(repos)),
        "original_repos": len(originals),
        "stars": sum(int(repo.get("stargazers_count", 0)) for repo in originals),
        "followers": user.get("followers", 0),
        "commits": commit_count(),
        "code_bytes": sum(languages.values()),
        "top_langs": top_langs,
    }


def main():
    stats = build_stats()
    write_readme()
    for filename in THEMES:
        render_svg(filename, stats)
    print(json.dumps(stats, indent=2))


if __name__ == "__main__":
    main()
