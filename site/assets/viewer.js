// Full-size viewer. Any element with [data-lb] opens it.
// Wide pieces (panoramas) open at full screen height and scroll sideways,
// with an overview strip that shows where you are.
(function () {
  // one entry per piece, even when several buttons open the same piece
  const triggers = Array.from(document.querySelectorAll('[data-lb]'));
  if (!triggers.length) return;
  const items = [], indexOf = new Map();
  triggers.forEach((el) => {
    if (!indexOf.has(el.dataset.full)) { indexOf.set(el.dataset.full, items.length); items.push(el); }
  });

  const icon = (d) => `<svg aria-hidden="true" width="20" height="20" viewBox="0 0 20 20" fill="none" stroke="currentColor" stroke-width="1.8"><path d="${d}"/></svg>`;
  const L = 'M12.5 4 6.5 10l6 6', R = 'M7.5 4l6 6-6 6', X = 'M4 4l12 12M16 4L4 16';

  const lb = document.createElement('div');
  lb.className = 'lb';
  lb.hidden = true;
  lb.setAttribute('role', 'dialog');
  lb.setAttribute('aria-modal', 'true');
  lb.innerHTML = `
    <div class="lb-top">
      <div class="lb-title"><strong></strong><span></span></div>
      <div class="lb-tools">
        <button type="button" class="lb-btn lb-prev" aria-label="Previous piece">${icon(L)}</button>
        <button type="button" class="lb-btn lb-next" aria-label="Next piece">${icon(R)}</button>
        <span class="lb-sep" aria-hidden="true"></span>
        <button type="button" class="lb-btn lb-close" aria-label="Close">${icon(X)}</button>
      </div>
    </div>
    <div class="lb-stage">
      <div class="lb-scroller" tabindex="0"><img alt="" draggable="false"></div>
      <button type="button" class="lb-nudge left" aria-label="Scroll left">${icon(L)}</button>
      <button type="button" class="lb-nudge right" aria-label="Scroll right">${icon(R)}</button>
    </div>
    <div class="lb-foot">
      <span class="lb-hint">Scroll, swipe or drag sideways. Click the overview to jump.</span>
      <button type="button" class="lb-mini" aria-label="Overview: click to jump to that part of the piece"><img alt=""><i></i></button>
    </div>`;
  document.body.appendChild(lb);

  const $ = (s) => lb.querySelector(s);
  const title = $('.lb-title strong'), count = $('.lb-title span');
  const scroller = $('.lb-scroller'), img = $('.lb-scroller img');
  const mini = $('.lb-mini'), miniImg = $('.lb-mini img'), rect = $('.lb-mini i');
  const prevB = $('.lb-prev'), nextB = $('.lb-next'), closeB = $('.lb-close');
  const nudgeL = $('.lb-nudge.left'), nudgeR = $('.lb-nudge.right');
  let idx = 0, wide = false, lastFocus = null;

  function update() {
    if (!wide) return;
    const sw = Math.max(scroller.scrollWidth, 1), cw = scroller.clientWidth, sl = scroller.scrollLeft;
    const w = Math.min(100, cw / sw * 100);
    rect.style.width = w + '%';
    rect.style.left = Math.min(100 - w, sl / sw * 100) + '%';
    nudgeL.classList.toggle('on', sl > 4);
    nudgeR.classList.toggle('on', sl + cw < sw - 4);
  }

  function show(i) {
    idx = (i + items.length) % items.length;
    const el = items[idx];
    const w = +el.dataset.w, h = +el.dataset.h;
    wide = w / h > 2.2;
    lb.classList.toggle('is-wide', wide);
    title.textContent = el.dataset.title || '';
    count.textContent = `${idx + 1} of ${items.length}`;
    lb.setAttribute('aria-label', (el.dataset.title || 'Artwork') + ', full size');
    img.alt = el.dataset.title || '';
    img.style.maxHeight = wide ? h + 'px' : '';
    img.src = el.dataset.full;
    miniImg.src = wide ? el.dataset.thumb : '';
    prevB.disabled = items.length < 2;
    nextB.disabled = items.length < 2;
    scroller.scrollLeft = 0;
    if (img.complete) update();
  }

  function open(i) {
    lastFocus = document.activeElement;
    lb.hidden = false;
    document.body.classList.add('lb-open');
    show(i);
    closeB.focus();
  }

  function close() {
    lb.hidden = true;
    document.body.classList.remove('lb-open');
    img.removeAttribute('src');
    if (lastFocus) lastFocus.focus();
  }

  triggers.forEach((el) => el.addEventListener('click', (e) => { e.preventDefault(); open(indexOf.get(el.dataset.full)); }));
  closeB.addEventListener('click', close);
  prevB.addEventListener('click', () => show(idx - 1));
  nextB.addEventListener('click', () => show(idx + 1));
  img.addEventListener('load', () => { scroller.scrollLeft = 0; update(); });
  scroller.addEventListener('scroll', update, { passive: true });
  window.addEventListener('resize', update);
  nudgeL.addEventListener('click', () => scroller.scrollBy({ left: -0.7 * scroller.clientWidth, behavior: 'smooth' }));
  nudgeR.addEventListener('click', () => scroller.scrollBy({ left: 0.7 * scroller.clientWidth, behavior: 'smooth' }));
  mini.addEventListener('click', (e) => {
    const r = miniImg.getBoundingClientRect();
    const ratio = Math.min(1, Math.max(0, (e.clientX - r.left) / r.width));
    scroller.scrollTo({ left: ratio * scroller.scrollWidth - scroller.clientWidth / 2, behavior: 'smooth' });
  });

  // click and drag to pan (mouse only; touch scrolls natively)
  let dragX = 0, dragSL = 0, dragging = false;
  scroller.addEventListener('pointerdown', (e) => {
    if (!wide || e.pointerType !== 'mouse') return;
    dragging = true; dragX = e.clientX; dragSL = scroller.scrollLeft;
    scroller.classList.add('dragging'); scroller.setPointerCapture(e.pointerId); e.preventDefault();
  });
  scroller.addEventListener('pointermove', (e) => { if (dragging) scroller.scrollLeft = dragSL - (e.clientX - dragX); });
  const stop = () => { dragging = false; scroller.classList.remove('dragging'); };
  scroller.addEventListener('pointerup', stop);
  scroller.addEventListener('pointercancel', stop);

  // click the dark area around a regular piece to close
  scroller.addEventListener('click', (e) => { if (!wide && e.target === scroller) close(); });

  document.addEventListener('keydown', (e) => {
    if (lb.hidden) return;
    if (e.key === 'Escape') { e.preventDefault(); close(); return; }
    if (e.key === 'ArrowRight' || e.key === 'ArrowLeft') {
      const dir = e.key === 'ArrowRight' ? 1 : -1;
      if (wide) {
        const atEnd = dir > 0 ? scroller.scrollLeft + scroller.clientWidth >= scroller.scrollWidth - 4 : scroller.scrollLeft <= 4;
        if (!atEnd) { e.preventDefault(); scroller.scrollBy({ left: dir * 0.35 * scroller.clientWidth, behavior: 'smooth' }); return; }
      }
      e.preventDefault(); show(idx + dir);
    }
    if (e.key === 'Tab') { // keep focus inside the viewer
      const f = Array.from(lb.querySelectorAll('button:not([disabled]), [tabindex="0"]')).filter((n) => n.offsetParent !== null);
      const first = f[0], last = f[f.length - 1];
      if (e.shiftKey && document.activeElement === first) { e.preventDefault(); last.focus(); }
      else if (!e.shiftKey && document.activeElement === last) { e.preventDefault(); first.focus(); }
    }
  });
})();
