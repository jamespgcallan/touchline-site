from pathlib import Path
import re

# Keep the visible desktop navigation deliberately small. Secondary sections are
# exposed through the shared More menu in mobile-nav.js and through page content.
CANONICAL_NAV = (
    '<nav class="links" aria-label="Primary navigation">'
    '<a href="index.html#latest">Latest</a>'
    '<a href="league-of-ireland-analysis.html">Irish Football</a>'
    '<a href="touchline-tactics.html">Tactics</a>'
    '<a href="archive.html">Archive</a>'
    '<a href="about.html">About</a>'
    '</nav>'
)
SCRIPT_TAG = '<script src="mobile-nav.js?v=20260912-clean"></script>'

changed = []
for path in Path('.').glob('*.html'):
    text = path.read_text(encoding='utf-8')
    updated = text

    # Standardise only the nav inside the page header, leaving any article or
    # footer navigation untouched.
    header_match = re.search(r'<header\b[^>]*>.*?</header>', updated, flags=re.S | re.I)
    if header_match:
        header = header_match.group(0)
        new_header = re.sub(
            r'<nav(?:\s+class="links")?[^>]*>.*?</nav>',
            CANONICAL_NAV,
            header,
            count=1,
            flags=re.S | re.I,
        )
        updated = updated[:header_match.start()] + new_header + updated[header_match.end():]

    # Ensure every page has the same Subscribe CTA wording and target.
    updated = re.sub(
        r'<a\s+class="nav-cta"[^>]*>.*?</a>',
        '<a class="nav-cta" href="index.html#subscribe">Subscribe</a>',
        updated,
        count=1,
        flags=re.S | re.I,
    )

    # Ensure exactly one shared navigation script is loaded at the end of every page.
    updated = re.sub(r'<script src="mobile-nav\.js(?:\?[^\"]*)?"(?: defer)?></script>', '', updated)
    if '</body>' in updated:
        updated = updated.replace('</body>', SCRIPT_TAG + '\n</body>', 1)

    if updated != text:
        path.write_text(updated, encoding='utf-8')
        changed.append(str(path))

print('Updated navigation:', ', '.join(changed) if changed else 'none')