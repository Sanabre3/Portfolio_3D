# Pipeline do samurai (`assets/samurai.glb`)

O personagem é gerado por script no Blender 5 (módulo `bpy`), a partir da malha
base do MakeHuman (hm08). A malha, os targets, o esqueleto, os pesos e os olhos
do MakeHuman são **CC0**. Todo o resto — roupa, armadura, cabelo, lança, texturas,
materiais e animações — é gerado aqui.

## Refazer o .glb

```bash
pip install bpy==5.0.1          # Blender como módulo Python (Python 3.11)
# baixe os assets CC0 do MakeHuman para ./mh (veja a lista abaixo)
python3 textures.py             # texturas procedurais -> ./tex
python3 mh.py                   # corpo masculino atlético + esqueleto de jogo -> body.npz
python3.11 build.py ../../assets/samurai.glb
```

Os scripts usam `/tmp/sam` como pasta de trabalho. Ajuste o caminho no topo de
cada arquivo se for rodar em outro lugar.

Arquivos do MakeHuman (repositório `makehumancommunity/makehuman`, pasta `makehuman/data`):
`3dobjs/base.obj`, `rigs/default.mhskel`, `rigs/default_weights.mhw`,
`targets/macrodetails/asian-male-young.target`,
`targets/macrodetails/universal-male-young-maxmuscle-averageweight.target`,
`targets/macrodetails/height/male-young-averagemuscle-averageweight-maxheight.target`,
`eyes/high-poly/high-poly.obj`, `eyes/high-poly/high-poly.mhclo`.

## O que cada arquivo faz

| Arquivo | Papel |
|---|---|
| `mh.py` | Aplica os targets (asiático, jovem, musculoso, mais alto), reduz o esqueleto de 163 para 69 ossos e colapsa os pesos |
| `cloth.py` | Gi, hakama, kyahan, tabi e luvas como camadas deslocadas da própria malha do corpo (herdam os pesos exatos) e remove o corpo escondido embaixo |
| `armor.py` / `assemble_armor.py` | Dō de 5 lamelas, peitoral, costas, watagami, cinto, kusazuri de 8 painéis, sode, kote, gola — tudo sobre o perfil real do corpo, com bisel e nós dourados |
| `hair.py` | ~420 mechas achatadas com fluxo por região (franja sobre o olho direito, costeletas) + calota + sobrancelhas |
| `face.py` | Encaixe do olho do MakeHuman pelo `.mhclo`, córnea separada e cor de pele por vértice |
| `spear.py` / `grip.py` | Yari (haste, empunhaduras, colar, lâmina em losango, borla, ponteira) e o encaixe no punho fechado |
| `feet.py` | Sola e tiras das sandálias |
| `textures.py` / `mats.py` | Texturas procedurais e materiais PBR (laca com verniz, tecido com sheen, aço, latão, madeira) |
| `anim.py` / `clips.py` | Clipes Idle, Walk e Run gravados com pé no chão por quadro |
| `build.py` | Monta tudo, junta malhas por material e exporta com Draco + WebP |

Ossos extras para física no jogo: `kusazuri_F/FL/L/BL/B/BR/R/FR` e `tassel`.
A mola é calculada em `src/player/model.js`.
