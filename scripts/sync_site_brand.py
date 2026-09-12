from pathlib import Path
import json
import re

SITE_NAME = 'Touchline Sport'
ALT_SITE_NAME = 'Touchline Studios'
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

    # Keep page-level Open Graph / X titles tidy on the homepage.
    if path.name == 'index.html':
        text = re.sub(r'<meta property="og:title" content="[^"]*">', f'<meta property="og:title" content="{SITE_NAME}">', text, count=1)
        text = re.sub(r'<meta name="twitter:title" content="[^"]*">', f'<meta name="twitter:title" content="{SITE_NAME}">', text, count=1)
        text = re.sub(r'<meta property="og:site_name" content="[^"]*">', f'<meta property="og:site_name" content="{SITE_NAME}">', text, count=1)

        # Make the Organization node match the preferred public name while retaining the old brand as an alternate.
        scripts = re.findall(r'(<script\s+type=["\']application/ld\+json["\']\s*>)(.*?)(</script>)', text, re.S | re.I)
        for full_open, raw, full_close in scripts:
            try:
                data = json.loads(raw.strip())
            except Exception:
                continue
            if isinstance(data, dict) and data.get('@type') == 'Organization':
                data['name'] = SITE_NAME
                data['alternateName'] = ALT_SITE_NAME
                replacement = full_open + '\n' + json.dumps(data, ensure_ascii=False, indent=2) + '\n' + full_close
                text = text.replace(full_open + raw + full_close, replacement, 1)
                break

        # Google says WebSite structured data on the domain homepage is the strongest explicit site-name signal.
        if '"@type": "WebSite"' not in text and '"@type":"WebSite"' not in text:
            website_schema = '''<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "WebSite",
  "name": "Touchline Sport",
  "alternateName": ["Touchline", "Touchline Studios", "touchlinesport.net"],
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
