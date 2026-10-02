// Skin secreta.
//
// Fica bloqueada ate o visitante ver todas as estacoes (visitados N/N) ou digitar o
// codigo. Ao desbloquear, troca o avatar uma vez e avisa como alternar:
//   teclado -> tecla T
//   celular -> 5 toques rapidos no nome (canto superior esquerdo)
// O .glb da skin so e baixado na primeira troca (quem nao desbloqueia nao baixa nada).
//
// O codigo evita W, A, S, D, E e T para nao andar nem abrir painel enquanto e digitado.
const CODE = 'yuki';
const TAPS = 5, TAP_WINDOW = 2500;

export function setupEasterEgg({ total, getVisited, toast, onToggle, isTouch }) {
  let unlocked = false, typed = '', taps = [];
  const hint = isTouch ? 'Toque 5 vezes no nome para alternar.' : 'Pressione T para alternar.';

  function unlock(reason) {
    if (unlocked) return;
    unlocked = true;
    onToggle(); // dispara o download; o aviso abaixo substitui o "carregando…"
    toast(`${reason} Skin secreta liberada. ${hint}`, 7000);
  }

  addEventListener('keydown', e => {
    if (e.repeat) return;
    const k = e.key.toLowerCase();
    if (k.length === 1) {
      typed = (typed + k).slice(-CODE.length);
      if (typed === CODE) unlock('Código aceito.');
    }
    if (unlocked && k === 't') onToggle();
  });

  const plate = document.querySelector('#hud .plate');
  if (plate) {
    plate.style.pointerEvents = 'auto';
    plate.addEventListener('pointerdown', () => {
      const now = performance.now();
      taps = taps.filter(t => now - t < TAP_WINDOW);
      taps.push(now);
      if (taps.length >= TAPS) {
        taps = [];
        if (unlocked) onToggle();
      }
    });
  }

  // Chamado pelo main.js quando o painel fecha: todas as estacoes vistas libera a skin.
  return {
    check() { if (!unlocked && getVisited() >= total) unlock('Você visitou todas as estações.'); },
    isUnlocked: () => unlocked
  };
}
