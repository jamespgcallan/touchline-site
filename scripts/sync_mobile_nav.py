from pathlib import Path

WORK_LINK = '<a href="work-with-me.html">Work With Me</a>'
SCRIPT_TAG = '<script src="mobile-nav.js"></script>'

changed = []
for path in Path('.').glob('*.html'):
    text = path.read_text(encoding='utf-8')
    updated = text

    if 'work-with-me.html' not in updated:
        for old, new in [
            ('<a href="index.html#pillars">About</a>', WORK_LINK + '\n      <a href="index.html#pillars">About</a>'),
            ('<a href="#pillars">About</a>', WORK_LINK + '\n      <a href="#pillars">About</a>'),
            ('<a href="index.html#subscribe">Newsletter</a>', WORK_LINK + '\n      <a href="index.html#subscribe">Newsletter</a>'),
            ('<a href="#subscribe">Newsletter</a>', WORK_LINK + '\n      <a href="#subscribe">Newsletter</a>'),
        ]:
            if old in updated:
                updated = updated.replace(old, new, 1)
                break

    # Ensure exactly one mobile nav script is loaded at the end of every page.
    updated = updated.replace('<script src="mobile-nav.js" defer></script>', '')
    updated = updated.replace('<script src="mobile-nav.js"></script>', '')
    if '</body>' in updated:
        updated = updated.replace('</body>', SCRIPT_TAG + '\n</body>', 1)

    if updated != text:
        path.write_text(updated, encoding='utf-8')
        changed.append(str(path))

print('Updated:', ', '.join(changed) if changed else 'none')
