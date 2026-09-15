from pathlib import Path
import re

ROOT = Path('.')

DESKTOP_NAV = (
    '<nav class="links" aria-label="Primary navigation">'
    '<a href="latest-news.html">Latest</a>'
    '<a href="league-of-ireland-analysis.html">Irish Football</a>'
    '<a href="touchline-tactics.html">Touchline Tactics</a>'
    '<a href="archive.html">Archive</a>'
    '<a href="about.html">About</a>'
    '<a href="work-with-me.html">Work With Us</a>'
    '</nav>'
)

FOOTER_BLOCK = '''<!-- TL_STUDIOS_FOOTER_START -->
<div style="max-width:1180px;margin:0 auto 28px;padding:0 32px;display:grid;grid-template-columns:1fr 1fr auto;gap:24px;align-items:end;">
  <div>
    <div style="font-family:Manrope,Arial,sans-serif;font-weight:800;font-size:15px;margin-bottom:4px;">Touchline Studios</div>
    <div style="font-family:Inter,Arial,sans-serif;font-size:13px;line-height:1.55;color:#6b5d4d;">Football Media, Communications, PR &amp; Strategy</div>
  </div>
  <div>
    <div style="font-family:Manrope,Arial,sans-serif;font-weight:800;font-size:15px;margin-bottom:4px;">Touchline Sport</div>
    <div style="font-family:Inter,Arial,sans-serif;font-size:13px;line-height:1.55;color:#6b5d4d;">Independent football journalism and analysis.</div>
  </div>
  <a href="work-with-me.html" style="font-family:Inter,Arial,sans-serif;font-size:13px;font-weight:700;color:#e8720f;white-space:nowrap;">Work With Us →</a>
</div>
<!-- TL_STUDIOS_FOOTER_END -->'''

HOMEPAGE_CSS = '''
  /* TL_STUDIOS_HOME_START */
  .studios{padding:86px 0;background:var(--ink);color:var(--paper);}
  .studios-grid{display:grid;grid-template-columns:.82fr 1.18fr;gap:58px;align-items:start;}
  .studios .eyebrow{font-family:'IBM Plex Mono',monospace;font-size:11.5px;letter-spacing:.04em;color:#f3c491;margin-bottom:14px;}
  .studios h2{font-family:'Manrope',sans-serif;font-weight:800;font-size:clamp(30px,4vw,44px);line-height:1.08;letter-spacing:-.02em;margin:0;}
  .studios-copy p{color:#c9c5b8;font-size:15.5px;line-height:1.75;margin:0 0 18px;max-width:66ch;}
  .studios-copy strong{color:var(--paper);}
  .studios-actions{display:flex;gap:12px;flex-wrap:wrap;margin-top:28px;}
  .studios-btn{display:inline-flex;align-items:center;padding:12px 20px;border-radius:99px;background:var(--accent);color:#fff;font-size:14px;font-weight:700;}
  .studios-note{display:inline-flex;align-items:center;padding:12px 0;color:#c9c5b8;font-size:13.5px;font-weight:600;}
  @media(max-width:800px){.studios-grid{grid-template-columns:1fr;gap:28px;}}
  /* TL_STUDIOS_HOME_END */
'''

HOMEPAGE_STUDIOS = '''<section class="studios" id="studios"><div class="wrap"><div class="studios-grid"><div><div class="eyebrow">TOUCHLINE STUDIOS</div><h2>We don’t just write about football.</h2></div><div class="studios-copy"><p>Touchline Studios also works within it. We help clubs, players and football organisations with <strong>PR, communications, media strategy and storytelling</strong>.</p><p>That might mean launching a partnership, telling the story behind an academy, improving how a club communicates or helping turn something genuinely interesting into something people actually want to read.</p><p>No corporate waffle. No pretending every new partnership is “ground-breaking”. Just better football communication.</p><div class="studios-actions"><a class="studios-btn" href="work-with-me.html">Work With Touchline →</a><a class="studios-note" href="about.html">How the media and studio sides fit together</a></div></div></div></div></section>'''

HOMEPAGE_PILLARS = '''<section class="pillars" id="pillars"><div class="wrap"><div class="section-title display">What we cover</div><div class="pillars-grid"><div class="pillar"><div class="pillar-num">01</div><h4>Irish Football</h4><p>League of Ireland clubs, players, academies, ownership and the wider Irish game.</p></div><div class="pillar"><div class="pillar-num">02</div><h4>Club Strategy</h4><p>Money, ownership, recruitment, commercial thinking and the decisions clubs make when nobody is watching the highlights.</p></div><div class="pillar"><div class="pillar-num">03</div><h4>Touchline Tactics</h4><p>How teams actually play. Build-up, pressing, structures and the occasional manager making football unnecessarily complicated.</p></div><div class="pillar"><div class="pillar-num">04</div><h4>Scouting &amp; Recruitment</h4><p>Players, squad building and recruitment profiles from Ireland and further afield.</p></div></div></div></section>'''

ABOUT_MAIN = '''<main>
<section class="hero"><div class="wrap"><span class="pill">About Touchline</span><h1>Football coverage, with a bit more digging.</h1><p class="lead">Touchline started with a fairly simple idea. Football coverage spends plenty of time talking about what happened. We wanted to spend a little more time asking why.</p></div></section>
<section class="section"><div class="wrap copy"><h2>What Touchline Sport is</h2><p>Why does one club develop players better than another? Why does a recruitment model work? Where does the money actually go? Why can one club communicate brilliantly with supporters while another can make announcing a new stand sound like a hostage statement?</p><p>That’s what Touchline Sport covers. It’s an independent football publication looking at Irish football and the wider game through club strategy, ownership, recruitment, academies, commercial thinking and tactics.</p><p>The aim is pretty simple: take the structures behind football seriously without taking ourselves too seriously.</p></div></section>
<section class="section"><div class="wrap"><h2>Two sides of the same Touchline</h2><div class="grid"><a class="card" href="index.html#latest"><strong>Touchline Sport</strong><p>Our publication and newsletter. Original reporting, features, analysis and tactical pieces, with Irish football sitting at the centre of it.</p></a><a class="card" href="work-with-me.html"><strong>Touchline Studios</strong><p>PR, communications, media strategy and storytelling for clubs, players and football organisations.</p></a><a class="card" href="football-club-strategy.html"><strong>Strategy &amp; Research</strong><p>Club structures, recruitment, commercial thinking and the sort of football questions that usually need a bit more digging.</p></a></div></div></section>
<section class="section"><div class="wrap copy"><h2>How the studio side works</h2><p>The same thinking that goes into Touchline Sport sits behind the commercial work: understand the club, understand the audience, find the interesting part and explain it properly. You’d be surprised how far that gets you.</p><p>Touchline Studios can help with media relations, communications strategy, partnership storytelling, club and executive positioning, football content and reputation work. The aim isn’t to turn every announcement into a campaign. It’s to work out what is actually worth saying and say it well.</p><div class="links"><a class="button" href="work-with-me.html">Work With Touchline</a><a class="button alt" href="contact.html">Get in touch</a></div></div></section>
<section class="section"><div class="wrap copy"><h2>Independent journalism stays independent</h2><p>Touchline Sport’s editorial coverage is separate from commercial work carried out through Touchline Studios. Working with the studio does not guarantee coverage in the publication, and where a relevant commercial relationship needs to be disclosed, it will be.</p><p>Football already has enough blurred lines. We’d rather keep ours fairly obvious.</p><div class="links"><a class="button alt" href="editorial-policy.html">Editorial Policy</a><a class="button alt" href="james-callan.html">About James</a></div></div></section>
</main>'''

JAMES_MAIN = '''<main>
<section class="hero"><div class="wrap"><span class="pill">Founder, writer &amp; strategist</span><h1>James <em>Callan</em></h1><p class="lead">Irish football writer and communications strategist covering the League of Ireland, club ownership, recruitment, academies, commercial thinking and the tactical ideas that decide what happens on the pitch.</p><a class="award" href="football-content-awards-2026-finalist.html"><span aria-hidden="true">🏆</span><span><strong>Football Content Awards 2026 finalist</strong><small>Best New Content Creator</small></span></a></div></section>
<section class="section"><div class="wrap copy"><h2>About James</h2><p>James founded Touchline Sport to look beyond the result and work out how football clubs actually function. The publication connects boardroom decisions with recruitment, academy pathways, culture and what eventually appears on the pitch.</p><p>Through Touchline Studios, he also works across football communications, PR, strategy, partnerships and storytelling. The two sides are deliberately connected without being the same thing: one is independent editorial work, the other helps football organisations communicate and think more clearly.</p><p>He holds a BA (Hons) in Business and Law from TU Dublin, where his thesis examined the use of EU competition law to regulate multi-club ownership. His football education includes training in talent identification, opposition analysis and advanced reporting, alongside postgraduate study in football business and business intelligence and digital marketing.</p><p>James is also Head of Social Media at LOI Talk and works across football strategy, partnerships, operations and storytelling. Touchline is the public home for that mix of writing, analysis and football work.</p></div></section>
<section class="section"><div class="wrap"><h2>Areas of work</h2><div class="grid"><a class="card" href="league-of-ireland-analysis.html"><strong>League of Ireland</strong><p>Academies, ownership, club finance, recruitment and the structures shaping Irish football.</p></a><a class="card" href="work-with-me.html"><strong>Communications &amp; PR</strong><p>Media strategy, club communications, partnership storytelling and helping football organisations work out what is actually worth saying.</p></a><a class="card" href="football-club-strategy.html"><strong>Club strategy</strong><p>How clubs recruit, grow revenue, develop players, organise departments and build for more than one season.</p></a></div><div class="links"><a class="button" href="archive.html">Read the work</a><a class="button alt" href="work-with-me.html">Work With Touchline</a></div></div></section>
</main>'''

WORK_MAIN = '''<main>
<section class="hero"><div class="wrap hero-inner"><span class="pill">Touchline Studios</span><h1>Football has enough people shouting. <em>We help work out what’s actually worth saying.</em></h1><p class="hero-sub">Touchline Studios works with clubs, players and football organisations across PR, communications, media strategy and storytelling. Basically, if there’s a good story there, we’ll help find it, shape it and get it in front of the right people. And if there isn’t one, we’ll probably tell you that too.</p></div></section>
<section class="section soft"><div class="wrap"><div class="section-head"><div class="eyebrow">WHAT WE CAN HELP WITH</div><h2>Football communication that still sounds like football.</h2><p>No enormous menu of “solutions”. Just the areas where Touchline can genuinely be useful.</p></div><div class="services">
  <article class="service-card dark"><div class="service-num">01</div><h3>PR &amp; Media</h3><p>Press releases, media pitches, interview opportunities, announcements and journalist outreach. The aim isn’t getting a logo into as many places as possible. It’s finding stories people might genuinely care about.</p></article>
  <article class="service-card"><div class="service-num">02</div><h3>Communications Strategy</h3><p>What should your club talk about? What shouldn’t it talk about? Who are you trying to reach and what do you actually want them to understand about you? We help make that clearer.</p></article>
  <article class="service-card"><div class="service-num">03</div><h3>Football Storytelling</h3><p>Academies, community programmes, facilities, recruitment projects and commercial work. Clubs do interesting things every week and then occasionally announce them with a photo of three people beside a pull-up banner. We help tell the better version.</p></article>
  <article class="service-card dark"><div class="service-num">04</div><h3>Partnerships &amp; Commercial PR</h3><p>A sponsor doesn’t really want another logo placement and a club doesn’t need another post saying it’s “delighted to announce”. We help turn partnerships into stories, campaigns and content that make sense for both sides.</p></article>
  <article class="service-card"><div class="service-num">05</div><h3>Club &amp; Executive Positioning</h3><p>For owners, executives, sporting directors, coaches and football organisations looking to communicate with a clearer public voice. Interviews, thought leadership, LinkedIn and long-form content without making everybody sound like they’ve swallowed a business textbook.</p></article>
  <article class="service-card"><div class="service-num">06</div><h3>Reputation &amp; Crisis Communications</h3><p>Football moves quickly and the conversation around a club can move even quicker. We help work out what needs to be said, who should say it and when saying nothing may actually be the smarter option.</p></article>
</div></div></section>
<section class="section"><div class="wrap approach"><div class="approach-copy"><div class="eyebrow">WHY TOUCHLINE</div><h2>We actually cover the game too.</h2><p>Touchline Sport is our independent football publication covering Irish football, club strategy, ownership, recruitment, academies, commercial thinking and tactics.</p><p>That means we’re not approaching football like another industry with a badge stuck on it. We spend every week writing about how clubs work, how supporters experience them and why some ideas land while others disappear into the usual football fog.</p><p>The publication remains editorially independent from commercial work. Working with Touchline Studios does not buy coverage in Touchline Sport.</p></div><div class="approach-points">
  <div class="point"><strong>Understand the club</strong><span>Before deciding what to say, work out what is actually happening and why anyone should care.</span></div>
  <div class="point"><strong>Understand the audience</strong><span>Supporters, journalists, partners and players do not all need the same message dressed up in different graphics.</span></div>
  <div class="point"><strong>Keep it useful</strong><span>Good communication should leave somebody clearer, more interested or more likely to act. Preferably all three, but football rarely gives you everything.</span></div>
</div></div></section>
<section class="cta"><div class="wrap"><div class="cta-box"><div><span class="pill">Got something in mind?</span><h2>Tell us what you’re working on.</h2><p>A launch, a partnership, a club story, a communications problem or an idea that still needs working out. Send it over and we’ll see where Touchline can genuinely help.</p></div><a class="btn" href="mailto:jamespgcallan@gmail.com">Get in touch →</a></div></div></section>
</main>'''


def save(path, text):
    path.write_text(text, encoding='utf-8')


def replace_main(text, replacement):
    return re.sub(r'<main>.*?</main>', replacement, text, count=1, flags=re.S | re.I)


def replace_header_nav(text):
    header = re.search(r'<header\b[^>]*>.*?</header>', text, flags=re.S | re.I)
    if not header:
        return text
    new_header = re.sub(r'<nav(?:\s+class="links")?[^>]*>.*?</nav>', DESKTOP_NAV, header.group(0), count=1, flags=re.S | re.I)
    return text[:header.start()] + new_header + text[header.end():]


def add_footer_positioning(text):
    text = re.sub(r'\s*<!-- TL_STUDIOS_FOOTER_START -->.*?<!-- TL_STUDIOS_FOOTER_END -->\s*', '\n', text, flags=re.S)
    if '<!-- TL_EXPLORE_END -->' in text:
        return text.replace('<!-- TL_EXPLORE_END -->', '<!-- TL_EXPLORE_END -->\n' + FOOTER_BLOCK, 1)
    footer = re.search(r'<footer\b[^>]*>', text, flags=re.I)
    if footer:
        return text[:footer.end()] + '\n' + FOOTER_BLOCK + text[footer.end():]
    return text


def update_homepage(path):
    text = path.read_text(encoding='utf-8')
    text = re.sub(
        r'<p class="hero-sub">.*?</p>',
        '<p class="hero-sub">Touchline looks at how clubs grow, spend, recruit, rebuild and occasionally make a complete mess of it. From the League of Ireland to the wider game, we cover the money, people, academies, recruitment, tactics and decisions sitting behind what happens on the pitch.<br><br>Independent football media from <strong>Touchline Studios</strong>. Written by <a href="james-callan.html"><strong>James Callan</strong></a>.</p>',
        text,
        count=1,
        flags=re.S,
    )
    text = re.sub(r'<section class="pillars" id="pillars">.*?</section>', HOMEPAGE_PILLARS, text, count=1, flags=re.S)
    if 'TL_STUDIOS_HOME_START' not in text:
        text = text.replace('</style>', HOMEPAGE_CSS + '\n</style>', 1)
    if '<section class="studios" id="studios">' not in text:
        text = text.replace('<section class="subscribe"', HOMEPAGE_STUDIOS + '\n<section class="subscribe"', 1)
    text = re.sub(
        r'(<section class="subscribe"[^>]*>.*?<h2 class="display">No noise\. Just football\.</h2>)<p>.*?</p>',
        r'\1<p>Two or three proper football stories a week. Irish football, tactics, club strategy and whatever else has sent us down a completely unnecessary rabbit hole.</p>',
        text,
        count=1,
        flags=re.S,
    )
    return text


def update_about(path):
    text = path.read_text(encoding='utf-8')
    text = re.sub(r'<meta name="description" content="[^"]*">', '<meta name="description" content="About Touchline Sport, the independent football publication, and Touchline Studios, its football PR, communications and strategy arm.">', text, count=1)
    text = text.replace('Independent football analysis covering Irish football, tactics, recruitment and club strategy.', 'Independent football journalism from Touchline Sport, alongside PR, communications and strategy work through Touchline Studios.')
    text = replace_main(text, ABOUT_MAIN)
    return text


def update_james(path):
    text = path.read_text(encoding='utf-8')
    text = re.sub(r'<meta name="description" content="[^"]*">', '<meta name="description" content="James Callan is an Irish football writer and communications strategist, and founder of Touchline Sport and Touchline Studios.">', text, count=1)
    text = text.replace('Irish football writer and strategist covering the League of Ireland, club strategy, recruitment and tactics.', 'Irish football writer and communications strategist covering the League of Ireland, club strategy, recruitment, PR and football storytelling.')
    text = text.replace('"jobTitle":"Football Brand and Commercial Strategist"', '"jobTitle":"Football Writer and Communications Strategist"')
    text = text.replace('"description":"Irish football writer, strategist and founder of Touchline Sport."', '"description":"Irish football writer and communications strategist, and founder of Touchline Sport and Touchline Studios."')
    text = replace_main(text, JAMES_MAIN)
    return text


def update_work(path):
    text = path.read_text(encoding='utf-8')
    text = re.sub(r'<title>.*?</title>', '<title>Work With Touchline | Football PR, Communications &amp; Strategy</title>', text, count=1, flags=re.S)
    text = re.sub(r'<meta name="description" content="[^"]*">', '<meta name="description" content="Work with Touchline Studios on football PR, communications, media strategy, partnership storytelling and club positioning.">', text, count=1)
    text = replace_main(text, WORK_MAIN)
    return text


changed = []
for filename, updater in {
    'index.html': update_homepage,
    'about.html': update_about,
    'james-callan.html': update_james,
    'work-with-me.html': update_work,
}.items():
    path = ROOT / filename
    if not path.exists():
        continue
    original = path.read_text(encoding='utf-8')
    updated = updater(path)
    updated = replace_header_nav(updated)
    updated = add_footer_positioning(updated)
    if updated != original:
        save(path, updated)
        changed.append(filename)

# The PR/comms route should be visible from every page without changing
# Touchline Sport's publication name, NewsArticle publisher or site-name schema.
for path in ROOT.glob('*.html'):
    if path.name in changed:
        continue
    original = path.read_text(encoding='utf-8')
    updated = replace_header_nav(original)
    updated = add_footer_positioning(updated)
    if updated != original:
        save(path, updated)
        changed.append(path.name)

print('Touchline Studios positioning sync:', ', '.join(changed) if changed else 'none')
