import * as THREE from 'three';

// ---------------------------------------------------------------------------
// Personagem: guerreiro de armadura lamelar, inspirado em RPG, com lanca.
//
// Hierarquia (a animacao gira articulacoes, nunca move posicoes):
//   root -> hips -> torso -> ombro -> cotovelo -> mao
//                         -> pescoco -> cabeca
//                         -> arma (presa ao tronco, nao ao braco)
//                -> kusazuri (saia de placas, 4 paineis pendulares)
//                -> quadril -> joelho -> pe
//
// A arma fica no tronco de proposito: se ficasse na mao, herdaria a rotacao do
// cotovelo e balancaria junto com o passo. Presa ao tronco, ela acompanha o
// corpo e o braco direito assume uma pose fixa de porte (ver animation.js).
// ---------------------------------------------------------------------------

export const LOOK = {
  skin:      0xD9A884,
  skinShade: 0xB98A62,
  hair:      0x141014,   // preto azulado
  cloth:     0x22222A,   // camada interna: gola alta, mangas, hakama
  clothDark: 0x16161C,
  wrap:      0x2E2E38,   // faixas de mao e canela
  lacquer:   0x7A2320,   // laca vermelha das placas
  lacquerHi: 0x9C3028,
  lacquerLo: 0x561715,
  lacing:    0xB08C3C,   // cordoalha dourada entre as lamelas
  steel:     0x8A8C92,
  shaft:     0x3E2A1C,   // cabo da lanca
  tassel:    0x8C2A22,
  glasses:   true,       // false remove os oculos
  frame:     0x141416,
  lens:      0xBFDCEA
};

function mat(color, roughness = 0.8, metalness = 0) {
  return new THREE.MeshStandardMaterial({ color, roughness, metalness });
}

export function makeCharacter(look = LOOK) {
  const MAT = {
    skin:   mat(look.skin, 0.85),
    skinD:  mat(look.skinShade, 0.85),
    hair:   mat(look.hair, 0.75),
    cloth:  mat(look.cloth, 0.98),
    clothD: mat(look.clothDark, 0.98),
    wrap:   mat(look.wrap, 1.0),
    lacq:   mat(look.lacquer, 0.28, 0.12),
    lacqHi: mat(look.lacquerHi, 0.24, 0.14),
    lacqLo: mat(look.lacquerLo, 0.32, 0.1),
    lace:   mat(look.lacing, 0.35, 0.65),
    steel:  mat(look.steel, 0.22, 0.9),
    shaft:  mat(look.shaft, 0.7),
    tassel: mat(look.tassel, 0.95),
    frame:  mat(look.frame, 0.35, 0.4),
    lens:   new THREE.MeshPhysicalMaterial({ color: look.lens, transparent: true, opacity: 0.26, roughness: 0.08 })
  };

  const add = (parent, geo, material, x, y, z) => {
    const m = new THREE.Mesh(geo, material);
    m.position.set(x, y, z);
    m.castShadow = true;
    m.receiveShadow = true;
    parent.add(m);
    return m;
  };
  const plate = (parent, w, h, d, x, y, z, material = MAT.lacq) =>
    add(parent, new THREE.BoxGeometry(w, h, d), material, x, y, z);

  // Uma lamela: placa laqueada + trecho de cordoalha dourada na frente.
  function lame(parent, w, h, d, x, y, z, material = MAT.lacq, cords = 3) {
    const p = plate(parent, w, h, d, x, y, z, material);
    for (let i = 0; i < cords; i++) {
      const cx = x + (i - (cords - 1) / 2) * (w / (cords + 0.6));
      add(parent, new THREE.BoxGeometry(0.018, h * 0.78, 0.012), MAT.lace, cx, y, z + d / 2 + 0.006);
    }
    // aresta superior clara, para a placa ler como laca e nao como massa chapada
    add(parent, new THREE.BoxGeometry(w, h * 0.16, d * 1.02), MAT.lacqHi, x, y + h * 0.42, z);
    return p;
  }

  const root = new THREE.Group();
  const hips = new THREE.Group();
  hips.position.y = 0.95;
  root.add(hips);

  const torso = new THREE.Group();
  hips.add(torso);

  // ---- camada interna ----
  const body = add(torso, new THREE.CapsuleGeometry(0.2, 0.36, 6, 18), MAT.cloth, 0, 0.3, 0);
  body.scale.set(1, 1, 0.74);
  const pelvis = add(torso, new THREE.CapsuleGeometry(0.185, 0.1, 4, 14), MAT.clothD, 0, 0.02, 0);
  pelvis.scale.set(1, 1, 0.8);
  // gola alta
  add(torso, new THREE.CylinderGeometry(0.115, 0.125, 0.16, 16), MAT.cloth, 0, 0.6, 0);

  // ---- do: cuirass de 5 lamelas ----
  const cuirass = new THREE.Group();
  cuirass.position.y = 0.12;
  torso.add(cuirass);
  for (let i = 0; i < 5; i++) {
    const t = i / 4;
    const w = 0.5 - t * 0.05;
    const l = lame(cuirass, w, 0.085, 0.33 - t * 0.02, 0, -0.02 + i * 0.085, 0.01, i === 0 ? MAT.lacqLo : MAT.lacq, 3);
    l.scale.z = 1;
  }
  // placa do peito e alcas sobre os ombros (watagami)
  lame(cuirass, 0.42, 0.12, 0.3, 0, 0.42, 0.015, MAT.lacq, 2);
  [-1, 1].forEach(s => {
    const strap = plate(torso, 0.12, 0.05, 0.3, s * 0.155, 0.52, 0.0);
    strap.rotation.z = s * 0.12;
    add(torso, new THREE.TorusGeometry(0.022, 0.007, 8, 14), MAT.lace, s * 0.13, 0.5, 0.15);
  });
  // obi (faixa) na cintura
  const obi = add(torso, new THREE.CylinderGeometry(0.215, 0.215, 0.1, 20), MAT.lacqLo, 0, 0.04, 0);
  obi.scale.z = 0.8;

  // ---- kusazuri: 4 paineis de placas que pendem da cintura ----
  const skirt = [];
  [[0, 0.17, 0], [Math.PI, -0.17, 0], [Math.PI / 2, 0, 0], [-Math.PI / 2, 0, 0]].forEach((cfg, idx) => {
    const panel = new THREE.Group();
    panel.position.set(idx === 2 ? 0.2 : idx === 3 ? -0.2 : 0, -0.02, cfg[1]);
    panel.rotation.y = cfg[0];
    hips.add(panel);
    const wide = idx < 2 ? 0.34 : 0.26;
    for (let i = 0; i < 3; i++) {
      lame(panel, wide - i * 0.02, 0.13, 0.05, 0, -0.1 - i * 0.14, 0.04, MAT.lacq, idx < 2 ? 3 : 2);
    }
    skirt.push(panel);
  });

  // ---- cabeca ----
  const neck = add(torso, new THREE.CylinderGeometry(0.065, 0.075, 0.1, 12), MAT.skin, 0, 0.64, 0);
  void neck;
  const head = new THREE.Group();
  head.position.y = 0.78;
  torso.add(head);

  const skull = add(head, new THREE.SphereGeometry(0.14, 24, 20), MAT.skin, 0, 0, 0);
  skull.scale.set(0.93, 1.06, 1);
  const jaw = add(head, new THREE.SphereGeometry(0.108, 16, 14), MAT.skin, 0, -0.058, 0.024);
  jaw.scale.set(0.92, 0.86, 1);
  add(head, new THREE.ConeGeometry(0.023, 0.052, 8), MAT.skin, 0, -0.024, 0.132).rotation.x = Math.PI / 2;

  // cabelo baguncado: calota + mechas angulares em varias direcoes
  const capHair = add(head, new THREE.SphereGeometry(0.148, 22, 18, 0, 6.3, 0, 1.5), MAT.hair, 0, 0.004, 0);
  capHair.scale.set(0.97, 1.06, 1.03);
  const strands = [
    [-0.09, 0.12, 0.09, 0.5, -0.3], [0.02, 0.15, 0.1, 0.7, 0.1], [0.1, 0.11, 0.07, 0.4, 0.5],
    [-0.13, 0.06, -0.02, 0.2, -0.8], [0.14, 0.05, -0.03, 0.2, 0.8], [0, 0.14, -0.08, -0.6, 0],
    [-0.06, 0.13, -0.05, -0.4, -0.4], [0.07, 0.12, -0.06, -0.4, 0.4]
  ];
  strands.forEach(s => {
    const m = add(head, new THREE.ConeGeometry(0.036, 0.15, 6), MAT.hair, s[0], s[1], s[2]);
    m.rotation.x = s[3];
    m.rotation.z = s[4];
  });
  // franja caindo sobre o olho direito
  const fringe = add(head, new THREE.BoxGeometry(0.085, 0.12, 0.045), MAT.hair, -0.045, 0.045, 0.108);
  fringe.rotation.z = 0.22;
  add(head, new THREE.BoxGeometry(0.2, 0.05, 0.05), MAT.hair, 0.03, 0.078, 0.1).rotation.z = -0.1;
  // mechas laterais ate a mandibula
  [-1, 1].forEach(s => {
    const side = add(head, new THREE.BoxGeometry(0.035, 0.17, 0.06), MAT.hair, s * 0.128, -0.03, 0.03);
    side.rotation.z = s * 0.06;
  });

  [-1, 1].forEach(s => {
    add(head, new THREE.SphereGeometry(0.019, 10, 8), mat(0x1A130E, 0.3), s * 0.053, 0.004, 0.121);
    if (look.glasses) {
      add(head, new THREE.TorusGeometry(0.044, 0.008, 8, 18), MAT.frame, s * 0.055, 0.004, 0.125);
      add(head, new THREE.CircleGeometry(0.041, 18), MAT.lens, s * 0.055, 0.004, 0.1255);
      add(head, new THREE.BoxGeometry(0.012, 0.01, 0.11), MAT.frame, s * 0.107, 0.004, 0.062);
    }
  });
  if (look.glasses) add(head, new THREE.BoxGeometry(0.03, 0.008, 0.01), MAT.frame, 0, 0.012, 0.131);

  // ---- bracos, sode e kote ----
  const limbs = {};
  [-1, 1].forEach(side => {
    const k = side < 0 ? 'R' : 'L'; // de frente para +z, a direita do personagem fica em -x

    const shoulder = new THREE.Group();
    shoulder.position.set(side * 0.235, 0.47, 0);
    torso.add(shoulder);

    add(shoulder, new THREE.CapsuleGeometry(0.062, 0.2, 5, 12), MAT.cloth, 0, -0.14, 0);

    // sode: pauldron de 4 lamelas que desce pelo braco
    const sode = new THREE.Group();
    sode.position.set(side * 0.055, 0.02, 0);
    shoulder.add(sode);
    for (let i = 0; i < 4; i++) {
      const w = 0.2 - i * 0.012;
      lame(sode, w, 0.085, 0.22, side * 0.015 * i, -0.02 - i * 0.095, 0, MAT.lacq, 2);
    }
    sode.rotation.z = -side * 0.1;

    const elbow = new THREE.Group();
    elbow.position.y = -0.27;
    shoulder.add(elbow);
    add(elbow, new THREE.CapsuleGeometry(0.052, 0.19, 5, 12), MAT.cloth, 0, -0.13, 0);
    // kote: bracadeira laqueada no antebraco
    lame(elbow, 0.125, 0.1, 0.125, 0, -0.1, 0, MAT.lacq, 2);
    add(elbow, new THREE.CylinderGeometry(0.058, 0.058, 0.06, 12), MAT.wrap, 0, -0.22, 0);
    const hand = add(elbow, new THREE.SphereGeometry(0.06, 12, 10), MAT.skin, 0, -0.27, 0);
    hand.scale.set(0.82, 1, 0.62);

    limbs['arm' + k] = shoulder;
    limbs['elb' + k] = elbow;

    // ---- pernas: hakama larga, haidate, canela enfaixada, sandalia ----
    const hip = new THREE.Group();
    hip.position.set(side * 0.11, 0, 0);
    hips.add(hip);
    const thigh = add(hip, new THREE.CapsuleGeometry(0.115, 0.26, 5, 12), MAT.cloth, 0, -0.2, 0);
    thigh.scale.z = 0.92;
    lame(hip, 0.17, 0.1, 0.14, side * 0.02, -0.3, 0.055, MAT.lacq, 2);

    const knee = new THREE.Group();
    knee.position.y = -0.44;
    hip.add(knee);
    add(knee, new THREE.CapsuleGeometry(0.095, 0.16, 5, 12), MAT.cloth, 0, -0.14, 0);
    add(knee, new THREE.CylinderGeometry(0.062, 0.072, 0.2, 12), MAT.wrap, 0, -0.33, 0);
    const foot = add(knee, new THREE.BoxGeometry(0.115, 0.05, 0.25), MAT.clothD, 0, -0.455, 0.05);
    void foot;
    add(knee, new THREE.BoxGeometry(0.125, 0.028, 0.29), MAT.shaft, 0, -0.487, 0.05);

    limbs['leg' + k] = hip;
    limbs['knee' + k] = knee;
  });

  // ---- lanca (yari) ----
  const weapon = new THREE.Group();
  weapon.position.set(-0.3, 0.1, 0.13);
  weapon.rotation.z = 0.1;
  weapon.rotation.x = -0.05;
  torso.add(weapon);

  add(weapon, new THREE.CylinderGeometry(0.023, 0.026, 2.4, 12), MAT.shaft, 0, 0.35, 0);
  // faixas de empunhadura
  [-0.05, 0.12, 0.3].forEach(y =>
    add(weapon, new THREE.CylinderGeometry(0.028, 0.028, 0.07, 12), MAT.wrap, 0, y, 0));
  // contrapeso na base
  add(weapon, new THREE.CylinderGeometry(0.032, 0.032, 0.09, 12), MAT.steel, 0, -0.82, 0);
  // habaki dourado e lamina
  add(weapon, new THREE.CylinderGeometry(0.038, 0.034, 0.08, 12), MAT.lace, 0, 1.5, 0);
  const blade = add(weapon, new THREE.ConeGeometry(0.048, 0.42, 4), MAT.steel, 0, 1.75, 0);
  blade.rotation.y = Math.PI / 4;
  blade.scale.z = 0.45;
  // borla
  add(weapon, new THREE.ConeGeometry(0.035, 0.1, 8), MAT.tassel, 0, 1.42, 0);
  const tassels = [];
  for (let i = 0; i < 5; i++) {
    const a = (i / 5) * Math.PI * 2;
    const th = add(weapon, new THREE.CylinderGeometry(0.006, 0.004, 0.17, 5), MAT.tassel,
      Math.cos(a) * 0.022, 1.3, Math.sin(a) * 0.022);
    tassels.push(th);
  }

  return { root, hips, torso, head, limbs, skirt, weapon, tassels, carry: 'R' };
}

export function makeContactShadow(scene) {
  const m = new THREE.Mesh(
    new THREE.CircleGeometry(0.5, 24),
    new THREE.MeshBasicMaterial({ color: 0x000000, transparent: true, opacity: 0.28 })
  );
  m.rotation.x = -Math.PI / 2;
  m.position.y = 0.022;
  scene.add(m);
  return m;
}
