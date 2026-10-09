# 🛠️ Implementações Manuais — Passo a Passo

Esta pasta é dedicada à implementação manual de cada modelo e componente de controle de avatar, construindo o entendimento aprofundado de cada arquitetura do zero.

---

## 🗺️ Roteiro de Implementação

| Módulo | Modelo / Conceito | Objetivo de Aprendizado | Arquivos Chave |
| :--- | :--- | :--- | :--- |
| **01_ditto_core** | LivePortrait + Ditto | Espaço de movimento em 21 keypoints 3D implícitos, tensores `x_s` e `x_d`, rotação 66-bins, distorção de volume `WarpF3D` e decodificador neural SPADE. Separação entre gerador de movimento (`.npz`) e renderização de pixels. | `core.py`, `renderer.py` |
| **02_vasa1_audio_motion** | VASA-1 (Microsoft) | Desacoplamento de identidade, pose rígida e dinâmica não-rígida a partir de áudio de fala (HuBERT) sem controles manuais. | `vasa_dynamics.py` |
| **03_auhead_facs_control** | AUHead (ICLR 2026) | Controle anatômico via Action Units do FACS (Paul Ekman). Mapeamento de ativação muscular (zigomático, corrugador, masseter) para deslocamentos dos keypoints 3D (`delta_exp`). | `facs_mapping.py` |
| **04_instruct_avatar_nlp** | InstructAvatar (AAAI 2025) | Controle dramático por linguagem natural. Parser textual interpretando intenção emocional e atitude de cabeça para modular intensidade de AUs e pose. | `instruct_controller.py` |
| **05_audio2photoreal_dialogue** | Audio2Photoreal (Meta CVPR) | Dinâmica de conversação e escuta ativa (*backchannel*). Detecção de picos de energia na fala do interlocutor e geração de acenos de concordância em tempo hábil. | `conversational_agent.py` |
| **06_omnihuman_dual_system** | OmniHuman-1.5 (ByteDance) | Arquitetura de dois sistemas: Sistema 1 reativo (prosódia da fala) + Sistema 2 deliberativo (plano semântico de intenções derivado via LLM). | `dual_system.py` |
| **07_motion_diffusion_mdm** | Motion Diffusion Models | Paradigma estocástico contra o colapso para a média (problema 1-para-Muitos). Amostragem DDIM com sementes diversas para uma mesma fala. | `diffusion_sampler.py` |
