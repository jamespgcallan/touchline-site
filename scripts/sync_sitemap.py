from datetime import date, datetime
from html.parser import HTMLParser
from pathlib import Path
import subprocess
from urllib.parse import urljoin, urlsplit, urlunsplit
from xml.sax.saxutils import escape

BASE_URL = "https://touchlinesport.net/"
SITE_HOSTS = {"touchlinesport.net", "www.touchlinesport.net"}
EXCLUDED_FILENAMES = {"404.html", "404.htm"}
AUTOMATION_AUTHORS = {"github-actions[bot]"}


class SeoHeadParser(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.canonical = None
        self.noindex = False
        self.modified_time = None
        self.published_time = None

    def handle_starttag(self, tag, attrs):
        attrs = {str(k).lower(): (v or "") for k, v in attrs}
        tag = tag.lower()

        if tag == "link":
            rel_tokens = {token.strip().lower() for token in attrs.get("rel", "").split()}
            if "canonical" in rel_tokens and attrs.get("href") and self.canonical is None:
                self.canonical = attrs["href"].strip()

        if tag == "meta":
            name = attrs.get("name", "").strip().lower()
            content = attrs.get("content", "").strip()
            content_lower = content.lower()
            if name in {"robots", "googlebot"} and "noindex" in {
                token.strip() for token in content_lower.replace(";", ",").split(",")
            }:
                self.noindex = True

            prop = attrs.get("property", "").strip().lower()
            if prop == "article:modified_time" and content:
                self.modified_time = content
            elif prop == "article:published_time" and content:
                self.published_time = content


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


def iso_date(value):
    if not value:
        return None
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00")).date().isoformat()
    except Exception:
        if len(value) >= 10:
            candidate = value[:10]
            try:
                return date.fromisoformat(candidate).isoformat()
            except Exception:
                return None
    return None


def git_lastmod(path):
    # Ignore housekeeping commits made by our own automation. Those can alter
    # navigation/SEO boilerplate without meaningfully changing the page content.
    result = subprocess.run(
        ["git", "log", "--format=%an%x09%cs", "--", str(path)],
        check=False,
        capture_output=True,
        text=True,
    )
    rows = [row for row in result.stdout.splitlines() if row.strip()]
    for row in rows:
        try:
            author, stamp = row.split("\t", 1)
        except ValueError:
            continue
        if author.strip().lower() not in AUTOMATION_AUTHORS and stamp.strip():
            return stamp.strip()

    if rows:
        try:
            return rows[0].split("\t", 1)[1].strip()
        except Exception:
            pass
    return date.today().isoformat()


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

    # Article metadata is the strongest signal for editorial pages. For other
    # pages, use the most recent non-automation Git commit touching that file.
    lastmod = iso_date(parser.modified_time) or iso_date(parser.published_time) or git_lastmod(path)

    return {
        "loc": loc,
        "lastmod": lastmod,
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
