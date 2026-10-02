import * as THREE from 'three';
import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js';
import { DRACOLoader } from 'three/addons/loaders/DRACOLoader.js';
import { RoomEnvironment } from 'three/addons/environments/RoomEnvironment.js';

// ---------------------------------------------------------------------------
// Personagens em .glb: modelo gerado no TRELLIS.2, rig e animacoes do Mixamo
// (Idle, LookAround, Walk, Run). O pipeline fica em tools/samurai/
// (combine_mixamo.py monta o arquivo).
//
// Aqui ficam: carregamento, mistura dos clipes pela velocidade e a fisica
// secundaria (molas) nas placas da saia e na borla da lanca. Os clipes animam
// o corpo; as molas rodam depois do mixer e sobrescrevem so os ossos delas.
// ---------------------------------------------------------------------------

// Avatares disponiveis.
//   dev     -> avatar principal (voce, estilo anime). Ainda nao existe: gere assets/dev.glb.
//   secreto -> skin secreta (easter egg). So e baixado quando o visitante desbloqueia.
//   samurai -> reserva enquanto o dev.glb nao existe.
// ?personagem=<chave> na URL forca um deles (para testar).
// speed = velocidade natural de cada clipe (m/s), medida no proprio clipe.
// timeScale = velocidade do jogo / velocidade natural -> o pe nao escorrega.
export const AVATARES = {
  dev:     { url: './assets/dev.glb',        speed: { Walk: 1.02, Run: 6.7 } }, // mesmos clipes do Mixamo; medir de novo com o dev.glb
  secreto: { url: './assets/personagem.glb', speed: { Walk: 1.02, Run: 6.7 } },
  samurai: { url: './assets/samurai.glb',    speed: { Walk: 1.4,  Run: 3.3 } }
};

// Ordem de tentativa do avatar inicial. Quando o dev.glb existir, pode tirar 'samurai'.
const INICIAL = ['dev', 'samurai'];
const DRACO = 'https://unpkg.com/three@0.160.0/examples/jsm/libs/draco/gltf/';

let loader = null;
function getLoader() {
  if (!loader) loader = new GLTFLoader().setDRACOLoader(new DRACOLoader().setDecoderPath(DRACO));
  return loader;
}

export function loadAvatar(key, renderer, onProgress) {
  const cfg = AVATARES[key];
  if (!cfg) return Promise.reject(new Error('avatar desconhecido: ' + key));
  return new Promise((resolve, reject) => {
    getLoader().load(cfg.url, gltf => resolve(Object.assign(setup(gltf, renderer, cfg), { key })), e => {
      if (e.total && onProgress) onProgress(e.loaded / e.total);
    }, reject);
  });
}

// Avatar inicial: o da URL, se houver; senao o primeiro de INICIAL que carregar.
export async function loadDefaultAvatar(renderer, onProgress) {
  const forced = new URLSearchParams(location.search).get('personagem');
  const order = forced && AVATARES[forced] ? [forced] : INICIAL;
  let lastErr = null;
  for (const key of order) {
    try { return await loadAvatar(key, renderer, onProgress); }
    catch (err) { lastErr = err; console.warn(AVATARES[key].url + ' nao carregou:', err); }
  }
  throw lastErr;
}

function setup(gltf, renderer, cfg) {
  const root = new THREE.Group();
  const model = gltf.scene;
  root.add(model);

  // Reflexos so no personagem: a sala continua com a luz que ja tinha,
  // mas laca, aco e latao ganham um ambiente para refletir.
  const pmrem = new THREE.PMREMGenerator(renderer);
  const env = pmrem.fromScene(new RoomEnvironment(), 0.04).texture;
  pmrem.dispose();

  model.traverse(o => {
    if (!o.isMesh) return;
    o.castShadow = true;
    o.receiveShadow = true;
    o.frustumCulled = false; // a malha anima alem da caixa de repouso
    const mats = Array.isArray(o.material) ? o.material : [o.material];
    mats.forEach(m => {
      m.envMap = env;
      m.envMapIntensity = m.metalness > 0.5 ? 0.9 : 0.45;
      if (m.name === 'Cornea') { m.depthWrite = false; }
    });
  });

  const mixer = new THREE.AnimationMixer(model);
  const clip = n => gltf.animations.find(a => a.name === n);
  const act = {};
  ['Idle', 'Walk', 'Run'].forEach(n => {
    act[n] = mixer.clipAction(clip(n));
    act[n].play();
    act[n].setEffectiveWeight(n === 'Idle' ? 1 : 0);
  });

  // "Looking Around": entra quando o personagem fica parado por um tempo e volta ao Idle no fim
  const look = clip('LookAround') ? mixer.clipAction(clip('LookAround')) : null;
  if (look) { look.setLoop(THREE.LoopOnce); look.clampWhenFinished = true; look.play(); look.setEffectiveWeight(0); look.paused = true; }
  let still = 0, lookMix = 0, looking = false;

  const bone = n => model.getObjectByName(n);
  const springs = makeSkirt(model, bone);
  const tassel = makeTassel(bone('tassel'));

  let walkPhase = 0;
  const lastRoot = new THREE.Vector3();
  const vel = new THREE.Vector3(), accel = new THREE.Vector3(), prevVel = new THREE.Vector3();
  let first = true;

  // ---- Animacoes de uma vez so: parar e virar 180 graus ----
  // O deslocamento para a frente vem do proprio clipe (root motion), guardado no .glb
  // em userData.rootmotion: a distancia percorrida em cada quadro.
  let RM = {};
  model.traverse(o => { if (o.userData && o.userData.rootmotion) { try { RM = JSON.parse(o.userData.rootmotion); } catch (e) {} } });
  const once = {};
  ['StopWalk', 'StopWalkF', 'TurnWalk', 'TurnRun'].forEach(n => {
    const c = clip(n); if (!c) return;
    const a = mixer.clipAction(c); a.setLoop(THREE.LoopOnce); a.clampWhenFinished = true;
    a.play(); a.paused = true; a.setEffectiveWeight(0); once[n] = a;
  });
  let cur = null, curT = 0, curD = 0, mix = 0, fading = false, lastSpeed = 0, stopToggle = false;
  const FADE_IN = 0.15, FADE_OUT = 0.25;
  function start(name) {
    const a = once[name]; if (!a) return false;
    cur = name; curT = 0; curD = 0; fading = false;
    a.reset(); a.paused = false; a.setEffectiveWeight(0);
    return true;
  }
  function distAt(name, t) {
    const r = RM[name]; if (!r) return 0;
    const f = Math.min(1, t / r.duration) * (r.d.length - 1), i = Math.floor(f), k = f - i;
    return r.d[i] + ((r.d[Math.min(i + 1, r.d.length - 1)]) - r.d[i]) * k;
  }

  // speed em m/s. info = { inputMag, turnDiff } vindo do controle.
  // Devolve { override, rootMove, freeze, yawSnap } para o main.js aplicar no corpo.
  function update(dt, speed, info = {}) {
    dt = Math.min(dt, 0.05);
    const out = { override: false, rootMove: 0, freeze: false, yawSnap: 0 };
    const inputMag = info.inputMag || 0, turnDiff = info.turnDiff || 0;

    // gatilhos
    if (!cur) {
      if (lastSpeed > 0.7 && lastSpeed < 3.0 && inputMag < 0.08) {
        stopToggle = !stopToggle; start(stopToggle ? 'StopWalkF' : 'StopWalk');
      } else if (speed > 0.6 && turnDiff > 2.5) {
        start(speed > 2.8 ? 'TurnRun' : 'TurnWalk');
      }
    }
    lastSpeed = speed;

    if (cur) {
      const a = once[cur], dur = a.getClip().duration, isTurn = cur.startsWith('Turn');
      curT += dt;
      // parar pode ser interrompido se o jogador voltar a andar
      if (!isTurn && inputMag > 0.08 && curT > 0.2) fading = true;
      if (curT >= dur - (isTurn ? 0.02 : FADE_OUT)) fading = true;
      const d = distAt(cur, curT); out.rootMove = d - curD; curD = d;
      out.override = true; out.freeze = isTurn;
      if (isTurn && curT >= dur - 0.02) {
        // fim da virada: o corpo gira 180 de uma vez e o clipe sai no mesmo quadro (sem girar duas vezes)
        out.yawSnap = Math.PI; a.setEffectiveWeight(0); a.paused = true; cur = null; mix = 0;
      } else {
        mix += ((fading ? 0 : 1) - mix) * Math.min(1, dt / (fading ? FADE_OUT : FADE_IN) * 2.5);
        a.setEffectiveWeight(mix);
        if (fading && mix < 0.02) { a.setEffectiveWeight(0); a.paused = true; cur = null; mix = 0; }
      }
      if (fading && !isTurn) out.override = inputMag < 0.08; // voltou a andar: o jogo retoma o controle
    }

    // Pesos da locomocao: parado -> andando -> correndo, reduzidos enquanto um clipe unico toca.
    const wWalk = smooth(0.05, 1.0, speed) * (1 - smooth(2.2, 3.6, speed));
    const wRun = smooth(2.2, 3.6, speed);
    const wIdle = 1 - smooth(0.05, 0.6, speed);
    still = speed < 0.05 && !cur ? still + dt : 0;
    if (look) {
      if (!looking && still > 7) { looking = true; look.reset(); look.paused = false; look.setEffectiveWeight(0); }
      if (looking && (speed > 0.05 || cur || look.time >= look.getClip().duration - 0.6)) { looking = false; still = 0; }
      lookMix += ((looking ? 1 : 0) - lookMix) * Math.min(1, dt * 3);
    }
    const keep = 1 - mix;
    if (look) look.setEffectiveWeight(wIdle * lookMix * keep);
    act.Idle.setEffectiveWeight(wIdle * (1 - lookMix) * keep);
    act.Walk.setEffectiveWeight(wWalk * (1 - wIdle * 0.5) * keep);
    act.Run.setEffectiveWeight(wRun * keep);

    // ciclos por segundo = velocidade / distancia percorrida em um ciclo do clipe
    const dW = act.Walk.getClip().duration, dR = act.Run.getClip().duration;
    const cps = (1 - wRun) * speed / (cfg.speed.Walk * dW) + wRun * speed / (cfg.speed.Run * dR);
    walkPhase = (walkPhase + dt * cps) % 1;
    act.Walk.time = walkPhase * act.Walk.getClip().duration;
    act.Run.time = walkPhase * act.Run.getClip().duration;
    act.Walk.timeScale = 0; act.Run.timeScale = 0; // tempo controlado aqui
    mixer.update(dt);

    // Velocidade e aceleracao do corpo (para a inercia das molas).
    model.updateMatrixWorld(true);
    const p = root.position;
    if (first) { lastRoot.copy(p); first = false; }
    vel.copy(p).sub(lastRoot).divideScalar(Math.max(dt, 1e-3));
    accel.copy(vel).sub(prevVel).divideScalar(Math.max(dt, 1e-3));
    prevVel.copy(vel); lastRoot.copy(p);

    springs.forEach(s => s.step(dt, accel));
    if (tassel) tassel.step(dt, accel);
    return out;
  }

  return { root, model, mixer, update, radius: 0.42, height: 1.85 };
}

function smooth(a, b, x) { const t = Math.min(1, Math.max(0, (x - a) / (b - a))); return t * t * (3 - 2 * t); }

// ---- Kusazuri: cada painel e um pendulo amortecido em torno do cinto. ----
// O alvo do angulo vem da perna: se o joelho avanca na direcao do painel,
// empurra a placa para fora. A aceleracao do corpo entra como inercia.
function makeSkirt(model, bone) {
  const names = ['F', 'FL', 'L', 'BL', 'B', 'BR', 'R', 'FR'];
  const knees = [bone('lowerleg01L'), bone('lowerleg01R')];
  const hipsJ = [bone('upperleg01L'), bone('upperleg01R')];
  const hj = new THREE.Vector3(), kj = new THREE.Vector3();
  const FLARE = Math.atan(0.24); // inclinacao que o painel ja tem no modelo
  const hips = bone('root');
  const out = [];
  const tmp = new THREE.Vector3(), pivot = new THREE.Vector3(), nW = new THREE.Vector3();
  const qW = new THREE.Quaternion(), qP = new THREE.Quaternion(), qInv = new THREE.Quaternion();
  const down = new THREE.Vector3(), axisW = new THREE.Vector3(), axisL = new THREE.Vector3();
  names.forEach(n => {
    const b = bone('kusazuri_' + n);
    if (!b) return;
    const rest = b.quaternion.clone();
    // direcao para fora do painel, no espaco do osso root (horizontal)
    const headLocal = b.position.clone();
    const outward = new THREE.Vector3(headLocal.x, 0, headLocal.z);
    let ang = 0, vel = 0;
    out.push({
      step(dt, accel) {
        b.quaternion.copy(rest);
        b.updateMatrixWorld(true);
        b.getWorldPosition(pivot);
        hips.getWorldQuaternion(qP);
        nW.copy(outward).applyQuaternion(qP); nW.y = 0; nW.normalize();
        // quanto a coxa invade o painel: amostra a coxa entre o quadril e o joelho
        // e exige que a linha do painel passe por fora dela (raio da hakama ~12 cm).
        let need = 0;
        for (let i = 0; i < 2; i++) {
          hipsJ[i].getWorldPosition(hj); knees[i].getWorldPosition(kj);
          for (const t of [0.45, 0.7, 1.0]) {
            tmp.lerpVectors(hj, kj, t);
            const depth = pivot.y - tmp.y;
            if (depth < 0.08 || depth > 0.42) continue;
            const along = tmp.sub(pivot).dot(nW);
            need = Math.max(need, Math.atan2(along + 0.12, depth) - FLARE);
          }
        }
        const push = need;
        const target = Math.max(0, push) - accel.dot(nW) * 0.012;
        // mola critica-ish
        const k = 140, c = 14;
        vel += (k * (target - ang) - c * vel) * dt;
        ang += vel * dt;
        ang = Math.max(-0.25, Math.min(0.9, ang));
        // eixo de giro: horizontal, tangente ao cinto
        down.set(0, -1, 0);
        axisW.crossVectors(down, nW).normalize();
        b.getWorldQuaternion(qW); qInv.copy(qW).invert();
        axisL.copy(axisW).applyQuaternion(qInv).normalize();
        b.quaternion.multiply(new THREE.Quaternion().setFromAxisAngle(axisL, ang));
      }
    });
  });
  return out;
}

// ---- Borla: pendulo esferico pendurado no colar da lanca. ----
function makeTassel(b) {
  if (!b) return null;
  const rest = b.quaternion.clone();
  const dir = new THREE.Vector3(0, -1, 0), v = new THREE.Vector3();
  const g = new THREE.Vector3(0, -9.8, 0), f = new THREE.Vector3();
  const qP = new THREE.Quaternion(), yAxis = new THREE.Vector3(0, 1, 0);
  const localDir = new THREE.Vector3();
  return {
    step(dt, accel) {
      // forca = gravidade - aceleracao do corpo; a borla se alinha a ela com atraso
      f.copy(g).sub(accel.clone().multiplyScalar(0.8)).normalize();
      v.addScaledVector(f.sub(dir), 60 * dt).multiplyScalar(Math.exp(-6 * dt));
      dir.addScaledVector(v, dt).normalize();
      b.parent.getWorldQuaternion(qP);
      localDir.copy(dir).applyQuaternion(qP.invert());
      // gira a partir da pose de repouso (sem torcer a borla em torno do eixo)
      const restDir = yAxis.clone().applyQuaternion(rest);
      b.quaternion.setFromUnitVectors(restDir, localDir).multiply(rest);
    }
  };
}
