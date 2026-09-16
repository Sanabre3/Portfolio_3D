import { TUNE } from '../config/theme.js';

// Estado de entrada compartilhado. mx/mz vao de -1 a 1 em espaco de tela.
export const input = { mx: 0, mz: 0, running: false };
export const isTouch = matchMedia('(hover:none)').matches;

const keys = {};
const stick = { x: 0, y: 0 };

export function attachControls({ dom, rig, onInteract, onClose, isPanelOpen }) {
  if (!isTouch) document.body.classList.add('desk');

  addEventListener('keydown', e => {
    keys[e.key.toLowerCase()] = true;
    if (e.key === 'Shift') input.running = true;
    if (e.key.toLowerCase() === 'e') isPanelOpen() ? onClose() : onInteract();
    if (e.key === 'Escape') onClose();
    if ([' ', 'ArrowUp', 'ArrowDown', 'ArrowLeft', 'ArrowRight'].includes(e.key)) e.preventDefault();
  });
  addEventListener('keyup', e => {
    keys[e.key.toLowerCase()] = false;
    if (e.key === 'Shift') input.running = false;
  });

  // Arraste gira a camera. Pinca faz zoom.
  let drag = null, pinch = 0;
  dom.addEventListener('pointerdown', e => {
    drag = { x: e.clientX, y: e.clientY, id: e.pointerId };
    dom.setPointerCapture(e.pointerId);
  });
  dom.addEventListener('pointermove', e => {
    if (!drag || drag.id !== e.pointerId) return;
    rig.orbit(-(e.clientX - drag.x) * 0.006, (e.clientY - drag.y) * 0.004);
    drag.x = e.clientX; drag.y = e.clientY;
  });
  ['pointerup', 'pointercancel'].forEach(t => dom.addEventListener(t, () => { drag = null; }));
  dom.addEventListener('wheel', e => rig.zoom(e.deltaY * 0.0022), { passive: true });
  dom.addEventListener('touchmove', e => {
    if (e.touches.length === 2) {
      const d = Math.hypot(e.touches[0].clientX - e.touches[1].clientX,
                           e.touches[0].clientY - e.touches[1].clientY);
      if (pinch) rig.zoom((pinch - d) * 0.012);
      pinch = d; drag = null;
    }
  }, { passive: true });
  dom.addEventListener('touchend', () => { pinch = 0; });

  // Direcional analogico
  const stickEl = document.getElementById('stick');
  const knob = document.getElementById('knob');
  let sid = null;
  const move = e => {
    const t = [...e.touches].find(t => t.identifier === sid);
    if (!t) return;
    const r = stickEl.getBoundingClientRect();
    let dx = t.clientX - (r.left + r.width / 2);
    let dy = t.clientY - (r.top + r.height / 2);
    const d = Math.hypot(dx, dy), max = 48;
    if (d > max) { dx = dx / d * max; dy = dy / d * max; }
    knob.style.transform = `translate(${dx}px,${dy}px)`;
    stick.x = dx / max; stick.y = dy / max;
  };
  stickEl.addEventListener('touchstart', e => { sid = e.changedTouches[0].identifier; move(e); e.preventDefault(); }, { passive: false });
  stickEl.addEventListener('touchmove', e => { move(e); e.preventDefault(); }, { passive: false });
  ['touchend', 'touchcancel'].forEach(t => stickEl.addEventListener(t, () => {
    sid = null; stick.x = 0; stick.y = 0; knob.style.transform = 'translate(0,0)';
  }));

  const runBtn = document.getElementById('run');
  runBtn.onclick = () => { input.running = !input.running; runBtn.classList.toggle('on', input.running); };
  document.getElementById('act').onclick = () => isPanelOpen() ? onClose() : onInteract();
}

export function readInput() {
  let x = 0, z = 0;
  if (keys['w'] || keys['arrowup']) z -= 1;
  if (keys['s'] || keys['arrowdown']) z += 1;
  if (keys['a'] || keys['arrowleft']) x -= 1;
  if (keys['d'] || keys['arrowright']) x += 1;
  x += stick.x; z += stick.y;
  input.mx = x; input.mz = z;
  return Math.min(1, Math.hypot(x, z));
}

export const maxSpeed = () => input.running ? TUNE.run : TUNE.walk;
