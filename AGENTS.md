# Repository Guidelines

## Project Structure & Module Organization
- `config.yml` holds the site metadata, menu config, and PaperMod options; keep edits focused and validated locally.
- Draft and publish content in `content/posts/`; follow the front matter template in `archetypes/default.md` and leave `draft: true` until review is complete.
- Store shared assets under `static/` (e.g., `static/img/<slug>/`); Hugo serves them directly without processing.
- `themes/PaperMod` is tracked as a submodule—override components in `layouts/` instead of editing theme files in place.
- `public/` and `resources/_gen/` are build artifacts; never hand-edit them, and exclude them from commits unless troubleshooting deployment.

## Build, Test, and Development Commands
- `hugo new posts/<slug>.md` scaffolds a Markdown draft using the archetype above.
- `hugo server -D --disableFastRender` launches a live preview with drafts; reload the browser after changing configs.
- `hugo --gc --minify` mirrors the GitHub Pages workflow, cleaning stale files and producing the deployable bundle.

## Coding Style & Naming Conventions
- Match existing filenames (`YYYY-week-##.md`) and use kebab-case slugs in front matter for consistent URLs.
- Write titles in Title Case, keep headings sentence case, and prefer fenced code blocks with language hints for snippets.
- Use 2-space indentation in front matter blocks and avoid trailing whitespace so Hugo’s formatter stays clean.

## Testing Guidelines
- The Hugo build is the primary check; run `hugo --minify` before pushing and resolve any warnings, especially broken links or missing images.
- During review, scan the local preview for taxonomy pages and search to confirm the post metadata renders as expected.

## Commit & Pull Request Guidelines
- Follow the concise, imperative style seen in history (`add 2025 week 34 post`), grouping related assets with their article.
- PRs should summarize the change, list new content paths, link any tracking issue, and include screenshots when layout or styling shifts.
- Ensure the `github pages` workflow in `.github/workflows/gh-pages.yml` passes; only merges to `main` trigger deployment via the configured `REPO_TOKEN`.

## Deployment & CI Notes
- Work against branches; let the CI publish to GitHub Pages so `main` stays the single source of truth.
- If a secret rotates or the deploy job fails, re-run the workflow from GitHub Actions after validating the updated credentials.
