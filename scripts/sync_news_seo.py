from pathlib import Path
from datetime import date, datetime, timedelta, timezone
import json
import re
import xml.etree.ElementTree as ET
from xml.sax.saxutils import escape

BASE_URL = 'https://touchlinesport.net/'
AUTHOR_URL = BASE_URL + 'james-callan.html'
ORG_ID = BASE_URL + '#organization'


def update_newsarticle_schema(path: Path):
    text = path.read_text(encoding='utf-8')
    original = text
    found_news = False

    pattern = re.compile(r'(<script\s+type=["\']application/ld\+json["\']\s*>)(.*?)(</script>)', re.S | re.I)

    def repl(match):
        nonlocal found_news
        raw = match.group(2).strip()
        try:
            data = json.loads(raw)
        except Exception:
            return match.group(0)

        nodes = data.get('@graph', []) if isinstance(data, dict) and '@graph' in data else [data]
        changed = False
        for node in nodes:
            if not isinstance(node, dict):
                continue
            node_type = node.get('@type')
            if node_type == 'NewsArticle' or (isinstance(node_type, list) and 'NewsArticle' in node_type):
                found_news = True
                node['author'] = {
                    '@type': 'Person',
                    '@id': AUTHOR_URL + '#james-callan',
                    'name': 'James Callan',
                    'url': AUTHOR_URL,
                }
                node['publisher'] = {
                    '@type': 'Organization',
                    '@id': ORG_ID,
                    'name': 'Touchline Sport',
                    'url': BASE_URL,
                    'logo': {
                        '@type': 'ImageObject',
                        'url': BASE_URL + 'logo.png'
                    }
                }
                node['isAccessibleForFree'] = True
                image = node.get('image')
                if isinstance(image, str):
                    node['image'] = [image]
                changed = True

        if not changed:
            return match.group(0)
        return match.group(1) + '\n' + json.dumps(data, ensure_ascii=False, indent=2) + '\n' + match.group(3)

    text = pattern.sub(repl, text)

    if found_news:
        if '<meta name="author"' not in text:
            text = text.replace('</title>', '</title>\n<meta name="author" content="James Callan">', 1)
        if '<meta name="robots"' not in text:
            text = text.replace('</title>', '</title>\n<meta name="robots" content="index,follow,max-image-preview:large">', 1)
        # Make unlinked James Callan bylines clickable where the common byline class is used.
        text = re.sub(
            r'<span class="byline">\s*James Callan\s*</span>',
            '<a class="byline" rel="author" href="james-callan.html">James Callan</a>',
            text,
        )

    if text != original:
        path.write_text(text, encoding='utf-8')
    return found_news, text


def extract_article(path: Path):
    text = path.read_text(encoding='utf-8')
    scripts = re.findall(r'<script\s+type=["\']application/ld\+json["\']\s*>(.*?)</script>', text, re.S | re.I)
    for raw in scripts:
        try:
            data = json.loads(raw.strip())
        except Exception:
            continue
        nodes = data.get('@graph', []) if isinstance(data, dict) and '@graph' in data else [data]
        for node in nodes:
            if not isinstance(node, dict):
                continue
            node_type = node.get('@type')
            if node_type == 'NewsArticle' or (isinstance(node_type, list) and 'NewsArticle' in node_type):
                published = node.get('datePublished')
                headline = node.get('headline')
                page = node.get('mainEntityOfPage')
                if isinstance(page, dict):
                    loc = page.get('@id')
                else:
                    loc = page
                if not loc:
                    loc = BASE_URL + path.name
                if published and headline:
                    return {'loc': loc, 'date': published, 'headline': headline}
    return None


article_files = []
for path in Path('.').glob('*.html'):
    is_news, _ = update_newsarticle_schema(path)
    if is_news:
        article_files.append(path)

# Build a Google News sitemap containing only articles published in the last two days.
today = date.today()
cutoff = today - timedelta(days=2)
articles = []
for path in article_files:
    item = extract_article(path)
    if not item:
        continue
    try:
        published_date = datetime.fromisoformat(item['date'].replace('Z', '+00:00')).date()
    except Exception:
        try:
            published_date = date.fromisoformat(item['date'][:10])
        except Exception:
            continue
    if cutoff <= published_date <= today:
        item['published_date'] = published_date.isoformat()
        articles.append(item)

articles.sort(key=lambda x: x['published_date'], reverse=True)
news_lines = [
    '<?xml version="1.0" encoding="UTF-8"?>',
    '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" xmlns:news="http://www.google.com/schemas/sitemap-news/0.9">'
]
for item in articles:
    news_lines.extend([
        '  <url>',
        f'    <loc>{escape(item["loc"])}</loc>',
        '    <news:news>',
        '      <news:publication>',
        '        <news:name>Touchline Sport</news:name>',
        '        <news:language>en</news:language>',
        '      </news:publication>',
        f'      <news:publication_date>{item["published_date"]}</news:publication_date>',
        f'      <news:title>{escape(item["headline"])}</news:title>',
        '    </news:news>',
        '  </url>'
    ])
news_lines.append('</urlset>')
Path('news-sitemap.xml').write_text('\n'.join(news_lines) + '\n', encoding='utf-8')

print(f'News SEO checked on {len(article_files)} article pages; {len(articles)} current articles added to news-sitemap.xml')
