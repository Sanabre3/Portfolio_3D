import * as THREE from 'three';
import { TUNE } from '../config/theme.js';

// Camera de terceira pessoa: orbita amortecida, com raycast contra
// paredes e moveis para nao atravessar geometria.
export class CameraRig {
  constructor(camera) {
    this.camera = camera;
    this.yaw = 0; this.pitch = 0.30; this.dist = TUNE.camDist;
    this.tYaw = 0; this.tPitch = 0.30; this.tDist = TUNE.camDist;
    this.target = new THREE.Vector3();
    this.ray = new THREE.Raycaster();
    this.zoomTween = null;
  }

  orbit(dYaw, dPitch) {
    this.tYaw += dYaw;
    this.tPitch = Math.max(-0.05, Math.min(1.1, this.tPitch + dPitch));
  }

  zoom(delta) {
    this.tDist = Math.max(TUNE.camMin, Math.min(TUNE.camMax, this.tDist + delta));
  }

  // Aproxima a camera de uma estacao ao interagir.
  // Guarda o enquadramento anterior para restore() poder desfazer.
  focus(fromPos, stationPos, duration = 0.8) {
    this.saved = { pitch: this.tPitch, dist: this.tDist };
    this.zoomTween = {
      t: 0, duration,
      from: { yaw: this.tYaw, pitch: this.tPitch, dist: this.tDist },
      to: {
        yaw: Math.atan2(fromPos.x - stationPos[0], fromPos.z - stationPos[1]),
        pitch: 0.16, dist: 2.5
      }
    };
  }

  // Volta ao enquadramento de antes da interacao, sem girar o yaw
  // (o jogador pode ter arrastado a camera enquanto o painel estava aberto).
  restore(duration = 0.6) {
    if (!this.saved) return;
    this.zoomTween = {
      t: 0, duration,
      from: { yaw: this.tYaw, pitch: this.tPitch, dist: this.tDist },
      to:   { yaw: this.tYaw, pitch: this.saved.pitch, dist: this.saved.dist }
    };
    this.saved = null;
  }

  update(dt, focusPoint, solids) {
    if (this.zoomTween) {
      const z = this.zoomTween;
      z.t = Math.min(1, z.t + dt / z.duration);
      const e = z.t < 0.5 ? 4 * z.t ** 3 : 1 - Math.pow(-2 * z.t + 2, 3) / 2;
      this.tDist = z.from.dist + (z.to.dist - z.from.dist) * e;
      this.tPitch = z.from.pitch + (z.to.pitch - z.from.pitch) * e;
      let dy = z.to.yaw - z.from.yaw;
      while (dy > Math.PI) dy -= Math.PI * 2;
      while (dy < -Math.PI) dy += Math.PI * 2;
      this.tYaw = z.from.yaw + dy * e;
      if (z.t >= 1) this.zoomTween = null;
    }

    const k = Math.min(1, dt * TUNE.camDamp);
    this.yaw += (this.tYaw - this.yaw) * k;
    this.pitch += (this.tPitch - this.pitch) * k;
    this.dist += (this.tDist - this.dist) * Math.min(1, dt * (TUNE.camDamp - 2));

    this.target.copy(focusPoint);
    const cp = Math.cos(this.pitch);
    const off = new THREE.Vector3(Math.sin(this.yaw) * cp, Math.sin(this.pitch), Math.cos(this.yaw) * cp);

    let dist = this.dist;
    this.ray.set(this.target, off.clone().normalize());
    const hit = this.ray.intersectObjects(solids, false);
    if (hit.length && hit[0].distance < dist) dist = Math.max(1.2, hit[0].distance - 0.25);

    this.camera.position.copy(this.target).add(off.normalize().multiplyScalar(dist));
    this.camera.lookAt(this.target.x, this.target.y - 0.12, this.target.z);
  }
}
