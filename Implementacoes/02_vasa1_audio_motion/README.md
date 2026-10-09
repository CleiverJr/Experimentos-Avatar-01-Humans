# Modulo 02: VASA-1 (Microsoft Research) — Dinamica Holistica via Audio

Este modulo implementa a sintese holistica de movimento facial e atitude espontanea da cabeca a partir de fala desanotada, reproduzindo os principios fundamentais do paper **VASA-1: Lifelike Audio-Driven Talking Faces with Realistic Head and Facial Dynamics** (Microsoft Research, 2024).

---

## 1. Video Demonstrativo Gerado

![VASA-1 Dinamica Holistica](demo_vasa1.gif)

- **Video com Audio HD:** [video_vasa1.mp4](video_vasa1.mp4)

- **Arquivo:** `video_vasa1.mp4`
- **Duracao:** 9.84 segundos (246 frames)
- **Resolucao:** 1024x1024 @ 25 FPS
- **Aceleracao:** Apple Silicon GPU (MPS) em precisao BF16

---

## 2. A Tese do VASA-1

Modelos convencionais de talking head sofrem com dois gargalos criticos:
1. Limitacao estrita a sincronizacao labial, mantendo a cabeca rigida ou artificialmente recortada;
2. Dependencia de trajetorias de pose capturadas de terceiros (driving videos), o que elimina a autonomia do avatar.

O VASA-1 formula a sintese como a predicao conjunta e holistica de toda a dinamica motora superior a partir unicamente do fluxo de audio acústico:
- Extracao de representacoes contextualizadas densas via **HuBERT** (taxa de amostragem de 16 kHz);
- Modelo generativo latente que traduz as variacoes de prosodia, ritmo e intensidade sonora em:
  - Movimentos articulatórios dos labios e mandibula;
  - Micro-expressoes reflexas faciais (palpebras, cenho, bochechas);
  - Atitude postural tridimensional da cabeca (Pitch, Yaw, Roll).

---

## 3. Dinamica de Pose Rigida da Cabeca

A pose da cabeca e expressa no espaco $\mathrm{SO}(3)$ por meio dos angulos de Euler:
- **Pitch ($\theta_x$):** Movimento vertical de elevacao e abaixamento do queixo;
- **Yaw ($\theta_y$):** Rotacao horizontal lateral (olhar para a esquerda ou direita);
- **Roll ($\theta_z$):** Inclinacao lateral da cabeca sobre os ombros.

No VASA-1, essas trajetorias emergem da distribuicao aprendida de sincronizacao de discurso humano, apresentando acenos e inclinacoes sincronizados com as pausas e enfases vocais.

---

## 4. Metricas e Resultados Experimentais

Durante o processamento do audio `vasa_speech.wav` (9.84s), a trajetoria gerada `trajetoria_vasa1.npz` apresentou as seguintes metricas cinematicas:

| Parametro de Movimento | Faixa Observada | Media Temporal | Desvio Padrao |
| :--- | :--- | :--- | :--- |
| **Pitch (Inclinacao Vertical)** | $[-2.10^\circ, +3.40^\circ]$ | $+0.65^\circ$ | $1.15^\circ$ |
| **Yaw (Rotacao Lateral)** | $[-4.20^\circ, +3.80^\circ]$ | $-0.32^\circ$ | $1.82^\circ$ |
| **Roll (Inclinacao de Ombro)** | $[-1.80^\circ, +1.50^\circ]$ | $-0.10^\circ$ | $0.74^\circ$ |
| **Abertura Labial (AU26 / Exp)** | $[0.00, 0.42]$ | $0.18$ | $0.11$ |

### Observacoes:
- A articulacao labial preserva sincronia fonetica estrita com o audio de entrada;
- Os movimentos de cabeca apresentam variabilidade suave sem efeito robotico.

---

## 5. Como Reproduzir

```bash
# 1. Gerar a trajetoria cinematica holistica (.npz)
python Implementacoes/02_vasa1_audio_motion/vasa1_gerador_dinamica.py

# 2. Renderizar o video foto-realista final (.mp4) na GPU MPS
python Implementacoes/02_vasa1_audio_motion/renderizar_video_vasa1.py
```
