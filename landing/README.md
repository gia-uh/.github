# Project landing pages

Every gia-uh project shown on [uhgia.org](https://uhgia.org) has its own site at
`<project>.uhgia.org`. The sites share one template: the paper, type and rules of
uhgia.org, with the project's logo and accent colour. This folder holds the template
(`render.py`, `landing.css`, `fonts/`); `.github/workflows/landing.yml` builds and
deploys it.

## Add a site to a project

1. Put `logo.svg` at the repo root.
2. Write `landing.yaml` at the repo root (format below).
3. Add `.github/workflows/site.yml`:

   ```yaml
   name: site
   on:
     push:
       branches: [main]
     workflow_dispatch:
   permissions:
     contents: read
     pages: write
     id-token: write
   concurrency:
     group: pages
     cancel-in-progress: false
   jobs:
     site:
       uses: gia-uh/.github/.github/workflows/landing.yml@main
       # with:                                   # only if the project has docs
       #   docs-build: uv run mkdocs build -d _docs
       #   docs-dir: _docs
   ```

   A docs generator that needs its base URL (mkdocs `site_url`) uses
   `https://<project>.uhgia.org/docs/`.
4. In the repo settings, Pages source is "GitHub Actions" and the custom domain is
   `<project>.uhgia.org`; the DNS record is a CNAME to `gia-uh.github.io`.

## landing.yaml

Every text is a pair `{es, en}`. The renderer fails, listing what is wrong, when a
text lacks a language, `features` does not have three items, the logo is missing, or
`install` does not name the PyPI package linked in `links.pypi`.

```yaml
name: Legio
accent: "#B7322A"          # the logo's main colour
logo: logo.svg             # optional, this is the default
tagline:
  es: Orquestación de agentes sobre colas
  en: Agent orchestration on queues
intro:
  es: Dos frases sobre qué es y para quién.
  en: Two sentences on what it is and who it is for.
install: pip install legio
links:                     # each optional
  docs: /docs/
  code: https://github.com/gia-uh/legio
  pypi: https://pypi.org/project/legio/
features:                  # exactly three
  - es: ...
    en: ...
  - es: ...
    en: ...
  - es: ...
    en: ...
example:
  lang: python
  code: |
    # a short example that runs as written
status:
  es: v0.1.7 · PyPI · licencia MIT
  en: v0.1.7 · PyPI · MIT licence
```

Preview locally:

```bash
uv run --no-project --with pyyaml python <path-to>/landing/render.py landing.yaml _site
python3 -m http.server -d _site 8000
```
