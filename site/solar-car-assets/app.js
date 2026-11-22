'use strict';
(() => {
  const config = window.SOLAR_CAR || {};
  if (/^https:\/\/github\.com\/[A-Za-z0-9_.-]+\/[A-Za-z0-9_.-]+\/?$/.test(config.githubUrl || '')) {
    document.querySelectorAll('[data-source-link]').forEach(link => {
      link.href = config.githubUrl;
      link.target = '_blank';
      link.rel = 'noopener';
    });
    const title = document.querySelector('[data-source-title]');
    if (title) title.textContent = 'Исходники на GitHub';
    const heroLink = document.querySelector('.hero [data-source-link]');
    if (heroLink) heroLink.textContent = 'Исходники на GitHub';
  }
  const id = config.youtubeId;
  if (!/^[A-Za-z0-9_-]{11}$/.test(id || '')) return;
  const section = document.getElementById('video');
  const container = document.getElementById('video-container');
  section.hidden = false;
  const button = document.createElement('button');
  button.type = 'button'; button.className = 'video-load';
  button.setAttribute('aria-label', 'Загрузить видео поездки в плеере YouTube');
  const poster = document.createElement('img');
  poster.src = 'solar-car-assets/car-hero.webp'; poster.alt = ''; poster.loading = 'lazy';
  const label = document.createElement('span'); label.textContent = 'Смотреть поездку';
  button.append(poster, label);
  button.addEventListener('click', () => {
    const iframe = document.createElement('iframe');
    iframe.src = `https://www.youtube-nocookie.com/embed/${id}?autoplay=1&rel=0`;
    iframe.title = 'Солнечная машинка — видео поездки';
    iframe.allow = 'accelerometer; autoplay; encrypted-media; gyroscope; picture-in-picture; fullscreen';
    iframe.allowFullscreen = true;
    iframe.referrerPolicy = 'strict-origin-when-cross-origin';
    container.replaceChildren(iframe);
  }, { once: true });
  container.append(button);
  document.getElementById('youtube-link').href = `https://www.youtube.com/watch?v=${id}`;
})();
