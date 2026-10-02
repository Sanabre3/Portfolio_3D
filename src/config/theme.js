// Dimensoes da sala, em metros. O personagem tem ~1,75 m.
export const ROOM = { W: 20, D: 14, H: 4.2 };

// Ajuste fino de movimento e camera.
export const TUNE = {
  walk: 1.5,          // m/s caminhando (ritmo do clipe Walk do Mixamo)
  run: 5.0,           // m/s correndo
  accel: 9,           // suavizacao ao acelerar (maior = mais responsivo)
  brake: 12,          // suavizacao ao frear
  turn: 11,           // velocidade de giro do corpo
  camDist: 5.2,       // distancia inicial da camera
  camMin: 2.2,
  camMax: 9,
  camDamp: 9,
  playerRadius: 0.42, // raio de colisao (armadura ocupa mais espaco)
  interact: 2.3,      // distancia para poder interagir
  labelFade: 4.2      // distancia em que o rotulo comeca a aparecer
};

// Cor de fundo e nevoa.
export const ATMOS = { bg: 0x0D0B09, fogDensity: 0.034, exposure: 1.05 };
