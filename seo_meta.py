"""Inject self-canonical, Open Graph, Twitter card, and sitemap into built HTML."""
from __future__ import annotations

import re
from datetime import date
from html import escape
from pathlib import Path

SITE = "https://aipmandy.github.io/how-to-become-an-executive"
OG = f"{SITE}/og.png"
START = "<!-- seo-meta -->"
END = "<!-- /seo-meta -->"


def page_url(rel: str) -> str:
    rel = rel.replace("\\", "/")
    if rel in ("index.html", ""):
        return SITE + "/"
    return f"{SITE}/{rel}"


def _attr(html: str, key: str) -> str:
    m = re.search(
        rf'<meta[^>]+(?:property|name)=["\']{re.escape(key)}["\'][^>]*content=["\']([^"\']*)["\']',
        html,
        re.I,
    )
    if m:
        return m.group(1)
    m = re.search(
        rf'<meta[^>]+content=["\']([^"\']*)["\'][^>]*(?:property|name)=["\']{re.escape(key)}["\']',
        html,
        re.I,
    )
    return m.group(1) if m else ""


def block_for(rel: str, html: str) -> str:
    title = ""
    tm = re.search(r"<title>(.*?)</title>", html, re.I | re.S)
    if tm:
        title = re.sub(r"\s+", " ", tm.group(1)).strip()
    desc = _attr(html, "description") or "普通人成为高管保姆级指南：10章、50项任务、七阶段路线与模板。AI酋长Andy 免费开源。"
    url = page_url(rel)
    t = escape(title, quote=True)
    d = escape(desc, quote=True)
    ld = ""
    if rel in ("index.html", ""):
        import json
        person = {
            "@type": "Person",
            "@id": "https://github.com/AIPMAndy#person",
            "name": "AI酋长Andy",
            "alternateName": ["AI Chief Andy", "Andy Liu", "AIPMAndy"],
            "url": "https://metaver.vip/",
            "sameAs": ["https://x.com/AIPMAndy", "https://github.com/AIPMAndy", "https://metaver.vip/"],
            "jobTitle": "流量 AI 联合创始人、星觉 AI 创始人",
            "worksFor": {"@type": "Organization", "name": "星觉科技"},
            "address": {"@type": "PostalAddress", "addressLocality": "北京", "addressCountry": "CN"},
            "description": "AI酋长Andy（Andy Liu，GitHub / X @AIPMAndy）：流量 AI 联合创始人、星觉 AI 创始人。星觉科技，北京。",
        }
        work = {
            "@type": "Book",
            "@id": SITE + "/#work",
            "name": "普通人成为高管保姆级指南",
            "url": SITE + "/",
            "inLanguage": "zh-CN",
            "author": {"@id": "https://github.com/AIPMAndy#person"},
            "publisher": {"@id": "https://github.com/AIPMAndy#person"},
        }
        ld = '<script type="application/ld+json">' + json.dumps({"@context": "https://schema.org", "@graph": [person, work]}, ensure_ascii=False, separators=(",", ":")) + "</script>"

    return (
        f"{START}"
        f'<link rel="canonical" href="{url}">'
        f'<meta property="og:type" content="website">'
        f'<meta property="og:locale" content="zh_CN">'
        f'<meta property="og:site_name" content="普通人成为高管保姆级指南">'
        f'<meta property="og:url" content="{url}">'
        f'<meta property="og:title" content="{t}">'
        f'<meta property="og:description" content="{d}">'
        f'<meta property="og:image" content="{OG}">'
        f'<meta property="og:image:width" content="1200">'
        f'<meta property="og:image:height" content="630">'
        f'<meta name="twitter:card" content="summary_large_image">'
        f'<meta name="twitter:site" content="@AIPMAndy">'
        f'<meta name="twitter:creator" content="@AIPMAndy">'
        f'<meta name="twitter:title" content="{t}">'
        f'<meta name="twitter:description" content="{d}">'
        f'<meta name="twitter:image" content="{OG}">'
        f"{ld}{END}"
    )


def inject_html(path: Path, root: Path) -> None:
    html = path.read_text(encoding="utf-8")
    html = re.sub(re.escape(START) + r".*?" + re.escape(END), "", html, flags=re.S)
    rel = path.relative_to(root).as_posix()
    block = block_for(rel, html)
    if re.search(r"<head[^>]*>", html, re.I):
        html = re.sub(r"(<head[^>]*>)", r"\1" + block, html, count=1, flags=re.I)
    else:
        html = block + html
    path.write_text(html, encoding="utf-8")


def write_sitemap(root: Path) -> None:
    pages = sorted(
        p.relative_to(root).as_posix()
        for p in root.rglob("*.html")
        if ".git" not in p.parts
    )
    today = date.today().isoformat()
    urls = []
    for rel in pages:
        loc = page_url(rel)
        prio = "1.0" if rel == "index.html" else "0.7"
        urls.append(
            f"  <url><loc>{loc}</loc><lastmod>{today}</lastmod><changefreq>monthly</changefreq><priority>{prio}</priority></url>"
        )
    xml = (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        + "\n".join(urls)
        + "\n</urlset>\n"
    )
    (root / "sitemap.xml").write_text(xml, encoding="utf-8")
    (root / "robots.txt").write_text(
        "User-agent: *\nAllow: /\n\n"
        f"Sitemap: {SITE}/sitemap.xml\n",
        encoding="utf-8",
    )


def apply(root: Path | None = None) -> None:
    root = Path(root or Path(__file__).resolve().parent)
    for p in sorted(root.rglob("*.html")):
        if ".git" in p.parts:
            continue
        inject_html(p, root)
    write_sitemap(root)


if __name__ == "__main__":
    apply()
