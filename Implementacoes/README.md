# Implementações Manuais — Catálogo de Módulos e Resultados

Esta pasta reúne a implementação manual dos módulos investigados no projeto, desde os fundamentos geométricos e anatômicos até difusão de movimento, simulação cognitiva dual e o comparativo mestre SOTA.

---

## Mapa de Módulos Implementados

| Módulo | Paradigma / Modelo | Script de Movimento | Script de Renderização | Trajetória (`.npz`) | Vídeo Demonstrativo (`.mp4`) | Destaque Técnico |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **01_ditto_core** | LivePortrait / Ditto | [`01_espaco_latente.py`](01_ditto_core/01_espaco_latente.py) | — | — | — | Formulação algébrica de SO(3), 66 bins e 21 keypoints 3D canônicos. |
| **02_vasa1_audio_motion** | VASA-1 (Microsoft) | [`vasa1_gerador_dinamica.py`](02_vasa1_audio_motion/vasa1_gerador_dinamica.py) | [`renderizar_video_vasa1.py`](02_vasa1_audio_motion/renderizar_video_vasa1.py) | `trajetoria_vasa1.npz` | [`video_vasa1.mp4`](02_vasa1_audio_motion/video_vasa1.mp4)<br>*(9.84s \| 246 frames)* | Síntese holística não-rígida a partir de fala natural (HuBERT). |
| **03_auhead_facs_control** | AUHead (ICLR 2026) | [`auhead_facs_mapeador.py`](03_auhead_facs_control/auhead_facs_mapeador.py) | [`renderizar_video_auhead.py`](03_auhead_facs_control/renderizar_video_auhead.py)<br>[`comparativo_vasa_vs_auhead.py`](03_auhead_facs_control/comparativo_vasa_vs_auhead.py) | `trajetoria_auhead.npz` | [`video_auhead.mp4`](03_auhead_facs_control/video_auhead.mp4)<br>[`video_comparativo...`](03_auhead_facs_control/video_comparativo_vasa_vs_auhead.mp4)<br>*(2048x1024 split-screen)* | Controle muscular preciso via Action Units (AU01, AU04, AU12, AU15). |
| **04_instruct_avatar_nlp** | InstructAvatar (AAAI 2025) | [`instruct_avatar_parser.py`](04_instruct_avatar_nlp/instruct_avatar_parser.py) | [`renderizar_video_instruct.py`](04_instruct_avatar_nlp/renderizar_video_instruct.py) | `trajetoria_instruct.npz` | [`video_instruct.mp4`](04_instruct_avatar_nlp/video_instruct.mp4)<br>*(10.80s \| 270 frames)* | Direção cênica em linguagem natural com modulação labial dinâmica. |
| **05_audio2photoreal_dialogue** | Audio2Photoreal (Meta) | [`audio2photoreal_diadico.py`](05_audio2photoreal_dialogue/audio2photoreal_diadico.py) | [`renderizar_video_diadico.py`](05_audio2photoreal_dialogue/renderizar_video_diadico.py) | `trajetoria_diadica.npz` | [`video_diadico.mp4`](05_audio2photoreal_dialogue/video_diadico.mp4)<br>*(14.68s \| 367 frames)* | Escuta ativa (*backchannel*), VAD acústico e acenos de cabeça com boca selada. |
| **06_omnihuman_dual_system** | OmniHuman-1.5 (ByteDance) | [`omnihuman_sistema_dual.py`](06_omnihuman_dual_system/omnihuman_sistema_dual.py) | [`renderizar_video_omnihuman.py`](06_omnihuman_dual_system/renderizar_video_omnihuman.py) | `trajetoria_omnihuman.npz` | [`video_omnihuman.mp4`](06_omnihuman_dual_system/video_omnihuman.mp4)<br>*(10.76s \| 269 frames)* | Sistema 1 (fonação HuBERT) + Sistema 2 (arcos de intenção cênica e *gaze aversion*). |
| **07_motion_diffusion_mdm** | MDM (ICLR 2023) & DDPM | [`mdm_difusao_cinematica.py`](07_motion_diffusion_mdm/mdm_difusao_cinematica.py) | [`renderizar_video_mdm.py`](07_motion_diffusion_mdm/renderizar_video_mdm.py) | `trajetoria_mdm.npz` | [`video_mdm.mp4`](07_motion_diffusion_mdm/video_mdm.mp4)<br>*(12.48s \| 312 frames)* | Difusão estocástica reversa, predição direta x_0 e quebra da regressão à média. |
| **08_comparativo_mestre_sota** | Comparativo Mestre SOTA | [`gerar_trajetorias_comparativo.py`](08_comparativo_mestre_sota/gerar_trajetorias_comparativo.py) | [`renderizar_grade_comparativa.py`](08_comparativo_mestre_sota/renderizar_grade_comparativa.py) | 6 arquivos `.npz` calibrados | [`video_comparativo_mestre.mp4`](08_comparativo_mestre_sota/video_comparativo_mestre.mp4)<br>*(9.69s \| 1920x1370)* | Grade 2x3 com inferência simultânea de todos os 6 modelos SOTA na Prova de Fogo. |

---

## Síntese dos Experimentos Executados

### Módulo 01 — Ditto Core & Espaço Latente
- **Foco:** Fundamentos de cinemática e geometria projetiva.
- **Resultados:** Validação formal da ortogonalidade da matriz de rotação R em SO(3) (R^T R = I, det(R) = 1.0), verificação do mapeamento biunívoco dos 66 bins em [-90°, +90°], e isolamento da deformação de 21 keypoints na equação x = R x_c + t + delta_exp.

### Módulo 02 — VASA-1 (Microsoft Research)
- **Foco:** Síntese holística sem intervenção manual de controladores.
- **Resultados:** Trajetória fluida de 246 frames (9.84s) gerada na GPU MPS. A atitude da cabeça variou naturalmente (Pitch: [-2.1°, +3.4°], Yaw: [-4.2°, +3.8°]), reproduzindo a prosódia do áudio em tempo real com micro-expressões reflexas.

### Módulo 03 — AUHead (ICLR 2026) & Split-Screen Comparativo
- **Foco:** Controle biomecânico por Action Units do sistema FACS (Paul Ekman).
- **Resultados:**
  - Demonstração solo: 365 frames (14.60s) modulando sobrancelhas, cantos dos lábios e glabela;
  - Comparativo split-screen: vídeo lado a lado em 2048x1024 demonstrando a diferença entre VASA-1 neutro e AUHead com injeção de raiva (AU04) e felicidade (AU12).

### Módulo 04 — InstructAvatar (AAAI 2025)
- **Foco:** Direção cênica através de prompts em linguagem natural livre.
- **Resultados:** Parser semântico convertendo instruções como *"postura altiva, olhar focado e sorriso comedido"* em vetores contínuos de pose e AUs. Implementação de atenuação adaptativa em fala ativa, eliminando o problema dos dentes expostos/boca travada.

### Módulo 05 — Audio2Photoreal (Meta Reality Labs, CVPR 2024)
- **Foco:** Dinâmica conversacional diádica e escuta ativa (*backchanneling*).
- **Resultados:** Transição entre fala ativa (0s-4.8s), escuta atenta do interlocutor com 2 acenos harmônicos de cabeça e boca 100% selada em repouso (4.8s-9.6s), e retorno da palavra pelo avatar (9.6s-14.68s).

### Módulo 06 — OmniHuman-1.5 (ByteDance, 2025)
- **Foco:** Arquitetura cognitiva dual (Sistema 1 Reativo + Sistema 2 Deliberativo).
- **Resultados:** Segmentação em 3 arcos cognitivos:
  - Arco 1 (Pensamento Analítico): queixo recolhido (Pitch = +1.5°);
  - Arco 2 (Desvio Cognitivo do Olhar / *Gaze Aversion*): inclinação lateral durante pausa reflexiva (Delta Yaw = -3.80°);
  - Arco 3 (Iluminação e Convicção Assertiva): queixo elevado (Delta Pitch = -3.20°) e olhar direto.

### Módulo 07 — Motion Diffusion Model (MDM / DDPM)
- **Foco:** Superação da regressão à média (*Regression-to-the-Mean*) em mapeamento 1-para-Muitos.
- **Resultados:** Amostragem estocástica multi-seed (Semente 42 vs 101) para o mesmo áudio condicional:
  - Diversidade Angular de Cabeça (Diversity): 3.720° (poses vivas e variadas para a mesma frase);
  - Consistência Labial Fonética: 0.0045 (fidelidade estrita da articulação de boca);
  - Suavidade Cinemática: 0.0537°/frame^2 (movimento contínuo e sem tremores).

### Módulo 08 — Comparativo Mestre SOTA (A Prova de Fogo)
- **Foco:** Inferência simultânea dos 6 modelos em grade 2x3 (1920x1370) submetidos ao mesmo prompt de 3 fases (foco, silêncio de 2.2s e clímax).
- **Resultados:** Evidência visual direta da superioridade de cada técnica: VASA-1 como baseline acústico, AUHead controlando músculos específicos, InstructAvatar eliminando dentes expostos, Audio2Photoreal acenando com boca selada na escuta, OmniHuman desviando o olhar para pensar (*gaze aversion*), e MDM garantindo movimento estocástico vivo sem colapsar para a média estática.
