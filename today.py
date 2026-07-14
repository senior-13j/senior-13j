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
LINKEDIN = "linkedin.com/in/arkadii-kotliarov-781aaa19a"
PROFILE_URL = f"https://github.com/{USER_NAME}/{USER_NAME}"

ASCII_ART = [
    ".   .........    ....                ",
    " ..       ..       .                 ",
    "              ..                     ",
    ".  .                                 ",
    " ....  .                             ",
    "                  ..                 ",
    "..  .     ..  .++**+-.     . ..      ",
    "-===+=+*+*****%@%%@%*#-==+#**##*+-:::",
    "***##########%@*++*+ =#**#%%%%##*++++",
    "**######*#%%##%++++=  #*##%%%####*###",
    "-=+====#+=+++##*#***+.+#**%@@%%**+*++",
    ":::::::-:---=**+**:++ :**###@%#*+++++",
    "+***+===+###%*+++*-.:  +++*++*#%%%%#%",
    "==+*+-:-+****+*=+**-- -+===---==++*##",
    "===+*+=*-:----=+++*=:.--=======----=-",
    "==+++=**-:.....=+**=. ...:=*****====+",
    "+**++++*+=====-==++-.  =***#*******##",
    "###%###%%###@%==-===-  *#%##%%%%%%%%%",
    "@@@%@@%%%@@@@@===-==: +#%@%##+==-:::.",
    "**==*#=-#@@@@@%=-----*@%@@@@%#+-::...",
    "++===+*#@@@@@@@@*++*@@%@@@@@@@%#=:...",
    "=+=+=*#@@@@@@@@@@@@@@@@@@@@@@@@@#+:..",
    "+*++*=%@@@@@@@@@@@@@@@@@@@@@@@@@@%*-:",
    "*++=++@@@@@@@@@@@@@@@@@@%@@@@@@@@@@#.",
    "==+==#@@@@@@@@@@@@@@@@@@%@@@@@@@@@%= ",
    "#####@@@@@@@@@@@@@@@@@@@%@@@@%@@@*+==",
    "%%%#@@@@@@@@@@@@@@@@@@@%@@@@%:-+=:-++",
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
        tspan(prefix, "cc", 390, y)
        + tspan(label, "key")
        + ":"
        + tspan(dot_fill(label, value), "cc")
        + tspan(value, value_cls)
    )


def section_line(y, label):
    return tspan(f"- {label}", None, 390, y) + " " + "-" * 53


def render_svg(filename, stats):
    theme = THEMES[filename]
    top_langs = stats["top_langs"]
    first_lang = top_langs[0] if top_langs else ("TypeScript", 0)
    other_bytes = max(0, stats["code_bytes"] - first_lang[1])

    rows = [
        (30, section_line(30, f"arkadii@{USER_NAME}")),
        (50, data_line(50, "OS", "Arch Linux, Hyprland, Web")),
        (70, data_line(70, "Uptime", stats["account_age"])),
        (90, data_line(90, "Host", "Senior Frontend React Engineer")),
        (110, data_line(110, "Kernel", "React, Next.js, TypeScript, AI SDK")),
        (130, data_line(130, "IDE", "Cursor, VS Code, Codex CLI")),
        (150, tspan(". ", "cc", 390, 150)),
        (170, data_line(170, "Languages.Programming", "TypeScript, JavaScript, Python")),
        (190, data_line(190, "Languages.Computer", "HTML, CSS, JSON, YAML, SQL")),
        (210, data_line(210, "Languages.Real", "English, Russian")),
        (230, tspan(". ", "cc", 390, 230)),
        (250, data_line(250, "Focus.Frontend", "React, Next.js, realtime UX")),
        (270, data_line(270, "Focus.Delivery", "CI/CD, Docker, QA, mentoring")),
        (310, section_line(310, "Contact")),
        (330, data_line(330, "LinkedIn", LINKEDIN)),
        (350, data_line(350, "GitHub", f"github.com/{USER_NAME}")),
        (370, data_line(370, "Location", "Belgrade, Serbia")),
        (390, data_line(390, "Availability", "open to senior frontend roles")),
        (410, data_line(410, "Profile", "React, Next.js, TypeScript, AI UX")),
        (450, section_line(450, "GitHub Stats")),
        (
            470,
            tspan(". ", "cc", 390, 470)
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
            490,
            tspan(". ", "cc", 390, 490)
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
            510,
            tspan(". ", "cc", 390, 510)
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
        tspan(line[:48], x=15, y=30 + i * 18) for i, line in enumerate(ASCII_ART)
    )
    data_lines = "\n".join(line for _, line in rows)

    svg = f"""<?xml version='1.0' encoding='UTF-8'?>
<svg xmlns="http://www.w3.org/2000/svg" font-family="ConsolasFallback,Consolas,monospace" width="985px" height="530px" font-size="16px">
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
<rect width="985px" height="530px" fill="{theme["bg"]}" rx="15"/>
<text x="15" y="30" fill="{theme["fg"]}" class="ascii">
{ascii_lines}
</text>
<text x="390" y="30" fill="{theme["fg"]}">
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
