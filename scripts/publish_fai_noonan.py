from pathlib import Path
import re
import urllib.request

SLUG = 'fai-shamrock-rovers-noonan-transfer-investigation.html'
TITLE = 'FAI Opens Investigation Into Shamrock Rovers Over Noonan Transfers'
SUBTITLE = 'FIFA referred agency agreements involving Michael and Alex Noonan back to the FAI for examination under third-party ownership rules.'
REMOTE_IMAGE = 'https://www.ipswichstar.co.uk/resources/images/21403246.jpg/'
LOCAL_IMAGE_PATH = Path('images/fai-shamrock-rovers-noonan-investigation.jpg')
LOCAL_IMAGE_URL = 'https://touchlinesport.net/images/fai-shamrock-rovers-noonan-investigation.jpg'
DATE = '2026-09-13'
DISPLAY_DATE = '13 Sep 2026'


def write(path, text):
    Path(path).write_text(text, encoding='utf-8')


def try_download_image():
    LOCAL_IMAGE_PATH.parent.mkdir(parents=True, exist_ok=True)
    try:
        req = urllib.request.Request(
            REMOTE_IMAGE,
            headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/142 Safari/537.36',
                'Referer': 'https://www.ipswichstar.co.uk/'
            },
        )
        with urllib.request.urlopen(req, timeout=25) as response:
            data = response.read()
        if len(data) < 5000 or not data.startswith(b'\xff\xd8'):
            raise ValueError('Downloaded file was not a valid JPEG')
        LOCAL_IMAGE_PATH.write_bytes(data)
        print(f'Saved article image locally: {len(data)} bytes')
        return LOCAL_IMAGE_URL
    except Exception as exc:
        if LOCAL_IMAGE_PATH.exists():
            LOCAL_IMAGE_PATH.unlink()
        print(f'Image download unavailable; retaining supplied remote URL: {exc}')
        return REMOTE_IMAGE


image_url = try_download_image()

article = Path(SLUG)
if article.exists() and image_url == LOCAL_IMAGE_URL:
    text = article.read_text(encoding='utf-8').replace(REMOTE_IMAGE, LOCAL_IMAGE_URL)
    write(article, text)

home_path = Path('index.html')
home = home_path.read_text(encoding='utf-8')

# Homepage social preview follows the latest article.
home = re.sub(r'(<meta property="og:image" content=")[^"]+(">)', rf'\g<1>{image_url}\g<2>', home, count=1)
home = re.sub(r'(<meta name="twitter:image" content=")[^"]+(">)', rf'\g<1>{image_url}\g<2>', home, count=1)

# Read-the-latest button.
home = re.sub(
    r'(<div class="hero-actions"><a class="btn-primary" href=")[^"]+(">Read the latest →</a>)',
    rf'\g<1>{SLUG}\g<2>',
    home,
    count=1,
)

new_featured = (
    '<div class="featured"><div><span class="pill">Latest · Irish Football</span>'
    f'<h2>{TITLE}</h2><p>{SUBTITLE}</p>'
    f'<a class="read" href="{SLUG}">Read the piece <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M5 12h14M13 5l7 7-7 7"/></svg></a>'
    f'</div><div class="featured-art" style="background-image:url(\'{image_url}\');background-size:cover;background-repeat:no-repeat;background-position:center;"></div></div>'
)
home = re.sub(
    r'<div class="featured"><div><span class="pill">Latest · Irish Football</span>.*?</div><div class="featured-art"[^>]*></div></div>',
    new_featured,
    home,
    count=1,
    flags=re.S,
)

new_home_card = (
    f'<a class="card" href="{SLUG}"><div class="card-art" style="background-image:url(\'{image_url}\');background-size:cover;background-position:center;"></div>'
    f'<div class="card-body"><span class="pill">Ireland</span><h3>{TITLE}</h3><p>{SUBTITLE}</p>'
    f'<div class="meta"><span>{DISPLAY_DATE}</span><span class="dot"></span><span>5 min read</span></div></div></a>'
)
if f'<a class="card" href="{SLUG}">' not in home:
    section_start = home.find('<div class="wrap category-block" id="irish">')
    grid_start = home.find('<div class="grid">', section_start)
    if section_start == -1 or grid_start == -1:
        raise SystemExit('Irish homepage grid marker not found')
    insert_at = grid_start + len('<div class="grid">')
    home = home[:insert_at] + new_home_card + home[insert_at:]

home = re.sub(
    r'(<a class="view-all" href="archive.html#irish">)\d+( pieces · View all →</a>)',
    r'\g<1>63\g<2>',
    home,
    count=1,
)
write(home_path, home)

# Irish Football category page.
category_path = Path('league-of-ireland-analysis.html')
category = category_path.read_text(encoding='utf-8')
category = re.sub(r'(<meta property="og:image" content=")[^"]+(">)', rf'\g<1>{image_url}\g<2>', category, count=1)
new_category_card = (
    f'<a class="card" href="{SLUG}"><div class="art" style="background-image:url(\'{image_url}\')"></div>'
    f'<div class="body"><small>FAI · Governance</small><h2>{TITLE}</h2><p>{SUBTITLE}</p></div></a>'
)
if f'<a class="card" href="{SLUG}">' not in category:
    grid_start = category.find('<div class="grid">')
    if grid_start == -1:
        raise SystemExit('Irish Football category grid marker not found')
    insert_at = grid_start + len('<div class="grid">')
    category = category[:insert_at] + new_category_card + category[insert_at:]
write(category_path, category)

# Archive, newest first.
archive_path = Path('archive.html')
archive = archive_path.read_text(encoding='utf-8')
archive = re.sub(r'(<span class="pill">)\d+( pieces and counting</span>)', r'\g<1>136\g<2>', archive, count=1)
archive = re.sub(r'(<span class="category-count">)62( pieces</span>)', r'\g<1>63\g<2>', archive, count=1)
new_archive_item = f'''<li class="arch-item">
          <a href="{SLUG}">
            <span class="arch-copy">
              <span class="arch-title">{TITLE}</span>
              <span class="arch-description">{SUBTITLE}</span>
            </span>
            <span class="arch-meta">
              <time class="arch-date" datetime="{DATE}">{DISPLAY_DATE}</time>
              <span class="arch-arrow">→</span>
            </span>
          </a>
        </li>
'''
if f'<a href="{SLUG}">' not in archive:
    irish_start = archive.find('<div class="wrap category-block" id="irish">')
    list_start = archive.find('<ul class="arch-list">', irish_start)
    if irish_start == -1 or list_start == -1:
        raise SystemExit('Irish archive list marker not found')
    insert_at = list_start + len('<ul class="arch-list">')
    archive = archive[:insert_at] + new_archive_item + archive[insert_at:]
write(archive_path, archive)

# Normal sitemap.
sitemap_path = Path('sitemap.xml')
sitemap = sitemap_path.read_text(encoding='utf-8')
for loc in [
    'https://touchlinesport.net/',
    'https://touchlinesport.net/league-of-ireland-analysis.html',
    'https://touchlinesport.net/archive.html',
]:
    pattern = rf'(<url><loc>{re.escape(loc)}</loc><lastmod>)\d{{4}}-\d{{2}}-\d{{2}}(</lastmod>)'
    sitemap = re.sub(pattern, rf'\g<1>{DATE}\g<2>', sitemap, count=1)
new_url = f'https://touchlinesport.net/{SLUG}'
if new_url not in sitemap:
    entry = f'  <url><loc>{new_url}</loc><lastmod>{DATE}</lastmod><changefreq>monthly</changefreq><priority>0.9</priority></url>\n'
    sitemap = sitemap.replace('</urlset>', entry + '</urlset>')
write(sitemap_path, sitemap)

print('FAI Noonan investigation article surfaces published')
