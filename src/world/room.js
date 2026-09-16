import * as THREE from 'three';
import { ROOM } from '../config/theme.js';
import { woodTexture, plasterTexture, rugTexture } from '../core/textures.js';

export function buildRoom(scene) {
  const wood = woodTexture();
  wood.repeat.set(7, 5);

  const floor = new THREE.Mesh(
    new THREE.PlaneGeometry(ROOM.W, ROOM.D),
    new THREE.MeshStandardMaterial({ map: wood, bumpMap: wood, bumpScale: 0.035, roughness: 0.72, metalness: 0.02 })
  );
  floor.rotation.x = -Math.PI / 2;
  floor.receiveShadow = true;
  scene.add(floor);

  const rug = new THREE.Mesh(
    new THREE.PlaneGeometry(9, 7),
    new THREE.MeshStandardMaterial({ map: rugTexture(), roughness: 0.96 })
  );
  rug.rotation.x = -Math.PI / 2;
  rug.position.set(0, 0.012, 0.6);
  rug.receiveShadow = true;
  scene.add(rug);

  const plaster = plasterTexture();
  plaster.repeat.set(5, 1.4);
  const wallMat = new THREE.MeshStandardMaterial({ map: plaster, bumpMap: plaster, bumpScale: 0.02, roughness: 0.95 });
  const trimMat = new THREE.MeshStandardMaterial({ color: 0x3A2E22, roughness: 0.7 });

  const wall = (w, x, z, ry) => {
    const m = new THREE.Mesh(new THREE.BoxGeometry(w, ROOM.H, 0.3), wallMat);
    m.position.set(x, ROOM.H / 2, z);
    m.rotation.y = ry || 0;
    m.receiveShadow = true;
    scene.add(m);
  };
  wall(ROOM.W, 0, -ROOM.D / 2);
  wall(ROOM.W, 0, ROOM.D / 2);
  wall(ROOM.D, -ROOM.W / 2, 0, Math.PI / 2);
  wall(ROOM.D, ROOM.W / 2, 0, Math.PI / 2);

  const ceil = new THREE.Mesh(
    new THREE.PlaneGeometry(ROOM.W, ROOM.D),
    new THREE.MeshStandardMaterial({ color: 0x2A241C, roughness: 1 })
  );
  ceil.rotation.x = Math.PI / 2;
  ceil.position.y = ROOM.H;
  scene.add(ceil);

  // Rodapé
  [[ROOM.W, 0, -ROOM.D / 2 + 0.16, 0], [ROOM.W, 0, ROOM.D / 2 - 0.16, 0],
   [ROOM.D, -ROOM.W / 2 + 0.16, 0, Math.PI / 2], [ROOM.D, ROOM.W / 2 - 0.16, 0, Math.PI / 2]]
  .forEach(b => {
    const m = new THREE.Mesh(new THREE.BoxGeometry(b[0], 0.22, 0.1), trimMat);
    m.position.set(b[1], 0.11, b[2]);
    m.rotation.y = b[3];
    scene.add(m);
  });

  // Luminárias pendentes
  for (let i = 0; i < 3; i++) {
    const g = new THREE.Group();
    const cord = new THREE.Mesh(new THREE.CylinderGeometry(0.012, 0.012, 0.9), trimMat);
    cord.position.y = ROOM.H - 0.45;
    const shade = new THREE.Mesh(
      new THREE.ConeGeometry(0.42, 0.34, 20, 1, true),
      new THREE.MeshStandardMaterial({ color: 0x3A2E22, roughness: 0.6, side: THREE.DoubleSide })
    );
    shade.position.y = ROOM.H - 1.0;
    const bulb = new THREE.Mesh(
      new THREE.SphereGeometry(0.09, 12, 10),
      new THREE.MeshStandardMaterial({ color: 0xFFE6B8, emissive: 0xFFCE8A, emissiveIntensity: 2.4 })
    );
    bulb.position.y = ROOM.H - 1.12;
    g.add(cord, shade, bulb);
    g.position.set(-6 + i * 6, 0, -1);
    scene.add(g);
  }

  return { floor };
}

// Poeira suspensa. Devolve a funcao de update para o loop chamar.
export function buildDust(scene, count = 260) {
  const geo = new THREE.BufferGeometry();
  const pos = new Float32Array(count * 3);
  const vel = [];
  for (let i = 0; i < count; i++) {
    pos[i * 3] = (Math.random() - 0.5) * ROOM.W;
    pos[i * 3 + 1] = Math.random() * 3.2 + 0.2;
    pos[i * 3 + 2] = (Math.random() - 0.5) * ROOM.D;
    vel.push(0.02 + Math.random() * 0.05);
  }
  geo.setAttribute('position', new THREE.BufferAttribute(pos, 3));
  const points = new THREE.Points(geo, new THREE.PointsMaterial({
    color: 0xE8D8B0, size: 0.035, transparent: true, opacity: 0.5, depthWrite: false
  }));
  scene.add(points);

  return (dt, t) => {
    const a = geo.attributes.position;
    for (let i = 0; i < count; i++) {
      let y = a.getY(i) + vel[i] * dt;
      if (y > 3.6) y = 0.15;
      a.setY(i, y);
      a.setX(i, a.getX(i) + Math.sin(t * 0.4 + i) * 0.0012);
    }
    a.needsUpdate = true;
  };
}
