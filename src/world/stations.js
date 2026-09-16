import * as THREE from 'three';
import { BUILD } from './props.js';
import { labelTexture } from '../core/textures.js';

// Caixas de colisao em XZ, preenchidas ao montar as estacoes.
export const colliders = [];

export function buildStations(scene, stations) {
  stations.forEach(s => {
    const g = new THREE.Group();
    g.position.set(s.pos[0], 0, s.pos[1]);
    g.rotation.y = s.rot;

    const builder = BUILD[s.kind];
    if (!builder) { console.warn('kind desconhecido:', s.kind); return; }
    const size = builder(g);
    scene.add(g);
    s.obj = g;

    // A caixa gira junto com o movel.
    const cos = Math.abs(Math.cos(s.rot)), sin = Math.abs(Math.sin(s.rot));
    colliders.push({
      x: s.pos[0], z: s.pos[1],
      w: (cos * size[0] + sin * size[1]) / 2,
      d: (cos * size[1] + sin * size[0]) / 2
    });

    const label = new THREE.Sprite(new THREE.SpriteMaterial({
      map: labelTexture(s.tag), transparent: true, depthTest: false, opacity: 0
    }));
    label.scale.set(3.2, 0.8, 1);
    label.position.set(s.pos[0], 2.75, s.pos[1]);
    label.renderOrder = 10;
    scene.add(label);
    s.label = label;

    const ring = new THREE.Mesh(
      new THREE.RingGeometry(1.15, 1.32, 40),
      new THREE.MeshBasicMaterial({ color: 0xD6C49E, transparent: true, opacity: 0, side: THREE.DoubleSide })
    );
    ring.rotation.x = -Math.PI / 2;
    ring.position.set(s.pos[0], 0.02, s.pos[1]);
    scene.add(ring);
    s.ring = ring;
  });

  // A fonte pode nao estar pronta quando o rotulo e desenhado. Refaz depois.
  if (document.fonts && document.fonts.ready) {
    document.fonts.ready.then(() => stations.forEach(s => {
      if (!s.label) return;
      const old = s.label.material.map;
      s.label.material.map = labelTexture(s.tag);
      s.label.material.needsUpdate = true;
      if (old) old.dispose();
    }));
  }
}
