import os
import requests
from collections import defaultdict
from datetime import datetime, timezone


def fetch_starred_repos(username: str, token: str) -> list[dict]:
    repos = []
    page = 1
    while True:
        url = f"https://api.github.com/users/{username}/starred"
        headers = {"Authorization": f"token {token}"}
        params = {"per_page": 100, "page": page}
        resp = requests.get(url, headers=headers, params=params, timeout=30)
        resp.raise_for_status()
        data = resp.json()
        if not data:
            break
        repos.extend(data)
        page += 1
    return repos


def get_username_from_repo(repo_full_name: str) -> str:
    return repo_full_name.split("/")[0]


def group_by_language(repos: list[dict]) -> dict[str, list[dict]]:
    groups = defaultdict(list)
    for repo in repos:
        lang = repo.get("language") or "Other"
        groups[lang].append(repo)
    return dict(sorted(groups.items(), key=lambda x: -len(x[1])))


def generate_config(username: str, repo_name: str) -> str:
    return f"""title: {username}'s Star List
description: Auto-generated list of all GitHub starred repositories
theme: jekyll-theme-cayman
baseurl: /{repo_name}
url: ""
"""


def generate_index(username: str, by_language: dict[str, list[dict]], total: int) -> str:
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    
    lines = [
        "---",
        "layout: default",
        f"title: {username}'s Star List",
        "---",
        "",
        f"> Total: **{total}** repos | Last updated: {now}",
        "",
        "## Languages",
        "",
    ]
    
    for lang, repos_list in by_language.items():
        slug = lang.lower().replace(" ", "-").replace(".", "").replace("#", "sharp")
        count = len(repos_list)
        lines.append(f"- [{lang}]({slug}.html) ({count})")
    
    lines.append("")
    return "\n".join(lines)


def generate_language_page(lang: str, repos_list: list[dict]) -> str:
    slug = lang.lower().replace(" ", "-").replace(".", "").replace("#", "sharp")
    
    lines = [
        "---",
        "layout: default",
        f"title: {lang}",
        "---",
        "",
        f"# {lang}",
        "",
        "[← Back to README](README.html)",
        "",
        "| Repository | Description | Stars | Updated |",
        "| --- | --- | ---: | ---: |",
    ]
    
    for repo in sorted(repos_list, key=lambda r: -r.get("stargazers_count", 0)):
        name = repo["full_name"]
        desc = (repo.get("description") or "-").replace("|", "\\|")
        if len(desc) > 80:
            desc = desc[:77] + "..."
        stars = repo.get("stargazers_count", 0)
        updated = repo.get("updated_at", "")[:10]
        lines.append(
            f"| [{name}](https://github.com/{name}) | {desc} | {stars} | {updated} |"
        )
    
    lines.append("")
    return "\n".join(lines)


def main():
    token = os.environ.get("GITHUB_TOKEN", "")
    repo_full_name = os.environ.get("GITHUB_REPOSITORY", "")

    if not token:
        print("Error: GITHUB_TOKEN not set")
        return

    username = get_username_from_repo(repo_full_name) if repo_full_name else ""
    if not username:
        print("Error: GITHUB_REPOSITORY not set")
        return

    print(f"Fetching starred repos for {username}...")
    repos = fetch_starred_repos(username, token)
    print(f"Found {len(repos)} starred repos")

    by_language = group_by_language(repos)
    
    os.makedirs("_site", exist_ok=True)
    
    # Generate _config.yml
    repo_name = repo_full_name.split("/")[-1] if repo_full_name else ""
    config = generate_config(username, repo_name)
    with open("_site/_config.yml", "w", encoding="utf-8") as f:
        f.write(config)
    
    # Generate index as README.md
    index = generate_index(username, by_language, len(repos))
    with open("_site/README.md", "w", encoding="utf-8") as f:
        f.write(index)
    
    # Also create index.md for GitHub Pages
    with open("_site/index.md", "w", encoding="utf-8") as f:
        f.write(index)
    
    # Generate language pages
    for lang, repos_list in by_language.items():
        slug = lang.lower().replace(" ", "-").replace(".", "").replace("#", "sharp")
        content = generate_language_page(lang, repos_list)
        with open(f"_site/{slug}.md", "w", encoding="utf-8") as f:
            f.write(content)
    
    print(f"Generated {len(by_language) + 1} files in _site/")


if __name__ == "__main__":
    main()
