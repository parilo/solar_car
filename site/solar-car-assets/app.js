'use strict';
(() => {
  const page = document.documentElement;
  const languages = new Set(['en', 'ru', 'zh', 'fr', 'es']);
  const storageKey = 'solar-car-language';
  const currentLanguage = page.dataset.language;
  const home = new URL(page.dataset.home, location.href);
  let savedLanguage;
  try { savedLanguage = localStorage.getItem(storageKey); } catch (_) { /* Storage can be disabled. */ }
  // English is the default, regardless of the browser's language. Only an
  // explicit previous choice changes a later visit to the root page.
  if (currentLanguage === 'en' && languages.has(savedLanguage) && savedLanguage !== 'en') {
    const destination = new URL(`${savedLanguage}/`, home);
    destination.hash = location.hash;
    location.replace(destination.href);
    return;
  }
  try { localStorage.setItem(storageKey, currentLanguage); } catch (_) { /* Links still work. */ }
  const picker = document.querySelector('.language-picker');
  document.querySelectorAll('[data-language-choice]').forEach(link => {
    // Keep the reader at the same section when changing language.
    const updateHash = () => { link.hash = location.hash; };
    updateHash();
    window.addEventListener('hashchange', updateHash);
    link.addEventListener('click', () => {
      try { localStorage.setItem(storageKey, link.dataset.languageChoice); } catch (_) { /* Optional. */ }
    });
  });
  document.addEventListener('click', event => {
    if (picker && !picker.contains(event.target)) picker.open = false;
  });
  document.addEventListener('keydown', event => {
    if (event.key === 'Escape' && picker?.open) {
      picker.open = false;
      picker.querySelector('summary').focus();
    }
  });
  const config = window.SOLAR_CAR || {};
  if (/^https:\/\/github\.com\/[A-Za-z0-9_.-]+\/[A-Za-z0-9_.-]+\/?$/.test(config.githubUrl || '')) {
    document.querySelectorAll('[data-source-link]').forEach(link => {
      link.href = config.githubUrl;
      link.target = '_blank';
      link.rel = 'noopener';
    });
  }
  const id = config.youtubeId;
  if (!/^[A-Za-z0-9_-]{11}$/.test(id || '')) return;
  const section = document.getElementById('video');
  const container = document.getElementById('video-container');
  section.hidden = false;
  const button = document.createElement('button');
  button.type = 'button'; button.className = 'video-load';
  button.setAttribute('aria-label', container.dataset.loadLabel);
  const poster = document.createElement('img');
  poster.src = container.dataset.poster; poster.alt = ''; poster.loading = 'eager';
  poster.fetchPriority = 'high';
  const label = document.createElement('span'); label.textContent = container.dataset.playLabel;
  button.append(poster, label);
  button.addEventListener('click', () => {
    const iframe = document.createElement('iframe');
    iframe.src = `https://www.youtube-nocookie.com/embed/${id}?autoplay=1&rel=0`;
    iframe.title = container.dataset.iframeTitle;
    iframe.allow = 'accelerometer; autoplay; encrypted-media; gyroscope; picture-in-picture; fullscreen';
    iframe.allowFullscreen = true;
    iframe.referrerPolicy = 'strict-origin-when-cross-origin';
    container.replaceChildren(iframe);
  }, { once: true });
  container.append(button);
  document.getElementById('youtube-link').href = `https://www.youtube.com/watch?v=${id}`;
})();
