import { isTouch } from '../player/controls.js';

export class HUD {
  constructor(total) {
    document.getElementById('total').textContent = total;
    this.prompt = document.getElementById('prompt');
    this.title = document.getElementById('ptitle');
    this.key = document.getElementById('pkey');
    this.room = document.getElementById('room');
    this.toastEl = document.getElementById('toast');
    this.flash = document.getElementById('flash');
    this.current = null;
  }

  setActive(station) {
    if (station === this.current) return;
    this.current = station;
    if (station) {
      this.title.textContent = station.tag;
      this.key.textContent = isTouch ? 'toque em VER' : 'pressione E';
      this.prompt.classList.add('on');
      this.room.textContent = station.tag.toLowerCase();
    } else {
      this.prompt.classList.remove('on');
      this.room.textContent = 'estúdio';
    }
  }

  toast(msg, ms = 6000) {
    this.toastEl.textContent = msg;
    this.toastEl.classList.add('on');
    clearTimeout(this._t);
    this._t = setTimeout(() => this.toastEl.classList.remove('on'), ms);
  }

  flashIn()  { this.flash.style.opacity = '.92'; }
  flashOut() { this.flash.style.opacity = '0'; }
}

// Tela de entrada. Espera o personagem carregar (loading: Promise), mostra o
// progresso na barra e chama onStart depois que o usuario clica.
export function gate(renderer, scene, camera, onStart, loading = Promise.resolve()) {
  const fill = document.getElementById('barfill');
  const enter = document.getElementById('enter');
  fill.style.width = '10%';
  gate.progress = f => { fill.style.width = (10 + f * 70).toFixed(0) + '%'; };
  loading.finally(() => {
    fill.style.width = '85%';
    renderer.compile(scene, camera);   // pre-compila shaders para nao travar no primeiro frame
    requestAnimationFrame(() => {
      fill.style.width = '100%';
      enter.classList.add('ready');
    });
  });
  enter.onclick = () => {
    document.getElementById('gate').classList.add('off');
    onStart();
  };
}
