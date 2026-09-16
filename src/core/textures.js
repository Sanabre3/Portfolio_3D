import * as THREE from 'three';

function canvas(w, h) {
  const c = document.createElement('canvas');
  c.width = w; c.height = h;
  return c;
}

function grain(g, w, h, amount) {
  const im = g.getImageData(0, 0, w, h);
  for (let i = 0; i < w * h; i++) {
    const d = i * 4, n = (Math.random() - 0.5) * amount;
    im.data[d] = Math.max(0, Math.min(255, im.data[d] + n));
    im.data[d + 1] = Math.max(0, Math.min(255, im.data[d + 1] + n));
    im.data[d + 2] = Math.max(0, Math.min(255, im.data[d + 2] + n));
  }
  g.putImageData(im, 0, 0);
}

// Tabua corrida: pranchas com tom variado, veio em bezier e emendas.
export function woodTexture() {
  const c = canvas(512, 512), g = c.getContext('2d');
  g.fillStyle = '#6A4E33'; g.fillRect(0, 0, 512, 512);
  for (let i = 0; i < 8; i++) {
    const y = i * 64, t = 0.82 + Math.random() * 0.3;
    g.fillStyle = `rgb(${Math.round(106 * t)},${Math.round(78 * t)},${Math.round(51 * t)})`;
    g.fillRect(0, y, 512, 63);
    g.strokeStyle = 'rgba(28,18,10,.55)'; g.lineWidth = 2;
    g.beginPath(); g.moveTo(0, y + 63); g.lineTo(512, y + 63); g.stroke();
    for (let k = 0; k < 26; k++) {
      const dark = Math.random() < 0.5;
      g.strokeStyle = `rgba(${dark ? '30,20,10' : '200,170,130'},${0.05 + Math.random() * 0.1})`;
      g.lineWidth = 1 + Math.random() * 1.6;
      const yy = y + Math.random() * 60;
      g.beginPath(); g.moveTo(0, yy);
      g.bezierCurveTo(170, yy + (Math.random() - 0.5) * 7, 340, yy + (Math.random() - 0.5) * 7, 512, yy);
      g.stroke();
    }
    const sx = Math.random() * 512;
    g.strokeStyle = 'rgba(24,16,8,.5)'; g.lineWidth = 2;
    g.beginPath(); g.moveTo(sx, y); g.lineTo(sx, y + 63); g.stroke();
  }
  grain(g, 512, 512, 22);
  const t = new THREE.CanvasTexture(c);
  t.wrapS = t.wrapT = THREE.RepeatWrapping;
  t.colorSpace = THREE.SRGBColorSpace;
  t.anisotropy = 8;
  return t;
}

export function plasterTexture() {
  const c = canvas(256, 256), g = c.getContext('2d');
  g.fillStyle = '#9C8A6E'; g.fillRect(0, 0, 256, 256);
  for (let i = 0; i < 900; i++) {
    const dark = Math.random() < 0.5;
    g.fillStyle = `rgba(${dark ? '60,48,32' : '220,205,178'},${Math.random() * 0.1})`;
    g.beginPath();
    g.arc(Math.random() * 256, Math.random() * 256, Math.random() * 16 + 3, 0, 6.3);
    g.fill();
  }
  grain(g, 256, 256, 16);
  const t = new THREE.CanvasTexture(c);
  t.wrapS = t.wrapT = THREE.RepeatWrapping;
  t.colorSpace = THREE.SRGBColorSpace;
  return t;
}

export function rugTexture() {
  const c = canvas(256, 256), g = c.getContext('2d');
  g.fillStyle = '#6B463A'; g.fillRect(0, 0, 256, 256);
  g.strokeStyle = '#8A5140'; g.lineWidth = 14; g.strokeRect(16, 16, 224, 224);
  g.strokeStyle = '#5A3A30'; g.lineWidth = 6; g.strokeRect(34, 34, 188, 188);
  g.fillStyle = '#8A5140'; g.fillRect(96, 96, 64, 64);
  g.globalAlpha = 0.16;
  for (let i = 0; i < 256; i += 3) {
    g.strokeStyle = i % 6 ? '#2E1C16' : '#C79A78'; g.lineWidth = 1;
    g.beginPath(); g.moveTo(i, 0); g.lineTo(i, 256); g.stroke();
    g.beginPath(); g.moveTo(0, i); g.lineTo(256, i); g.stroke();
  }
  g.globalAlpha = 1;
  grain(g, 256, 256, 18);
  const t = new THREE.CanvasTexture(c);
  t.colorSpace = THREE.SRGBColorSpace;
  return t;
}

// Foto do cavalete. Troque por uma imagem real com THREE.TextureLoader se preferir.
export function photoTexture() {
  const c = canvas(256, 320), g = c.getContext('2d');
  const sky = g.createLinearGradient(0, 0, 0, 200);
  sky.addColorStop(0, '#E7B27A'); sky.addColorStop(1, '#B98A72');
  g.fillStyle = sky; g.fillRect(0, 0, 256, 320);
  g.fillStyle = '#F6D9A4'; g.beginPath(); g.arc(170, 120, 30, 0, 6.3); g.fill();
  g.fillStyle = '#5A4A46'; g.beginPath();
  g.moveTo(0, 230); g.lineTo(70, 160); g.lineTo(130, 215); g.lineTo(190, 155); g.lineTo(256, 225);
  g.lineTo(256, 320); g.lineTo(0, 320); g.closePath(); g.fill();
  g.fillStyle = '#3A3230'; g.beginPath();
  g.moveTo(0, 262); g.lineTo(90, 212); g.lineTo(180, 268); g.lineTo(256, 232);
  g.lineTo(256, 320); g.lineTo(0, 320); g.closePath(); g.fill();
  grain(g, 256, 320, 14);
  const t = new THREE.CanvasTexture(c);
  t.colorSpace = THREE.SRGBColorSpace;
  return t;
}

export function labelTexture(text) {
  const c = canvas(512, 128), g = c.getContext('2d');
  g.clearRect(0, 0, 512, 128);
  g.font = '600 52px "Barlow Condensed", sans-serif';
  g.textAlign = 'center'; g.textBaseline = 'middle';
  g.lineWidth = 8; g.strokeStyle = 'rgba(8,6,4,.85)'; g.strokeText(text, 256, 64);
  g.fillStyle = '#F2EAD6'; g.fillText(text, 256, 64);
  const t = new THREE.CanvasTexture(c);
  t.colorSpace = THREE.SRGBColorSpace;
  return t;
}
