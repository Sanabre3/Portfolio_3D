// Cada estacao do estudio. pos = [x, z] em metros, origem no centro da sala.
// rot = rotacao em radianos. url = '' esconde o iframe e mostra so o texto.
// kind precisa existir em BUILD, em ../world/props.js

export const STATIONS = [
  {
    id: 'odometro', kind: 'desk', pos: [-6.2, -5.0], rot: 0,
    tag: 'Odômetro WhatsApp', year: '2026 · em produção',
    desc: 'O motorista fotografa o painel do carro e manda no WhatsApp. Um modelo de visão lê a quilometragem, valida o número e grava direto na planilha da frota. Zero digitação, zero erro de transcrição.',
    stack: ['Node.js', 'IA de visão', 'WhatsApp API', 'Google Sheets'],
    url: ''
  },
  {
    id: 'globo', kind: 'globe', pos: [-1.0, -5.4], rot: 0,
    tag: 'Portfólio v2', year: 'em construção',
    desc: 'Single page em Vite + TypeScript com um globo terrestre navegável desenhado a partir de dados geográficos reais. Cada região abre um capítulo diferente do trabalho.',
    stack: ['Vite', 'TypeScript', 'd3-geo', 'Canvas'],
    url: ''
  },
  {
    id: 'zone', kind: 'jukebox', pos: [4.4, -5.2], rot: 0,
    tag: 'Zone Player', year: '2026',
    desc: 'Player de música com estética lo-fi. Arrasta arquivos de áudio para a crate e toca local, ou conecta YouTube e Spotify pelas APIs oficiais. Tem equalizador, troca de tema e alternância de lado A e B do disco.',
    stack: ['Web Audio', 'Spotify Web Playback', 'YouTube Data API', 'Vercel'],
    url: 'https://zone-player.vercel.app/'
  },
  {
    id: 'sobre', kind: 'shelf', pos: [-8.6, -1.0], rot: Math.PI / 2,
    tag: 'Sobre mim', year: 'Niterói, RJ',
    desc: 'Comecei pelo básico e nunca pulei etapa. Cada projeto aqui existe porque o anterior deixou uma pergunta em aberto. Disciplina vence talento — quando o talento não se disciplina.',
    stack: ['React', 'Next.js', 'Node', 'TypeScript', 'Supabase'],
    url: ''
  },
  {
    id: 'locadora', kind: 'crates', pos: [8.2, -1.4], rot: -Math.PI / 2,
    tag: 'Locadora IA', year: '2026',
    desc: 'Locadora com camada de inteligência artificial no catálogo e nas recomendações.',
    stack: ['Node.js', 'IA', 'Vercel'],
    url: 'https://locadora-ia.vercel.app/'
  },
  {
    id: 'foto', kind: 'easel', pos: [-4.6, 1.6], rot: 0.4,
    tag: 'Matheus Azevedo · Fotografia', year: '2026 · cliente',
    desc: 'Portfólio para fotógrafo, construído em volta das imagens: galeria em destaque, apresentação do trabalho e caminho direto para o contato. O mote do cliente abre o site — transformar o que você ama em arte.',
    stack: ['JavaScript', 'galeria responsiva', 'Vercel'],
    url: 'https://photografer-portfolio.vercel.app/'
  },
  {
    id: 'dash', kind: 'party', pos: [3.6, 1.8], rot: 0,
    tag: 'Decoration Dash', year: '2025 · acesso por login',
    desc: 'Sistema de gerenciamento de eventos para quem monta decoração: montagem do salão arrastando itens pelo mapa, controle de itens por evento e relatório final exportado em PDF para o cliente assinar.',
    stack: ['React', 'drag & drop', 'jsPDF', 'área restrita'],
    url: 'https://decoration-dash.vercel.app/login'
  },
  {
    id: 'betesda', kind: 'glass', pos: [-0.6, 5.6], rot: Math.PI,
    tag: 'Missão Betesda', year: '2026 · cliente',
    desc: 'Site completo para uma igreja em São Gonçalo: área de membros com cadastro e login, agenda de eventos que o administrador edita pelo próprio site, grupos de crescimento com mapa, pedidos de oração, aniversariantes do mês e contagem regressiva para o próximo culto.',
    stack: ['JavaScript', 'área de membros', 'Google Maps', 'Vercel'],
    url: 'https://missao-betesda.vercel.app/'
  },
  {
    id: 'pokedex', kind: 'pedestal', pos: [-7.4, 5.0], rot: 0,
    tag: 'Pokédex', year: '2024 · estudo',
    desc: 'Pokédex das três primeiras gerações, com filtro por tipo, filtro por geração, lista de favoritos, paginação e alternância de tema claro e escuro. Foi onde os estados assíncronos deixaram de ser decorados e passaram a ser entendidos.',
    stack: ['JavaScript', 'PokéAPI', 'Fetch', 'Vercel'],
    url: 'https://g-test-lemon.vercel.app/'
  },
  {
    id: 'contato', kind: 'radio', pos: [7.2, 5.2], rot: -Math.PI / 2,
    tag: 'Contato', year: 'disponível',
    desc: 'Aberto a projetos freelance e posições full stack. Respondo rápido e gosto de escopo escrito antes de começar.',
    stack: ['e-mail', 'LinkedIn', 'GitHub'],
    url: ''
  }
];
