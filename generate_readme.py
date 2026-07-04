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


# ==================== gh-pages site functions ====================

def generate_config(username: str, repo_name: str) -> str:
    return f"""title: {username}'s Star List
description: Auto-generated list of all GitHub starred repositories
baseurl: /{repo_name}
url: ""
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

header {
  text-align: center;
  padding: 2rem 0;
  border-bottom: 1px solid #e1e4e8;
  margin-bottom: 2rem;
}

header h1 {
  margin: 0;
  font-size: 2rem;
}

header h1 a {
  color: #24292e;
  text-decoration: none;
}

header p {
  color: #586069;
  margin: 0.5rem 0 0;
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
  display: flex;
  align-items: flex-start;
  gap: 1rem;
  padding: 1rem;
  border: 1px solid #e1e4e8;
  border-radius: 8px;
  transition: border-color 0.2s ease;
}

.repo-item:hover {
  border-color: #0366d6;
}

.repo-avatar {
  width: 40px;
  height: 40px;
  border-radius: 4px;
  flex-shrink: 0;
}

.repo-info {
  flex: 1;
  min-width: 0;
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

.back-to-top {
  position: fixed;
  bottom: 2rem;
  right: 2rem;
  width: 40px;
  height: 40px;
  background: #0366d6;
  color: #fff;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  text-decoration: none;
  font-size: 1.2rem;
  box-shadow: 0 2px 8px rgba(0,0,0,0.2);
  transition: opacity 0.2s;
}

.back-to-top:hover {
  opacity: 0.8;
}

footer {
  margin-top: 3rem;
  padding: 2rem 0;
  border-top: 1px solid #e1e4e8;
  text-align: center;
  color: #586069;
  font-size: 0.9rem;
}

.back-to-top {
  position: fixed !important;
  bottom: 2rem !important;
  right: 2rem !important;
  width: 40px !important;
  height: 40px !important;
  min-width: 40px !important;
  min-height: 40px !important;
  background: #0366d6 !important;
  color: #fff !important;
  border-radius: 50% !important;
  display: flex !important;
  align-items: center !important;
  justify-content: center !important;
  text-decoration: none !important;
  font-size: 1.2rem !important;
  box-shadow: 0 2px 8px rgba(0,0,0,0.2) !important;
  z-index: 9999 !important;
  line-height: 1 !important;
}

.back-to-top:hover {
  opacity: 0.8 !important;
  text-decoration: none !important;
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
  
  .repo-item {
    flex-direction: column;
    align-items: flex-start;
  }
  
  .repo-header {
    flex-direction: column;
    align-items: flex-start;
  }
}
"""


def generate_layout(username: str) -> str:
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{{{{ page.title | default: site.title }}}}</title>
  <meta name="description" content="{{{{ site.description }}}}">
  <link rel="icon" href="https://github.com/{username}.png" type="image/png">
  <link rel="stylesheet" href="{{{{ site.baseurl }}}}/assets/style.css">
</head>
<body>
  {{{{ % if page.title == site.title %}}}}
  <header>
    <h1>{{{{ site.title }}}}</h1>
    <p>{{{{ site.description }}}}</p>
  </header>
  {{{{ % endif %}}}}
  
  <main>
    {{{{ content }}}}
  </main>
  
  <footer>
    <p>Auto-generated by <a href="https://github.com/interset-wq/github_star_list" target="_blank">GitHub Star List</a></p>
  </footer>
  
  <a href="javascript:void(0)" onclick="window.scrollTo({{top:0,behavior:'smooth'}})" class="back-to-top">↑</a>
</body>
</html>
"""


def generate_site_index(username: str, by_language: dict[str, list[dict]], total: int) -> str:
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
        lines.append(f'  <a href="{{{{ site.baseurl }}}}/{slug}.html" class="lang-card" target="_blank">')
        lines.append(f'    <span class="lang-name">{lang}</span>')
        lines.append(f'    <span class="lang-count">{count}</span>')
        lines.append("  </a>")
    
    lines.append("</div>")
    lines.append("")
    return "\n".join(lines)


def generate_language_page(lang: str, repos_list: list[dict]) -> str:
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
        owner = name.split("/")[0]
        desc = (repo.get("description") or "").replace("|", "\\|")
        if len(desc) > 100:
            desc = desc[:97] + "..."
        stars = repo.get("stargazers_count", 0)
        updated = repo.get("updated_at", "")[:10]
        lines.append(f'<div class="repo-item">')
        lines.append(f'  <img src="https://github.com/{owner}.png" class="repo-avatar" alt="{owner}">')
        lines.append(f'  <div class="repo-info">')
        lines.append(f'    <div class="repo-header">')
        lines.append(f'      <a href="https://github.com/{name}" class="repo-name" target="_blank">{name}</a>')
        lines.append(f'      <span class="repo-stars">★ {stars:,}</span>')
        lines.append(f"    </div>")
        if desc:
            lines.append(f'    <p class="repo-desc">{desc}</p>')
        lines.append(f'    <span class="repo-date">Updated: {updated}</span>')
        lines.append(f"  </div>")
        lines.append(f"</div>")
    
    lines.append("</div>")
    lines.append("")
    return "\n".join(lines)


# ==================== readme branch functions ====================

def generate_readme_index(username: str, by_language: dict[str, list[dict]], total: int) -> str:
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    
    lines = [
        f"# {username}'s Star List",
        "",
        f"> **{total}** repos starred | Updated: {now}",
        "",
        "---",
        "",
    ]
    
    for lang, repos_list in by_language.items():
        slug = lang.lower().replace(" ", "-").replace(".", "").replace("#", "sharp")
        lines.append(f"- [{lang} ({len(repos_list)})]({slug}.md)")
    
    lines.append("")
    return "\n".join(lines)


def generate_readme_lang(lang: str, repos_list: list[dict]) -> str:
    lines = [
        f"# {lang}",
        "",
        f"[← All Languages](README.md)",
        "",
    ]
    
    for repo in sorted(repos_list, key=lambda r: -r.get("stargazers_count", 0)):
        name = repo["full_name"]
        owner = name.split("/")[0]
        desc = (repo.get("description") or "-").replace("|", "\\|")
        if len(desc) > 60:
            desc = desc[:57] + "..."
        stars = repo.get("stargazers_count", 0)
        lines.append(f"## [{name}](https://github.com/{name})")
        lines.append("")
        lines.append(f'<img src="https://github.com/{owner}.png" width="20" height="20"> {desc}')
        lines.append("")
        lines.append(f"⭐ {stars:,}")
        lines.append("")
    
    return "\n".join(lines)


# ==================== main ====================

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
    
    # Generate gh-pages site
    os.makedirs("_site", exist_ok=True)
    os.makedirs("_site/assets", exist_ok=True)
    os.makedirs("_site/_layouts", exist_ok=True)
    
    with open("_site/_config.yml", "w", encoding="utf-8") as f:
        f.write(generate_config(username, repo_name))
    
    with open("_site/assets/style.css", "w", encoding="utf-8") as f:
        f.write(generate_css())
    
    with open("_site/_layouts/default.html", "w", encoding="utf-8") as f:
        f.write(generate_layout(username))
    
    with open("_site/index.md", "w", encoding="utf-8") as f:
        f.write(generate_site_index(username, by_language, len(repos)))
    
    for lang, repos_list in by_language.items():
        slug = lang.lower().replace(" ", "-").replace(".", "").replace("#", "sharp")
        with open(f"_site/{slug}.md", "w", encoding="utf-8") as f:
            f.write(generate_language_page(lang, repos_list))
    
    # gh-pages README with link to site
    site_url = f"https://{username}.github.io/{repo_name}/"
    with open("_site/README.md", "w", encoding="utf-8") as f:
        f.write(f"# {username}'s Star List\n\n> **{len(repos)}** repos starred\n\n[View Static Site →]({site_url})\n")
    
    print(f"Generated site files in _site/")
    
    # Generate readme branch files
    os.makedirs("readme_files", exist_ok=True)
    
    with open("readme_files/README.md", "w", encoding="utf-8") as f:
        f.write(generate_readme_index(username, by_language, len(repos)))
    
    for lang, repos_list in by_language.items():
        slug = lang.lower().replace(" ", "-").replace(".", "").replace("#", "sharp")
        with open(f"readme_files/{slug}.md", "w", encoding="utf-8") as f:
            f.write(generate_readme_lang(lang, repos_list))
    
    print(f"Generated readme files in readme_files/")


if __name__ == "__main__":
    main()
