from pathlib import Path
import html
import re

LATEST = Path('latest-news.html')
INDEX = Path('index.html')
ARCHIVE = Path('archive.html')

COUNTRY_HINTS = {
    'England/UK': (
        'manchester united', 'man utd', 'brighton', 'newcastle', 'chelsea', 'arsenal',
        'tottenham', 'aston villa', 'leeds', 'west ham', 'wrexham', 'aldershot',
        'premier league', 'carabao cup', 'fa cup',
    ),
    'Italy': ('inter', 'ac milan', 'juventus', 'serie a', 'como', 'napoli', 'roma', 'lazio'),
    'Germany': ('bayern', 'bundesliga', 'kaiserslautern', 'dortmund', 'leverkusen'),
    'Spain': ('real madrid', 'barcelona', 'la liga', 'atletico madrid'),
    'France': ('psg', 'paris saint-germain', 'ligue 1', 'marseille', 'lyon'),
    'Poland': ('legia warsaw', 'ekstraklasa', 'polish football', 'łazienkowska'),
}


def clean(value):
    return re.sub(r'\s+', ' ', html.unescape(re.sub(r'<[^>]+>', '', value or ''))).strip()


def esc(value):
    return html.escape(value or '', quote=True)


def parse_stories(text):
    stories = []
    for match in re.finditer(r'<article class="story">(.*?)</article>', text, re.S | re.I):
        block = match.group(1)
        href = re.search(r'<a class="story-image" href="([^"]+)"', block, re.I)
        image = re.search(r'<img src="([^"]+)"', block, re.I)
        section = re.search(r'<div class="story-kicker">(.*?)</div>', block, re.S | re.I)
        title = re.search(r'<h2><a href="[^"]+">(.*?)</a></h2>', block, re.S | re.I)
        description = re.search(r'<p>(.*?)</p>', block, re.S | re.I)
        meta = re.search(r'<div class="story-meta">(.*?)</div>', block, re.S | re.I)
        if not all([href, section, title, description, meta]):
            continue
        stories.append({
            'href': html.unescape(href.group(1)),
            'image': html.unescape(image.group(1)) if image else '',
            'section': clean(section.group(1)),
            'title': clean(title.group(1)),
            'description': clean(description.group(1)),
            'meta': clean(meta.group(1)),
        })
    return stories


def home_card(item):
    parts = [p.strip() for p in item['meta'].split('·')]
    date = parts[0] if parts else ''
    read_time = parts[1] if len(parts) > 1 else '5 min read'
    return (
        f'<a class="card" href="{esc(item["href"])}">'
        f'<div class="card-art" style="background-image:url(\'{esc(item["image"])}\');background-size:cover;background-position:center;"></div>'
        f'<div class="card-body"><span class="pill">World</span><h3>{html.escape(item["title"])}</h3>'
        f'<p>{html.escape(item["description"])}</p><div class="meta"><span>{html.escape(date)}</span>'
        f'<span class="dot"></span><span>{html.escape(read_time)}</span></div></div></a>'
    )


def archive_item(item):
    parts = [p.strip() for p in item['meta'].split('·')]
    date_label = parts[0] if parts else ''
    try:
        from datetime import datetime
        date_iso = datetime.strptime(date_label, '%d %b %Y').date().isoformat()
    except Exception:
        date_iso = ''
    return (
        '<li class="arch-item">\n'
        f'          <a href="{esc(item["href"])}">\n'
        '            <span class="arch-copy">\n'
        f'              <span class="arch-title">{html.escape(item["title"])}</span>\n'
        f'              <span class="arch-description">{html.escape(item["description"])}</span>\n'
        '            </span>\n'
        '            <span class="arch-meta">\n'
        f'              <time class="arch-date" datetime="{esc(date_iso)}">{html.escape(date_label)}</time>\n'
        '              <span class="arch-arrow">→</span>\n'
        '            </span>\n'
        '          </a>\n'
        '        </li>\n'
    )


def infer_country(item):
    source = Path(item['href'])
    source_text = source.read_text(encoding='utf-8') if source.exists() else ''
    explicit = re.search(r'<meta\s+name=["\']touchline:archive-country["\']\s+content=["\']([^"\']+)', source_text, re.I)
    if explicit:
        return html.unescape(explicit.group(1)).strip()
    haystack = clean(item['title'] + ' ' + item['description'] + ' ' + source_text[:12000]).lower()
    for country, hints in COUNTRY_HINTS.items():
        if any(hint in haystack for hint in hints):
            return country
    return ''


if not LATEST.exists() or not INDEX.exists() or not ARCHIVE.exists():
    raise SystemExit('Required publication surfaces are missing')

stories = parse_stories(LATEST.read_text(encoding='utf-8'))
world_stories = [s for s in stories if s['section'].strip().lower() in {'world', 'world football'}]
if not world_stories:
    print('World surface sync: no World stories found')
    raise SystemExit(0)

# Keep the homepage World grid genuinely newest-first, rather than leaving the featured story out of the grid.
index = INDEX.read_text(encoding='utf-8')
original_index = index
start = index.find('<div class="wrap category-block" id="world">')
end = index.find('<div class="wrap category-block" id="scouting">', start)

archive = ARCHIVE.read_text(encoding='utf-8')
original_archive = archive
world_start = archive.find('<div class="wrap category-block" id="world">')
world_end = archive.find('<div class="wrap category-block" id="everything-else">', world_start)

# Add the newest World article to the correct country group when that group can be identified.
latest_world = world_stories[0]
country = infer_country(latest_world)
if world_start >= 0 and world_end >= 0 and country:
    world_block = archive[world_start:world_end]
    already_present = f'href="{latest_world["href"]}"' in world_block
    world_block = re.sub(
        rf'<li class="arch-item">\s*<a href="{re.escape(latest_world["href"])}">.*?</li>\s*',
        '',
        world_block,
        flags=re.S | re.I,
    )
    country_title = re.search(
        rf'<div class="country-block[^\"]*">.*?<h4 class="country-title">{re.escape(country)}</h4>.*?</div>\s*</div>\s*</div>',
        world_block,
        flags=re.S | re.I,
    )
    if country_title:
        country_block = country_title.group(0)
        marker = '<ul class="arch-list">'
        if marker in country_block:
            country_block = country_block.replace(marker, marker + archive_item(latest_world), 1)
            country_count = len(re.findall(r'<li class="arch-item">', country_block))
            country_block = re.sub(
                r'<span class="country-count">\d+ pieces</span>',
                f'<span class="country-count">{country_count} pieces</span>',
                country_block,
                count=1,
            )
            world_block = world_block[:country_title.start()] + country_block + world_block[country_title.end():]
            world_count = len(re.findall(r'<li class="arch-item">', world_block))
            world_block = re.sub(
                r'<span class="category-count">\d+ pieces</span>',
                f'<span class="category-count">{world_count} pieces</span>',
                world_block,
                count=1,
            )
            archive = archive[:world_start] + world_block + archive[world_end:]
            total_count = len(re.findall(r'<li class="arch-item">', archive))
            archive = re.sub(
                r'<span class="pill">\d+ pieces and counting</span>',
                f'<span class="pill">{total_count} pieces and counting</span>',
                archive,
                count=1,
            )
            if already_present:
                print(f'World archive refreshed: {latest_world["title"]}')

if archive != original_archive:
    ARCHIVE.write_text(archive, encoding='utf-8')

# Use the archive's real World count on the homepage and display the three newest World stories.
world_count_match = re.search(
    r'<div class="wrap category-block" id="world">.*?<span class="category-count">(\d+) pieces</span>',
    archive,
    flags=re.S | re.I,
)
world_count = world_count_match.group(1) if world_count_match else None
if start >= 0 and end >= 0:
    old = index[start:end]
    head_match = re.search(r'^(.*?<div class="grid">)', old, re.S | re.I)
    if head_match:
        head = head_match.group(1)
        if world_count:
            head = re.sub(r'\d+ pieces · View all →', f'{world_count} pieces · View all →', head, count=1)
        cards = ''.join(home_card(item) for item in world_stories[:3])
        index = index[:start] + head + cards + '</div></div>\n' + index[end:]

if index != original_index:
    INDEX.write_text(index, encoding='utf-8')

print(f'World surface synced to: {latest_world["title"]} ({country or "archive country unresolved"})')
