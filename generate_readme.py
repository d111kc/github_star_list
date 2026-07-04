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


def generate_index(username: str, by_language: dict[str, list[dict]], total: int) -> str:
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    
    lines = [
        f"# {username}'s Star List",
        "",
        f"> Total: **{total}** repos | Last updated: {now}",
        "",
        "## Languages",
        "",
    ]
    
    for lang, repos_list in by_language.items():
        slug = lang.lower().replace(" ", "-").replace(".", "").replace("#", "sharp")
        count = len(repos_list)
        lines.append(f"- [{lang}]({slug}.md) ({count})")
    
    lines.append("")
    return "\n".join(lines)


def generate_language_page(lang: str, repos_list: list[dict]) -> str:
    slug = lang.lower().replace(" ", "-").replace(".", "").replace("#", "sharp")
    
    lines = [
        f"# {lang}",
        "",
        f"[← Back to index](index.md)",
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
    
    # Generate index
    index = generate_index(username, by_language, len(repos))
    with open("_site/index.md", "w", encoding="utf-8") as f:
        f.write(index)
    
    # Generate language pages
    for lang, repos_list in by_language.items():
        slug = lang.lower().replace(" ", "-").replace(".", "").replace("#", "sharp")
        content = generate_language_page(lang, repos_list)
        with open(f"_site/{slug}.md", "w", encoding="utf-8") as f:
            f.write(content)
    
    # Add .nojekyll
    with open("_site/.nojekyll", "w") as f:
        f.write("")
    
    print(f"Generated {len(by_language) + 1} files in _site/")


if __name__ == "__main__":
    main()
