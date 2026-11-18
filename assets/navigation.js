// The anchors and directory are rendered in HTML. These enhancements also support
// bookmarked subsections inside disclosures and return focus to the reading position.
(() => {
  const nav = document.querySelector('.desk-nav');
  const directory = nav.querySelector('.desk-directory');
  const summary = directory.querySelector('summary');
  const sections = Array.from(document.querySelectorAll('main > section[aria-labelledby]'));
  const links = Array.from(nav.querySelectorAll('a[href^="#"]'));
  let active = '';
  let pending = false;

  function setActive() {
    pending = false;
    const edge = nav.offsetHeight + 28;
    const current = sections.filter(section => section.getBoundingClientRect().top <= edge).pop() || sections[0];
    const next = current.getAttribute('aria-labelledby');
    if (active === next) return;
    active = next;
    for (const link of links) {
      if (link.hash === '#' + next) link.setAttribute('aria-current', 'location');
      else link.removeAttribute('aria-current');
    }
  }

  function track() {
    if (!pending) {
      pending = true;
      requestAnimationFrame(setActive);
    }
  }

  function openPath(target) {
    for (let node = target; node; node = node.parentElement) {
      if (node.tagName === 'DETAILS') node.open = true;
    }
  }

  function focusTarget(target) {
    if (target.tagName === 'DETAILS') target = target.querySelector('summary');
    if (!target.hasAttribute('tabindex') && target.tagName !== 'SUMMARY') target.tabIndex = -1;
    target.focus({preventScroll: true});
  }

  nav.addEventListener('click', event => {
    const link = event.target.closest('a[href^="#"]');
    if (!link || event.ctrlKey || event.metaKey || event.shiftKey || event.altKey) return;
    const target = document.getElementById(link.hash.slice(1));
    if (!target) return;
    directory.open = false;
    openPath(target);
    focusTarget(target);
  });

  document.addEventListener('click', event => {
    if (directory.open && !directory.contains(event.target)) directory.open = false;
  });
  document.addEventListener('keydown', event => {
    if (event.key === 'Escape' && directory.open) {
      directory.open = false;
      summary.focus();
    }
  });

  function followFragment() {
    const target = document.getElementById(location.hash.slice(1));
    if (target && links.some(link => link.hash === location.hash)) {
      openPath(target);
      target.scrollIntoView({block: 'start', behavior: 'instant'});
    }
    track();
  }
  window.addEventListener('scroll', track, {passive: true});
  window.addEventListener('resize', track);
  window.addEventListener('hashchange', followFragment);
  window.addEventListener('load', followFragment, {once: true});
  track();
})();
