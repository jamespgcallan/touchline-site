from pathlib import Path
from datetime import datetime, timezone
from email.utils import format_datetime
import json
import re
from xml.sax.saxutils import escape

BASE_URL = 'https://touchlinesport.net/'
FEED_URL = BASE_URL + 'feed.xml'
MAX_ITEMS = 30


def iter_jsonld_nodes(text):
    scripts = re.findall(r'<script\s+type=["\']application/ld\+json["\']\s*>(.*?)</script>', text, re.S | re.I)
    for raw in scripts:
        try:
            data = json.loads(raw.strip())
        except Exception:
            continue
        if isinstance(data, dict) and '@graph' in data:
            nodes = data.get('@graph', [])
        elif isinstance(data, list):
            nodes = data
        else:
            nodes = [data]
        for node in nodes:
            if isinstance(node, dict):
                yield node


def first_image(node):
    image = node.get('image')
    if isinstance(image, str):
        return image
    if isinstance(image, list) and image:
        first = image[0]
        if isinstance(first, str):
            return first
        if isinstance(first, dict):
            return first.get('url') or first.get('contentUrl')
    if isinstance(image, dict):
        return image.get('url') or image.get('contentUrl')
    return None


def article_url(node, path):
    page = node.get('mainEntityOfPage')
    if isinstance(page, dict):
        url = page.get('@id') or page.get('url')
    else:
        url = page
    return url or node.get('url') or (BASE_URL + path.name)


def parse_date(value):
    if not value:
        return None
    try:
        dt = datetime.fromisoformat(str(value).replace('Z', '+00:00'))
    except Exception:
        return None
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt


def extract_article(path):
    text = path.read_text(encoding='utf-8')
    for node in iter_jsonld_nodes(text):
        node_type = node.get('@type')
        types = node_type if isinstance(node_type, list) else [node_type]
        if not any(t in ('NewsArticle', 'Article') for t in types):
            continue

        title = node.get('headline') or node.get('name')
        published = parse_date(node.get('datePublished'))
        if not title or not published:
            continue

        description = node.get('description') or ''
        if not description:
            meta = re.search(r'<meta\s+name=["\']description["\']\s+content=["\'](.*?)["\']', text, re.I | re.S)
            if meta:
                description = meta.group(1).strip()

        author = node.get('author')
        if isinstance(author, dict):
            author_name = author.get('name') or 'James Callan'
        elif isinstance(author, list) and author and isinstance(author[0], dict):
            author_name = author[0].get('name') or 'James Callan'
        elif isinstance(author, str):
            author_name = author
        else:
            author_name = 'James Callan'

        section = node.get('articleSection')
        if isinstance(section, list):
            section = section[0] if section else None

        return {
            'title': str(title).strip(),
            'url': article_url(node, path),
            'published': published,
            'description': str(description).strip(),
            'image': first_image(node),
            'author': str(author_name).strip(),
            'section': str(section).strip() if section else None,
        }
    return None


articles = []
seen = set()
for path in Path('.').glob('*.html'):
    item = extract_article(path)
    if not item or item['url'] in seen:
        continue
    seen.add(item['url'])
    articles.append(item)

articles.sort(key=lambda x: x['published'], reverse=True)
articles = articles[:MAX_ITEMS]

now = datetime.now(timezone.utc)
lines = [
    '<?xml version="1.0" encoding="UTF-8"?>',
    '<rss version="2.0" xmlns:atom="http://www.w3.org/2005/Atom" xmlns:media="http://search.yahoo.com/mrss/" xmlns:dc="http://purl.org/dc/elements/1.1/">',
    '  <channel>',
    '    <title>Touchline Sport</title>',
    f'    <link>{escape(BASE_URL)}</link>',
    '    <description>Independent football journalism covering Irish football, recruitment, club strategy, ownership, academies and tactical analysis.</description>',
    '    <language>en-ie</language>',
    f'    <lastBuildDate>{escape(format_datetime(now))}</lastBuildDate>',
    f'    <atom:link href="{escape(FEED_URL)}" rel="self" type="application/rss+xml" />',
    '    <image>',
    f'      <url>{escape(BASE_URL + "logo.png")}</url>',
    '      <title>Touchline Sport</title>',
    f'      <link>{escape(BASE_URL)}</link>',
    '    </image>',
]

for item in articles:
    lines.extend([
        '    <item>',
        f'      <title>{escape(item["title"])}</title>',
        f'      <link>{escape(item["url"])}</link>',
        f'      <guid isPermaLink="true">{escape(item["url"])}</guid>',
        f'      <pubDate>{escape(format_datetime(item["published"]))}</pubDate>',
        f'      <dc:creator>{escape(item["author"])}</dc:creator>',
    ])
    if item['description']:
        lines.append(f'      <description>{escape(item["description"])}</description>')
    if item['section']:
        lines.append(f'      <category>{escape(item["section"])}</category>')
    if item['image']:
        lines.append(f'      <media:content url="{escape(item["image"])}" medium="image" />')
    lines.append('    </item>')

lines.extend(['  </channel>', '</rss>'])
Path('feed.xml').write_text('\n'.join(lines) + '\n', encoding='utf-8')
print(f'RSS feed rebuilt with {len(articles)} articles')
