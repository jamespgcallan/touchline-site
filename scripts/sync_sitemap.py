from datetime import date
from html.parser import HTMLParser
from pathlib import Path
import subprocess
from urllib.parse import urljoin, urlsplit, urlunsplit
from xml.sax.saxutils import escape

BASE_URL = "https://touchlinesport.net/"
SITE_HOSTS = {"touchlinesport.net", "www.touchlinesport.net"}
EXCLUDED_FILENAMES = {"404.html", "404.htm"}


class SeoHeadParser(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.canonical = None
        self.noindex = False

    def handle_starttag(self, tag, attrs):
        attrs = {str(k).lower(): (v or "") for k, v in attrs}
        tag = tag.lower()

        if tag == "link":
            rel_tokens = {token.strip().lower() for token in attrs.get("rel", "").split()}
            if "canonical" in rel_tokens and attrs.get("href") and self.canonical is None:
                self.canonical = attrs["href"].strip()

        if tag == "meta":
            name = attrs.get("name", "").strip().lower()
            content = attrs.get("content", "").strip().lower()
            if name in {"robots", "googlebot"} and "noindex" in {
                token.strip() for token in content.replace(";", ",").split(",")
            }:
                self.noindex = True


def normalise_canonical(raw_url):
    if not raw_url:
        return None

    absolute = urljoin(BASE_URL, raw_url.strip())
    parsed = urlsplit(absolute)
    host = parsed.netloc.lower()
    if host not in SITE_HOSTS:
        return None

    path = parsed.path or "/"
    if path == "/index.html":
        path = "/"

    # Keep sitemap URLs clean: no fragments or tracking/query parameters.
    return urlunsplit(("https", "touchlinesport.net", path, "", ""))


def page_url(path, parser):
    fallback = BASE_URL if path.name == "index.html" else BASE_URL + path.name

    if parser.canonical:
        canonical = normalise_canonical(parser.canonical)
        if canonical is None:
            return None
        return canonical

    return fallback


def git_lastmod(path):
    # If another SEO synchroniser changed the file earlier in this workflow,
    # use today's date so Google gets a truthful freshness signal.
    dirty = subprocess.run(
        ["git", "diff", "--quiet", "--", str(path)],
        check=False,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    if dirty.returncode != 0:
        return date.today().isoformat()

    result = subprocess.run(
        ["git", "log", "-1", "--format=%cs", "--", str(path)],
        check=False,
        capture_output=True,
        text=True,
    )
    stamp = result.stdout.strip()
    return stamp or date.today().isoformat()


def parse_page(path):
    if path.name in EXCLUDED_FILENAMES:
        return None

    text = path.read_text(encoding="utf-8", errors="ignore")
    parser = SeoHeadParser()
    try:
        parser.feed(text)
    except Exception:
        pass

    if parser.noindex:
        return None

    loc = page_url(path, parser)
    if not loc:
        return None

    return {
        "loc": loc,
        "lastmod": git_lastmod(path),
        "source": path.name,
    }


entries_by_url = {}
for path in sorted(Path(".").glob("*.html")):
    item = parse_page(path)
    if not item:
        continue

    existing = entries_by_url.get(item["loc"])
    if existing is None:
        entries_by_url[item["loc"]] = item
        continue

    # Prefer the file whose natural public URL matches the canonical URL.
    natural = BASE_URL if path.name == "index.html" else BASE_URL + path.name
    if natural == item["loc"]:
        entries_by_url[item["loc"]] = item

entries = sorted(
    entries_by_url.values(),
    key=lambda item: (0 if item["loc"] == BASE_URL else 1, item["loc"]),
)

lines = [
    '<?xml version="1.0" encoding="UTF-8"?>',
    '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">',
]
for item in entries:
    lines.extend([
        "  <url>",
        f'    <loc>{escape(item["loc"])}</loc>',
        f'    <lastmod>{item["lastmod"]}</lastmod>',
        "  </url>",
    ])
lines.append("</urlset>")

Path("sitemap.xml").write_text("\n".join(lines) + "\n", encoding="utf-8")
print(f"Main sitemap rebuilt with {len(entries)} canonical, indexable HTML URLs")
