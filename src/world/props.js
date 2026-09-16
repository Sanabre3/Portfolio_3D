import * as THREE from 'three';
import { woodTexture, photoTexture } from '../core/textures.js';

// Funcoes de animacao registradas pelos props. O loop chama cada uma com o tempo.
export const anims = [];

const wood = woodTexture();

// Paleta de materiais. Mexa aqui para mudar a cor de tudo de uma vez.
export const M = {
  wood:   new THREE.MeshStandardMaterial({ map: wood, roughness: 0.65 }),
  darkw:  new THREE.MeshStandardMaterial({ color: 0x3E2E20, roughness: 0.7 }),
  midw:   new THREE.MeshStandardMaterial({ color: 0x6B4F33, roughness: 0.75 }),
  manila: new THREE.MeshStandardMaterial({ color: 0xB8A275, roughness: 0.8 }),
  black:  new THREE.MeshStandardMaterial({ color: 0x17161A, roughness: 0.5 }),
  metal:  new THREE.MeshStandardMaterial({ color: 0x6A6862, roughness: 0.35, metalness: 0.75 }),
  red:    new THREE.MeshStandardMaterial({ color: 0x9C3428, roughness: 0.6 }),
  teal:   new THREE.MeshStandardMaterial({ color: 0x2F6B5C, roughness: 0.6 }),
  gold:   new THREE.MeshStandardMaterial({ color: 0xB08C3C, roughness: 0.4, metalness: 0.6 }),
  cloth:  new THREE.MeshStandardMaterial({ color: 0xB9A98A, roughness: 1 })
};
M.wood.map.repeat.set(1, 1);
M.wood.map.needsUpdate = true;

export function emissive(color, intensity) {
  return new THREE.MeshStandardMaterial({ color, emissive: color, emissiveIntensity: intensity, roughness: 0.4 });
}
export function box(w, h, d, mat, x, y, z, parent) {
  const m = new THREE.Mesh(new THREE.BoxGeometry(w, h, d), mat);
  m.position.set(x, y, z);
  m.castShadow = true; m.receiveShadow = true;
  parent.add(m);
  return m;
}
export function cyl(rt, rb, h, mat, x, y, z, parent, seg = 18) {
  const m = new THREE.Mesh(new THREE.CylinderGeometry(rt, rb, h, seg), mat);
  m.position.set(x, y, z);
  m.castShadow = true; m.receiveShadow = true;
  parent.add(m);
  return m;
}

// Cada builder recebe o grupo da estacao e devolve [largura, profundidade]
// em metros, usado para montar a caixa de colisao.
export const BUILD = {
  desk(g) {
    box(2.4, 0.08, 1.1, M.wood, 0, 0.76, 0, g);
    [[-1.1, -0.48], [1.1, -0.48], [-1.1, 0.48], [1.1, 0.48]]
      .forEach(p => box(0.09, 0.76, 0.09, M.darkw, p[0], 0.38, p[1], g));
    box(0.7, 0.68, 0.9, M.midw, 0.78, 0.38, 0, g);
    box(0.06, 0.4, 0.04, M.black, -0.5, 1.0, -0.1, g);
    box(0.9, 0.56, 0.05, M.black, -0.5, 1.32, -0.12, g);
    const scr = box(0.84, 0.5, 0.01, emissive(0x5FBFA4, 1.3), -0.5, 1.32, -0.09, g);
    box(0.48, 0.02, 0.17, M.black, -0.5, 0.82, 0.25, g);
    cyl(0.07, 0.07, 0.12, M.red, 0.35, 0.86, 0.2, g);
    cyl(0.05, 0.09, 0.5, M.metal, 1.0, 1.05, -0.2, g);
    const glow = new THREE.PointLight(0x8FE0C4, 6, 4, 2); glow.position.set(-0.5, 1.3, 0.2); g.add(glow);
    const warm = new THREE.PointLight(0xFFC98A, 8, 5, 2); warm.position.set(1.0, 1.35, -0.2); g.add(warm);
    anims.push(t => { scr.material.emissiveIntensity = 1.15 + Math.sin(t * 5.4) * 0.12 + Math.sin(t * 23) * 0.05; });
    return [2.6, 1.3];
  },

  jukebox(g) {
    box(1.1, 2.0, 0.8, M.darkw, 0, 1.0, 0, g);
    box(1.0, 0.28, 0.06, emissive(0xC9A83E, 1.1), 0, 1.86, -0.4, g);
    box(0.9, 0.62, 0.05, M.black, 0, 1.34, -0.41, g);
    const bars = [];
    for (let i = 0; i < 9; i++) {
      const b = box(0.06, 0.3, 0.03, emissive([0x7FD8C0, 0xC9A83E, 0xE08A6E][i % 3], 1.5), -0.36 + i * 0.09, 1.2, -0.43, g);
      b.geometry.translate(0, 0.15, 0);
      bars.push(b);
    }
    box(0.86, 0.5, 0.05, new THREE.MeshStandardMaterial({ color: 0x2A2018, roughness: 0.9 }), 0, 0.66, -0.41, g);
    cyl(0.07, 0.07, 0.08, M.red, -0.2, 1.0, -0.44, g).rotation.x = Math.PI / 2;
    const l = new THREE.PointLight(0xE8A050, 9, 5, 2); l.position.set(0, 1.6, -0.6); g.add(l);
    anims.push(t => bars.forEach((b, i) => {
      b.scale.y = 0.25 + Math.abs(Math.sin(t * 3.4 + i * 0.8)) * 1.5 + Math.abs(Math.sin(t * 9 + i)) * 0.4;
    }));
    return [1.3, 1.0];
  },

  globe(g) {
    cyl(0.34, 0.44, 0.2, M.darkw, 0, 0.1, 0, g);
    cyl(0.16, 0.2, 1.0, M.midw, 0, 0.6, 0, g);
    cyl(0.36, 0.3, 0.1, M.wood, 0, 1.14, 0, g);
    const wire = new THREE.Mesh(
      new THREE.SphereGeometry(0.42, 24, 18),
      new THREE.MeshStandardMaterial({ color: 0xCDBB94, wireframe: true, emissive: 0x8A7A52, emissiveIntensity: 0.7 })
    );
    wire.position.y = 1.62; g.add(wire);
    const core = new THREE.Mesh(
      new THREE.SphereGeometry(0.36, 20, 16),
      new THREE.MeshStandardMaterial({ color: 0x2A2418, emissive: 0x4A3E22, emissiveIntensity: 0.5, roughness: 0.9 })
    );
    core.position.y = 1.62; g.add(core);
    const l = new THREE.PointLight(0xE8D2A0, 7, 4, 2); l.position.set(0, 1.62, 0); g.add(l);
    anims.push(t => { wire.rotation.y = t * 0.4; wire.rotation.z = 0.4; core.rotation.y = t * 0.4; });
    return [0.9, 0.9];
  },

  shelf(g) {
    box(1.9, 2.2, 0.1, M.darkw, 0, 1.1, -0.26, g);
    box(0.08, 2.2, 0.56, M.midw, -0.95, 1.1, 0, g);
    box(0.08, 2.2, 0.56, M.midw, 0.95, 1.1, 0, g);
    const cols = [0x8A3C2E, 0xC9A83E, 0x4E8C7C, 0xCDBB94, 0x7A5C9A, 0xB0553E];
    for (let r = 0; r < 4; r++) {
      box(1.9, 0.06, 0.56, M.midw, 0, 0.35 + r * 0.56, 0, g);
      for (let i = 0; i < 9; i++) {
        const h = 0.28 + ((i * 3 + r * 5) % 4) * 0.05;
        box(0.13, h, 0.34, new THREE.MeshStandardMaterial({ color: cols[(i + r * 2) % 6], roughness: 0.85 }),
            -0.8 + i * 0.2, 0.38 + r * 0.56 + h / 2, 0, g);
      }
    }
    cyl(0.16, 0.2, 0.22, M.midw, -0.55, 2.31, 0, g);
    for (let i = 0; i < 6; i++) {
      const a = i * 1.05;
      const leaf = box(0.07, 0.26, 0.07, M.teal, -0.55 + Math.cos(a) * 0.12, 2.54, Math.sin(a) * 0.12, g);
      leaf.rotation.z = Math.cos(a) * 0.4;
      leaf.rotation.x = Math.sin(a) * 0.4;
    }
    return [2.0, 0.7];
  },

  crates(g) {
    const crate = (x, y, z, s, mat) => {
      box(s, s, s, mat, x, y, z, g);
      const lip = new THREE.Mesh(new THREE.BoxGeometry(s * 1.01, s * 0.08, s * 1.01), M.darkw);
      lip.position.set(x, y + s * 0.3, z);
      g.add(lip);
    };
    crate(0, 0.35, 0, 0.7, M.wood);
    crate(0.62, 0.28, 0.3, 0.56, M.midw);
    crate(-0.1, 0.95, -0.05, 0.56, M.wood);
    box(0.3, 0.42, 0.06, M.red, -0.1, 1.5, -0.05, g);
    box(0.26, 0.38, 0.06, M.black, -0.1, 1.5, -0.02, g);
    box(0.3, 0.42, 0.06, M.gold, 0.34, 1.5, 0.12, g);
    return [1.6, 1.2];
  },

  easel(g) {
    const a = box(0.07, 1.9, 0.07, M.midw, -0.4, 0.95, 0, g); a.rotation.z = 0.12;
    const b = box(0.07, 1.9, 0.07, M.midw, 0.4, 0.95, 0, g); b.rotation.z = -0.12;
    const c = box(0.07, 1.8, 0.07, M.midw, 0, 0.9, 0.4, g); c.rotation.x = -0.2;
    box(0.95, 0.06, 0.16, M.wood, 0, 0.86, 0.02, g);
    box(0.92, 1.14, 0.05, M.darkw, 0, 1.5, 0, g);
    const photo = new THREE.Mesh(
      new THREE.PlaneGeometry(0.78, 1.0),
      new THREE.MeshStandardMaterial({ map: photoTexture(), roughness: 0.5 })
    );
    photo.position.set(0, 1.5, 0.03); g.add(photo);
    const l = new THREE.SpotLight(0xFFE0B0, 14, 4, 0.8, 0.6, 1.6);
    l.position.set(0, 2.6, 1.0); l.target.position.set(0, 1.5, 0);
    g.add(l, l.target);
    return [1.1, 0.9];
  },

  party(g) {
    cyl(0.16, 0.24, 0.72, M.darkw, 0, 0.36, 0, g);
    cyl(0.82, 0.82, 0.06, M.cloth, 0, 0.74, 0, g, 26);
    cyl(0.86, 0.7, 0.46, M.cloth, 0, 0.5, 0, g, 26);
    cyl(0.1, 0.13, 0.26, M.red, 0, 0.9, 0, g);
    for (let i = 0; i < 7; i++) {
      const a = i * 0.9;
      const f = box(0.07, 0.2, 0.07, [M.gold, M.manila, M.red][i % 3], Math.cos(a) * 0.1, 1.12, Math.sin(a) * 0.1, g);
      f.rotation.z = Math.cos(a) * 0.5;
      f.rotation.x = Math.sin(a) * 0.5;
    }
    box(0.24, 0.18, 0.24, M.teal, 0.5, 0.86, 0.22, g);
    box(0.2, 0.16, 0.2, M.gold, -0.45, 0.85, -0.25, g);
    const balloons = [];
    [[0x9C3428, -0.5, 1.9, 0.3], [0xB08C3C, 0.15, 2.15, -0.2], [0x2F6B5C, 0.55, 1.8, 0.25]].forEach(b => {
      const s = new THREE.Mesh(new THREE.SphereGeometry(0.17, 16, 14),
        new THREE.MeshStandardMaterial({ color: b[0], roughness: 0.35 }));
      s.position.set(b[1], b[2], b[3]);
      s.scale.y = 1.18;
      s.castShadow = true;
      g.add(s);
      balloons.push(s);
    });
    anims.push(t => balloons.forEach((s, i) => {
      s.position.y += Math.sin(t * 1.3 + i * 2.1) * 0.0016;
      s.rotation.z = Math.sin(t * 0.9 + i) * 0.12;
    }));
    return [1.5, 1.5];
  },

  glass(g) {
    box(2.4, 0.18, 0.3, M.darkw, 0, 0.09, 0, g);
    box(0.16, 3.0, 0.28, M.darkw, -1.1, 1.5, 0, g);
    box(0.16, 3.0, 0.28, M.darkw, 1.1, 1.5, 0, g);
    box(2.4, 0.16, 0.3, M.darkw, 0, 3.0, 0, g);
    const cols = [0x9C3428, 0xD6C49E, 0x9C3428];
    for (let i = 0; i < 3; i++) {
      const p = new THREE.Mesh(new THREE.PlaneGeometry(0.6, 2.4),
        new THREE.MeshStandardMaterial({
          color: cols[i], emissive: cols[i], emissiveIntensity: 0.85,
          transparent: true, opacity: 0.92, side: THREE.DoubleSide, roughness: 0.3
        }));
      p.position.set(-0.68 + i * 0.68, 1.6, 0.02);
      g.add(p);
      box(0.03, 2.4, 0.06, M.darkw, -0.34 + i * 0.68, 1.6, 0, g);
    }
    const l = new THREE.PointLight(0xE8CFA0, 16, 7, 2); l.position.set(0, 1.8, 0.7); g.add(l);
    return [2.6, 0.5];
  },

  pedestal(g) {
    cyl(0.32, 0.4, 0.16, M.darkw, 0, 0.08, 0, g);
    cyl(0.2, 0.24, 1.0, M.midw, 0, 0.6, 0, g);
    cyl(0.34, 0.28, 0.09, M.wood, 0, 1.14, 0, g);
    const ball = new THREE.Group();
    const top = new THREE.Mesh(new THREE.SphereGeometry(0.2, 20, 12, 0, 6.3, 0, Math.PI / 2),
      new THREE.MeshStandardMaterial({ color: 0xB03A2C, roughness: 0.32 }));
    const bot = new THREE.Mesh(new THREE.SphereGeometry(0.2, 20, 12, 0, 6.3, Math.PI / 2, Math.PI / 2),
      new THREE.MeshStandardMaterial({ color: 0xE8E0D0, roughness: 0.32 }));
    const belt = new THREE.Mesh(new THREE.CylinderGeometry(0.203, 0.203, 0.045, 24),
      new THREE.MeshStandardMaterial({ color: 0x2A2420, roughness: 0.6 }));
    const btn = new THREE.Mesh(new THREE.CylinderGeometry(0.06, 0.06, 0.42, 16),
      new THREE.MeshStandardMaterial({ color: 0xF2EEE4, emissive: 0xF2EEE4, emissiveIntensity: 0.35 }));
    btn.rotation.x = Math.PI / 2;
    ball.add(top, bot, belt, btn);
    ball.position.y = 1.55;
    ball.castShadow = true;
    g.add(ball);
    const l = new THREE.PointLight(0xD8564A, 7, 4, 2); l.position.set(0, 1.55, 0); g.add(l);
    anims.push(t => { ball.position.y = 1.55 + Math.sin(t * 1.6) * 0.07; ball.rotation.y = t * 0.5; });
    return [0.85, 0.85];
  },

  radio(g) {
    box(1.0, 0.07, 0.6, M.wood, 0, 0.68, 0, g);
    [[-0.42, -0.22], [0.42, -0.22], [-0.42, 0.22], [0.42, 0.22]]
      .forEach(p => box(0.06, 0.68, 0.06, M.darkw, p[0], 0.34, p[1], g));
    box(0.62, 0.44, 0.36, new THREE.MeshStandardMaterial({ color: 0x7A4A2E, roughness: 0.6 }), 0, 0.94, 0, g);
    box(0.44, 0.3, 0.03, new THREE.MeshStandardMaterial({ color: 0x2A2018, roughness: 0.95 }), 0, 0.96, 0.19, g);
    const led = box(0.05, 0.05, 0.03, emissive(0x6FD8B4, 2), 0.22, 0.78, 0.19, g);
    cyl(0.012, 0.012, 0.7, M.metal, 0.24, 1.5, -0.1, g).rotation.z = -0.28;
    cyl(0.05, 0.05, 0.04, M.gold, -0.2, 0.8, 0.2, g).rotation.x = Math.PI / 2;
    anims.push(t => { led.material.emissiveIntensity = 1.2 + Math.abs(Math.sin(t * 1.7)) * 2.2; });
    return [1.1, 0.8];
  }
};
