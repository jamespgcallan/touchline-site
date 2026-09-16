from pathlib import Path
from datetime import datetime
import html
import re

LATEST_PATH = Path('latest-news.html')
INDEX_PATH = Path('index.html')
ARCHIVE_PATH = Path('archive.html')
IRISH_PATH = Path('league-of-ireland-analysis.html')


def clean(value: str) -> str:
    return re.sub(r'\s+', ' ', html.unescape(re.sub(r'<[^>]+>', '', value or ''))).strip()


def escaped(value: str) -> str:
    return html.escape(value or '', quote=True)


def latest_home_card(href, image, title, description, date_label, read_time):
    return (
        f'<a class="card" href="{escaped(href)}">'
        f'<div class="card-art" style="background-image:url(\'{escaped(image)}\');background-size:cover;background-position:center;"></div>'
        '<div class="card-body"><span class="pill">Ireland</span>'
        f'<h3>{html.escape(title)}</h3><p>{html.escape(description)}</p>'
        f'<div class="meta"><span>{html.escape(date_label)}</span><span class="dot"></span><span>{html.escape(read_time)}</span></div>'
        '</div></a>'
    )


def latest_irish_card(href, image, section, title, description):
    return (
        f'<a class="card" href="{escaped(href)}">'
        f'<div class="art" style="background-image:url(\'{escaped(image)}\')"></div>'
        f'<div class="body"><small>{html.escape(section)}</small>'
        f'<h2>{html.escape(title)}</h2><p>{html.escape(description)}</p></div></a>'
    )


def archive_item(href, title, description, date_label, date_iso):
    return (
        '<li class="arch-item">\n'
        f'          <a href="{escaped(href)}">\n'
        '            <span class="arch-copy">\n'
        f'              <span class="arch-title">{html.escape(title)}</span>\n'
        f'              <span class="arch-description">{html.escape(description)}</span>\n'
        '            </span>\n'
        '            <span class="arch-meta">\n'
        f'              <time class="arch-date" datetime="{escaped(date_iso)}">{html.escape(date_label)}</time>\n'
        '              <span class="arch-arrow">→</span>\n'
        '            </span>\n'
        '          </a>\n'
        '        </li>\n'
    )


if not LATEST_PATH.exists() or not INDEX_PATH.exists():
    raise SystemExit('latest-news.html or index.html missing')

latest = LATEST_PATH.read_text(encoding='utf-8')
original_latest = latest

# Keep RSS available to feed readers and aggregators, but do not make it a prominent reader CTA.
latest = re.sub(
    r'<div class="hero-actions">\s*<a href="feed\.xml">Follow the RSS feed</a>\s*(<a href="archive\.html">.*?</a>)\s*</div>',
    r'<div class="hero-actions">\1</div>',
    latest,
    count=1,
    flags=re.S | re.I,
)

first_story = re.search(r'<article class="story">(.*?)</article>', latest, flags=re.S | re.I)
if not first_story:
    raise SystemExit('Could not find first latest story')

block = first_story.group(1)
href_match = re.search(r'<a class="story-image" href="([^"]+)"', block, flags=re.I)
img_match = re.search(r'<img src="([^"]+)"', block, flags=re.I)
section_match = re.search(r'<div class="story-kicker">(.*?)</div>', block, flags=re.S | re.I)
title_match = re.search(r'<h2><a href="[^"]+">(.*?)</a></h2>', block, flags=re.S | re.I)
desc_match = re.search(r'<p>(.*?)</p>', block, flags=re.S | re.I)
meta_match = re.search(r'<div class="story-meta">(.*?)</div>', block, flags=re.S | re.I)

if not all([href_match, section_match, title_match, desc_match, meta_match]):
    raise SystemExit('Could not parse latest story details')

href = html.unescape(href_match.group(1))
image = html.unescape(img_match.group(1)) if img_match else ''
section = clean(section_match.group(1))
title = clean(title_match.group(1))
description = clean(desc_match.group(1))
meta = clean(meta_match.group(1))
meta_parts = [part.strip() for part in meta.split('·')]
date_label = meta_parts[0] if meta_parts else ''
read_time = meta_parts[1] if len(meta_parts) > 1 else '5 min read'
try:
    date_iso = datetime.strptime(date_label, '%d %b %Y').date().isoformat()
except Exception:
    date_iso = ''

if latest != original_latest:
    LATEST_PATH.write_text(latest, encoding='utf-8')

index = INDEX_PATH.read_text(encoding='utf-8')
original_index = index

# The homepage's "Read the latest" button must always point at the newest published article.
index = re.sub(
    r'<a class="btn-primary" href="[^"]+">Read the latest →</a>',
    f'<a class="btn-primary" href="{escaped(href)}">Read the latest →</a>',
    index,
    count=1,
    flags=re.I,
)

featured = (
    '<div class="featured"><div>'
    f'<span class="pill">Latest · {html.escape(section)}</span>'
    f'<h2>{html.escape(title)}</h2>'
    f'<p>{html.escape(description)}</p>'
    f'<a class="read" href="{escaped(href)}">Read the piece '
    '<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">'
    '<path d="M5 12h14M13 5l7 7-7 7"/></svg></a>'
    '</div>'
    f'<div class="featured-art" style="background-image:url(\'{escaped(image)}\');background-size:cover;background-repeat:no-repeat;background-position:center;"></div>'
    '</div>'
)

index, replacements = re.subn(
    r'<div class="featured"><div><span class="pill">.*?</span><h2>.*?</h2><p>.*?</p><a class="read" href="[^"]+">Read the piece.*?</a></div><div class="featured-art" style="[^"]*"></div></div>',
    featured,
    index,
    count=1,
    flags=re.S | re.I,
)

if replacements == 0:
    raise SystemExit('Could not update homepage featured story')

if image:
    escaped_image = escaped(image)
    index = re.sub(r'<meta property="og:image" content="[^"]*">', f'<meta property="og:image" content="{escaped_image}">', index, count=1, flags=re.I)
    index = re.sub(r'<meta name="twitter:image" content="[^"]*">', f'<meta name="twitter:image" content="{escaped_image}">', index, count=1, flags=re.I)

is_irish_story = 'ireland' in section.lower() or 'irish' in section.lower()
irish_count = None

if is_irish_story and ARCHIVE_PATH.exists():
    archive = ARCHIVE_PATH.read_text(encoding='utf-8')
    original_archive = archive
    start = archive.find('<div class="wrap category-block" id="irish">')
    end = archive.find('<div class="wrap category-block" id="world">', start)
    if start >= 0 and end >= 0:
        irish_block = archive[start:end]
        existed = f'href="{href}"' in irish_block
        irish_block = re.sub(rf'<li class="arch-item">\s*<a href="{re.escape(href)}">.*?</li>\s*', '', irish_block, flags=re.S | re.I)
        marker = '<ul class="arch-list">'
        irish_block = irish_block.replace(marker, marker + archive_item(href, title, description, date_label, date_iso), 1)
        irish_count = len(re.findall(r'<li class="arch-item">', irish_block))
        irish_block = re.sub(r'<span class="category-count">\d+ pieces</span>', f'<span class="category-count">{irish_count} pieces</span>', irish_block, count=1)
        archive = archive[:start] + irish_block + archive[end:]
        if not existed:
            archive = re.sub(r'<span class="pill">(\d+) pieces and counting</span>', lambda m: f'<span class="pill">{int(m.group(1)) + 1} pieces and counting</span>', archive, count=1)
    if archive != original_archive:
        ARCHIVE_PATH.write_text(archive, encoding='utf-8')

if is_irish_story:
    irish_home = re.search(r'(<div class="wrap category-block" id="irish">.*?<div class="grid">)(.*?)(</div></div>\s*<div class="wrap category-block" id="world">)', index, flags=re.S | re.I)
    if irish_home:
        cards = re.findall(r'<a class="card".*?</a>', irish_home.group(2), flags=re.S | re.I)
        cards = [card for card in cards if f'href="{href}"' not in card]
        head = irish_home.group(1)
        if irish_count is not None:
            head = re.sub(r'\d+ pieces · View all →', f'{irish_count} pieces · View all →', head, count=1)
        new_grid = head + latest_home_card(href, image, title, description, date_label, read_time) + ''.join(cards[:4]) + irish_home.group(3)
        index = index[:irish_home.start()] + new_grid + index[irish_home.end():]

    if IRISH_PATH.exists():
        irish_page = IRISH_PATH.read_text(encoding='utf-8')
        original_irish_page = irish_page
        if image:
            irish_page = re.sub(r'<meta property="og:image" content="[^"]*">', f'<meta property="og:image" content="{escaped(image)}">', irish_page, count=1, flags=re.I)
        grid_match = re.search(r'(<h2>Featured analysis</h2><div class="grid">)(.*?)(</div><div class="note">)', irish_page, flags=re.S | re.I)
        if grid_match:
            cards = re.findall(r'<a class="card".*?</a>', grid_match.group(2), flags=re.S | re.I)
            cards = [card for card in cards if f'href="{href}"' not in card]
            new_grid = grid_match.group(1) + latest_irish_card(href, image, section, title, description) + ''.join(cards[:7]) + grid_match.group(3)
            irish_page = irish_page[:grid_match.start()] + new_grid + irish_page[grid_match.end():]
        if irish_page != original_irish_page:
            IRISH_PATH.write_text(irish_page, encoding='utf-8')

if index != original_index:
    INDEX_PATH.write_text(index, encoding='utf-8')

print(f'Latest surface synced to: {title}')
