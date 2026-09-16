(function () {
  var buttons = document.querySelectorAll('[data-share-button]');
  if (!buttons.length) return;

  var canonical = document.querySelector('link[rel="canonical"]');
  var ogUrl = document.querySelector('meta[property="og:url"]');
  var titleElement = document.querySelector('h1');
  var articleTitle = titleElement ? titleElement.textContent.trim() : document.title;
  var cleanUrl = ogUrl && ogUrl.content ? ogUrl.content : (canonical ? canonical.href : window.location.href);
  var shareUrl;

  try {
    shareUrl = new URL(cleanUrl, window.location.href);
  } catch (error) {
    shareUrl = new URL(window.location.href);
  }

  // Keep the clean canonical URL shareable while retaining the existing
  // social-card cache-busting parameter used across Touchline articles.
  if (!shareUrl.searchParams.has('share')) {
    shareUrl.searchParams.set('share', 'card3');
  }

  var shareData = {
    title: articleTitle,
    text: articleTitle,
    url: shareUrl.href
  };

  function labelNode(button) {
    var existing = button.querySelector('[data-share-label]') || button.querySelector('span');
    if (existing) return existing;

    // Some older article templates use plain button text rather than a span.
    // Wrap that text so success feedback is visible without removing any icons.
    var text = '';
    Array.prototype.slice.call(button.childNodes).forEach(function (node) {
      if (node.nodeType === Node.TEXT_NODE && node.textContent.trim()) {
        text += node.textContent.trim();
        button.removeChild(node);
      }
    });

    var span = document.createElement('span');
    span.setAttribute('data-share-label', '');
    span.textContent = text || 'Share article';
    button.appendChild(span);
    return span;
  }

  buttons.forEach(function (button) {
    var label = labelNode(button);
    button.dataset.shareDefaultLabel = label.textContent || 'Share article';
    button.setAttribute('aria-label', button.getAttribute('aria-label') || 'Share this article');
  });

  function showStatus(message) {
    buttons.forEach(function (button) {
      labelNode(button).textContent = message;
    });

    window.setTimeout(function () {
      buttons.forEach(function (button) {
        labelNode(button).textContent = button.dataset.shareDefaultLabel || 'Share article';
        button.setAttribute('aria-label', 'Share this article');
      });
    }, 1800);
  }

  function copyFallback() {
    if (navigator.clipboard && window.isSecureContext) {
      return navigator.clipboard.writeText(shareData.url);
    }

    return new Promise(function (resolve, reject) {
      var field = document.createElement('textarea');
      field.value = shareData.url;
      field.setAttribute('readonly', '');
      field.style.position = 'fixed';
      field.style.left = '-9999px';
      field.style.opacity = '0';
      document.body.appendChild(field);
      field.focus();
      field.select();

      var copied = false;
      try {
        copied = document.execCommand('copy');
      } catch (error) {
        copied = false;
      }

      document.body.removeChild(field);
      if (copied) resolve();
      else reject(new Error('Copy command failed'));
    });
  }

  buttons.forEach(function (button) {
    button.addEventListener('click', async function () {
      button.setAttribute('aria-label', 'Sharing article');

      if (navigator.share) {
        try {
          await navigator.share(shareData);
          showStatus('Shared ✓');
          return;
        } catch (error) {
          // Closing the native share sheet is intentional; restore the button.
          if (error && error.name === 'AbortError') {
            showStatus(button.dataset.shareDefaultLabel || 'Share article');
            return;
          }
          // If native sharing fails for another reason, fall through to copy.
        }
      }

      try {
        await copyFallback();
        button.setAttribute('aria-label', 'Article link copied');
        showStatus('Link copied ✓');
      } catch (error) {
        window.prompt('Copy this article link:', shareData.url);
        showStatus('Copy link');
      }
    });
  });
}());
