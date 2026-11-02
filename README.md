# Karen Donnelly Park

A lightweight website for Friends of Karen Donnelly Park, a neighborhood green space in Philadelphia. The site’s content comes from a published Google Doc, so volunteers can update the page without any knowledge of coding, and the entire stack is free.

## How it works

The hourly GitHub Actions workflow runs `fetch_doc.py`. The script downloads the published document, extracts its content and styles, and generates `index.html`. If the generated file changes, the workflow commits and pushes the update. You can also run the workflow manually from the **Actions** tab.

The published Google Doc is the content source of truth; `index.html` is generated output. Avoid editing the generated page directly, since the next update can overwrite those changes.

The site publishes to [karendonnellypark.org](karendonnellypark.org).

## Run locally

Requires Python 3 and the `requests` and `beautifulsoup4` packages.

```bash
python -m pip install requests beautifulsoup4
python fetch_doc.py
python -m http.server 8000
