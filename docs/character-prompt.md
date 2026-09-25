# Prompt de criação do personagem

Personagem original. O prompt descreve tipos de peça (armadura lamelar, sode,
kusazuri, yari), não um personagem existente de nenhuma obra.

## Prompt principal

> Full body character sheet of an original RPG warrior, front view, standing
> at ease with a long spear held vertically in his right hand, butt of the
> shaft resting near the floor.
>
> **Build:** tall and broad-shouldered, heavy-set but athletic, confident
> relaxed posture, weight on one leg.
>
> **Face:** mid-twenties, warm brown skin, strong jaw, thick dark eyebrows,
> narrow dark eyes, faint confident half-smile, thin-rimmed rectangular black
> glasses.
>
> **Hair:** messy medium-length black hair, thick uneven strands falling over
> the forehead and partly covering the right eye, tapered sideburns reaching
> the jawline, slight blue sheen in the highlights.
>
> **Under-layer:** charcoal black gi with a high standing collar, long fitted
> sleeves, dark grey cloth wraps around both forearms, wide pleated hakama
> trousers in near-black, calf wraps and split-toe sandals.
>
> **Armour:** oxblood red lacquered lamellar over the black layer — a chest
> cuirass of five stacked horizontal lames, broad layered shoulder guards that
> hang down the upper arm, a waist sash, and a skirt of four hanging plate
> panels reaching mid-thigh, plus thigh plates and forearm bracers. Every lame
> is joined by visible antique-gold braided cord; the lacquer catches a soft
> highlight along each plate's top edge.
>
> **Spear:** dark wood shaft roughly two heads taller than the character,
> bound with grey grip wraps at three points, a brass collar under a straight
> polished steel blade, a deep red tassel below the blade, and a steel
> counterweight cap at the base.
>
> **Style:** clean cel-shaded anime illustration, crisp black line art,
> flat shading with one soft rim light from the upper left, neutral off-white
> background, subtle contact shadow under the feet.

## Variações úteis

- **Retrato:** troque a primeira linha por `Bust portrait, three-quarter view,
  shoulders and head only` e mantenha rosto, cabelo, gola e ombreiras.
- **Pose de combate:** `low fighting stance, spear levelled forward with both
  hands, cloth and tassel caught mid-motion`.
- **Folha de referência:** `character turnaround sheet, four views — front,
  three-quarter, side and back — same scale, evenly spaced, neutral pose`.

## Negativos

> blurry, low detail, extra fingers, extra limbs, deformed hands, watermark,
> signature, text, cluttered background, oversaturated colours, photorealistic

## Relação com o código

O modelo 3D em `src/player/character.js` segue esta mesma descrição peça por
peça. Se mudar o prompt, os pontos de ajuste no código são:

| Peça no prompt | Onde mexer |
|---|---|
| Cores de laca, cordoalha, tecido, cabelo | objeto `LOOK`, topo do arquivo |
| Número de lamelas do peito | laço `for (let i = 0; i < 5; i++)` em `cuirass` |
| Ombreiras (sode) | laço dentro de `sode`, 4 lamelas |
| Saia de placas (kusazuri) | bloco `skirt`, 4 painéis de 3 lamelas |
| Lança: comprimento, lâmina, borla | bloco `weapon`, no fim do arquivo |
| Óculos | `LOOK.glasses = false` remove |
