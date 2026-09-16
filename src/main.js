import * as THREE from 'three';
import { STATIONS } from './config/projects.js';
import { ROOM, TUNE } from './config/theme.js';
import { createRenderer, createScene, createCamera, addLights } from './core/scene.js';
import { buildRoom, buildDust } from './world/room.js';
import { buildStations, colliders } from './world/stations.js';
import { anims } from './world/props.js';
import { makeCharacter, makeContactShadow } from './player/character.js';
import { poseCharacter } from './player/animation.js';
import { input, isTouch, attachControls, readInput, maxSpeed } from './player/controls.js';
import { CameraRig } from './camera/follow.js';
import { Panel } from './ui/panel.js';
import { HUD, gate } from './ui/hud.js';

const renderer = createRenderer();
const scene = createScene();
const camera = createCamera();
addLights(scene);

buildRoom(scene);
const updateDust = buildDust(scene);
buildStations(scene, STATIONS);

const CH = makeCharacter();
CH.root.position.set(0, 0, 3.2);
scene.add(CH.root);
const contactShadow = makeContactShadow(scene);

// Geometria que a camera nao pode atravessar. O proprio personagem fica de fora.
const solids = [];
scene.traverse(o => {
  if (!o.isMesh || !o.geometry || o.geometry.type !== 'BoxGeometry') return;
  let p = o, inChar = false;
  while (p) { if (p === CH.root) { inChar = true; break; } p = p.parent; }
  if (!inChar) solids.push(o);
});

const rig = new CameraRig(camera);
const panel = new Panel();
const hud = new HUD(STATIONS.length);

let started = false, busy = false, active = null;
let speed = 0, phase = 0, facing = 0;
const focusPoint = new THREE.Vector3();
const step = new THREE.Vector3();

function interact() {
  if (!active || busy) return;
  busy = true;
  const s = active;
  rig.focus(CH.root.position, s.pos);
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
  onClose: () => panel.close(),
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
  speed += (goal - speed) * Math.min(1, dt * k);

  if (speed > 0.02) {
    step.set(wx, 0, wz).multiplyScalar(speed * dt);
    const next = CH.root.position.clone().add(step);
    collide(next);
    CH.root.position.copy(next);
    facing = Math.atan2(wx, wz);
  }

  // Giro suave do corpo pelo caminho mais curto.
  let diff = facing - CH.root.rotation.y;
  while (diff > Math.PI) diff -= Math.PI * 2;
  while (diff < -Math.PI) diff += Math.PI * 2;
  CH.root.rotation.y += diff * Math.min(1, dt * TUNE.turn);

  phase += dt * (3.4 + speed * 2.3);
  poseCharacter(CH, {
    phase, t,
    amp: Math.min(1, speed / TUNE.walk),
    run01: Math.min(1, speed / 3.4)
  });

  contactShadow.position.set(CH.root.position.x, 0.022, CH.root.position.z);

  // Rotulos por proximidade e escolha da estacao ativa.
  let best = null, bd = TUNE.interact;
  STATIONS.forEach(s => {
    const d = Math.hypot(CH.root.position.x - s.pos[0], CH.root.position.z - s.pos[1]);
    const wanted = d < TUNE.labelFade ? Math.max(0, 1 - (d - 2) / 2.2) : 0;
    s.label.material.opacity += (wanted - s.label.material.opacity) * Math.min(1, dt * 7);
    const ring = s === active ? 0.5 + Math.sin(t * 3) * 0.16 : 0;
    s.ring.material.opacity += (ring - s.ring.material.opacity) * Math.min(1, dt * 8);
    if (d < bd) { bd = d; best = s; }
  });
  if (best !== active) { active = best; hud.setActive(best); }

  focusPoint.set(CH.root.position.x, 1.42, CH.root.position.z);
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
  last = performance.now();
  setTimeout(() => hud.toast(isTouch
    ? 'Direcional para andar · arraste a tela para girar a câmera · CORRER para acelerar'
    : 'WASD para andar · Shift para correr · arraste para girar a câmera · E para interagir'
  , 6800), 900);
});
