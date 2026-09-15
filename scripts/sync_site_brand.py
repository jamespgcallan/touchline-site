from pathlib import Path
import json
import re

SITE_NAME = 'Touchline Sport'
BASE_URL = 'https://touchlinesport.net/'

# Compact titles make the main site sections easier for Google and readers to understand.
# Touchline Sport remains the publication/search name. Touchline Studios may appear in
# commercial copy, so do not globally replace every occurrence of that phrase.
PAGE_TITLES = {
    'index.html': 'Touchline Sport',
    'latest-news.html': 'Latest Football News & Analysis | Touchline Sport',
    'archive.html': 'Archive | Touchline Sport',
    'league-of-ireland-analysis.html': 'Irish Football | Touchline Sport',
    'touchline-tactics.html': 'Touchline Tactics | Touchline Sport',
    'football-club-strategy.html': 'Football Club Strategy | Touchline Sport',
    'scouting.html': 'Scouting Reports | Touchline Sport',
    'graphics.html': 'Football Graphics | Touchline Sport',
    'about.html': 'About | Touchline Sport',
    'james-callan.html': 'James Callan | Touchline Sport',
    'editorial-policy.html': 'Editorial Policy | Touchline Sport',
    'contact.html': 'Contact | Touchline Sport',
    'work-with-me.html': 'Work With Me | Touchline Sport',
}

changed = []
for path in Path('.').glob('*.html'):
    text = path.read_text(encoding='utf-8')
    original = text

    # Keep the visible masthead/publication chrome on Touchline Sport without
    # erasing intentional Touchline Studios references in commercial sections.
    header_match = re.search(r'<header\b[^>]*>.*?</header>', text, flags=re.S | re.I)
    if header_match:
        header = header_match.group(0).replace('Touchline Studios', SITE_NAME)
        text = text[:header_match.start()] + header + text[header_match.end():]

    # Search/social site-name signals should always identify the publication as Touchline Sport.
    text = re.sub(
        r'<meta property="og:site_name" content="[^"]*">',
        f'<meta property="og:site_name" content="{SITE_NAME}">',
        text,
        flags=re.I,
    )

    if path.name in PAGE_TITLES:
        text = re.sub(r'<title>.*?</title>', f'<title>{PAGE_TITLES[path.name]}</title>', text, count=1, flags=re.S | re.I)

    if path.name == 'index.html':
        text = re.sub(r'<meta property="og:title" content="[^"]*">', f'<meta property="og:title" content="{SITE_NAME}">', text, count=1)
        text = re.sub(r'<meta name="twitter:title" content="[^"]*">', f'<meta name="twitter:title" content="{SITE_NAME}">', text, count=1)

        # Make the Organization and WebSite nodes use only the publication/search brand.
        scripts = list(re.finditer(r'(<script\s+type=["\']application/ld\+json["\']\s*>)(.*?)(</script>)', text, re.S | re.I))
        replacements = []
        saw_website = False
        for match in scripts:
            raw = match.group(2)
            try:
                data = json.loads(raw.strip())
            except Exception:
                continue
            if not isinstance(data, dict):
                continue
            schema_type = data.get('@type')
            if schema_type == 'Organization':
                data['name'] = SITE_NAME
                data.pop('alternateName', None)
            elif schema_type == 'WebSite':
                saw_website = True
                data['name'] = SITE_NAME
                data['alternateName'] = ['Touchline', 'touchlinesport.net']
                data['url'] = BASE_URL
            else:
                continue
            replacement = match.group(1) + '\n' + json.dumps(data, ensure_ascii=False, indent=2) + '\n' + match.group(3)
            replacements.append((match.start(), match.end(), replacement))

        for start, end, replacement in reversed(replacements):
            text = text[:start] + replacement + text[end:]

        if not saw_website:
            website_schema = '''<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "WebSite",
  "name": "Touchline Sport",
  "alternateName": ["Touchline", "touchlinesport.net"],
  "url": "https://touchlinesport.net/"
}
</script>
'''
            marker = '<link rel="preconnect" href="https://fonts.googleapis.com">'
            if marker in text:
                text = text.replace(marker, website_schema + marker, 1)
            else:
                text = text.replace('</head>', website_schema + '</head>', 1)

    if text != original:
        path.write_text(text, encoding='utf-8')
        changed.append(path.name)

print('Brand/site-name sync:', ', '.join(changed) if changed else 'none')
