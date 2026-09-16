// Ciclo de caminhada e corrida. Braco e perna opostos em contrafase,
// joelho dobrando so na fase de recuo, quadril subindo a cada passo.
// state = { speed, phase, t, amp, run01 }

export function poseCharacter(CH, state) {
  const { phase, t, amp, run01 } = state;
  const L = CH.limbs;
  const sw = Math.sin(phase);
  const sw2 = Math.sin(phase + Math.PI);

  L.legL.rotation.x = sw * 0.72 * amp;
  L.legR.rotation.x = sw2 * 0.72 * amp;

  // max(0, -sin) impede o joelho de dobrar para o lado errado
  L.kneeL.rotation.x = Math.max(0, -Math.sin(phase - 0.9)) * 1.15 * amp;
  L.kneeR.rotation.x = Math.max(0, -Math.sin(phase + Math.PI - 0.9)) * 1.15 * amp;

  L.armL.rotation.x = sw2 * 0.62 * amp;
  L.armR.rotation.x = sw * 0.62 * amp;
  L.armL.rotation.z = 0.1 + run01 * 0.12;
  L.armR.rotation.z = -0.1 - run01 * 0.12;

  // Correndo, os cotovelos fecham mais
  L.elbL.rotation.x = -(0.25 + Math.max(0, sw) * 0.5) * amp - run01 * 0.5;
  L.elbR.rotation.x = -(0.25 + Math.max(0, sw2) * 0.5) * amp - run01 * 0.5;

  // Parado: respiracao e olhar lento em volta
  CH.hips.position.y = 0.92 + Math.abs(Math.sin(phase)) * 0.055 * amp + Math.sin(t * 1.6) * 0.006 * (1 - amp);
  CH.hips.rotation.z = Math.sin(phase) * 0.05 * amp;
  CH.torso.rotation.y = -Math.sin(phase) * 0.11 * amp;
  CH.torso.rotation.x = run01 * 0.2 + Math.sin(t * 1.4) * 0.008 * (1 - amp);
  CH.head.rotation.y = Math.sin(phase) * 0.05 * amp + Math.sin(t * 0.6) * 0.06 * (1 - amp);
  CH.head.rotation.x = -run01 * 0.12;
}
