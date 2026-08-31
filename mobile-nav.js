document.addEventListener('DOMContentLoaded', () => {
  const header = document.querySelector('header');
  const navRow = header?.querySelector('.nav-row');
  const desktopNav = header?.querySelector('nav');
  const subscribe = header?.querySelector('.nav-cta');
  if (!header || !navRow || !desktopNav) return;

  const style = document.createElement('style');
  style.textContent = `
    .mobile-menu-btn,.mobile-menu-panel{display:none}
    @media(max-width:600px){
      header{position:sticky;top:0;overflow:visible}
      .nav-row{flex-wrap:nowrap!important;position:relative}
      header nav{display:none!important}
      header .nav-cta{display:none!important}
      .mobile-menu-btn{display:inline-flex;align-items:center;gap:9px;border:1px solid rgba(33,31,26,.12);background:#fff;color:#1c1a17;border-radius:999px;padding:9px 14px;font:600 13px 'Inter',sans-serif;cursor:pointer;margin-left:auto}
      .mobile-menu-icon{width:16px;height:12px;display:flex;flex-direction:column;justify-content:space-between}
      .mobile-menu-icon span{display:block;height:2px;border-radius:2px;background:currentColor;transition:transform .2s,opacity .2s}
      .mobile-menu-btn[aria-expanded='true'] .mobile-menu-icon span:nth-child(1){transform:translateY(5px) rotate(45deg)}
      .mobile-menu-btn[aria-expanded='true'] .mobile-menu-icon span:nth-child(2){opacity:0}
      .mobile-menu-btn[aria-expanded='true'] .mobile-menu-icon span:nth-child(3){transform:translateY(-5px) rotate(-45deg)}
      .mobile-menu-panel{position:absolute;display:none;top:calc(100% + 14px);left:0;right:0;background:#fbf3e7;border:1px solid rgba(33,31,26,.10);border-radius:16px;padding:10px;box-shadow:0 18px 40px rgba(33,31,26,.14);z-index:999}
      .mobile-menu-panel.open{display:block}
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
