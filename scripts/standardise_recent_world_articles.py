from pathlib import Path
import re

FILES = {
    'inter-dario-baccin-recruitment-plan-piero-ausilio-exit.html': 'standard',
    'jj-gabriel-man-utd-exit-request.html': 'jj',
}

STANDARD_STYLE = r'''<!-- TL_STANDARD_ARTICLE_STYLE_START -->
<style>
:root{--paper:#fbf3e7;--paper-soft:#f5e5cf;--ink:#1c1a17;--ink-soft:#6b5d4d;--accent:#e8720f;--accent-soft:#fbe2c4;--line:rgba(33,31,26,.10);--max:1180px;--radius:18px}
*{box-sizing:border-box}html{scroll-behavior:smooth}body{margin:0;background:var(--paper);color:var(--ink);font-family:'Inter',-apple-system,sans-serif;-webkit-font-smoothing:antialiased;line-height:1.5}a{color:inherit;text-decoration:none}.wrap{max-width:var(--max);margin:0 auto;padding:0 32px}.pill{display:inline-flex;align-items:center;padding:5px 13px;border-radius:99px;background:var(--accent-soft);color:var(--accent);font-family:'IBM Plex Mono',monospace;font-size:11.5px;letter-spacing:.03em;font-weight:500}
header{padding:26px 0;position:sticky;top:0;background:rgba(251,243,231,.86);backdrop-filter:blur(10px);z-index:20}.nav-row{display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:14px}.logo{display:flex;align-items:center;gap:9px;font-family:'Manrope',sans-serif;font-weight:800;font-size:18px}.logo-mark{width:30px;height:30px;object-fit:contain}nav.links{display:flex;gap:30px}nav.links a{font-size:14px;font-weight:500;color:var(--ink-soft)}nav.links a:hover{color:var(--ink)}.nav-cta{background:var(--ink);color:var(--paper);padding:9px 18px;border-radius:99px;font-size:13.5px;font-weight:600}.nav-cta:hover{background:var(--accent)}
.article-head{padding:48px 0 30px;max-width:800px}.article-head .pill{margin-bottom:20px}.article-head h1{font-family:'Manrope',sans-serif;font-weight:800;font-size:clamp(30px,4.6vw,46px);line-height:1.08;letter-spacing:-.02em;margin:0 0 18px}.article-dek{font-family:'Source Serif 4',serif;font-style:italic;font-size:19px;color:var(--ink-soft);line-height:1.55;margin:0 0 24px}.article-meta{display:flex;align-items:center;gap:10px;flex-wrap:wrap;font-family:'IBM Plex Mono',monospace;font-size:12.5px;color:#8a8474;padding-top:20px;border-top:1px solid var(--line)}.article-meta .byline{color:var(--ink);font-weight:600}.dot{width:3px;height:3px;border-radius:50%;background:#a89f8c}.article-image,.header-image{width:100%;aspect-ratio:16/8;object-fit:cover;border-radius:var(--radius);display:block;margin:8px 0}.article-body{max-width:720px;padding:36px 0 10px}.article-body p{font-family:'Source Serif 4',serif;font-size:18px;line-height:1.75;color:#2b2823;margin:0 0 24px}.article-body h2{font-family:'Manrope',sans-serif;font-weight:700;font-size:23px;letter-spacing:-.005em;margin:46px 0 20px}.article-body blockquote{margin:30px 0;padding:8px 0 8px 24px;border-left:4px solid var(--accent);font-family:'Source Serif 4',serif;font-style:italic;font-size:22px;line-height:1.5;color:#2b2823}.article-body blockquote p{font-size:22px;line-height:1.5;margin:0 0 14px;color:inherit}.article-body blockquote p:last-child{margin-bottom:0}.body-image{width:100%;height:auto;aspect-ratio:16/9;object-fit:cover;border-radius:var(--radius);display:block;margin:24px 0 38px}.cta-box{margin:48px 0 20px;padding:32px 28px;background:var(--ink);color:var(--paper);border-radius:var(--radius);text-align:center}.cta-box p{font-family:'Inter',sans-serif;font-size:15px;color:#d9d3c4;max-width:48ch;margin:0 auto 20px;line-height:1.6}.btn-primary{background:var(--accent);color:var(--ink);padding:13px 24px;border-radius:99px;font-weight:700;font-size:14px;display:inline-block}.btn-primary:hover{background:var(--accent-soft)}.article-foot-nav{max-width:720px;padding:20px 0 60px;border-top:1px solid var(--line);margin-top:12px}.article-foot-nav a{font-family:'IBM Plex Mono',monospace;font-size:13px;font-weight:500;color:var(--ink-soft)}.article-foot-nav a:hover{color:var(--accent)}.share-row{display:flex;align-items:center}.share-row-top{justify-content:flex-end;margin-top:16px}.share-row-bottom{justify-content:flex-start;margin:20px 0 8px}.share-button{display:inline-flex;align-items:center;gap:8px;min-height:40px;padding:9px 14px;border:1px solid var(--line)!important;border-radius:99px;background:transparent!important;color:var(--ink-soft)!important;font-family:'Inter',sans-serif;font-size:13px;font-weight:600;cursor:pointer}.share-button:hover{color:var(--accent)!important;background:var(--accent-soft)!important}.share-button svg{width:18px;height:18px;fill:none;stroke:currentColor;stroke-width:1.8;stroke-linecap:round;stroke-linejoin:round}footer{border-top:1px solid var(--line);padding:34px 0}.fine-print{font-family:'IBM Plex Mono',monospace;font-size:11px;line-height:1.7;color:#928d7d;max-width:900px;margin:0 0 22px}.foot-row{display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:14px;font-size:13px;color:var(--ink-soft)}.foot-links{display:flex;gap:22px;flex-wrap:wrap}.foot-links a:hover{color:var(--accent)}
@media(max-width:600px){nav.links{display:none}.article-body p{font-size:16.5px}.article-body blockquote,.article-body blockquote p{font-size:20px}.wrap{padding:0 20px}.foot-row{flex-direction:column;align-items:flex-start}.body-image,.article-image,.header-image{border-radius:14px}}
</style>
<!-- TL_STANDARD_ARTICLE_STYLE_END -->'''

JJ_OVERRIDE = r'''<!-- TL_JJ_OLD_TEMPLATE_OVERRIDE_START -->
<style>
/* Make the JJ page use the established Touchline article presentation used by older pieces. */
.report-head{padding:0!important}.report-head>.wrap{max-width:1180px;margin:0 auto;padding:0 32px}.article-hero{max-width:800px!important;padding:48px 0 30px!important;border-radius:0!important;background:none!important;color:var(--ink)!important;overflow:visible!important}.article-hero .pill{margin-bottom:20px!important;background:var(--accent-soft)!important;color:var(--accent)!important}.article-hero h1{font-family:'Manrope',sans-serif!important;font-weight:800!important;font-size:clamp(30px,4.6vw,46px)!important;line-height:1.08!important;letter-spacing:-.02em!important;margin:0 0 18px!important;max-width:none!important}.article-hero .article-dek{color:var(--ink-soft)!important;margin:0 0 24px!important}.article-hero .article-meta{color:#8a8474!important;padding-top:20px!important;border-top:1px solid var(--line)!important}.article-hero .article-meta .byline{color:var(--ink)!important}.article-hero .dot{background:#a89f8c!important}.header-image{width:100%!important;aspect-ratio:16/8!important;object-fit:cover!important;border-radius:var(--radius)!important;margin:8px 0!important}.article-body{max-width:720px!important;margin-left:0!important;margin-right:0!important;padding:36px 0 10px!important}.article-body p:first-child::first-letter{font:inherit!important;line-height:inherit!important;float:none!important;margin:0!important;color:inherit!important}.article-foot-nav{max-width:720px!important;margin-left:0!important;margin-right:0!important}.share-row-top{justify-content:flex-end!important;margin-top:16px!important}
@media(max-width:600px){.report-head>.wrap{padding:0 20px}.article-hero{padding:36px 0 24px!important}.header-image{aspect-ratio:3/2!important;border-radius:14px!important}.article-body{max-width:none!important;padding:32px 0 8px!important}.article-foot-nav{max-width:none!important}}
</style>
<!-- TL_JJ_OLD_TEMPLATE_OVERRIDE_END -->'''

STYLE_RE = re.compile(r'\s*<!-- TL_STANDARD_ARTICLE_STYLE_START -->.*?<!-- TL_STANDARD_ARTICLE_STYLE_END -->\s*', re.S)
JJ_RE = re.compile(r'\s*<!-- TL_JJ_OLD_TEMPLATE_OVERRIDE_START -->.*?<!-- TL_JJ_OLD_TEMPLATE_OVERRIDE_END -->\s*', re.S)
BASE_STYLE_RE = re.compile(r'\s*<style>\s*:root\{.*?</style>\s*', re.S)

for filename, mode in FILES.items():
    path = Path(filename)
    if not path.exists():
        continue
    text = path.read_text(encoding='utf-8')
    original = text

    # Remove any prior managed standardisation and any page-local base article CSS.
    text = STYLE_RE.sub('\n', text)
    text = JJ_RE.sub('\n', text)
    text = BASE_STYLE_RE.sub('\n', text, count=1)

    # Remove exact consecutive duplicate breadcrumbs produced by older sync passes.
    breadcrumb = re.compile(r'(<!-- TL_BREADCRUMB_START -->.*?<!-- TL_BREADCRUMB_END -->)(?:\s*<nav aria-label="Breadcrumb".*?</nav>)?', re.S)
    m = breadcrumb.search(text)
    if m:
        managed = re.search(r'<!-- TL_BREADCRUMB_START -->.*?<!-- TL_BREADCRUMB_END -->', m.group(0), re.S)
        if managed:
            text = text[:m.start()] + managed.group(0) + text[m.end():]

    insert = STANDARD_STYLE + ('\n' + JJ_OVERRIDE if mode == 'jj' else '') + '\n'
    marker = '<link rel="alternate" type="application/rss+xml"'
    if marker in text:
        text = text.replace(marker, insert + marker, 1)
    else:
        text = text.replace('</head>', insert + '</head>', 1)

    if text != original:
        path.write_text(text, encoding='utf-8')
        print('Standardised:', filename)
    else:
        print('Already standard:', filename)
