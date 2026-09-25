// Ciclo de caminhada e corrida.
// Braco e perna opostos em contrafase, joelho dobrando so na fase de recuo,
// quadril subindo a cada passo.
//
// Se o personagem carrega arma (CH.carry === 'R' ou 'L'), esse braco sai do
// ciclo e assume uma pose fixa de porte — o outro compensa com amplitude maior,
// que e como o corpo realmente equilibra um peso de um lado so.
//
// state = { phase, t, amp, run01 }

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

  const carry = CH.carry;
  const swingArm = (key, s, gain) => {
    L['arm' + key].rotation.x = s * 0.62 * amp * gain;
    L['arm' + key].rotation.z = (key === 'L' ? 0.1 : -0.1) - (key === 'L' ? -1 : 1) * run01 * 0.12;
    L['elb' + key].rotation.x = -(0.25 + Math.max(0, s) * 0.5) * amp - run01 * 0.5;
  };
  const holdArm = key => {
    const side = key === 'L' ? -1 : 1;
    // ombro levemente aberto, cotovelo fechado: mao na altura do cabo
    L['arm' + key].rotation.x = -0.06 + Math.sin(phase) * 0.04 * amp;
    L['arm' + key].rotation.z = -side * 0.24;
    L['elb' + key].rotation.x = -0.62 - run01 * 0.12;
    L['elb' + key].rotation.z = side * 0.1;
  };

  if (carry === 'R') { holdArm('R'); swingArm('L', sw2, 1.35); }
  else if (carry === 'L') { holdArm('L'); swingArm('R', sw, 1.35); }
  else { swingArm('L', sw2, 1); swingArm('R', sw, 1); }

  // Parado: respiracao e olhar lento em volta
  CH.hips.position.y = 0.95 + Math.abs(Math.sin(phase)) * 0.055 * amp + Math.sin(t * 1.6) * 0.006 * (1 - amp);
  CH.hips.rotation.z = Math.sin(phase) * 0.05 * amp;
  CH.torso.rotation.y = -Math.sin(phase) * 0.09 * amp;
  CH.torso.rotation.x = run01 * 0.2 + Math.sin(t * 1.4) * 0.008 * (1 - amp);
  CH.head.rotation.y = Math.sin(phase) * 0.05 * amp + Math.sin(t * 0.6) * 0.06 * (1 - amp);
  CH.head.rotation.x = -run01 * 0.12;

  // Kusazuri: as placas da saia batem contra a perna, com atraso por painel.
  if (CH.skirt) {
    CH.skirt.forEach((panel, i) => {
      const lag = phase - i * 0.5;
      panel.rotation.x = Math.sin(lag) * 0.16 * amp;
      panel.rotation.z = Math.cos(lag * 0.5) * 0.05 * amp;
    });
  }

  // Borla da lanca oscilando
  if (CH.tassels) {
    CH.tassels.forEach((th, i) => {
      th.rotation.x = Math.sin(phase * 0.8 + i) * 0.22 * amp + Math.sin(t * 1.1 + i) * 0.05;
      th.rotation.z = Math.cos(phase * 0.8 + i) * 0.18 * amp;
    });
  }
}
