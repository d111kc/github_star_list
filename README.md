# GitHub Star List

> Auto-generate a beautiful README listing all your GitHub starred repositories, organized by language.

<p align="center">
  <a href="https://github.com/interset-wq/github_star_list/generate">
    <img src="https://img.shields.io/badge/Use_this_template-238636?style=for-the-badge&logo=github" alt="Use this template">
  </a>
</p>

## Features

- Automatically fetches all your starred repos via GitHub API
- Groups repositories by programming language
- Shows repo description, stars count, and last update date
- Daily auto-update via GitHub Actions
- Deploys to GitHub Pages for easy viewing

## Quick Start

### Option 1: Use Template (Recommended)

1. Click the **"Use this template"** button above
2. Go to Settings → Actions → General → Workflow permissions → Select **"Read and write permissions"**
3. Go to Settings → Pages → Source → Select **"Deploy from a branch"** → Branch: `gh-pages` → Save
4. Wait for the workflow to run (or trigger it manually from Actions tab)
5. Your star list will be available at `https://<username>.github.io/<repo-name>/`

### Option 2: Fork

1. Fork this repository
2. Enable GitHub Actions and Pages (see steps above)

## How it works

```
┌─────────────────┐     ┌──────────────┐     ┌─────────────┐     ┌────────────┐
│ GitHub Actions   │────▶│ Fetch Stars  │────▶│ Generate    │────▶│ Deploy to  │
│ (Daily/Manual)   │     │ via API      │     │ README.md   │     │ gh-pages   │
└─────────────────┘     └──────────────┘     └─────────────┘     └────────────┘
```

1. GitHub Actions triggers on schedule/push/manual
2. Python script calls GitHub API to fetch your starred repos
3. Generates a categorized README.md
4. Pushes to `gh-pages` branch and deploys to GitHub Pages

## Preview

Your star list will be published as a static site with:
- Table of contents with language counts
- Repos grouped by programming language
- Sorted by stars (highest first)
- Search-friendly markdown format

## License

MIT
