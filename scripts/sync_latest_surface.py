from pathlib import Path
import html
import re

LATEST_PATH = Path('latest-news.html')
INDEX_PATH = Path('index.html')


def clean(value: str) -> str:
    return re.sub(r'\s+', ' ', html.unescape(re.sub(r'<[^>]+>', '', value or ''))).strip()


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

if not all([href_match, section_match, title_match, desc_match]):
    raise SystemExit('Could not parse latest story details')

href = html.unescape(href_match.group(1))
image = html.unescape(img_match.group(1)) if img_match else ''
section = clean(section_match.group(1))
title = clean(title_match.group(1))
description = clean(desc_match.group(1))

if latest != original_latest:
    LATEST_PATH.write_text(latest, encoding='utf-8')

index = INDEX_PATH.read_text(encoding='utf-8')
original_index = index

# The homepage's "Read the latest" button must always point at the newest published article.
index = re.sub(
    r'<a class="btn-primary" href="[^"]+">Read the latest →</a>',
    f'<a class="btn-primary" href="{html.escape(href, quote=True)}">Read the latest →</a>',
    index,
    count=1,
    flags=re.I,
)

featured = (
    '<div class="featured"><div>'
    f'<span class="pill">Latest · {html.escape(section)}</span>'
    f'<h2>{html.escape(title)}</h2>'
    f'<p>{html.escape(description)}</p>'
    f'<a class="read" href="{html.escape(href, quote=True)}">Read the piece '
    '<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">'
    '<path d="M5 12h14M13 5l7 7-7 7"/></svg></a>'
    '</div>'
    f'<div class="featured-art" style="background-image:url(\'{html.escape(image, quote=True)}\');background-size:cover;background-repeat:no-repeat;background-position:center;"></div>'
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
    escaped_image = html.escape(image, quote=True)
    index = re.sub(
        r'<meta property="og:image" content="[^"]*">',
        f'<meta property="og:image" content="{escaped_image}">',
        index,
        count=1,
        flags=re.I,
    )
    index = re.sub(
        r'<meta name="twitter:image" content="[^"]*">',
        f'<meta name="twitter:image" content="{escaped_image}">',
        index,
        count=1,
        flags=re.I,
    )

if index != original_index:
    INDEX_PATH.write_text(index, encoding='utf-8')

print(f'Latest surface synced to: {title}')
