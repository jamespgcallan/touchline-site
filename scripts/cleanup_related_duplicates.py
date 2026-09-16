from pathlib import Path
import re

# Some older article pages already contained a hand-added "More from Touchline"
# block before sync_publication_discovery.py began managing the same component.
# Preserve the single managed TL_RELATED block/style and remove any legacy copies.

RELATED_BLOCK_RE = re.compile(
    r'\s*<!-- TL_RELATED_START -->.*?<!-- TL_RELATED_END -->\s*',
    re.S | re.I,
)
RELATED_STYLE_RE = re.compile(
    r'\s*<!-- TL_RELATED_STYLE_START -->.*?<!-- TL_RELATED_STYLE_END -->\s*',
    re.S | re.I,
)
LEGACY_BLOCK_RE = re.compile(
    r'\s*<section\b[^>]*class=["\'][^"\']*\btl-related\b[^"\']*["\'][^>]*>.*?</section>\s*',
    re.S | re.I,
)
STYLE_TAG_RE = re.compile(r'\s*<style\b[^>]*>.*?</style>\s*', re.S | re.I)

BLOCK_TOKEN = '__TOUCHLINE_MANAGED_RELATED_BLOCK__'
STYLE_TOKEN = '__TOUCHLINE_MANAGED_RELATED_STYLE__'

changed = []

for path in Path('.').glob('*.html'):
    text = path.read_text(encoding='utf-8')
    original = text

    managed_blocks = RELATED_BLOCK_RE.findall(text)
    managed_styles = RELATED_STYLE_RE.findall(text)

    # Publication discovery should already leave one managed block/style. If a
    # page somehow contains more than one, preserve only the final generated copy.
    managed_block = managed_blocks[-1].strip() if managed_blocks else ''
    managed_style = managed_styles[-1].strip() if managed_styles else ''

    text = RELATED_BLOCK_RE.sub('\n', text)
    text = RELATED_STYLE_RE.sub('\n', text)

    if managed_block:
        # Put the managed component aside while removing unmarked legacy copies.
        foot = re.search(r'<div\s+class=["\']article-foot-nav["\']', text, re.I)
        if foot:
            text = text[:foot.start()] + BLOCK_TOKEN + '\n    ' + text[foot.start():]
        elif '</article>' in text:
            text = text.replace('</article>', BLOCK_TOKEN + '\n</article>', 1)

    # Remove any older unmarked copy of the component.
    text = LEGACY_BLOCK_RE.sub('\n', text)

    if managed_style:
        text = text.replace('</head>', STYLE_TOKEN + '\n</head>', 1)

    # Remove legacy style tags dedicated to the related component. Managed style
    # is protected by the token above.
    def clean_style(match):
        return '\n' if '.tl-related' in match.group(0) else match.group(0)

    text = STYLE_TAG_RE.sub(clean_style, text)

    if managed_block:
        text = text.replace(BLOCK_TOKEN, managed_block, 1)
    if managed_style:
        text = text.replace(STYLE_TOKEN, managed_style, 1)

    if text != original:
        path.write_text(text, encoding='utf-8')
        changed.append(path.name)

print('Related-module cleanup:', ', '.join(changed) if changed else 'none')
