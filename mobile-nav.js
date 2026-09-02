document.addEventListener('DOMContentLoaded', () => {
  const header = document.querySelector('header');
  const navRow = header?.querySelector('.nav-row');
  const desktopNav = header?.querySelector('nav.links') || header?.querySelector('nav');
  const subscribe = header?.querySelector('.nav-cta');
  if (!header || !navRow || !desktopNav) return;

  const style = document.createElement('style');
  style.textContent = `
    .mobile-menu-btn,.mobile-menu-panel{display:none}
    @media(max-width:600px){
      header{position:sticky;top:0;overflow:visible}
      .nav-row{flex-wrap:nowrap!important;position:relative}
      header nav.links{display:none!important}
      header .nav-cta{display:none!important}
      .mobile-menu-btn{display:inline-flex;align-items:center;gap:9px;border:1px solid rgba(33,31,26,.12);background:#fff;color:#1c1a17;border-radius:999px;padding:9px 14px;font:600 13px 'Inter',sans-serif;cursor:pointer;margin-left:auto}
      .mobile-menu-icon{width:16px;height:12px;display:flex;flex-direction:column;justify-content:space-between}
      .mobile-menu-icon span{display:block;height:2px;border-radius:2px;background:currentColor;transition:transform .2s,opacity .2s}
      .mobile-menu-btn[aria-expanded='true'] .mobile-menu-icon span:nth-child(1){transform:translateY(5px) rotate(45deg)}
      .mobile-menu-btn[aria-expanded='true'] .mobile-menu-icon span:nth-child(2){opacity:0}
      .mobile-menu-btn[aria-expanded='true'] .mobile-menu-icon span:nth-child(3){transform:translateY(-5px) rotate(-45deg)}
      .mobile-menu-panel{position:absolute;display:none;top:calc(100% + 14px);left:0;right:0;background:#fbf3e7;border:1px solid rgba(33,31,26,.10);border-radius:16px;padding:10px;box-shadow:0 18px 40px rgba(33,31,26,.14);z-index:9999}
      .mobile-menu-panel.open{display:block!important}
      .mobile-menu-panel a{display:block;padding:13px 14px;border-radius:10px;font:600 14px 'Inter',sans-serif;color:#1c1a17}
      .mobile-menu-panel a:hover,.mobile-menu-panel a:focus{background:#f5e5cf;outline:none}
      .mobile-menu-panel .mobile-subscribe{margin-top:6px;background:#1c1a17;color:#fbf3e7;text-align:center}
      .mobile-menu-panel .mobile-subscribe:hover,.mobile-menu-panel .mobile-subscribe:focus{background:#e8720f;color:#1c1a17}
      body.mobile-menu-open{overflow:hidden}
    }
  `;
  document.head.appendChild(style);

  const button = document.createElement('button');
  button.className = 'mobile-menu-btn';
  button.type = 'button';
  button.setAttribute('aria-expanded', 'false');
  button.setAttribute('aria-controls', 'mobile-site-menu');
  button.setAttribute('aria-label', 'Open site menu');
  button.innerHTML = '<span class="mobile-menu-icon" aria-hidden="true"><span></span><span></span><span></span></span><span>Menu</span>';

  const panel = document.createElement('nav');
  panel.id = 'mobile-site-menu';
  panel.className = 'mobile-menu-panel';
  panel.setAttribute('aria-label', 'Mobile navigation');

  desktopNav.querySelectorAll('a').forEach(link => {
    const clone = link.cloneNode(true);
    panel.appendChild(clone);
  });

  if (subscribe) {
    const sub = subscribe.cloneNode(true);
    sub.classList.remove('nav-cta');
    sub.classList.add('mobile-subscribe');
    panel.appendChild(sub);
  }

  if (subscribe) navRow.insertBefore(button, subscribe);
  else navRow.appendChild(button);
  navRow.appendChild(panel);

  const closeMenu = () => {
    button.setAttribute('aria-expanded', 'false');
    button.setAttribute('aria-label', 'Open site menu');
    panel.classList.remove('open');
    document.body.classList.remove('mobile-menu-open');
  };

  button.addEventListener('click', () => {
    const open = button.getAttribute('aria-expanded') === 'true';
    if (open) closeMenu();
    else {
      button.setAttribute('aria-expanded', 'true');
      button.setAttribute('aria-label', 'Close site menu');
      panel.classList.add('open');
      document.body.classList.add('mobile-menu-open');
    }
  });

  panel.addEventListener('click', e => {
    if (e.target.closest('a')) closeMenu();
  });

  document.addEventListener('keydown', e => {
    if (e.key === 'Escape') closeMenu();
  });

  document.addEventListener('click', e => {
    if (!header.contains(e.target)) closeMenu();
  });

  window.addEventListener('resize', () => {
    if (window.innerWidth > 600) closeMenu();
  });
});

/* Latest Touchline piece: Sabah FK — keep homepage/archive in sync without changing page structure. */
document.addEventListener('DOMContentLoaded', () => {
  const slug = 'who-are-sabah-fk.html';
  const title = 'Who Are Sabah FK? Meet Manchester United’s Champions League Wildcard';
  const subtitle = 'They were founded in 2017, have already dethroned Qarabağ and scored more goals than anyone in Champions League qualifying. Now Old Trafford is next.';
  const image = 'https://sabahfc.az/static/dist/img/sabahfc_meta.png';

  /* Homepage latest panel. The displaced latest article becomes a normal Irish card. */
  const featured = document.querySelector('.featured');
  if (featured) {
    const latestButton = document.querySelector('.hero-actions .btn-primary');
    if (latestButton) latestButton.href = slug;

    const pill = featured.querySelector('.pill');
    const heading = featured.querySelector('h2');
    const dek = featured.querySelector('p');
    const read = featured.querySelector('.read');
    const art = featured.querySelector('.featured-art');
    if (pill) pill.textContent = 'Latest · World';
    if (heading) heading.textContent = title;
    if (dek) dek.textContent = subtitle;
    if (read) read.href = slug;
    if (art) {
      art.style.backgroundImage = `url('${image}')`;
      art.style.backgroundSize = 'cover';
      art.style.backgroundPosition = 'center';
    }

    const irishGrid = document.querySelector('#irish .grid');
    if (irishGrid && !irishGrid.querySelector('[href="grow-your-own-loi-academies.html"]')) {
      const card = document.createElement('a');
      card.className = 'card';
      card.href = 'grow-your-own-loi-academies.html';
      card.innerHTML = `<div class="card-art" style="background-image:url('https://substackcdn.com/image/fetch/$s_!EWu1!,f_auto,q_auto:good,fl_progressive:steep/https%3A%2F%2Fsubstack-post-media.s3.amazonaws.com%2Fpublic%2Fimages%2F6281a6bf-e4cd-409a-968a-862b1cf1f4a9_2560x1340.jpeg');background-size:cover;background-position:center;"></div><div class="card-body"><span class="pill">Ireland</span><h3>Grow Your Own: Why LOI Clubs Must Back The Academy</h3><p>The League of Ireland is finally making serious money from young players. If that’s where the game is heading, why aren’t more clubs spending now to produce the next Mason Melia?</p><div class="meta"><span>31 Aug 2026</span><span class="dot"></span><span>7 min read</span></div></div>`;
      irishGrid.prepend(card);
    }

    const worldCount = document.querySelector('#world .view-all');
    if (worldCount) worldCount.textContent = '46 pieces · View all →';
  }

  /* Archive: total, World count, and a new Azerbaijan dropdown at the top of World. */
  if (document.body.querySelector('.page-hero') && document.querySelector('#world .cat-panel')) {
    const heroPill = document.querySelector('.page-hero .pill');
    if (heroPill) heroPill.textContent = '134 pieces and counting';

    const world = document.querySelector('#world');
    const worldCount = world?.querySelector('.category-count');
    if (worldCount) worldCount.textContent = '46 pieces';

    const countryList = world?.querySelector('.country-list');
    if (countryList && !Array.from(countryList.querySelectorAll('.country-title')).some(el => el.textContent.trim() === 'Azerbaijan')) {
      const block = document.createElement('div');
      block.className = 'country-block';
      block.innerHTML = `<div class="country-head" onclick="toggleCountry(this)" role="button" tabindex="0" aria-expanded="false"><div class="country-head-left"><span class="country-chevron"></span><h4 class="country-title">Azerbaijan</h4></div><span class="country-count">1 piece</span></div><div class="country-panel"><div class="country-panel-inner"><ul class="arch-list"><li class="arch-item"><a href="${slug}"><span class="arch-copy"><span class="arch-title">${title}</span><span class="arch-description">${subtitle}</span></span><span class="arch-meta"><time class="arch-date" datetime="2026-09-02">2 Sep 2026</time><span class="arch-arrow">→</span></span></a></li></ul></div></div>`;
      countryList.prepend(block);
    }
  }
});
