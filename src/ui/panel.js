// Painel do projeto. Renderiza o site real num iframe quando a estacao tem url.
export class Panel {
  constructor() {
    this.el = document.getElementById('panel');
    this.frame = document.getElementById('frame');
    this.site = document.getElementById('site');
    this.load = document.getElementById('load');
    this.timer = null;
    this.visited = {};

    this.site.addEventListener('load', () => {
      if (this.site.src) this.frame.classList.add('ready');
    });
    document.getElementById('close').onclick = () => this.close();
    this.el.onclick = e => { if (e.target === this.el) this.close(); };
  }

  isOpen() { return this.el.classList.contains('on'); }

  open(s) {
    this.visited[s.id] = true;
    document.getElementById('seen').textContent = Object.keys(this.visited).length;
    document.getElementById('cyr').textContent = s.year;
    document.getElementById('cti').textContent = s.tag;
    document.getElementById('cds').textContent = s.desc;

    const stack = document.getElementById('cst');
    stack.innerHTML = '';
    s.stack.forEach(k => {
      const e = document.createElement('span');
      e.textContent = k;
      stack.appendChild(e);
    });

    const go = document.getElementById('cgo');
    clearTimeout(this.timer);
    this.frame.classList.remove('ready');

    if (s.url) {
      this.frame.classList.remove('none');
      this.load.textContent = 'carregando o site…';
      this.site.src = s.url;
      go.href = s.url;
      go.style.display = '';
      // Sites com X-Frame-Options nao carregam aqui. Depois de 5s, avisa.
      this.timer = setTimeout(() => {
        if (!this.frame.classList.contains('ready')) {
          this.load.textContent = 'Este site não permite ser exibido aqui dentro. Use o botão abaixo para abrir em nova aba.';
        }
      }, 5000);
    } else {
      this.frame.classList.add('none');
      this.site.src = '';
      go.style.display = 'none';
    }

    this.el.classList.add('on');
    document.getElementById('close').focus();
  }

  close() {
    this.el.classList.remove('on');
    clearTimeout(this.timer);
    // Descarrega o iframe para o site nao continuar rodando atras do jogo.
    setTimeout(() => {
      if (!this.isOpen()) { this.site.src = ''; this.frame.classList.remove('ready'); }
    }, 300);
  }
}
