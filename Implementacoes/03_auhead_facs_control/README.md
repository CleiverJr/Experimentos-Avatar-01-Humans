# Modulo 03: AUHead (ICLR 2026) — Controle Anatomico via FACS e Comparativo Split-Screen

Este modulo implementa o controle anatomico e biomecanico baseado no Facial Action Coding System (FACS) de Paul Ekman, conforme formalizado pelo paper **AUHead: Biomechanically-Grounded Head and Facial Control via Action Units** (ICLR 2026).

---

## 1. Videos Demonstrativos Gerados

### A. Video Comparativo Split-Screen (VASA-1 Neutro vs AUHead Expressivo)
<video src="video_comparativo_vasa_vs_auhead.mp4" controls width="100%"></video>

- **Arquivo:** `video_comparativo_vasa_vs_auhead.mp4`
- **Formato:** 2048x1024 (1024x1024 lado a lado com telemetria em tempo real)
- **Duracao:** 7.64 segundos (191 frames @ 25 FPS)
- **Cenario:** Comparacao direta da mesma fala entre a expressao neutra e a ativacao controlada de Raiva (AU04) e Alegria (AU12).

### B. Video Solo AUHead
<video src="video_auhead.mp4" controls width="100%"></video>

- **Arquivo:** `video_auhead.mp4`
- **Formato:** 1024x1024 @ 25 FPS
- **Duracao:** 14.60 segundos (365 frames)

---

## 2. Fundamentacao Anatomica e Mapeamento Biomecanico

O sistema FACS decompõe os movimentos faciais em Action Units (AUs) associadas a grupos musculares especificos. No AUHead, essas acoes musculares sao mapeadas em perturbacoes diferenciais $\boldsymbol{\delta}_{exp} \in \mathbb{R}^{21 \times 3}$ nos keypoints canonicos:

| Action Unit | Nome Anatomico / Musculo | Modulacao nos Keypoints 3D | Efeito Visual |
| :--- | :--- | :--- | :--- |
| **AU01** | *Inner Brow Raiser* (Frontal medial) | $\Delta y_{1} = +0.012$, $\Delta y_{2} = -0.012$ | Cantos internos das sobrancelhas sobem (tristeza / surpresa) |
| **AU02** | *Outer Brow Raiser* (Frontal lateral) | $\Delta y_{1} = +0.020$, $\Delta y_{2} = -0.020$ | Sobrancelhas inteiras sao elevadas (atencao / espanto) |
| **AU04** | *Brow Lowerer* (Corrugador do supercilio) | $\Delta y_{1} = -0.008$, $\Delta y_{2} = +0.008$ | Glabela franzida e sobrancelhas aproximadas (raiva / foco) |
| **AU06** | *Cheek Raiser* (Orbicular do olho) | $\Delta y_{11, 15} = +0.018$, $\Delta y_{13, 16} = -0.005$ | Elevacao das macas do rosto e compressao palpebral |
| **AU12** | *Lip Corner Puller* (Zigomatico maior) | $\Delta x_{3, 7} = \pm 0.035$, $\Delta y_{13, 16} = -0.0028$ | Tracionamento dos cantos bucais para as orelhas (sorriso) |
| **AU15** | *Lip Corner Depressor* (Depressor labial) | $\Delta y_{20} = +0.010$, $\Delta y_{14} = +0.020$ | Cantos dos labios caem (tristeza / desapontamento) |
| **AU26** | *Jaw Drop* (Masseter / Pterigoideo) | $\Delta y_{19} = +0.001 \times 40$ | Abertura mandibular coordenada com o audio |
| **AU43** | *Eyes Closed* (Orbicular ocular palpebral) | $\Delta y_{11, 15} = +0.018$ | Oclusao palpebral estrita sem deformar o globo ocular |

---

## 3. Analise Comparativa: VASA-1 vs AUHead

No video split-screen `comparativo_vasa_vs_auhead.mp4`, os seguintes aspectos foram validados:
1. **Regiao da Glabela e Cenho:** Enquanto o VASA-1 mantem as sobrancelhas em posicao estatica, o AUHead ativa AU04 com precisao, aproximando o supercilio de maneira realista;
2. **Geometria Labial e Bucal:** A ativacao do zigomatico (AU12) curva os cantos da boca sem distorcer os dentes e preservando a oclusao labial nos momentos de fonação consonantal;
3. **Independencia Muscular:** Variacoes nas sobrancelhas nao induzem artefatos parasitas na regiao da boca ou no pescoco.

---

## 4. Como Reproduzir

```bash
# 1. Gerar a trajetoria com mapeamento FACS (.npz)
python Implementacoes/03_auhead_facs_control/auhead_facs_mapeador.py

# 2. Renderizar o video solo do AUHead
python Implementacoes/03_auhead_facs_control/renderizar_video_auhead.py

# 3. Gerar e renderizar o comparativo split-screen (2048x1024)
python Implementacoes/03_auhead_facs_control/comparativo_vasa_vs_auhead.py
```
