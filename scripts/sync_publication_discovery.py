from pathlib import Path
from datetime import datetime
from email.utils import format_datetime
import html as html_lib
import json
import re
from xml.sax.saxutils import escape

BASE_URL = "https://touchlinesport.net/"
FEED_URL = BASE_URL + "feed.xml"
LATEST_URL = BASE_URL + "latest-news.html"

NON_ARTICLE_PAGES = {
    "404.html", "index.html", "archive.html", "latest-news.html",
    "league-of-ireland-analysis.html", "touchline-tactics.html",
    "football-club-strategy.html", "scouting.html", "graphics.html",
    "about.html", "james-callan.html", "editorial-policy.html",
    "contact.html", "work-with-me.html", "football-content-awards-2026-finalist.html",
}

ARTICLE_TYPES = {"NewsArticle", "Article", "Report", "AnalysisNewsArticle"}
STOPWORDS = {
    "about", "after", "again", "against", "along", "also", "been", "before", "being",
    "between", "both", "could", "from", "have", "into", "ireland", "irish", "more",
    "news", "over", "sport", "that", "their", "there", "these", "they", "this",
    "touchline", "under", "what", "when", "where", "which", "while", "with", "would",
}

RSS_LINK = '<link rel="alternate" type="application/rss+xml" title="Touchline Sport RSS" href="https://touchlinesport.net/feed.xml">'

RELATED_STYLE = """<!-- TL_RELATED_STYLE_START -->
<style>
  .tl-related{margin:44px 0 28px;padding-top:28px;border-top:1px solid var(--line)}
  .tl-related-head{display:flex;align-items:end;justify-content:space-between;gap:18px;margin-bottom:18px}
  .tl-related-title{font-family:'Manrope',sans-serif;font-size:20px;font-weight:800;letter-spacing:-.01em;margin:0}
  .tl-related-all{font-family:'IBM Plex Mono',monospace;font-size:11px;color:var(--accent);font-weight:500}
  .tl-related-grid{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:14px}
  .tl-related-card{display:block;border:1px solid var(--line);border-radius:14px;overflow:hidden;background:#fff;transition:transform .18s ease,box-shadow .18s ease}
  .tl-related-card:hover{transform:translateY(-3px);box-shadow:0 10px 24px rgba(33,31,26,.08)}
  .tl-related-img{aspect-ratio:16/9;background:var(--paper-soft);background-size:cover;background-position:center}
  .tl-related-copy{padding:14px}
  .tl-related-kicker{font-family:'IBM Plex Mono',monospace;font-size:10px;color:var(--accent);margin-bottom:8px}
  .tl-related-card h3{font-family:'Manrope',sans-serif;font-size:14px;line-height:1.3;margin:0;font-weight:750}
  .tl-related-date{font-family:'IBM Plex Mono',monospace;font-size:9.5px;color:#928d7d;margin-top:10px}
  @media(max-width:700px){.tl-related-grid{grid-template-columns:1fr}.tl-related-img{aspect-ratio:16/8}}
</style>
<!-- TL_RELATED_STYLE_END -->"""

LD_PATTERN = re.compile(r'<script\s+type=["\']application/ld\+json["\']\s*>(.*?)</script>', re.S | re.I)


def clean_text(value):
    if value is None:
        return ""
    value = re.sub(r"<[^>]+>", " ", str(value))
    return re.sub(r"\s+", " ", html_lib.unescape(value)).strip()


def schema_nodes(text):
    for raw in LD_PATTERN.findall(text):
        try:
            data = json.loads(raw.strip())
        except Exception:
            continue
        nodes = data.get("@graph", []) if isinstance(data, dict) and "@graph" in data else [data]
        for node in nodes:
            if isinstance(node, dict):
                yield node


def type_values(node):
    value = node.get("@type")
    if isinstance(value, str):
        return {value}
    if isinstance(value, list):
        return {str(v) for v in value}
    return set()


def first_article_schema(text):
    for node in schema_nodes(text):
        if type_values(node) & ARTICLE_TYPES:
            return node
    return None


def meta_content(text, key, property_attr=False):
    attr = "property" if property_attr else "name"
    match = re.search(
        rf'<meta\s+{attr}=["\']{re.escape(key)}["\']\s+content=["\']([^"\']*)["\']',
        text,
        re.I,
    )
    return html_lib.unescape(match.group(1)).strip() if match else ""


def canonical_url(text, filename):
    match = re.search(r'<link\s+rel=["\']canonical["\'][^>]*href=["\']([^"\']+)["\']', text, re.I)
    if match:
        return html_lib.unescape(match.group(1)).strip()
    return BASE_URL + filename


def parse_datetime(value):
    if not value:
        return None
    try:
        dt = datetime.fromisoformat(str(value).strip().replace("Z", "+00:00"))
        return dt if dt.tzinfo else dt.astimezone()
    except Exception:
        return None


def article_image(node, text):
    image = node.get("image")
    if isinstance(image, list) and image:
        image = image[0]
    if isinstance(image, dict):
        image = image.get("url") or image.get("contentUrl")
    if isinstance(image, str) and image:
        return image
    return meta_content(text, "og:image", property_attr=True)


def article_url(node, text, filename):
    main = node.get("mainEntityOfPage")
    if isinstance(main, dict):
        main = main.get("@id") or main.get("url")
    if isinstance(main, str) and main.startswith("http"):
        return main
    return canonical_url(text, filename)


def article_keywords(node):
    value = node.get("keywords", [])
    if isinstance(value, str):
        parts = re.split(r"[,;]", value)
    elif isinstance(value, list):
        parts = value
    else:
        parts = []
    return {clean_text(v).lower() for v in parts if clean_text(v)}


def tokens(value):
    found = re.findall(r"[a-zA-ZÀ-ÿ0-9’'-]{4,}", clean_text(value).lower())
    return {t.strip("’'-") for t in found if t.strip("’'-") not in STOPWORDS}


def visible_read_time(text):
    match = re.search(r"(\d+)\s*min\s*read", clean_text(text), re.I)
    return f"{match.group(1)} min read" if match else ""


def extract_article(path):
    if path.name in NON_ARTICLE_PAGES:
        return None
    text = path.read_text(encoding="utf-8")
    node = first_article_schema(text)
    if not node:
        return None

    title = clean_text(node.get("headline"))
    if not title:
        h1 = re.search(r"<h1\b[^>]*>(.*?)</h1>", text, re.S | re.I)
        title = clean_text(h1.group(1)) if h1 else ""
    description = clean_text(node.get("description")) or meta_content(text, "description")
    published_raw = node.get("datePublished") or meta_content(text, "article:published_time", property_attr=True)
    published = parse_datetime(published_raw)
    if not title or not published:
        return None

    section = clean_text(node.get("articleSection"))
    if not section:
        pill = re.search(r'<span\s+class=["\']pill["\'][^>]*>(.*?)</span>', text, re.S | re.I)
        section = clean_text(pill.group(1)) if pill else "Football"
    url = article_url(node, text, path.name)
    if not url.startswith(BASE_URL):
        return None

    item = {
        "path": path,
        "filename": path.name,
        "title": title,
        "description": description,
        "published": published,
        "published_raw": str(published_raw),
        "section": section or "Football",
        "url": url,
        "image": article_image(node, text),
        "keywords": article_keywords(node),
        "read_time": visible_read_time(text),
    }
    item["title_tokens"] = tokens(title)
    item["body_tokens"] = tokens(title + " " + description + " " + " ".join(item["keywords"]))
    return item


def display_date(dt):
    return f"{dt.day} {dt.strftime('%b %Y')}"


def related_score(a, b):
    score = 0.0
    if a["section"].lower() == b["section"].lower():
        score += 10
    score += 5 * len(a["keywords"] & b["keywords"])
    score += 2.5 * len(a["title_tokens"] & b["title_tokens"])
    score += min(4, 0.75 * len(a["body_tokens"] & b["body_tokens"]))
    age_days = abs((a["published"].date() - b["published"].date()).days)
    if age_days <= 14:
        score += 2
    elif age_days <= 60:
        score += 1
    return score


def related_for(article, articles, count=3):
    candidates = [a for a in articles if a["filename"] != article["filename"]]
    candidates.sort(key=lambda other: (related_score(article, other), other["published"]), reverse=True)
    return candidates[:count]


def related_block(items):
    cards = []
    for item in items:
        image_style = ""
        if item["image"]:
            image_style = f" style=\"background-image:url('{html_lib.escape(item['image'], quote=True)}')\""
        cards.append(
            '<a class="tl-related-card" href="{href}">'
            '<div class="tl-related-img"{image_style}></div>'
            '<div class="tl-related-copy">'
            '<div class="tl-related-kicker">{section}</div>'
            '<h3>{title}</h3>'
            '<div class="tl-related-date">{date}</div>'
            '</div></a>'.format(
                href=html_lib.escape(item["filename"], quote=True),
                image_style=image_style,
                section=html_lib.escape(item["section"]),
                title=html_lib.escape(item["title"]),
                date=html_lib.escape(display_date(item["published"])),
            )
        )
    return (
        '<!-- TL_RELATED_START -->\n'
        '<section class="tl-related" aria-labelledby="tl-related-heading">\n'
        '  <div class="tl-related-head"><h2 class="tl-related-title" id="tl-related-heading">More from Touchline</h2>'
        '<a class="tl-related-all" href="latest-news.html">Latest news &amp; analysis →</a></div>\n'
        f'  <div class="tl-related-grid">{"".join(cards)}</div>\n'
        '</section>\n'
        '<!-- TL_RELATED_END -->'
    )


def add_rss_discovery(text):
    text = re.sub(
        r'\s*<link\s+rel=["\']alternate["\'][^>]*type=["\']application/rss\+xml["\'][^>]*>\s*',
        "\n",
        text,
        flags=re.I,
    )
    if "</head>" in text:
        text = text.replace("</head>", RSS_LINK + "\n</head>", 1)
    return text


def update_article_related(article, all_articles):
    path = article["path"]
    text = path.read_text(encoding="utf-8")
    original = text
    text = re.sub(r'\s*<!-- TL_RELATED_STYLE_START -->.*?<!-- TL_RELATED_STYLE_END -->\s*', "\n", text, flags=re.S)
    text = re.sub(r'\s*<!-- TL_RELATED_START -->.*?<!-- TL_RELATED_END -->\s*', "\n", text, flags=re.S)
    if "</head>" in text:
        text = text.replace("</head>", RELATED_STYLE + "\n</head>", 1)

    items = related_for(article, all_articles)
    if items:
        block = related_block(items)
        foot = re.search(r'<div\s+class=["\']article-foot-nav["\']', text, re.I)
        if foot:
            text = text[:foot.start()] + block + "\n    " + text[foot.start():]
        else:
            text = text.replace("</article>", block + "\n</article>", 1)

    text = add_rss_discovery(text)
    if text != original:
        path.write_text(text, encoding="utf-8")
        return True
    return False


def build_rss(articles):
    ordered = sorted(articles, key=lambda a: a["published"], reverse=True)[:50]
    if not ordered:
        return
    lines = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<rss version="2.0" xmlns:atom="http://www.w3.org/2005/Atom" xmlns:media="http://search.yahoo.com/mrss/">',
        "  <channel>",
        "    <title>Touchline Sport</title>",
        f"    <link>{BASE_URL}</link>",
        "    <description>Independent football news and analysis from Touchline Sport, covering Irish football, tactics, club strategy, recruitment and the business of the game.</description>",
        "    <language>en-ie</language>",
        f'    <atom:link href="{FEED_URL}" rel="self" type="application/rss+xml" />',
        f"    <lastBuildDate>{format_datetime(ordered[0]['published'])}</lastBuildDate>",
    ]
    for item in ordered:
        lines.extend([
            "    <item>",
            f"      <title>{escape(item['title'])}</title>",
            f"      <link>{escape(item['url'])}</link>",
            f'      <guid isPermaLink="true">{escape(item["url"])}</guid>',
            f"      <pubDate>{format_datetime(item['published'])}</pubDate>",
            f"      <description>{escape(item['description'])}</description>",
            f"      <category>{escape(item['section'])}</category>",
        ])
        if item["image"]:
            lines.append(f'      <media:content url="{html_lib.escape(item["image"], quote=True)}" medium="image" />')
        lines.append("    </item>")
    lines.extend(["  </channel>", "</rss>"])
    Path("feed.xml").write_text("\n".join(lines) + "\n", encoding="utf-8")


def latest_page(articles):
    ordered = sorted(articles, key=lambda a: a["published"], reverse=True)
    item_list = {
        "@context": "https://schema.org",
        "@type": "ItemList",
        "name": "Latest Touchline Sport articles",
        "itemListOrder": "https://schema.org/ItemListOrderDescending",
        "itemListElement": [
            {
                "@type": "ListItem",
                "position": idx,
                "name": item["title"],
                "url": item["url"],
            }
            for idx, item in enumerate(ordered, start=1)
        ],
    }
    cards = []
    for item in ordered:
        image = (
            f'<img src="{html_lib.escape(item["image"], quote=True)}" loading="lazy" alt="">'
            if item["image"] else '<div class="story-placeholder">Touchline Sport</div>'
        )
        meta = display_date(item["published"])
        if item["read_time"]:
            meta += f" · {item['read_time']}"
        cards.append(
            f'''<article class="story">
  <a class="story-image" href="{html_lib.escape(item["filename"], quote=True)}">{image}</a>
  <div class="story-copy">
    <div class="story-kicker">{html_lib.escape(item["section"])}</div>
    <h2><a href="{html_lib.escape(item["filename"], quote=True)}">{html_lib.escape(item["title"])}</a></h2>
    <p>{html_lib.escape(item["description"])}</p>
    <div class="story-meta">{html_lib.escape(meta)}</div>
  </div>
</article>'''
        )
    page = f'''<!DOCTYPE html>
<html lang="en">
<head>
<!-- Google tag (gtag.js) -->
<script async src="https://www.googletagmanager.com/gtag/js?id=G-2X872GP5L0"></script>
<script>
  window.dataLayer = window.dataLayer || [];
  function gtag(){{window.dataLayer.push(arguments);}}
  gtag('js', new Date());
  gtag('config', 'G-2X872GP5L0');
</script>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Latest Football News &amp; Analysis | Touchline Sport</title>
<meta name="description" content="The latest football news and analysis from Touchline Sport, with League of Ireland reporting, tactics, club strategy, recruitment and football business.">
<meta name="robots" content="index,follow,max-image-preview:large">
<link rel="canonical" href="{LATEST_URL}">
{RSS_LINK}
<meta property="og:type" content="website">
<meta property="og:site_name" content="Touchline Sport">
<meta property="og:title" content="Latest Football News &amp; Analysis | Touchline Sport">
<meta property="og:description" content="The newest reporting and analysis from Touchline Sport.">
<meta property="og:url" content="{LATEST_URL}">
<meta name="twitter:card" content="summary">
<meta name="twitter:title" content="Latest Football News &amp; Analysis | Touchline Sport">
<meta name="twitter:description" content="The newest reporting and analysis from Touchline Sport.">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Manrope:wght@500;600;700;800&family=Inter:wght@400;500;600&family=IBM+Plex+Mono:wght@400;500&display=swap" rel="stylesheet">
<script type="application/ld+json">
{json.dumps(item_list, ensure_ascii=False, indent=2)}
</script>
<style>
:root{{--paper:#fbf3e7;--paper-soft:#f5e5cf;--ink:#1c1a17;--ink-soft:#6b5d4d;--accent:#e8720f;--accent-soft:#fbe2c4;--line:rgba(33,31,26,.10);--max:1180px;--radius:18px}}
*{{box-sizing:border-box}}html{{scroll-behavior:smooth}}body{{margin:0;background:var(--paper);color:var(--ink);font-family:'Inter',-apple-system,sans-serif;-webkit-font-smoothing:antialiased;line-height:1.5}}a{{color:inherit;text-decoration:none}}.wrap{{max-width:var(--max);margin:0 auto;padding:0 32px}}
header{{padding:26px 0;position:sticky;top:0;background:rgba(251,243,231,.88);backdrop-filter:blur(10px);z-index:20}}.nav-row{{display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:14px}}.logo{{display:flex;align-items:center;gap:9px;font-family:'Manrope',sans-serif;font-weight:800;font-size:18px}}.logo-mark{{width:30px;height:30px;object-fit:contain}}nav.links{{display:flex;gap:30px}}nav.links a{{font-size:14px;font-weight:500;color:var(--ink-soft)}}nav.links a:hover{{color:var(--ink)}}.nav-cta{{background:var(--ink);color:var(--paper);padding:9px 18px;border-radius:99px;font-size:13.5px;font-weight:600}}
.hero{{padding:64px 0 28px}}.pill{{display:inline-flex;padding:5px 13px;border-radius:99px;background:var(--accent-soft);color:var(--accent);font-family:'IBM Plex Mono',monospace;font-size:11.5px;font-weight:500}}h1{{font-family:'Manrope',sans-serif;font-size:clamp(38px,6vw,64px);letter-spacing:-.035em;line-height:1;margin:18px 0 16px;max-width:900px}}.hero p{{max-width:65ch;color:var(--ink-soft);font-size:16px;line-height:1.7;margin:0}}.hero-actions{{display:flex;gap:12px;margin-top:24px;flex-wrap:wrap}}.hero-actions a{{font-size:13px;font-weight:650;border:1px solid var(--line);border-radius:99px;padding:10px 16px;background:#fff}}.hero-actions a:first-child{{background:var(--ink);color:var(--paper);border-color:var(--ink)}}
.latest-list{{padding:24px 0 80px}}.story{{display:grid;grid-template-columns:280px minmax(0,1fr);gap:28px;padding:28px 0;border-top:1px solid var(--line)}}.story:last-child{{border-bottom:1px solid var(--line)}}.story-image{{display:block;border-radius:16px;overflow:hidden;aspect-ratio:16/10;background:var(--paper-soft)}}.story-image img{{width:100%;height:100%;object-fit:cover;display:block}}.story-placeholder{{height:100%;display:flex;align-items:center;justify-content:center;font-family:'Manrope',sans-serif;font-weight:800;color:var(--accent)}}.story-kicker{{font-family:'IBM Plex Mono',monospace;font-size:11px;color:var(--accent);margin-bottom:9px}}.story h2{{font-family:'Manrope',sans-serif;font-size:clamp(21px,3vw,30px);line-height:1.15;letter-spacing:-.015em;margin:0 0 10px}}.story h2 a:hover{{color:var(--accent)}}.story p{{color:var(--ink-soft);font-size:14px;line-height:1.6;margin:0 0 14px;max-width:70ch}}.story-meta{{font-family:'IBM Plex Mono',monospace;font-size:10.5px;color:#928d7d}}
footer{{border-top:1px solid var(--line);padding:34px 0}}.fine-print{{font-family:'IBM Plex Mono',monospace;font-size:11px;line-height:1.7;color:#928d7d;max-width:900px;margin:0 0 22px}}.foot-row{{display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:14px;font-size:13px;color:var(--ink-soft)}}.foot-links{{display:flex;gap:22px;flex-wrap:wrap}}
@media(max-width:720px){{nav.links{{display:none}}.wrap{{padding:0 20px}}.story{{grid-template-columns:1fr;gap:16px}}.story-image{{aspect-ratio:16/9}}}}
</style>
</head>
<body>
<header><div class="wrap nav-row"><a class="logo" href="index.html"><img class="logo-mark" src="logo.png" alt="Touchline Sport"> Touchline Sport</a><nav class="links" aria-label="Primary navigation"><a href="latest-news.html">Latest</a><a href="league-of-ireland-analysis.html">Irish Football</a><a href="touchline-tactics.html">Touchline Tactics</a><a href="archive.html">Archive</a><a href="about.html">About</a></nav><a class="nav-cta" href="index.html#subscribe">Subscribe</a></div></header>
<main>
<section class="hero"><div class="wrap"><span class="pill">Latest from Touchline</span><h1>Latest News &amp; Analysis</h1><p>The newest Touchline Sport reporting and analysis, in one place. League of Ireland news sits alongside tactics, club strategy, recruitment and the business behind football.</p><div class="hero-actions"><a href="feed.xml">Follow the RSS feed</a><a href="archive.html">Browse the full archive</a></div></div></section>
<section class="latest-list"><div class="wrap">{''.join(cards)}</div></section>
</main>
<footer><div class="wrap"><p class="fine-print">© 2026 James Callan / Touchline Sport. All content on this website, including written articles, analysis, graphics and original research, is the intellectual property of James Callan and Touchline Sport unless otherwise stated. No content may be reproduced, republished or redistributed without prior permission.</p><div class="foot-row"><span>Touchline Sport</span><div class="foot-links"><a href="about.html">About</a><a href="editorial-policy.html">Editorial Policy</a><a href="contact.html">Contact</a><a href="james-callan.html">James Callan</a><a href="feed.xml">RSS</a></div></div></div></footer>
</body>
</html>
'''
    Path("latest-news.html").write_text(page, encoding="utf-8")


def add_rss_to_non_articles(article_paths):
    article_names = {p.name for p in article_paths}
    changed = 0
    for path in Path(".").glob("*.html"):
        if path.name in article_names:
            continue
        text = path.read_text(encoding="utf-8")
        updated = add_rss_discovery(text)
        if updated != text:
            path.write_text(updated, encoding="utf-8")
            changed += 1
    return changed


articles = [item for path in Path(".").glob("*.html") if (item := extract_article(path))]
articles.sort(key=lambda item: item["published"], reverse=True)

build_rss(articles)
latest_page(articles)

related_changes = sum(1 for item in articles if update_article_related(item, articles))
rss_page_changes = add_rss_to_non_articles([item["path"] for item in articles])

print(
    f"Publication discovery sync: {len(articles)} articles; "
    f"feed.xml rebuilt; latest-news.html rebuilt; "
    f"{related_changes} article related-link blocks refreshed; "
    f"{rss_page_changes} other pages advertised RSS."
)
