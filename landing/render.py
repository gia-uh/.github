"""Render a project's landing page from its landing.yaml.

    python render.py landing.yaml _site

Writes _site/index.html with the shared stylesheet, fonts and the project's
logo. Fails with a list of problems when the YAML is incomplete.
"""
import html
import re
import shutil
import sys
from pathlib import Path

import yaml

KIT = Path(__file__).parent
LANGS = ("es", "en")
UI = {
    "docs": {"es": "Documentación", "en": "Documentation"},
    "code": {"es": "Código", "en": "Code"},
    "pypi": {"es": "PyPI", "en": "PyPI"},
    "copy": {"es": "copiar", "en": "copy"},
    "copied": {"es": "copiado", "en": "copied"},
    "example": {"es": "Un ejemplo", "en": "An example"},
    "lang": {"es": "English", "en": "Español"},
    "group": {"es": "Grupo de Inteligencia Artificial", "en": "Artificial Intelligence Group"},
    "uh": {"es": "Universidad de La Habana", "en": "University of Havana"},
    "faculty": {"es": "Facultad de Matemática y Computación, San Lázaro y L, Vedado, La Habana",
                "en": "Faculty of Mathematics and Computer Science, San Lázaro y L, Vedado, Havana"},
    "more": {"es": "Otros proyectos del GIA", "en": "More GIA projects"},
}


def problems(d, root):
    out = []
    for key in ("name", "accent", "install"):
        if not d.get(key):
            out.append(f"missing `{key}`")
    for key in ("tagline", "intro", "status"):
        v = d.get(key) or {}
        out += [f"`{key}` has no `{lang}` text" for lang in LANGS if not v.get(lang)]
    feats = d.get("features") or []
    if len(feats) != 3:
        out.append(f"`features` must have 3 items, it has {len(feats)}")
    for i, f in enumerate(feats):
        out += [f"`features[{i}]` has no `{lang}` text" for lang in LANGS if not f.get(lang)]
    if not (root / d.get("logo", "logo.svg")).is_file():
        out.append(f"logo file `{d.get('logo', 'logo.svg')}` not found")
    if not (d.get("example") or {}).get("code"):
        out.append("missing `example.code`")
    pypi = (d.get("links") or {}).get("pypi", "")
    m = re.search(r"pypi\.org/project/([^/]+)", pypi)
    if m and m.group(1).lower() not in d.get("install", "").lower():
        out.append(f"`install` does not mention the PyPI package `{m.group(1)}`")
    if d.get("accent") and not re.fullmatch(r"#[0-9a-fA-F]{6}", d["accent"]):
        out.append("`accent` must be a #rrggbb colour")
    return out


def bi(v, tag="span"):
    """Both languages; CSS shows the one in <html data-l>."""
    return "".join(f'<{tag} class="{lang}" lang="{lang}">{html.escape(v[lang])}</{tag}>' for lang in LANGS)


def render(d):
    e = html.escape
    links = d.get("links") or {}
    buttons = "".join(
        f'<a class="btn" href="{e(links[k])}">{bi(UI[k])}</a>' for k in ("docs", "code", "pypi") if links.get(k))
    feats = "".join(f"<li>{bi(f)}</li>" for f in d["features"])
    ex = d["example"]
    logo = Path(d.get("logo", "logo.svg")).name
    return f"""<!doctype html>
<html lang="es" data-l="es">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{e(d['name'])} · {e(d['tagline']['es'])}</title>
<meta name="description" content="{e(d['intro']['es'])}">
<meta property="og:title" content="{e(d['name'])}">
<meta property="og:description" content="{e(d['tagline']['es'])}">
<meta name="theme-color" content="#D6D2C8">
<link rel="icon" href="{e(logo)}" type="image/svg+xml">
<link rel="preload" href="assets/BigShouldersDisplay.woff2" as="font" type="font/woff2" crossorigin>
<link rel="stylesheet" href="assets/landing.css">
<style>:root{{--accent:{e(d['accent'])}}}</style>
</head>
<body>
<header class="bar wrap">
  <a class="gia" href="https://uhgia.org/"><b>GIA</b> {bi(UI['uh'])}</a>
  <button class="lang" type="button" id="lang">{bi(UI['lang'])}</button>
</header>
<main class="wrap">
  <section class="hero">
    <img class="logo" src="{e(logo)}" alt="" width="112" height="112">
    <div>
      <h1>{e(d['name'])}</h1>
      <p class="tagline">{bi(d['tagline'])}</p>
    </div>
  </section>
  <p class="intro">{bi(d['intro'])}</p>
  <div class="install"><code id="cmd">{e(d['install'])}</code><button type="button" id="copy"><span class="idle">{bi(UI['copy'])}</span><span class="ok">{bi(UI['copied'])}</span></button></div>
  <nav class="btns">{buttons}</nav>
  <ul class="features">{feats}</ul>
  <section class="example">
    <h2>{bi(UI['example'])}</h2>
    <pre><code class="language-{e(ex.get('lang', 'python'))}">{e(ex['code'].rstrip())}</code></pre>
  </section>
  <p class="status">{bi(d['status'])}</p>
</main>
<footer class="wrap">
  <p><b>{bi(UI['group'])}</b> · {bi(UI['uh'])}</p>
  <p>{bi(UI['faculty'])}</p>
  <p><a href="https://uhgia.org/projects/">{bi(UI['more'])}</a> · <a href="https://github.com/gia-uh">github.com/gia-uh</a></p>
</footer>
<script>
const root = document.documentElement;
const set = (l) => {{ root.dataset.l = l; root.lang = l; try {{ localStorage.setItem("gia-lang", l); }} catch (_) {{}} }};
let saved = null; try {{ saved = localStorage.getItem("gia-lang"); }} catch (_) {{}}
set(saved || ((navigator.language || "es").toLowerCase().startsWith("es") ? "es" : "en"));
document.getElementById("lang").addEventListener("click", () => set(root.dataset.l === "es" ? "en" : "es"));
const copy = document.getElementById("copy");
copy.addEventListener("click", async () => {{
  try {{ await navigator.clipboard.writeText(document.getElementById("cmd").textContent); }} catch (_) {{ return; }}
  copy.classList.add("done"); setTimeout(() => copy.classList.remove("done"), 1500);
}});
</script>
</body>
</html>
"""


def main(src, out):
    src, out = Path(src), Path(out)
    d = yaml.safe_load(src.read_text(encoding="utf-8"))
    bad = problems(d, src.parent)
    if bad:
        sys.exit("landing.yaml:\n  " + "\n  ".join(bad))
    (out / "assets").mkdir(parents=True, exist_ok=True)
    (out / "index.html").write_text(render(d), encoding="utf-8")
    shutil.copy(KIT / "landing.css", out / "assets" / "landing.css")
    for f in (KIT / "fonts").glob("*.woff2"):
        shutil.copy(f, out / "assets" / f.name)
    shutil.copy(src.parent / d.get("logo", "logo.svg"), out / Path(d.get("logo", "logo.svg")).name)
    print(f"rendered {d['name']} into {out}")


if __name__ == "__main__":
    main(*sys.argv[1:3])
