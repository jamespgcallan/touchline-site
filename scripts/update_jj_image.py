from pathlib import Path

OLD = "https://static.independent.co.uk/2026/09/15/14/2276277245"
NEW = "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcSDv4InWOWvijlRQiaK4FVGGCp5_cL7dbANrRAQuIo79g&s=10"

changed = []
for path in Path('.').glob('*.html'):
    text = path.read_text(encoding='utf-8')
    updated = text.replace(OLD, NEW)
    if updated != text:
        path.write_text(updated, encoding='utf-8')
        changed.append(path.name)

print('JJ image updated in:', ', '.join(changed) if changed else 'none')
