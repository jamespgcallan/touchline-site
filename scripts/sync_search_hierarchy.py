from pathlib import Path
import html
import json
import re

BASE_URL = 'https://touchlinesport.net/'

SECTION_SPECS = {
    'league-of-ireland-analysis.html': {
        'label': 'Irish Football',
        'title': 'Irish Football | Touchline Sport',
        'h1': 'Irish Football',
        'description': 'Independent League of Ireland analysis from Touchline Sport, covering academies, player development, recruitment, ownership, finance and club strategy.',
        'schema_type': 'CollectionPage',
    },
    'touchline-tactics.html': {
        'label': 'Touchline Tactics',
        'title': 'Touchline Tactics | Touchline Sport',
        'h1': 'Touchline Tactics',
        'description': 'Long-form tactical analysis from Touchline Sport, breaking down how teams build, press, defend and create advantages.',
        'schema_type': 'CollectionPage',
    },
    'football-club-strategy.html': {
        'label': 'Football Club Strategy',
        'title': 'Football Club Strategy | Touchline Sport',
        'h1': 'Football Club Strategy',
        'description': 'Football club strategy from Touchline Sport, covering ownership, recruitment, academies, revenue, squad building and long-term planning.',
        'schema_type': 'CollectionPage',
    },
    'scouting.html': {
        'label': 'Scouting Reports',
        'title': 'Scouting Reports | Touchline Sport',
        'h1': 'Scouting Reports',
        'description': 'Independent scouting reports from Touchline Sport, covering player profiles, squad needs, recruitment targets and development pathways.',
        'schema_type': 'CollectionPage',
    },
    'archive.html': {
        'label': 'Archive',
        'title': 'Archive | Touchline Sport',
        'h1': 'Archive',
        'description': 'Browse the Touchline Sport archive of Irish football, tactics, club strategy, scouting and football business features.',
        'schema_type': 'CollectionPage',
    },
    'about.html': {
        'label': 'About',
        'title': 'About | Touchline Sport',
        'h1': 'About',
        'description': 'About Touchline Sport and James Callan, with independent football analysis focused on Irish football, tactics, scouting and club strategy.',
        'schema_type': 'AboutPage',
    },
}

LINK_NAMES = {
    'league-of-ireland-analysis.html': 'Irish Football',
    'touchline-tactics.html': 'Touchline Tactics',
    'football-club-strategy.html': 'Football Club Strategy',
    'scouting.html': 'Scouting Reports',
    'archive.html': 'Archive',
    'about.html': 'About',
}

NON_ARTICLE_PAGES = {
    'index.html', 'archive.html', 'league-of-ireland-analysis.html', 'touchline-tactics.html',
    'football-club-strategy.html', 'scouting.html', 'graphics.html', 'about.html',
    'james-callan.html', 'editorial-policy.html', 'contact.html', 'work-with-me.html',
}

EXPLORE_BLOCK = '''<!-- TL_EXPLORE_START -->
<nav aria-label="Explore Touchline Sport" style="max-width:1180px;margin:0 auto 26px;padding:0 32px;">
  <div style="font-family:Manrope,Arial,sans-serif;font-weight:800;font-size:15px;margin-bottom:12px;color:inherit;">Explore Touchline Sport</div>
  <div style="display:flex;flex-wrap:wrap;gap:10px 18px;font-family:Inter,Arial,sans-serif;font-size:13px;line-height:1.5;">
    <a href="league-of-ireland-analysis.html">Irish Football</a>
    <a href="touchline-tactics.html">Touchline Tactics</a>
    <a href="football-club-strategy.html">Football Club Strategy</a>
    <a href="scouting.html">Scouting Reports</a>
    <a href="archive.html">Archive</a>
    <a href="about.html">About</a>
  </div>
</nav>
<!-- TL_EXPLORE_END -->'''


def upsert_meta(text, name, content, property_attr=False):
    attr = 'property' if property_attr else 'name'
    pattern = rf'<meta\s+{attr}=["\']{re.escape(name)}["\']\s+content=["\'][^"\']*["\']\s*/?>'
    tag = f'<meta {attr}="{name}" content="{html.escape(content, quote=True)}">'
    if re.search(pattern, text, flags=re.I):
        return re.sub(pattern, tag, text, count=1, flags=re.I)
    return text.replace('</head>', tag + '\n</head>', 1)


def upsert_canonical(text, url):
    tag = f'<link rel="canonical" href="{url}">'
    if re.search(r'<link\s+rel=["\']canonical["\'][^>]*>', text, flags=re.I):
        return re.sub(r'<link\s+rel=["\']canonical["\'][^>]*>', tag, text, count=1, flags=re.I)
    return text.replace('</head>', tag + '\n</head>', 1)


def replace_or_add_page_schema(text, spec, filename):
    schema = {
        '@context': 'https://schema.org',
        '@type': spec['schema_type'],
        '@id': BASE_URL + filename + '#page',
        'name': spec['h1'],
        'url': BASE_URL + filename,
        'description': spec['description'],
        'isPartOf': {'@type': 'WebSite', 'name': 'Touchline Sport', 'url': BASE_URL},
        'publisher': {'@type': 'Organization', 'name': 'Touchline Sport', 'url': BASE_URL},
    }
    rendered = '<script type="application/ld+json">\n' + json.dumps(schema, ensure_ascii=False, indent=2) + '\n</script>'
    pattern = re.compile(r'<script\s+type=["\']application/ld\+json["\']\s*>(.*?)</script>', re.S | re.I)
    matches = list(pattern.finditer(text))
    for match in matches:
        try:
            data = json.loads(match.group(1).strip())
        except Exception:
            continue
        if isinstance(data, dict) and data.get('@type') in ('CollectionPage', 'AboutPage'):
            return text[:match.start()] + rendered + text[match.end():]
    return text.replace('</head>', rendered + '\n</head>', 1)


def clean_text(raw):
    return html.unescape(re.sub(r'<[^>]+>', '', raw)).strip()


def article_title(text, filename):
    match = re.search(r'<h1\b[^>]*>(.*?)</h1>', text, flags=re.S | re.I)
    if match:
        title = clean_text(match.group(1))
        if title:
            return title
    match = re.search(r'<title>(.*?)</title>', text, flags=re.S | re.I)
    if match:
        return clean_text(match.group(1)).split('| Touchline Sport')[0].strip()
    return filename.replace('.html', '').replace('-', ' ').title()


def category_for(filename):
    if filename.startswith('scout-report-'):
        return 'Scouting Reports', 'scouting.html'
    if filename in {'inside-cesc-fabregas-como-game-model.html'}:
        return 'Touchline Tactics', 'touchline-tactics.html'
    if filename in {
        'st-patricks-athletic-shamrock-rovers-ryan-sheridan.html',
        'grow-your-own-loi-academies.html',
        'braywatch-the-seaside-club-bringing-young-talent-back-to-life.html',
    } or 'loi' in filename:
        return 'Irish Football', 'league-of-ireland-analysis.html'
    if filename in {'chelsea-transfer-machine-2026.html', 'aldershot-town-complete-rebuild.html'}:
        return 'Football Club Strategy', 'football-club-strategy.html'
    return 'Archive', 'archive.html'


def breadcrumb_schema(title, category_label, category_href, filename):
    data = {
        '@context': 'https://schema.org',
        '@type': 'BreadcrumbList',
        'itemListElement': [
            {'@type': 'ListItem', 'position': 1, 'name': 'Touchline Sport', 'item': BASE_URL},
            {'@type': 'ListItem', 'position': 2, 'name': category_label, 'item': BASE_URL + category_href},
            {'@type': 'ListItem', 'position': 3, 'name': title, 'item': BASE_URL + filename},
        ],
    }
    return '<script type="application/ld+json">\n' + json.dumps(data, ensure_ascii=False, indent=2) + '\n</script>'


def remove_breadcrumb_schema(text):
    pattern = re.compile(r'<script\s+type=["\']application/ld\+json["\']\s*>(.*?)</script>', re.S | re.I)
    for match in reversed(list(pattern.finditer(text))):
        try:
            data = json.loads(match.group(1).strip())
        except Exception:
            continue
        if isinstance(data, dict) and data.get('@type') == 'BreadcrumbList':
            text = text[:match.start()] + text[match.end():]
    return text


changed = []
for path in Path('.').glob('*.html'):
    text = path.read_text(encoding='utf-8')
    original = text
    filename = path.name

    # Normalise simple links to the six main sections so Google sees the same labels everywhere.
    for href, label in LINK_NAMES.items():
        pattern = rf'(<a\b[^>]*href=["\'](?:\./)?{re.escape(href)}["\'][^>]*>)([^<>]*)(</a>)'
        text = re.sub(pattern, lambda m: m.group(1) + label + m.group(3), text, flags=re.I)

    # Make the six priority section pages structurally consistent.
    if filename in SECTION_SPECS:
        spec = SECTION_SPECS[filename]
        text = re.sub(r'<title>.*?</title>', f'<title>{spec["title"]}</title>', text, count=1, flags=re.S | re.I)
        text = upsert_meta(text, 'description', spec['description'])
        text = upsert_canonical(text, BASE_URL + filename)
        text = re.sub(r'<h1\b([^>]*)>.*?</h1>', rf'<h1\1>{spec["h1"]}</h1>', text, count=1, flags=re.S | re.I)
        text = replace_or_add_page_schema(text, spec, filename)

    # Add a shared Explore block inside the footer so the priority sections receive
    # strong, consistent internal links from every page.
    text = re.sub(r'\s*<!-- TL_EXPLORE_START -->.*?<!-- TL_EXPLORE_END -->\s*', '\n', text, flags=re.S)
    footer_match = re.search(r'<footer\b[^>]*>', text, flags=re.I)
    if footer_match:
        insert_at = footer_match.end()
        text = text[:insert_at] + '\n' + EXPLORE_BLOCK + '\n' + text[insert_at:]
    elif '</body>' in text:
        text = text.replace('</body>', EXPLORE_BLOCK + '\n</body>', 1)

    # Give every article a visible hierarchy trail and BreadcrumbList structured data.
    text = re.sub(r'\s*<!-- TL_BREADCRUMB_START -->.*?<!-- TL_BREADCRUMB_END -->\s*', '\n', text, flags=re.S)
    text = remove_breadcrumb_schema(text)
    if filename not in NON_ARTICLE_PAGES:
        title = article_title(text, filename)
        category_label, category_href = category_for(filename)
        crumbs = (
            '<!-- TL_BREADCRUMB_START -->\n'
            '<nav aria-label="Breadcrumb" style="max-width:1120px;margin:0 auto;padding:16px 32px 0;'
            'font-family:\'IBM Plex Mono\',monospace;font-size:11.5px;line-height:1.5;color:#6b5d4d;">'
            '<a href="index.html" style="color:inherit;">Touchline Sport</a>'
            '<span aria-hidden="true" style="padding:0 8px;">›</span>'
            f'<a href="{category_href}" style="color:inherit;">{html.escape(category_label)}</a>'
            '<span aria-hidden="true" style="padding:0 8px;">›</span>'
            f'<span aria-current="page">{html.escape(title)}</span>'
            '</nav>\n<!-- TL_BREADCRUMB_END -->'
        )
        header_close = re.search(r'</header>', text, flags=re.I)
        if header_close:
            text = text[:header_close.end()] + '\n' + crumbs + text[header_close.end():]
        elif '<body' in text:
            body_open = re.search(r'<body\b[^>]*>', text, flags=re.I)
            if body_open:
                text = text[:body_open.end()] + '\n' + crumbs + text[body_open.end():]
        text = text.replace('</head>', breadcrumb_schema(title, category_label, category_href, filename) + '\n</head>', 1)

    if text != original:
        path.write_text(text, encoding='utf-8')
        changed.append(filename)

print('Search hierarchy sync:', ', '.join(changed) if changed else 'none')
