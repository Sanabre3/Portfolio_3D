import * as THREE from 'three';
import { STATIONS } from './config/projects.js';
import { ROOM, TUNE } from './config/theme.js';
import { createRenderer, createScene, createCamera, addLights } from './core/scene.js';
import { buildRoom, buildDust } from './world/room.js';
import { buildStations, colliders } from './world/stations.js';
import { anims } from './world/props.js';
import { makeCharacter, makeContactShadow } from './player/character.js';
import { poseCharacter } from './player/animation.js';
import { loadDefaultAvatar, loadAvatar } from './player/model.js';
import { input, isTouch, attachControls, readInput, maxSpeed } from './player/controls.js';
import { CameraRig } from './camera/follow.js';
import { Panel } from './ui/panel.js';
import { HUD, gate } from './ui/hud.js';
import { setupEasterEgg } from './ui/easteregg.js';

const renderer = createRenderer();
const scene = createScene();
const camera = createCamera();
addLights(scene);

buildRoom(scene);
const updateDust = buildDust(scene);
buildStations(scene, STATIONS);

// Personagem procedural: aparece enquanto o .glb carrega e fica de reserva se ele falhar.
const CH = makeCharacter();
CH.root.position.set(0, 0, 3.2);
scene.add(CH.root);
const contactShadow = makeContactShadow(scene);
let body = CH.root;     // o que anda, gira e colide
let avatar = null;      // avatar .glb ativo, quando pronto
let baseAvatar = null;  // avatar inicial (dev); null = ficou o procedural

// Geometria que a camera nao pode atravessar. O proprio personagem fica de fora.
const solids = [];
const BLOCKING = ['BoxGeometry', 'CylinderGeometry'];
scene.traverse(o => {
  if (!o.isMesh || !o.geometry) return;
  if (!BLOCKING.includes(o.geometry.type) && !o.userData.blocksCamera) return;
  let p = o, inChar = false;
  while (p) { if (p === CH.root) { inChar = true; break; } p = p.parent; }
  if (!inChar) solids.push(o);
});

// Troca o que esta em cena mantendo posicao e direcao. a = null volta ao procedural.
function setAvatar(a) {
  const next = a ? a.root : CH.root;
  if (next === body) return;
  next.position.copy(body.position);
  next.rotation.y = body.rotation.y;
  scene.remove(body);
  scene.add(next);
  body = next;
  avatar = a;
}

const loading = loadDefaultAvatar(renderer, f => gate.progress && gate.progress(f))
  .then(a => { baseAvatar = a; setAvatar(a); })
  .catch(err => console.warn('nenhum .glb carregou, usando o personagem procedural:', err));

// Skin secreta: baixada so na primeira troca e guardada para as proximas.
let secret = null, swapping = false;
async function toggleSecret() {
  if (swapping) return;
  if (avatar && avatar.key === 'secreto') { setAvatar(baseAvatar); return; }
  if (!secret) {
    swapping = true;
    hud.toast('carregando a skin secreta…', 4000);
    try { secret = await loadAvatar('secreto', renderer); }
    catch (err) { console.warn(err); hud.toast('Não foi possível carregar a skin secreta.', 4000); return; }
    finally { swapping = false; }
    setAvatar(secret);
    renderer.compile(scene, camera); // compila os shaders da skin agora, nao no meio do passo
    return;
  }
  setAvatar(secret);
}

const rig = new CameraRig(camera);
const panel = new Panel();
const hud = new HUD(STATIONS.length);
const egg = setupEasterEgg({
  total: STATIONS.length,
  getVisited: () => Object.keys(panel.visited).length,
  toast: (m, ms) => hud.toast(m, ms),
  onToggle: toggleSecret,
  isTouch
});
// Qualquer forma de fechar o painel (E, Esc, X, clique fora) confere o desbloqueio.
const closePanel = panel.close.bind(panel);
panel.close = () => { closePanel(); egg.check(); };

let started = false, busy = false, active = null;
let speed = 0, phase = 0, facing = 0;
const focusPoint = new THREE.Vector3();
const step = new THREE.Vector3();

function interact() {
  if (!active || busy) return;
  busy = true;
  const s = active;
  rig.focus(body.position, s.pos);
  setTimeout(() => hud.flashIn(), 420);
  setTimeout(() => {
    panel.open(s);
    hud.flashOut();
    busy = false;
  }, 820);
}

attachControls({
  dom: renderer.domElement,
  rig,
  onInteract: interact,
  onClose: () => { panel.close(); rig.restore(); },
  isPanelOpen: () => panel.isOpen()
});

// Empurra o personagem para fora das caixas de colisao e das paredes.
function collide(pos) {
  const r = TUNE.playerRadius;
  colliders.forEach(c => {
    const dx = pos.x - c.x, dz = pos.z - c.z;
    const ox = c.w + r - Math.abs(dx);
    const oz = c.d + r - Math.abs(dz);
    if (ox > 0 && oz > 0) {
      if (ox < oz) pos.x = c.x + Math.sign(dx || 1) * (c.w + r);
      else pos.z = c.z + Math.sign(dz || 1) * (c.d + r);
    }
  });
  pos.x = Math.max(-ROOM.W / 2 + 0.6, Math.min(ROOM.W / 2 - 0.6, pos.x));
  pos.z = Math.max(-ROOM.D / 2 + 0.6, Math.min(ROOM.D / 2 - 0.6, pos.z));
}

function tick(dt, t) {
  const mag = readInput();
  const canMove = mag > 0.08 && !panel.isOpen() && !busy;

  // Movimento relativo a camera (padrao MMO).
  // F = (-sin yaw, -cos yaw) e o "para frente"; R = (cos yaw, -sin yaw) e o "para a direita".
  const dirX = Math.sin(rig.yaw), dirZ = Math.cos(rig.yaw);
  let wx = 0, wz = 0;
  if (canMove) {
    const nx = input.mx / mag, nz = input.mz / mag;
    wx = nx * dirZ + nz * dirX;
    wz = -nx * dirX + nz * dirZ;
    const len = Math.hypot(wx, wz) || 1;
    wx /= len; wz /= len;
  }

  const goal = canMove ? maxSpeed() * Math.min(1, mag * 1.3) : 0;
  const k = goal > speed ? TUNE.accel : TUNE.brake;

  // Diferenca entre para onde o jogador quer ir e para onde o corpo olha (dispara a virada de 180).
  const wantFacing = canMove ? Math.atan2(wx, wz) : body.rotation.y;
  let turnDiff = wantFacing - body.rotation.y;
  while (turnDiff > Math.PI) turnDiff -= Math.PI * 2;
  while (turnDiff < -Math.PI) turnDiff += Math.PI * 2;

  // O personagem .glb pode assumir o controle por um instante (parar, virar): ele devolve
  // quanto andar para a frente (root motion do clipe) e se o giro do corpo fica travado.
  const ctl = avatar ? avatar.update(dt, speed, { inputMag: canMove ? mag : 0, turnDiff: Math.abs(turnDiff) }) : null;

  if (ctl && ctl.override) {
    speed += (0 - speed) * Math.min(1, dt * TUNE.brake);
    if (ctl.freeze) speed = Math.max(speed, 0); // na virada o passo e do clipe
    if (Math.abs(ctl.rootMove) > 1e-5) {
      step.set(Math.sin(body.rotation.y), 0, Math.cos(body.rotation.y)).multiplyScalar(ctl.rootMove);
      const next = body.position.clone().add(step); collide(next); body.position.copy(next);
    }
  } else {
    speed += (goal - speed) * Math.min(1, dt * k);
    if (speed > 0.02) {
      step.set(wx, 0, wz).multiplyScalar(speed * dt);
      const next = body.position.clone().add(step);
      collide(next);
      body.position.copy(next);
      if (canMove) facing = Math.atan2(wx, wz);
    }
  }
  if (ctl && ctl.yawSnap) { body.rotation.y += ctl.yawSnap; facing = canMove ? wantFacing : body.rotation.y; speed = Math.max(speed, goal * 0.6); }

  // Giro suave do corpo pelo caminho mais curto (travado durante a virada de 180).
  if (!(ctl && ctl.freeze)) {
    let diff = facing - body.rotation.y;
    while (diff > Math.PI) diff -= Math.PI * 2;
    while (diff < -Math.PI) diff += Math.PI * 2;
    body.rotation.y += diff * Math.min(1, dt * TUNE.turn);
  }

  if (avatar) {
    // (animacao ja atualizada acima)
  } else {
    phase += dt * (3.4 + speed * 2.3);
    poseCharacter(CH, {
      phase, t,
      amp: Math.min(1, speed / TUNE.walk),
      run01: Math.min(1, speed / 3.4)
    });
  }

  contactShadow.position.set(body.position.x, 0.022, body.position.z);

  // Rotulos por proximidade e escolha da estacao ativa.
  let best = null, bd = TUNE.interact;
  STATIONS.forEach(s => {
    const d = Math.hypot(body.position.x - s.pos[0], body.position.z - s.pos[1]);
    const wanted = d < TUNE.labelFade ? Math.max(0, 1 - (d - 2) / 2.2) : 0;
    s.label.material.opacity += (wanted - s.label.material.opacity) * Math.min(1, dt * 7);
    const ring = s === active ? 0.5 + Math.sin(t * 3) * 0.16 : 0;
    s.ring.material.opacity += (ring - s.ring.material.opacity) * Math.min(1, dt * 8);
    if (d < bd) { bd = d; best = s; }
  });
  if (best !== active) { active = best; hud.setActive(best); }

  focusPoint.set(body.position.x, avatar ? 1.58 : 1.52, body.position.z);
  rig.update(dt, focusPoint, solids);

  updateDust(dt, t);
  anims.forEach(f => f(t));
}

let last = performance.now();
function loop(now) {
  const dt = Math.min(0.05, (now - last) / 1000);
  last = now;
  if (started) tick(dt, now / 1000);
  renderer.render(scene, camera);
  requestAnimationFrame(loop);
}
requestAnimationFrame(loop);

addEventListener('resize', () => {
  camera.aspect = innerWidth / innerHeight;
  camera.updateProjectionMatrix();
  renderer.setSize(innerWidth, innerHeight);
});

gate(renderer, scene, camera, () => {
  started = true;
  // o clique em ENTRAR ja prende o cursor para a camera seguir o mouse
  if (!isTouch && renderer.domElement.requestPointerLock) { const r = renderer.domElement.requestPointerLock(); if (r && r.catch) r.catch(() => {}); }
  last = performance.now();
  setTimeout(() => hud.toast(isTouch
    ? 'Direcional para andar · arraste a tela para girar a câmera · CORRER para acelerar'
    : 'Clique na tela para controlar a câmera com o mouse (Esc solta) · WASD para andar · Shift para correr · E para interagir'
  , 6800), 900);
}, loading);
