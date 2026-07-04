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
baseurl: /{repo_name}
url: ""

plugins:
  - jekyll-seo-tag

defaults:
  - scope:
      path: ""
    values:
      layout: default
"""


def generate_css() -> str:
    return """* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Oxygen, Ubuntu, sans-serif;
  line-height: 1.6;
  color: #24292e;
  background: #fff;
  max-width: 1200px;
  margin: 0 auto;
  padding: 2rem 1rem;
}

a {
  color: #0366d6;
  text-decoration: none;
}

a:hover {
  text-decoration: underline;
}

.back-link {
  display: inline-block;
  margin-bottom: 1rem;
  font-size: 0.9rem;
}

.stats {
  text-align: center;
  padding: 2rem 0;
  border-bottom: 1px solid #e1e4e8;
  margin-bottom: 2rem;
}

.stat-number {
  font-size: 2.5rem;
  font-weight: bold;
  color: #0366d6;
}

.stat-date {
  display: block;
  color: #586069;
  font-size: 0.9rem;
  margin-top: 0.5rem;
}

.lang-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(150px, 1fr));
  gap: 1rem;
}

.lang-card {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 1.5rem 1rem;
  border: 1px solid #e1e4e8;
  border-radius: 8px;
  transition: all 0.2s ease;
  text-decoration: none !important;
}

.lang-card:hover {
  border-color: #0366d6;
  box-shadow: 0 4px 12px rgba(3, 102, 214, 0.15);
  transform: translateY(-2px);
}

.lang-name {
  font-weight: 600;
  color: #24292e;
  text-align: center;
}

.lang-count {
  font-size: 0.85rem;
  color: #586069;
  margin-top: 0.25rem;
}

.repo-list {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.repo-item {
  padding: 1rem;
  border: 1px solid #e1e4e8;
  border-radius: 8px;
  transition: border-color 0.2s ease;
}

.repo-item:hover {
  border-color: #0366d6;
}

.repo-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 0.5rem;
}

.repo-name {
  font-weight: 600;
  font-size: 1.1rem;
}

.repo-stars {
  color: #e3b341;
  font-weight: 500;
}

.repo-desc {
  color: #586069;
  margin: 0.5rem 0;
  font-size: 0.95rem;
}

.repo-date {
  font-size: 0.8rem;
  color: #6a737d;
}

@media (max-width: 600px) {
  body {
    padding: 1rem;
  }
  
  .stat-number {
    font-size: 2rem;
  }
  
  .lang-grid {
    grid-template-columns: repeat(auto-fill, minmax(120px, 1fr));
  }
  
  .repo-header {
    flex-direction: column;
    align-items: flex-start;
  }
}
"""


def generate_layout() -> str:
    return """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{{ page.title | default: site.title }}</title>
  <meta name="description" content="{{ site.description }}">
  <link rel="stylesheet" href="{{ site.baseurl }}/assets/style.css">
</head>
<body>
  {{ content }}
</body>
</html>
"""


def generate_index(username: str, by_language: dict[str, list[dict]], total: int) -> str:
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    
    lines = [
        "---",
        "layout: default",
        f"title: {username}'s Star List",
        "---",
        "",
        '<div class="stats">',
        f'  <span class="stat-number">{total}</span> repos starred',
        f'  <span class="stat-date">Last updated: {now}</span>',
        "</div>",
        "",
        '<div class="lang-grid">',
    ]
    
    for lang, repos_list in by_language.items():
        slug = lang.lower().replace(" ", "-").replace(".", "").replace("#", "sharp")
        count = len(repos_list)
        lines.append(f'  <a href="{{{{ site.baseurl }}}}/{slug}.html" class="lang-card">')
        lines.append(f'    <span class="lang-name">{lang}</span>')
        lines.append(f'    <span class="lang-count">{count}</span>')
        lines.append("  </a>")
    
    lines.append("</div>")
    lines.append("")
    return "\n".join(lines)


def generate_language_page(lang: str, repos_list: list[dict], baseurl: str) -> str:
    lines = [
        "---",
        f"title: {lang}",
        "---",
        "",
        f'<a href="{{{{ site.baseurl }}}}/" class="back-link">← All Languages</a>',
        "",
        f"<h1>{lang}</h1>",
        f"<p>{len(repos_list)} repositories</p>",
        "",
        '<div class="repo-list">',
    ]
    
    for repo in sorted(repos_list, key=lambda r: -r.get("stargazers_count", 0)):
        name = repo["full_name"]
        desc = (repo.get("description") or "").replace("|", "\\|")
        if len(desc) > 100:
            desc = desc[:97] + "..."
        stars = repo.get("stargazers_count", 0)
        updated = repo.get("updated_at", "")[:10]
        lines.append(f'<div class="repo-item">')
        lines.append(f'  <div class="repo-header">')
        lines.append(f'    <a href="https://github.com/{name}" class="repo-name">{name}</a>')
        lines.append(f'    <span class="repo-stars">★ {stars:,}</span>')
        lines.append(f"  </div>")
        if desc:
            lines.append(f'  <p class="repo-desc">{desc}</p>')
        lines.append(f'  <span class="repo-date">Updated: {updated}</span>')
        lines.append(f"</div>")
    
    lines.append("</div>")
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
    repo_name = repo_full_name.split("/")[-1] if repo_full_name else ""
    
    os.makedirs("_site", exist_ok=True)
    os.makedirs("_site/assets", exist_ok=True)
    os.makedirs("_site/_layouts", exist_ok=True)
    
    # Generate _config.yml
    config = generate_config(username, repo_name)
    with open("_site/_config.yml", "w", encoding="utf-8") as f:
        f.write(config)
    
    # Generate CSS
    css = generate_css()
    with open("_site/assets/style.css", "w", encoding="utf-8") as f:
        f.write(css)
    
    # Generate layout
    layout = generate_layout()
    with open("_site/_layouts/default.html", "w", encoding="utf-8") as f:
        f.write(layout)
    
    # Generate index
    index = generate_index(username, by_language, len(repos))
    with open("_site/index.md", "w", encoding="utf-8") as f:
        f.write(index)
    
    # Generate README.md for GitHub view
    with open("_site/README.md", "w", encoding="utf-8") as f:
        f.write(index)
    
    # Generate language pages
    for lang, repos_list in by_language.items():
        slug = lang.lower().replace(" ", "-").replace(".", "").replace("#", "sharp")
        content = generate_language_page(lang, repos_list, f"/{repo_name}")
        with open(f"_site/{slug}.md", "w", encoding="utf-8") as f:
            f.write(content)
    
    print(f"Generated {len(by_language) + 1} files in _site/")


if __name__ == "__main__":
    main()
