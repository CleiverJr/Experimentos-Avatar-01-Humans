# Experimentos Avatar 01 — Humans

Repositório de pesquisa científica, validação matemática e implementações práticas dedicadas à **síntese, animação neural foto-realista e controle comportamental de avatares humanos** a partir de áudio de fala e linguagem natural.

O objetivo deste projeto é investigar, destrinchar matematicamente e implementar manualmente os princípios fundamentais dos principais modelos do estado da arte (**SOTA**), compreendendo desde a cinemática de deformação canônica em espaços latentes 3D até a modelagem generativa por difusão estocástica e sistemas cognitivos deliberativos.

---

## Sumário Executivo dos Experimentos e Resultados

Todos os 7 módulos foram implementados do zero, validados algebricamente e renderizados em **vídeos foto-realistas de alta fidelidade (1024x1024 @ 25 FPS)** com aceleração por hardware na GPU Apple Silicon (Metal Performance Shaders - MPS com precisão BF16).

| Módulo | Modelo / Paradigma | Paper de Referência | O que foi Testado na Prática | Vídeo Renderizado | Principais Resultados & Métricas |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **01** | **Ditto Core & Espaço Latente** | [LivePortrait.pdf](Artigos/LivePortrait.pdf) *(Guo et al., 2024)* | Decomposição de 21 keypoints 3D, matriz de rotação $\mathbf{R} \in \mathrm{SO}(3)$ via 66 bins, distorção $WarpF3D$ e decodificador SPADE. | — *(Validação Algébrica)* | $\mathbf{R}^T \mathbf{R} = \mathbf{I}$, $\det(\mathbf{R}) = 1.0000$. Desacoplamento perfeito entre identidade canônica e movimento. |
| **02** | **VASA-1 Audio Motion** | [VASA-1.pdf](Artigos/VASA-1.pdf) *(Microsoft Research, 2024)* | Síntese autônoma de dinâmica facial e pose livre de cabeça a partir de features HuBERT sem regras manuais. | [`video_vasa1.mp4`](Implementacoes/02_vasa1_audio_motion/video_vasa1.mp4)<br>*(9.84s \| 246 frames)* | Pitch $[-2.1^\circ, +3.4^\circ]$, Yaw $[-4.2^\circ, +3.8^\circ]$. Sincronia fonética estrita e micro-movimentos reflexos. |
| **03** | **AUHead FACS Control** | [AUHead.pdf](Artigos/AUHead.pdf) *(ICLR 2026)* | Mapeamento biomecânico de Action Units do FACS para micro-deformações dos 21 keypoints 3D + Comparativo Split-Screen. | [`video_auhead.mp4`](Implementacoes/03_auhead_facs_control/video_auhead.mp4)<br>[`video_comparativo...`](Implementacoes/03_auhead_facs_control/video_comparativo_vasa_vs_auhead.mp4)<br>*(2048x1024 lado a lado)* | AU04 reduz Y em $0.008$ (glabela/raiva); AU12 expande X em $0.035$ (zigomático/sorriso). Modulação anatômica cirúrgica. |
| **04** | **InstructAvatar NLP** | [InstructAvatar.pdf](Artigos/InstructAvatar.pdf) *(AAAI 2025)* | Direção cênica via linguagem natural; parser semântico de emoções e solução do "efeito boca aberta/dentes expostos". | [`video_instruct.mp4`](Implementacoes/04_instruct_avatar_nlp/video_instruct.mp4)<br>*(10.80s \| 270 frames)* | Modulação dinâmica de fala: atenuação de AUs em fala ativa garante contato bilabial natural em fonemas consonantais. |
| **05** | **Audio2Photoreal Dialogue** | [Audio2Photoreal.pdf](Artigos/Audio2Photoreal.pdf) *(Meta Reality Labs, CVPR 2024)* | Comportamento em conversa diádica (fala vs escuta com acenos de cabeça / *backchanneling* e boca 100% selada). | [`video_diadico.mp4`](Implementacoes/05_audio2photoreal_dialogue/video_diadico.mp4)<br>*(14.68s \| 367 frames)* | VAD detecta pausa do avatar; 2 acenos harmônicos de concordância ($\Delta \text{Pitch} \in [-1.8^\circ, +2.5^\circ]$) com boca imóvel. |
| **06** | **OmniHuman-1.5 Dual System** | [OmniHuman-1.5.pdf](Artigos/OmniHuman-1.5.pdf) *(ByteDance, 2025)* | Arquitetura cognitiva dual: Sistema 1 reativo (fonação HuBERT) + Sistema 2 deliberativo (arcos de intenção cênica). | [`video_omnihuman.mp4`](Implementacoes/06_omnihuman_dual_system/video_omnihuman.mp4)<br>*(10.76s \| 269 frames)* | Arco 2 (*Gaze Aversion*): desvio lateral $\Delta \text{Yaw} = -3.80^\circ$; Arco 3 (*Convicção*): elevação $\Delta \text{Pitch} = -3.20^\circ$. |
| **07** | **Motion Diffusion (MDM)** | [MDM_Motion_Diffusion.pdf](Artigos/MDM_Motion_Diffusion.pdf) *(Tevet et al., ICLR 2023)*<br>[DDPM.pdf](Artigos/DDPM.pdf) *(NeurIPS 2020)* | Superação da regressão à média (1-para-Muitos) via amostragem DDPM/DDIM com predição direta de $\hat{x}_0$ e perda $\mathcal{L}_{vel}$. | [`video_mdm.mp4`](Implementacoes/07_motion_diffusion_mdm/video_mdm.mp4)<br>*(12.48s \| 312 frames)* | Diversidade angular multi-seed: $3.720^\circ$; Preservação labial fonética: $0.0045$; Suavidade temporal: $0.0537^\circ/\text{frame}^2$. |

---

## Detalhamento Técnico dos Módulos Testados

```
                                ARQUITETURA CONCEITUAL DO PROJETO
                                
      ┌────────────────────────────────────────────────────────────────────────┐
      │                         SISTEMA COGNITIVO                              │
      │  [InstructAvatar: Comandos NLP]      [OmniHuman-1.5: Sistema 2 (LLM)]  │
      │  • Emoções cênicas em texto          • Arcos de reflexão & convicção   │
      └──────────────────┬─────────────────────────────────┬───────────────────┘
                         │                                 │
                         ▼                                 ▼
      ┌────────────────────────────────────────────────────────────────────────┐
      │                     MOTOR DE DIFUSÃO CINEMÁTICA                        │
      │  [MDM / DDPM: Tevet et al.]          [VASA-1: Dinâmica Holística]      │
      │  • Amostragem Estocástica Reversa    • Extração de features HuBERT     │
      │  • Predição Direta de Sinal x̂_0      • Resolução do Colapso à Média    │
      └──────────────────┬─────────────────────────────────┬───────────────────┘
                         │                                 │
                         ▼                                 ▼
      ┌────────────────────────────────────────────────────────────────────────┐
      │                    CONTROLE ANATÔMICO & BIOMECÂNICO                    │
      │  [AUHead: Action Units (FACS)]       [Audio2Photoreal: Diádico Meta]   │
      │  • Deformação muscular precisa       • Escuta ativa e acenos (Nodding) │
      │  • Preservação de contato bilabial   • Boca selada em repouso          │
      └──────────────────┬─────────────────────────────────┬───────────────────┘
                         │                                 │
                         ▼                                 ▼
      ┌────────────────────────────────────────────────────────────────────────┐
      │                       RENDERIZADOR FOTO-REALISTA                       │
      │  [LivePortrait / Ditto Core: 21 Keypoints 3D + SO(3)]                  │
      │  • Volume de Identidade (x_s) + Deformação Motora (x_d)                │
      │  • Distorção Tridimensional WarpF3D + Decodificador SPADE (GPU MPS)    │
      └────────────────────────────────────────────────────────────────────────┘
```

---

### Módulo 01: Ditto Core & Espaço Latente de Movimento (LivePortrait)
- **Localização:** [`Implementacoes/01_ditto_core/`](Implementacoes/01_ditto_core/)
- **Script:** [`01_espaco_latente.py`](Implementacoes/01_ditto_core/01_espaco_latente.py)
- **O que foi testado:**
  1. A formulação algébrica que governa o espaço de movimento canônico implícito de 21 keypoints tridimensionais ($\mathbf{x}_c \in \mathbb{R}^{21 \times 3}$);
  2. A conversão de tensores discretos de 66 bins em ângulos de Euler em graus (`bin66_to_degree`) e síntese da matriz ortogonal $\mathbf{R} \in \mathrm{SO}(3)$;
  3. A equação canônica de translação e deformação:
     $$\mathbf{x} = \mathbf{R} \mathbf{x}_c + \mathbf{t} + \boldsymbol{\delta}_{exp}$$
  4. O desacoplamento estrito entre as características de aparência do sujeito de origem ($\mathbf{x}_s$) e a trajetória motora condutora ($\mathbf{x}_d$).
- **Resultados:**
  - Validação estrita da ortogonalidade com tolerância $\epsilon < 10^{-6}$: $\mathbf{R}^T \mathbf{R} = \mathbf{I}$ e $\det(\mathbf{R}) = 1.000000$;
  - Isolamento bem-sucedido de deformação de volume ($WarpF3D$) e síntese de texturas via decodificador neural SPADE.

---

### Módulo 02: VASA-1 (Microsoft Research) — Dinâmica Holística via Áudio
- **Localização:** [`Implementacoes/02_vasa1_audio_motion/`](Implementacoes/02_vasa1_audio_motion/)
- **Scripts:** [`vasa1_gerador_dinamica.py`](Implementacoes/02_vasa1_audio_motion/vasa1_gerador_dinamica.py), [`renderizar_video_vasa1.py`](Implementacoes/02_vasa1_audio_motion/renderizar_video_vasa1.py)
- **O que foi testado:**
  1. Extração de representações acústicas auto-supervisionadas (HuBERT) a partir de fala natural em 16 kHz;
  2. Mapeamento direto áudio $\to$ dinâmica facial holística e atitude espontânea da cabeça em espaço 3D;
  3. Renderização neural completa foto-realista acelerada por hardware na GPU Apple Silicon (MPS).
- **Resultados:**
  - Vídeo sintetizado: [`video_vasa1.mp4`](Implementacoes/02_vasa1_audio_motion/video_vasa1.mp4) (9.84 segundos, 246 frames, 1024x1024);
  - Amplitude natural de movimento da cabeça sem diretivas explícitas: Pitch $[-2.1^\circ, +3.4^\circ]$, Yaw $[-4.2^\circ, +3.8^\circ]$, Roll $[-1.8^\circ, +1.5^\circ]$;
  - Sincronização labial de alta fidelidade com micro-expressões reflexas e piscares de olhos autônomos.

---

### Módulo 03: AUHead (ICLR 2026) — Controle Anatômico FACS e Comparativo
- **Localização:** [`Implementacoes/03_auhead_facs_control/`](Implementacoes/03_auhead_facs_control/)
- **Scripts:** [`auhead_facs_mapeador.py`](Implementacoes/03_auhead_facs_control/auhead_facs_mapeador.py), [`renderizar_video_auhead.py`](Implementacoes/03_auhead_facs_control/renderizar_video_auhead.py), [`comparativo_vasa_vs_auhead.py`](Implementacoes/03_auhead_facs_control/comparativo_vasa_vs_auhead.py)
- **O que foi testado:**
  1. Mapeamento cinemático de Action Units (AUs) do Facial Action Coding System de Paul Ekman para translações vetoriais dos 21 keypoints:
     - `AU01` / `AU02`: Elevação de sobrancelhas (músculo frontal medial e lateral);
     - `AU04`: Franzimento da glabela / aproximação superciliar (músculo corrugador);
     - `AU06`: Elevação de bochechas (músculo orbicular ocular);
     - `AU12`: Tracionamento do canto dos lábios em direção às orelhas (músculo zigomático maior);
     - `AU15`: Depressão dos cantos bucais (tristeza);
  2. Vídeo de demonstração solo e **vídeo comparativo split-screen lado a lado 2048x1024** (*VASA-1 neutro vs AUHead expressivo*).
- **Resultados:**
  - Vídeo solo: [`video_auhead.mp4`](Implementacoes/03_auhead_facs_control/video_auhead.mp4) (14.60 segundos, 365 frames);
  - Vídeo comparativo: [`video_comparativo_vasa_vs_auhead.mp4`](Implementacoes/03_auhead_facs_control/video_comparativo_vasa_vs_auhead.mp4) (7.64 segundos, 191 frames, 2048x1024 com overlay de telemetria em tempo real);
  - Modulação anatômica precisa: injeção de raiva com AU04 ($\Delta y = -0.008$ nos keypoints 1 e 2) e alegria com AU12 ($\Delta x = +0.035$ nos keypoints 3 e 7), com dentes e língua respeitando a geometria física.

---

### Módulo 04: InstructAvatar (AAAI 2025) — Direção Cênica via Linguagem Natural
- **Localização:** [`Implementacoes/04_instruct_avatar_nlp/`](Implementacoes/04_instruct_avatar_nlp/)
- **Scripts:** [`instruct_avatar_parser.py`](Implementacoes/04_instruct_avatar_nlp/instruct_avatar_parser.py), [`renderizar_video_instruct.py`](Implementacoes/04_instruct_avatar_nlp/renderizar_video_instruct.py)
- **O que foi testado:**
  1. Parser textual em linguagem natural livre para interpretação de comandos cênicos (ex: *"fale com altivez, olhar frontal compenetrado e sorriso sutil"*);
  2. Mapeamento de texto para atitude rígida de cabeça e intensidade contínua de AUs;
  3. **Correção do "efeito boca travada / dentes expostos":** implementação de envelope de fala ativa, atenuando temporariamente AUs expressivas nos picos fonéticos para viabilizar fechamento bilabial perfeito em fonemas consonantais (/p/, /b/, /m/).
- **Resultados:**
  - Vídeo sintetizado: [`video_instruct.mp4`](Implementacoes/04_instruct_avatar_nlp/video_instruct.mp4) (10.80 segundos, 270 frames, 1024x1024);
  - Atitude postural reproduzida com fidelidade: $\text{Pitch} = -2.5^\circ$ (queixo elevado e confiante), $\text{Yaw} = 0.0^\circ$ (olhar frontal cravado no público), $\text{AU12} = 0.28$ e $\text{AU06} = 0.20$ integrados sem travar a mandíbula.

---

### Módulo 05: Audio2Photoreal (Meta Reality Labs, CVPR 2024) — Diálogo Diádico
- **Localização:** [`Implementacoes/05_audio2photoreal_dialogue/`](Implementacoes/05_audio2photoreal_dialogue/)
- **Scripts:** [`audio2photoreal_diadico.py`](Implementacoes/05_audio2photoreal_dialogue/audio2photoreal_diadico.py), [`renderizar_video_diadico.py`](Implementacoes/05_audio2photoreal_dialogue/renderizar_video_diadico.py)
- **O que foi testado:**
  1. Alternância dinâmica de papéis em conversa diádica de 2 interlocutores: **Turno de Fala Ativa** vs **Turno de Escuta Ativa** (*Backchanneling*);
  2. Voice Activity Detection (VAD) acústico monitorando energia de fala em janelas móveis;
  3. Durante a escuta: supressão total de atividade labial (`vad_alpha = 0.0`, mantendo os lábios 100% selados em repouso) e injeção de acenos afirmativos de cabeça (*nodding*) senoidais amortecidos a $2.2\text{ Hz}$.
- **Resultados:**
  - Vídeo sintetizado: [`video_diadico.mp4`](Implementacoes/05_audio2photoreal_dialogue/video_diadico.mp4) (14.68 segundos, 367 frames, 1024x1024);
  - Três estados conversacionais perfeitos com HUD:
    - `0.0s a 4.8s`: Avatar fala ativamente com articulação fonética completa;
    - `4.8s a 9.6s`: Interlocutor fala; avatar escuta em silêncio absoluto com boca fechada e executa 2 acenos suaves de concordância ($\Delta \text{Pitch} \in [-1.8^\circ, +2.5^\circ]$);
    - `9.6s a 14.68s`: Avatar reassume a palavra com transição suave de pose.

---

### Módulo 06: OmniHuman-1.5 (ByteDance, 2025) — Arquitetura Cognitiva Dual
- **Localização:** [`Implementacoes/06_omnihuman_dual_system/`](Implementacoes/06_omnihuman_dual_system/)
- **Scripts:** [`omnihuman_sistema_dual.py`](Implementacoes/06_omnihuman_dual_system/omnihuman_sistema_dual.py), [`renderizar_video_omnihuman.py`](Implementacoes/06_omnihuman_dual_system/renderizar_video_omnihuman.py)
- **O que foi testado:**
  1. A divisão cognitiva de Daniel Kahneman aplicada a avatares autônomos:
     - **Sistema 1 (Reativo / Fonação Reflexa):** Motor acústico HuBERT que converte som em geometria labial e micro-movimentos imediatos;
     - **Sistema 2 (Deliberativo / Mente Ativa / MLLM):** Planejador semântico de alto nível que projeta arcos dramáticos cênicos ao longo do discurso;
  2. Implementação dos 3 Arcos Cognitivos do OmniHuman-1.5:
     - *Arco 1 (Pensamento Analítico):* Queixo contido ($\text{Pitch} = +1.5^\circ$) e postura compenetrada;
     - *Arco 2 (Desvio Cognitivo do Olhar / Gaze Aversion):* Durante pausas reflexivas, o ser humano desvia o olhar e inclina a cabeça para acessar a memória interna de trabalho;
     - *Arco 3 (Iluminação e Convicção Assertiva):* Queixo elevado ($\text{Pitch} = -3.2^\circ$), olhar fixado no público e ênfases motoras nas palavras-chave do clímax.
- **Resultados:**
  - Vídeo sintetizado: [`video_omnihuman.mp4`](Implementacoes/06_omnihuman_dual_system/video_omnihuman.mp4) (10.76 segundos, 269 frames, 1024x1024);
  - Validação das métricas:
    - Desvio de Olhar (Arco 2 - Gaze Aversion): $\Delta \text{Yaw} = -3.80^\circ$ e $\Delta \text{Pitch} = -1.80^\circ$;
    - Elevação Assertiva de Queixo (Arco 3): $\Delta \text{Pitch} = -3.20^\circ$.

---

### Módulo 07: Motion Diffusion Model (MDM / DDPM) — Difusão Cinemática Estocástica
- **Localização:** [`Implementacoes/07_motion_diffusion_mdm/`](Implementacoes/07_motion_diffusion_mdm/)
- **Scripts:** [`mdm_difusao_cinematica.py`](Implementacoes/07_motion_diffusion_mdm/mdm_difusao_cinematica.py), [`renderizar_video_mdm.py`](Implementacoes/07_motion_diffusion_mdm/renderizar_video_mdm.py)
- **O que foi testado:**
  1. **Resolução do Colapso da Regressão (*Regression to the Mean*):** Redes puramente determinísticas com perda MSE $L_2$ produzem a média estatística $\mathbb{E}[x \mid c]$, congelando a cabeça do avatar. O MDM modela a distribuição completa $p(x_0 \mid c)$ via difusão reversa;
  2. **Predição Direta do Sinal Limpo ($\hat{x}_0$-prediction):** Em vez de estimar ruído $\epsilon_t$, a rede estima diretamente $\hat{x}_0 = \mathcal{G}_\theta(x_t, t, c)$, viabilizando perdas geométricas cinemáticas a cada passo:
     $$\mathcal{L} = \mathcal{L}_{simple} + \lambda_{vel} \mathcal{L}_{vel}, \quad \text{onde } \mathcal{L}_{vel} = \frac{1}{N-1} \sum_{i=1}^{N-1} \big\|(x_0^{i+1} - x_0^i) - (\hat{x}_0^{i+1} - \hat{x}_0^i)\big\|^2$$
  3. Scheduler de variância DDPM/DDIM ($\beta_t \in [10^{-4}, 0.02]$, $T=50$ passos);
  4. Transformer Encoder temporal com Rotary / Sinusoidal Timestep Embeddings;
  5. Amostragem estocástica multi-seed (Semente 42 vs Semente 101) para o mesmo áudio.
- **Resultados e Métricas:**
  - Vídeo sintetizado: [`video_mdm.mp4`](Implementacoes/07_motion_diffusion_mdm/video_mdm.mp4) (12.48 segundos, 312 frames, 1024x1024);
  - **Diversidade Angular de Cabeça entre Sementes (Diversity Metric):** $3.720^\circ$ (diferentes ruídos exploram modos cinemáticos distintos e vivos para a mesma fala, eliminando a cabeça congelada);
  - **Consistência Labial Fonética (Lip-sync fidelity):** $0.0045$ (a boca articula os mesmos fonemas com precisão estrita em ambas as sementes);
  - **Suavidade Cinemática Temporal (Aceleração Média):** $0.0537^\circ/\text{frame}^2$ (fluidez física livre de tremores).

---

## Estrutura de Arquivos do Repositório

```text
Experimentos-Avatar-01-Humans/
├── Artigos/                                # Literatura científica completa em PDF
│   ├── AUHead.pdf                          # ICLR 2026 (FACS Action Units)
│   ├── Audio2Photoreal.pdf                 # Meta Reality Labs, CVPR 2024 (Conversação Diádica)
│   ├── DDPM.pdf                            # Ho et al., NeurIPS 2020 (Denoising Diffusion)
│   ├── InstructAvatar.pdf                  # AAAI 2025 (Direção via Linguagem Natural)
│   ├── LivePortrait.pdf                    # Guo et al., 2024 (21 Keypoints 3D)
│   ├── MDM_Motion_Diffusion.pdf            # Tevet et al., ICLR 2023 (Human Motion Diffusion)
│   ├── OmniHuman-1.5.pdf                   # ByteDance, 2025 (Arquitetura Cognitiva Dual)
│   └── VASA-1.pdf                          # Microsoft Research, 2024 (Dinâmica Holística)
│
├── data/                                   # Arquivos de dados de entrada
│   ├── vasa_portrait.jpg                   # Retrato neutro canônico de referência
│   ├── vasa_speech.wav                     # Fala de demonstração do VASA-1
│   ├── speech_diadico.wav                  # Áudio conversacional de teste diádico
│   ├── omnihuman_speech.wav                # Áudio de discurso reflexivo (OmniHuman)
│   └── mdm_speech.wav                      # Áudio explicativo de difusão cinemática
│
├── Implementacoes/                         # Código fonte dos 7 módulos
│   ├── 01_ditto_core/
│   │   └── 01_espaco_latente.py            # Validação algébrica de SO(3) e keypoints
│   ├── 02_vasa1_audio_motion/
│   │   ├── vasa1_gerador_dinamica.py       # Extração de dinâmica holística
│   │   ├── renderizar_video_vasa1.py       # Renderizador neural do VASA-1
│   │   ├── trajetoria_vasa1.npz            # Trajetória latente salva (246 frames)
│   │   └── video_vasa1.mp4                 # Vídeo final (9.84s, 1024x1024)
│   ├── 03_auhead_facs_control/
│   │   ├── auhead_facs_mapeador.py         # Mapeamento biomecânico de Action Units
│   │   ├── renderizar_video_auhead.py      # Renderizador do AUHead solo
│   │   ├── comparativo_vasa_vs_auhead.py   # Gerador do vídeo split-screen
│   │   ├── video_auhead.mp4                # Vídeo final AUHead solo (14.60s)
│   │   └── video_comparativo_vasa_vs_auhead.mp4 # Vídeo split-screen (2048x1024)
│   ├── 04_instruct_avatar_nlp/
│   │   ├── instruct_avatar_parser.py       # Parser semântico e envelope de fala ativa
│   │   ├── renderizar_video_instruct.py    # Renderizador do InstructAvatar
│   │   ├── trajetoria_instruct.npz         # Trajetória salva (270 frames)
│   │   └── video_instruct.mp4              # Vídeo final (10.80s, 1024x1024)
│   ├── 05_audio2photoreal_dialogue/
│   │   ├── audio2photoreal_diadico.py      # Motor de escuta ativa e VAD
│   │   ├── renderizar_video_diadico.py     # Renderizador com alternância de estados
│   │   ├── trajetoria_diadica.npz          # Trajetória salva (367 frames)
│   │   └── video_diadico.mp4               # Vídeo final diádico (14.68s, 1024x1024)
│   ├── 06_omnihuman_dual_system/
│   │   ├── omnihuman_sistema_dual.py       # Simulador dos Sistemas 1 e 2
│   │   ├── renderizar_video_omnihuman.py   # Renderizador com telemetria dos arcos
│   │   ├── trajetoria_omnihuman.npz        # Trajetória salva (269 frames)
│   │   └── video_omnihuman.mp4             # Vídeo final OmniHuman (10.76s, 1024x1024)
│   └── 07_motion_diffusion_mdm/
│       ├── mdm_difusao_cinematica.py       # Scheduler DDPM, Transformer e teste multi-seed
│       ├── renderizar_video_mdm.py         # Renderizador neural com telemetria MDM
│       ├── trajetoria_mdm.npz              # Trajetória salva (312 frames)
│       └── video_mdm.mp4                   # Vídeo final MDM (12.48s, 1024x1024)
│
├── referencia/                             # Motores de inferência e suporte
│   ├── ditto_lab.py                        # Classe de interface desacoplada (Lab & Renderer)
│   └── checkpoints/                        # Modelos e configurações pré-treinadas
└── README.md
```

---

## Como Executar e Reproduzir os Experimentos

### 1. Pré-requisitos do Ambiente
- macOS com Apple Silicon (M1/M2/M3/M4) ou Linux com GPU CUDA;
- Python 3.10;
- FFmpeg instalado no sistema (`brew install ffmpeg`).

```bash
# Ativar o ambiente virtual com PyTorch e aceleração MPS
conda activate safeai  # ou seu ambiente Python 3.10 com torch 2.x
```

### 2. Executando os Scripts de Trajetória e Renderização

Para reproduzir qualquer um dos módulos, execute os respectivos comandos na raiz do repositório:

```bash
# --- Módulo 01: Ditto Core & Espaço Latente ---
python Implementacoes/01_ditto_core/01_espaco_latente.py

# --- Módulo 02: VASA-1 Audio Motion ---
python Implementacoes/02_vasa1_audio_motion/vasa1_gerador_dinamica.py
python Implementacoes/02_vasa1_audio_motion/renderizar_video_vasa1.py

# --- Módulo 03: AUHead FACS & Comparativo Split-Screen ---
python Implementacoes/03_auhead_facs_control/auhead_facs_mapeador.py
python Implementacoes/03_auhead_facs_control/comparativo_vasa_vs_auhead.py

# --- Módulo 04: InstructAvatar NLP ---
python Implementacoes/04_instruct_avatar_nlp/instruct_avatar_parser.py
python Implementacoes/04_instruct_avatar_nlp/renderizar_video_instruct.py

# --- Módulo 05: Audio2Photoreal Diádico ---
python Implementacoes/05_audio2photoreal_dialogue/audio2photoreal_diadico.py
python Implementacoes/05_audio2photoreal_dialogue/renderizar_video_diadico.py

# --- Módulo 06: OmniHuman-1.5 Arquitetura Dual ---
python Implementacoes/06_omnihuman_dual_system/omnihuman_sistema_dual.py
python Implementacoes/06_omnihuman_dual_system/renderizar_video_omnihuman.py

# --- Módulo 07: Motion Diffusion Model (MDM / DDPM) ---
python Implementacoes/07_motion_diffusion_mdm/mdm_difusao_cinematica.py
python Implementacoes/07_motion_diffusion_mdm/renderizar_video_mdm.py
```

---

## Diretrizes de Engenharia e Eficiência
1. **Aceleração por Hardware Apple Silicon (MPS):** Todo o pipeline de decodificação neural $WarpF3D \to SPADE$ utiliza a GPU Apple Silicon com tensores em ponto flutuante `bfloat16`, atingindo taxas de renderização de ~4 a 6 frames por segundo em resolução nativa 1024x1024;
2. **Prevenção de Incompatibilidade de Dtype:** Todas as manipulações de matrizes de rotação e offsets de Action Units utilizam cast explícito `np.float32`, evitando a promoção indesejada para `float64` que causaria falhas no MLP de stitching do PyTorch;
3. **Limpeza Inteligente de Armazenamento:** Os scripts removem automaticamente os milhares de frames `.jpg` intermediários após a compressão final em `.mp4` via FFmpeg, preservando o disco e o repositório Git leves.
