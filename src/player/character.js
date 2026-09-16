import * as THREE from 'three';

// Personagem montado como hierarquia de grupos, para a animacao girar
// articulacoes em vez de mover posicoes.
//
//   root -> hips -> torso -> ombro -> cotovelo -> mao
//                -> cabeca
//        -> quadril -> joelho -> pe
//
// Troque as cores aqui.
export const SKIN_TONE = {
  skin:  0xD9A884,
  shirt: 0x8E9092,   // blusa cinza
  shirtD:0x6E7073,
  pant:  0x1C1C1E,   // calca preta
  shoe:  0x101012,   // tenis preto
  sole:  0x3A3A3E,
  hair:  0x241A12,   // cabelo curto
  frame: 0x141416,   // armacao dos oculos
  lens:  0xBFDCEA
};

export function makeCharacter() {
  const C = SKIN_TONE;
  const skin   = new THREE.MeshStandardMaterial({ color: C.skin, roughness: 0.85 });
  const shirt  = new THREE.MeshStandardMaterial({ color: C.shirt, roughness: 0.95 });
  const shirtD = new THREE.MeshStandardMaterial({ color: C.shirtD, roughness: 0.95 });
  const pant   = new THREE.MeshStandardMaterial({ color: C.pant, roughness: 0.98 });
  const shoe   = new THREE.MeshStandardMaterial({ color: C.shoe, roughness: 0.6 });
  const sole   = new THREE.MeshStandardMaterial({ color: C.sole, roughness: 0.9 });
  const hair   = new THREE.MeshStandardMaterial({ color: C.hair, roughness: 0.9 });
  const frame  = new THREE.MeshStandardMaterial({ color: C.frame, roughness: 0.35, metalness: 0.4 });
  const lens   = new THREE.MeshPhysicalMaterial({ color: C.lens, transparent: true, opacity: 0.28, roughness: 0.08, metalness: 0 });

  const root = new THREE.Group();
  const hips = new THREE.Group();
  hips.position.y = 0.92;
  root.add(hips);

  const torso = new THREE.Group();
  hips.add(torso);

  const chest = new THREE.Mesh(new THREE.CapsuleGeometry(0.195, 0.36, 6, 16), shirt);
  chest.position.y = 0.3; chest.scale.set(1, 1, 0.72); chest.castShadow = true;
  torso.add(chest);

  const collar = new THREE.Mesh(new THREE.TorusGeometry(0.105, 0.028, 8, 18), shirtD);
  collar.rotation.x = Math.PI / 2; collar.position.y = 0.56;
  torso.add(collar);

  const pelvis = new THREE.Mesh(new THREE.CapsuleGeometry(0.17, 0.1, 4, 14), pant);
  pelvis.position.y = 0.02; pelvis.scale.set(1, 1, 0.78); pelvis.castShadow = true;
  torso.add(pelvis);

  const neck = new THREE.Mesh(new THREE.CylinderGeometry(0.062, 0.07, 0.1, 12), skin);
  neck.position.y = 0.6;
  torso.add(neck);

  const head = new THREE.Group();
  head.position.y = 0.74;
  torso.add(head);

  const skull = new THREE.Mesh(new THREE.SphereGeometry(0.135, 22, 18), skin);
  skull.scale.set(0.93, 1.06, 1); skull.castShadow = true;
  head.add(skull);

  const jaw = new THREE.Mesh(new THREE.SphereGeometry(0.105, 16, 14), skin);
  jaw.position.set(0, -0.055, 0.022); jaw.scale.set(0.92, 0.86, 1);
  head.add(jaw);

  // Cabelo curto: calota colada ao cranio + nuca + franja baixa.
  const cap = new THREE.Mesh(new THREE.SphereGeometry(0.142, 22, 18, 0, 6.3, 0, 1.16), hair);
  cap.scale.set(0.95, 1.04, 1.02); cap.position.y = 0.006;
  head.add(cap);
  const nape = new THREE.Mesh(new THREE.SphereGeometry(0.138, 18, 14, 0, 6.3, 1.0, 0.55), hair);
  nape.scale.set(0.95, 1, 1.0); nape.position.z = -0.012;
  head.add(nape);
  const fringe = new THREE.Mesh(new THREE.BoxGeometry(0.19, 0.04, 0.05), hair);
  fringe.position.set(0, 0.068, 0.112); fringe.rotation.x = 0.24;
  head.add(fringe);

  [-1, 1].forEach(side => {
    const sideburn = new THREE.Mesh(new THREE.BoxGeometry(0.025, 0.07, 0.05), hair);
    sideburn.position.set(side * 0.122, -0.018, 0.018);
    head.add(sideburn);

    const ear = new THREE.Mesh(new THREE.SphereGeometry(0.032, 10, 8), skin);
    ear.position.set(side * 0.132, -0.012, 0.006); ear.scale.set(0.5, 1, 0.7);
    head.add(ear);

    const eye = new THREE.Mesh(new THREE.SphereGeometry(0.018, 10, 8),
      new THREE.MeshStandardMaterial({ color: 0x1A130E, roughness: 0.3 }));
    eye.position.set(side * 0.052, 0.005, 0.118);
    head.add(eye);

    // Oculos: aro, lente e haste.
    const rim = new THREE.Mesh(new THREE.TorusGeometry(0.043, 0.008, 8, 18), frame);
    rim.position.set(side * 0.054, 0.004, 0.122);
    head.add(rim);
    const glass = new THREE.Mesh(new THREE.CircleGeometry(0.04, 18), lens);
    glass.position.set(side * 0.054, 0.004, 0.1225);
    head.add(glass);
    const temple = new THREE.Mesh(new THREE.BoxGeometry(0.012, 0.01, 0.11), frame);
    temple.position.set(side * 0.105, 0.004, 0.06);
    head.add(temple);
  });

  const bridge = new THREE.Mesh(new THREE.BoxGeometry(0.03, 0.008, 0.01), frame);
  bridge.position.set(0, 0.01, 0.128);
  head.add(bridge);
  const brow = new THREE.Mesh(new THREE.BoxGeometry(0.14, 0.012, 0.02), hair);
  brow.position.set(0, 0.055, 0.116);
  head.add(brow);
  const nose = new THREE.Mesh(new THREE.ConeGeometry(0.022, 0.05, 8), skin);
  nose.rotation.x = Math.PI / 2; nose.position.set(0, -0.022, 0.128);
  head.add(nose);

  const limbs = {};
  [-1, 1].forEach(side => {
    const k = side < 0 ? 'L' : 'R';

    const shoulder = new THREE.Group();
    shoulder.position.set(side * 0.225, 0.47, 0);
    torso.add(shoulder);
    const upper = new THREE.Mesh(new THREE.CapsuleGeometry(0.058, 0.2, 5, 12), shirt);
    upper.position.y = -0.14; upper.castShadow = true;
    shoulder.add(upper);

    const elbow = new THREE.Group();
    elbow.position.y = -0.27;
    shoulder.add(elbow);
    const fore = new THREE.Mesh(new THREE.CapsuleGeometry(0.05, 0.19, 5, 12), skin);
    fore.position.y = -0.13; fore.castShadow = true;
    elbow.add(fore);
    const hand = new THREE.Mesh(new THREE.SphereGeometry(0.058, 12, 10), skin);
    hand.position.y = -0.26; hand.scale.set(0.8, 1, 0.6);
    elbow.add(hand);
    const cuff = new THREE.Mesh(new THREE.TorusGeometry(0.055, 0.015, 8, 14), shirtD);
    cuff.rotation.x = Math.PI / 2; cuff.position.y = -0.02;
    elbow.add(cuff);

    limbs['arm' + k] = shoulder;
    limbs['elb' + k] = elbow;

    const hip = new THREE.Group();
    hip.position.set(side * 0.105, 0, 0);
    hips.add(hip);
    const thigh = new THREE.Mesh(new THREE.CapsuleGeometry(0.085, 0.26, 5, 12), pant);
    thigh.position.y = -0.2; thigh.castShadow = true;
    hip.add(thigh);

    const knee = new THREE.Group();
    knee.position.y = -0.42;
    hip.add(knee);
    const shin = new THREE.Mesh(new THREE.CapsuleGeometry(0.07, 0.25, 5, 12), pant);
    shin.position.y = -0.19; shin.castShadow = true;
    knee.add(shin);
    const foot = new THREE.Mesh(new THREE.BoxGeometry(0.115, 0.075, 0.26), shoe);
    foot.position.set(0, -0.385, 0.05); foot.castShadow = true;
    knee.add(foot);
    const soleM = new THREE.Mesh(new THREE.BoxGeometry(0.12, 0.028, 0.265), sole);
    soleM.position.set(0, -0.418, 0.05);
    knee.add(soleM);

    limbs['leg' + k] = hip;
    limbs['knee' + k] = knee;
  });

  return { root, hips, torso, head, limbs };
}

// Sombra de contato: disco escuro sob os pes, complementa a sombra projetada.
export function makeContactShadow(scene) {
  const m = new THREE.Mesh(
    new THREE.CircleGeometry(0.42, 24),
    new THREE.MeshBasicMaterial({ color: 0x000000, transparent: true, opacity: 0.26 })
  );
  m.rotation.x = -Math.PI / 2;
  m.position.y = 0.022;
  scene.add(m);
  return m;
}
