import * as THREE from 'three';
import { ATMOS } from '../config/theme.js';

export function createRenderer() {
  const renderer = new THREE.WebGLRenderer({ antialias: true, powerPreference: 'high-performance' });
  renderer.setPixelRatio(Math.min(devicePixelRatio, 2));
  renderer.setSize(innerWidth, innerHeight);
  renderer.shadowMap.enabled = true;
  renderer.shadowMap.type = THREE.PCFSoftShadowMap;
  renderer.outputColorSpace = THREE.SRGBColorSpace;
  renderer.toneMapping = THREE.ACESFilmicToneMapping;
  renderer.toneMappingExposure = ATMOS.exposure;
  renderer.domElement.style.position = 'fixed';
  renderer.domElement.style.inset = '0';
  document.body.appendChild(renderer.domElement);
  return renderer;
}

export function createScene() {
  const scene = new THREE.Scene();
  scene.background = new THREE.Color(ATMOS.bg);
  scene.fog = new THREE.FogExp2(ATMOS.bg, ATMOS.fogDensity);
  return scene;
}

export function createCamera() {
  return new THREE.PerspectiveCamera(52, innerWidth / innerHeight, 0.1, 120);
}

// Luz ambiente fria + dois refletores quentes. Só o primeiro projeta sombra,
// para não multiplicar o custo do shadow map.
export function addLights(scene) {
  scene.add(new THREE.HemisphereLight(0x6A5842, 0x0E0B08, 0.55));

  const key = new THREE.SpotLight(0xFFD9A0, 90, 26, 0.85, 0.7, 1.6);
  key.position.set(-3, 4.0, -2);
  key.target.position.set(-2, 0, 0);
  key.castShadow = true;
  key.shadow.mapSize.set(1024, 1024);
  key.shadow.camera.near = 1;
  key.shadow.camera.far = 22;
  key.shadow.bias = -0.002;
  key.shadow.normalBias = 0.03;
  scene.add(key, key.target);

  const key2 = new THREE.SpotLight(0xFFCE95, 60, 24, 0.9, 0.75, 1.6);
  key2.position.set(5, 4.0, 3);
  key2.target.position.set(4, 0, 3);
  scene.add(key2, key2.target);

  const fill = new THREE.PointLight(0xE8C08A, 22, 16, 1.8);
  fill.position.set(0, 2.6, 2);
  scene.add(fill);
}
