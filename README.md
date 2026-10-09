# Experimentos Avatar 01 — Humans

Repositório de pesquisa científica e implementações práticas para **síntese, animação neural foto-realista e controle comportamental de avatares humanos** a partir de áudio de fala e linguagem natural.

O projeto investiga os princípios de modelos do estado da arte (SOTA): desde a cinemática de deformação canônica em espaços latentes 3D até a modelagem generativa por difusão estocástica e arquiteturas cognitivas duais.

---

## Modulos e Demonstracoes em Video

Cada modulo possui um documento dedicado com fundamentacao matematica aprofundada dentro de sua respectiva pasta em `Implementacoes/`.

---

### Modulo 01: Ditto Core e Espaco Latente (LivePortrait)
- **Paper:** [LivePortrait.pdf](Artigos/LivePortrait.pdf) *(Guo et al., 2024)*
- **Documentacao Completa:** [Implementacoes/01_ditto_core/README.md](Implementacoes/01_ditto_core/README.md)
- **Resumo:** Decomposição do rosto em 21 keypoints 3D implícitos ($\mathbf{x}_c \in \mathbb{R}^{21 \times 3}$) e matriz de rotação $\mathbf{R} \in \mathrm{SO}(3)$ via 66 bins. Desacoplamento estrito entre o volume de identidade neutra ($\mathbf{x}_s$) e a deformação motora ($\mathbf{x}_d$).
- **Validacao Algebrica:** $\mathbf{R}^T \mathbf{R} = \mathbf{I}$, $\det(\mathbf{R}) = 1.000000$.

---

### Modulo 02: VASA-1 (Microsoft Research) — Dinamica Holistica via Audio
- **Paper:** [VASA-1.pdf](Artigos/VASA-1.pdf) *(Microsoft Research, 2024)*
- **Documentacao Completa:** [Implementacoes/02_vasa1_audio_motion/README.md](Implementacoes/02_vasa1_audio_motion/README.md)
- **Resumo:** Síntese autônoma de dinâmica facial e atitude da cabeça em espaço 3D a partir de representações acústicas HuBERT, sem intervenção de controladores manuais.

<video src="Implementacoes/02_vasa1_audio_motion/video_vasa1.mp4" controls width="100%"></video>

- **Metricas:** 9.84s (246 frames @ 25 FPS). Pitch $[-2.1^\circ, +3.4^\circ]$, Yaw $[-4.2^\circ, +3.8^\circ]$. Sincronia fonética estrita com micro-movimentos reflexos.

---

### Modulo 03: AUHead (ICLR 2026) — Controle Anatomico via FACS e Comparativo
- **Paper:** [AUHead.pdf](Artigos/AUHead.pdf) *(ICLR 2026)*
- **Documentacao Completa:** [Implementacoes/03_auhead_facs_control/README.md](Implementacoes/03_auhead_facs_control/README.md)
- **Resumo:** Mapeamento de Action Units do sistema FACS de Paul Ekman para translações vetoriais dos 21 keypoints anatômicos (AU01, AU04, AU06, AU12, AU15, AU26, AU43).

#### Comparativo Split-Screen: VASA-1 Neutro vs AUHead Expressivo (2048x1024)
<video src="Implementacoes/03_auhead_facs_control/video_comparativo_vasa_vs_auhead.mp4" controls width="100%"></video>

#### Demonstracao Solo AUHead (1024x1024)
<video src="Implementacoes/03_auhead_facs_control/video_auhead.mp4" controls width="100%"></video>

- **Metricas:** AU04 gera compressão glabelar de $-0.008$ nos keypoints 1 e 2 (raiva); AU12 gera expansão zigomática de $+0.035$ nos keypoints 3 e 7 (sorriso), respeitando a anatomia dentária.

---

### Modulo 04: InstructAvatar (AAAI 2025) — Direcao Cenica via Linguagem Natural
- **Paper:** [InstructAvatar.pdf](Artigos/InstructAvatar.pdf) *(AAAI 2025)*
- **Documentacao Completa:** [Implementacoes/04_instruct_avatar_nlp/README.md](Implementacoes/04_instruct_avatar_nlp/README.md)
- **Resumo:** Parser semântico que traduz instruções cênicas de texto livre em pose e intensidade de AUs. Introdução de atenuação adaptativa durante a fala ativa para garantir oclusão bilabial nos fonemas /p/, /b/, /m/, eliminando o problema de dentes expostos.

<video src="Implementacoes/04_instruct_avatar_nlp/video_instruct.mp4" controls width="100%"></video>

- **Metricas:** 10.80s (270 frames). Atitude com $\text{Pitch} = -2.5^\circ$ (altivez) e olhar frontal compenetrado com $\text{AU12} = 0.28$ e $\text{AU06} = 0.20$.

---

### Modulo 05: Audio2Photoreal (Meta Reality Labs, CVPR 2024) — Dialogo Diadico
- **Paper:** [Audio2Photoreal.pdf](Artigos/Audio2Photoreal.pdf) *(Meta Reality Labs, CVPR 2024)*
- **Documentacao Completa:** [Implementacoes/05_audio2photoreal_dialogue/README.md](Implementacoes/05_audio2photoreal_dialogue/README.md)
- **Resumo:** Alternância de papéis em conversa diádica: fala ativa vs escuta ativa (*backchanneling*). Durante a fala do interlocutor, o avatar mantém a boca 100% selada em repouso e realiza acenos harmônicos de cabeça amortecidos a $2.2\text{ Hz}$.

<video src="Implementacoes/05_audio2photoreal_dialogue/video_diadico.mp4" controls width="100%"></video>

- **Metricas:** 14.68s (367 frames). 0s-4.8s (fala ativa), 4.8s-9.6s (escuta atenta com 2 acenos $\Delta \text{Pitch} \in [-1.8^\circ, +2.5^\circ]$ e boca imóvel), 9.6s-14.68s (retomada da palavra).

---

### Modulo 06: OmniHuman-1.5 (ByteDance, 2025) — Arquitetura Cognitiva Dual
- **Paper:** [OmniHuman-1.5.pdf](Artigos/OmniHuman-1.5.pdf) *(ByteDance, 2025)*
- **Documentacao Completa:** [Implementacoes/06_omnihuman_dual_system/README.md](Implementacoes/06_omnihuman_dual_system/README.md)
- **Resumo:** Divisão cognitiva inspirada em Daniel Kahneman: Sistema 1 reativo (fonação HuBERT) acoplado ao Sistema 2 deliberativo (planejador de intenções em 3 arcos: introspecção analítica, desvio cognitivo de olhar / *gaze aversion* e convicção assertiva com queixo elevado).

<video src="Implementacoes/06_omnihuman_dual_system/video_omnihuman.mp4" controls width="100%"></video>

- **Metricas:** 10.76s (269 frames). Desvio lateral de olhar (Arco 2): $\Delta \text{Yaw} = -3.80^\circ$; Elevação de queixo na convicção (Arco 3): $\Delta \text{Pitch} = -3.20^\circ$.

---

### Modulo 07: Motion Diffusion Model (MDM / DDPM) — Difusao Cinematica Estocastica
- **Papers:** [MDM_Motion_Diffusion.pdf](Artigos/MDM_Motion_Diffusion.pdf) *(Tevet et al., ICLR 2023)* & [DDPM.pdf](Artigos/DDPM.pdf) *(NeurIPS 2020)*
- **Documentacao Completa:** [Implementacoes/07_motion_diffusion_mdm/README.md](Implementacoes/07_motion_diffusion_mdm/README.md)
- **Resumo:** Superação do colapso da regressão à média (problema 1-para-Muitos) via difusão reversa. Predição direta do sinal limpo $\hat{x}_0 = \mathcal{G}_\theta(x_t, t, c)$ com perdas geométricas de velocidade articular $\mathcal{L}_{vel} = \|\Delta x_0 - \Delta \hat{x}_0\|^2$. Amostragem estocástica multi-seed para a mesma fala.

<video src="Implementacoes/07_motion_diffusion_mdm/video_mdm.mp4" controls width="100%"></video>

- **Metricas:** 12.48s (312 frames). Diversidade angular da cabeça entre sementes: $3.720^\circ$; Fidelidade e consistência labial fonética: $0.0045$; Suavidade temporal: $0.0537^\circ/\text{frame}^2$.

---

## Tabela Sintetica de Resultados

| Modulo | Modelo | Duracao | Frames | Resolucao | Metrica Chave |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **01** | LivePortrait Core | — | — | — | $\mathbf{R}^T\mathbf{R} = \mathbf{I}$, $\det(\mathbf{R}) = 1.000$ |
| **02** | VASA-1 (Microsoft) | 9.84s | 246 | 1024x1024 | Pitch $[-2.1^\circ, +3.4^\circ]$, Yaw $[-4.2^\circ, +3.8^\circ]$ |
| **03** | AUHead FACS Solo | 14.60s | 365 | 1024x1024 | AU04: $-0.008$, AU12: $+0.035$ |
| **03** | Comparativo Split-Screen | 7.64s | 191 | 2048x1024 | Comparativo lado a lado VASA-1 vs AUHead |
| **04** | InstructAvatar NLP | 10.80s | 270 | 1024x1024 | Pitch: $-2.5^\circ$, contato labial preservado |
| **05** | Audio2Photoreal Diadico | 14.68s | 367 | 1024x1024 | 2 acenos ($2.2\text{ Hz}$), boca selada em repouso |
| **06** | OmniHuman-1.5 Dual | 10.76s | 269 | 1024x1024 | Desvio de olhar: $-3.8^\circ$, queixo: $-3.2^\circ$ |
| **07** | Motion Diffusion MDM | 12.48s | 312 | 1024x1024 | Diversidade: $3.720^\circ$, fidelidade labial: $0.0045$ |

---

## Como Executar

```bash
# 1. Ativar o ambiente com PyTorch e aceleracao MPS
conda activate safeai

# 2. Executar qualquer modulo (exemplo Modulo 07)
python Implementacoes/07_motion_diffusion_mdm/mdm_difusao_cinematica.py
python Implementacoes/07_motion_diffusion_mdm/renderizar_video_mdm.py
```

Consulte o README interno de cada modulo para instrucoes detalhadas e referencias de codigo.
