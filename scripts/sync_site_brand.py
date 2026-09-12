from pathlib import Path
import json
import re

SITE_NAME = 'Touchline Sport'
BASE_URL = 'https://touchlinesport.net/'

# Compact titles make the main site sections easier for Google and readers to understand.
PAGE_TITLES = {
    'index.html': 'Touchline Sport',
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

    # Use the public site name consistently in visible site chrome and metadata.
    text = text.replace('Touchline Studios', SITE_NAME)

    if path.name in PAGE_TITLES:
        text = re.sub(r'<title>.*?</title>', f'<title>{PAGE_TITLES[path.name]}</title>', text, count=1, flags=re.S | re.I)

    if path.name == 'index.html':
        text = re.sub(r'<meta property="og:title" content="[^"]*">', f'<meta property="og:title" content="{SITE_NAME}">', text, count=1)
        text = re.sub(r'<meta name="twitter:title" content="[^"]*">', f'<meta name="twitter:title" content="{SITE_NAME}">', text, count=1)
        text = re.sub(r'<meta property="og:site_name" content="[^"]*">', f'<meta property="og:site_name" content="{SITE_NAME}">', text, count=1)

        # Make the Organization and WebSite nodes use only the current public brand.
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
