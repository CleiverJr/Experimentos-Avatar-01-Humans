# Pesquisa Trilha D: Sintese e Controle de Avatares Neurais

> **Arquivo PDF Oficial:** [`Implementacoes/relatorio_experimentos_avatar.pdf`](relatorio_experimentos_avatar.pdf) *(Documento clean de 2 paginas para apresentacao em reuniao)*

---

## 1. Detalhe Importante: Natureza dos Modelos e Abordagem Pratica

**Detalhe Importante:** Os modelos de ponta apresentados na literatura recente, como Vasa-1 da Microsoft, Omnihuman-1.5 da ByteDance, Audio2Photoreal da Meta e InstructAvatar, nao possuem pesos de rede nem codigos-fonte liberados publicamente. O motivo justificado oficialmente pelas empresas para nao liberarem esses modelos e a preocupacao com o uso indevido para geracao de deepfakes.

Portanto, os experimentos realizados aqui foram, de certa forma, uma "gambiarra" tecnica para conseguir reproduzir e testar esses SOTAs. Utilizamos como base o motor de codigo aberto do LivePortrait / Ditto (ACM MM 2025), que fornece a espinha dorsal anatomica latente (21 keypoints tridimensionais e matriz de rotacao craniofacial), e implementamos diretamente sobre esse espaco os principios matematicos, mecanismos de controle facial, dinamicas de olhar e acenos propostos em cada artigo.

---

## 2. Os 4 Principais Gargalos de Avatares e Como Foram Resolvidos

1. **Boca aberta e dentes expostos no silencio:** Modelos comuns guiados por audio deixam a boca inerte e entreaberta quando a pessoa para de falar. Resolvemos isso aplicando uma camada de Voice Activity Detection (VAD) que forca o fechamento labial estrito (`vad_alpha = 0.0`) na ausencia de voz, eliminando a sensacao de dentes flutuantes.
2. **Cabeca congelada (colapso MSE):** Treinar redes neurais com erro medio quadratico tradicional faz o avatar paralisar a cabeca. Superamos esse problema com difusao estocastica (MDM), mantendo micro-movimentos organicos continuos.
3. **Avatar passivo que nao reage ao interlocutor:** Adotamos a dinamica diadica do Audio2Photoreal da Meta. Durante a fala do usuario, o avatar assume o papel de ouvinte, selando a boca e balancando a cabeca afirmativamente (head nods) em escuta ativa.
4. **Olhar fixo de teleprompter:** Implementamos o Gaze Aversion inspirado no Omnihuman da ByteDance, no qual o avatar desvia a cabeca e os olhos para pensar antes de responder perguntas, simulando deliberacao cognitiva humana.

---

## 3. O Que Cada Modelo Agrega na Pratica

- **VASA-1 (Microsoft, 2024):** Sintese holistica livre direto do som. Serve de baseline puro sem intervencoes manuais.
- **AUHead (ICLR 2026):** Controle de musculos faciais isolados via FACS de Paul Ekman. Permite franzir a testa em foco (AU04) ou abrir um grande sorriso genuino (AU12 e AU06).
- **InstructAvatar (AAAI 2025):** Direcao cenica em texto livre (postura altiva, queixo elevado) com fechamento labial automatico durante pausas.
- **Audio2Photoreal (Meta, CVPR 2024):** Dinamica de conversa real entre duas pessoas: o avatar escuta ativamente com acenos harmonicos de cabeca e boca 100% selada.
- **OmniHuman-1.5 (ByteDance, 2025):** Arquitetura de Dois Sistemas: fonacao rapida somada a mente deliberativa que desvia o olhar (Gaze Aversion) para refletir.
- **Motion Diffusion Model (MDM, ICLR 2023):** Amostragem estocastica livre que quebra a rigidez da pose media, garantindo movimentacao natural contínua.

---

## 4. O Experimento Mestre: A Prova de Fogo (Grade 2x3)

Colocamos os 6 modelos lado a lado com a mesma entrada (audio de 9.69 segundos com fala analitica, uma pausa critica de 2.2 segundos em silencio absoluto, e um climax oratorio final). A comparacao evidenciou com clareza visual o que cada modelo melhora:

| Modelo | Fase 1: Fala Inicial | Fase 2: Silencio de 2.2s | Fase 3: Climax | Diferencial Observado |
| :--- | :--- | :--- | :--- | :--- |
| **VASA-1** | Fala neutra direta. | Boca semi-aberta passiva (sem VAD). | Fala comum sem intencao. | Baseline puro de comparacao. |
| **AUHead** | Cenho franzido evidente (AU04). | Relaxamento muscular gradual. | Grande sorriso Duchenne (AU12). | Expressividade muscular cirurgica. |
| **InstructAvatar** | Postura ereta (Pitch -4.5 deg). | Labios 100% selados (`vad=0`). | Queixo erguido e oratoria firme. | Presenca cenica e boca fechada. |
| **Audio2Photoreal** | Turno de fala normal. | 2 Acenos claros (+5.5 deg) e boca selada. | Retomada suave de conversa. | Escuta ativa (concorda acenando). |
| **OmniHuman-1.5** | Foco compenetrado inicial. | Gaze Aversion: vira o rosto (-9 deg). | Foco direto frontal e queixo alto. | Desvia o olhar para pensar. |
| **Motion Diffusion** | Cinematica estocastica viva. | Dinamica postural organica continua. | Rica amplitude angular tridimensional. | Elimina a cabeca congelada/rigida. |

---

## 5. Recomendacoes Diretas para Decisao de Produto

Se fossemos escolher a receita ideal para colocar um avatar em producao hoje:

1. **Camada VAD Obrigatoria:** Qualquer solucao comercial de audio para movimento precisa de um modulo de Voice Activity Detection. Se o som parou, o deslocamento dos labios deve ser zerado (`vad_alpha = 0.0`). Isso resolve completamente o vício visual de boca entreaberta ou dentes aparentes.
2. **Para Assistentes e Atendimento Interativo:** Adotar a combinacao de Audio2Photoreal com InstructAvatar. O avatar escuta o interlocutor acenando a cabeca afirmativamente e mantem os labios fechados, gerando sensacao imediata de atencao.
3. **Para Videoaulas e Apresentacoes Longas:** Utilizar a arquitetura cognitiva do Omnihuman com AUHead. O desvio reflexivo de olhar (Gaze Aversion) antes de responder e os sorrisos em momentos-chave removem a impressao de robo lendo texto.
4. **Custo e Latencia:** O pipeline opera em tempo real na etapa de keypoints e levou cerca de 4 minutos para renderizar 10 segundos de video full-HD em hardware Apple Silicon com GPU MPS. E perfeitamente viavel tanto para pre-gravacao quanto para servidores CUDA.

---

**Relatorio de Pesquisa Trilha D** — Cleiver Junior | Experimentos Avatar 01 Humans  
**Codigos, videos e demonstracoes:** github.com/CleiverJr/Experimentos-Avatar-01-Humans
