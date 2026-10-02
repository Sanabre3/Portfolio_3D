# Estúdio Sanabre

Portfólio navegável em 3D. O visitante controla um personagem dentro de um estúdio e
caminha até cada estação para abrir o projeto correspondente, com o site real
renderizado dentro do painel.

Sem etapa de build. Three.js entra por importmap (CDN).

## Rodar

Módulos ES não funcionam abrindo o arquivo direto (`file://`). Suba um servidor local:

```bash
npx serve .
# ou
python3 -m http.server 5173
```

E abra `http://localhost:3000` (ou a porta que aparecer).

## Publicar na Vercel

É estático. `vercel` na raiz, ou arraste a pasta no dashboard. Nenhuma configuração.

## Onde mexer

| Quero mudar | Arquivo |
|---|---|
| Projetos: título, ano, descrição, stack, URL, posição na sala | `src/config/projects.js` |
| Tamanho da sala, velocidades, câmera, distância de interação | `src/config/theme.js` |
| Cores dos materiais | `src/world/props.js` (objeto `M`) |
| Piso, parede, tapete, luminárias, poeira | `src/world/room.js` |
| Formato de cada móvel | `src/world/props.js` (objeto `BUILD`) |
| Personagem 3D (samurai .glb): carregamento, mistura dos clipes, molas da saia e da borla | `src/player/model.js` |
| Modelo, roupa, armadura, cabelo, lança e animações do .glb | `tools/samurai/` (gera `assets/samurai.glb`) |
| Personagem procedural de reserva (aparece enquanto o .glb carrega) | `src/player/character.js`, `src/player/animation.js` |
| Teclado, joystick, botões | `src/player/controls.js` |
| Comportamento da câmera | `src/camera/follow.js` |
| Painel do projeto e iframe | `src/ui/panel.js` |
| Texturas geradas por código | `src/core/textures.js` |
| Visual da interface | `src/style.css` |

## Adicionar um projeto

1. Em `src/config/projects.js`, copie um bloco e ajuste. `pos` é `[x, z]` em metros,
   com origem no centro da sala. `rot` é a rotação em radianos.
2. `kind` precisa existir em `BUILD` (`src/world/props.js`). Reaproveite um existente
   ou escreva um novo — a função recebe o grupo e devolve `[largura, profundidade]`
   para o cálculo de colisão.
3. `url: ''` esconde o iframe e mostra só o texto.

## Personagem

`assets/samurai.glb` (1,2 MB, Draco + WebP): corpo com esqueleto de 69 ossos, roupa e
armadura com materiais PBR, clipes Idle, Walk e Run. A velocidade dos clipes acompanha a
velocidade real do personagem (o pé não escorrega) e Walk e Run trocam sem perder o passo.
As placas da saia (kusazuri) e a borla da lança têm física de mola: a coxa empurra a placa
e a inércia do corpo balança as duas.

Se o .glb não carregar, o personagem procedural entra no lugar sem quebrar a página.

## Limitação conhecida

Sites que enviam `X-Frame-Options: DENY` ou `frame-ancestors` restrito não abrem
dentro do iframe. Depois de 5 segundos o painel troca a mensagem e oferece o botão
para abrir em nova aba. Seus deploys na Vercel permitem por padrão.
