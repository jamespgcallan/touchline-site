(function () {
  var buttons = document.querySelectorAll('[data-share-button]');
  if (!buttons.length) return;

  var canonical = document.querySelector('link[rel="canonical"]');
  var titleElement = document.querySelector('h1');
  var articleTitle = titleElement ? titleElement.textContent.trim() : document.title;
  var cleanUrl = canonical ? canonical.href : window.location.href;
  var shareUrl = new URL(cleanUrl, window.location.href);

  // Keep this value aligned with the article's og:url when deliberately refreshing a failed social-card cache.
  shareUrl.searchParams.set('share', 'card2');

  var shareData = {
    title: articleTitle,
    text: articleTitle,
    url: shareUrl.href
  };

  function showCopied() {
    buttons.forEach(function (button) {
      var label = button.querySelector('span');
      if (label) label.textContent = 'Link copied';
      button.setAttribute('aria-label', 'Article link copied');
    });
    window.setTimeout(function () {
      buttons.forEach(function (button) {
        var label = button.querySelector('span');
        if (label) label.textContent = 'Share';
        button.setAttribute('aria-label', 'Share this article');
      });
    }, 1800);
  }

  function copyFallback() {
    if (navigator.clipboard && window.isSecureContext) {
      return navigator.clipboard.writeText(shareData.url);
    }
    var field = document.createElement('textarea');
    field.value = shareData.url;
    field.setAttribute('readonly', '');
    field.style.position = 'fixed';
    field.style.opacity = '0';
    document.body.appendChild(field);
    field.select();
    document.execCommand('copy');
    document.body.removeChild(field);
    return Promise.resolve();
  }

  buttons.forEach(function (button) {
    button.addEventListener('click', async function () {
      if (navigator.share) {
        try {
          await navigator.share(shareData);
          return;
        } catch (error) {
          if (error && error.name === 'AbortError') return;
        }
      }
      try {
        await copyFallback();
        showCopied();
      } catch (error) {
        window.prompt('Copy this article link:', shareData.url);
      }
    });
  });
}());
