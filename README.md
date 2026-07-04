# GitHub Star List

[![Generate Star List](https://github.com/interset-wq/github_star_list/actions/workflows/main.yml/badge.svg)](https://github.com/interset-wq/github_star_list/actions/workflows/main.yml)

> Auto-generate a beautiful README listing all your GitHub starred repositories, organized by language.

## Quick Start

1. **Use this template** - Click the green "Use this template" button above

2. **Enable GitHub Actions** - Go to your repo's Settings → Actions → General → Workflow permissions, select **"Read and write permissions"**

3. **Wait or trigger** - The workflow runs daily at 00:00 UTC, or manually trigger it from the Actions tab

That's it! Your starred repos will appear in README.md.

## Features

- Automatically fetches all your starred repos via GitHub API
- Groups repositories by programming language
- Shows repo description, stars count, and last update date
- Daily auto-update via GitHub Actions
- Manual trigger support

## How it works

1. GitHub Actions triggers on schedule/push/manual
2. Python script calls GitHub API to fetch your starred repos
3. Generates a categorized README.md
4. Auto-commits the changes back to your repo

## License

MIT
