# 🧬 Experimentos Avatar 01 — Humans

Repositório de pesquisa, literatura científica e implementações práticas dedicadas à **síntese, animação e controle comportamental de avatares foto-realistas** a partir de áudio de fala e instruções textuais em linguagem natural.

O objetivo deste projeto é investigar e reimplementar os princípios dos principais modelos do estado da arte (SOTA), compreendendo do zero o funcionamento matemático de cada arquitetura e construindo um motor generativo expressivo de alta fidelidade.

---

## 🔬 Modelos e Literatura Estudada (`Artigos/`)

O repositório reúne os papers seminais dos modelos estudados e implementados:

| Modelo | Paper de Referência | Conceito Chave | Status |
| :--- | :--- | :--- | :---: |
| **VASA-1** | [VASA-1.pdf](Artigos/VASA-1.pdf) *(Microsoft Research, 2024)* | Dinâmica holística facial e pose de cabeça desacopladas da identidade em espaço latente 3D. | 📚 Em estudo / Lab pronto |
| **AUHead** | [AUHead.pdf](Artigos/AUHead.pdf) *(ICLR 2026)* | Controle anatômico e muscular fisiológico baseado em Action Units do sistema FACS de Paul Ekman. | 📚 Em estudo / Lab pronto |
| **InstructAvatar** | [InstructAvatar.pdf](Artigos/InstructAvatar.pdf) *(AAAI 2025)* | Modulação de estilo motor e emoções sutis via prompts de linguagem natural livre. | 📚 Em estudo / Lab pronto |
| **Audio2Photoreal** | [Audio2Photoreal.pdf](Artigos/Audio2Photoreal.pdf) *(Meta Reality Labs, CVPR 2024)* | Comportamento em conversações diádicas (fala ativa + escuta reativa com acenos de cabeça). | 📚 Em estudo / Lab pronto |
| **OmniHuman-1.5** | [OmniHuman-1.5.pdf](Artigos/OmniHuman-1.5.pdf) *(ByteDance, 2025)* | Arquitetura cognitiva dual: Sistema 1 reativo (fala e prosódia) e Sistema 2 deliberativo (planejamento via LLM). | 📚 Em estudo / Lab pronto |
| **Motion Diffusion (MDM)** | [MDM_Motion_Diffusion.pdf](Artigos/MDM_Motion_Diffusion.pdf) *(Tevet et al.)* & [DDPM.pdf](Artigos/DDPM.pdf) | Modelagem generativa estocástica resolvendo o problema 1-para-Muitos sem colapsar para a média. | 📚 Em estudo / Lab pronto |
| **LivePortrait** | [LivePortrait.pdf](Artigos/LivePortrait.pdf) *(Guo et al., 2024)* | Espaço de movimento implícito baseado em 21 keypoints 3D com costura e retargeting suave. | 📚 Em estudo / Lab pronto |

---

## 📊 Salto de Qualidade: Malha Geométrica 2D vs. Talking Head Neural

Nos primeiros experimentos de síntese facial, testou-se um deformador geométrico baseado em triangulação 2D de Delaunay com ~45 pontos colocados à mão. Em seguida, migrou-se para uma arquitetura neural baseada em **difusão de movimento latente (LMDM) + distorção volumétrica 3D (WarpF3D) + decodificador SPADE (Ditto)**.

A comparação objetiva dos resultados para o mesmo áudio de teste de 8 segundos demonstra o salto de expressividade:

| Métrica (via MediaPipe) | Malha Geométrica 2D | Talking Head Neural | Diferencial |
| :--- | :---: | :---: | :---: |
| **Amplitude de abertura da boca (dp)** | 0,0004 | **0,040** | **~100× maior articulação** |
| **AUC Fala / Silêncio (0.5 = aleatório)** | 0,35 | **0,78** | **Sincronia labial real** |
| **Abertura na Fala ÷ Abertura no Silêncio** | 0,8× | **5,1×** | **Boca fecha nos silêncios** |
| **Movimento de cabeça (dp em pixels)** | 1,4 px | **3,5 px** | **Pose dinâmica natural** |
| **Frequência de piscadas** | 0/min | **7,5/min** | **Olhar vivo e orgânico** |

---

## 📂 Estrutura do Repositório

```
Experimentos-Avatar-01-Humans/
├── Artigos/                       # Papers em PDF referentes aos modelos do projeto
├── implementacoes_manuais/        # Reimplementação didática modelo por modelo
│   ├── 01_ditto_core/             # Núcleo geométrico, tensores x_s/x_d e Lab x Renderer
│   ├── 02_vasa1_audio_motion/     # Dinâmica holística e pose livre via áudio
│   ├── 03_auhead_facs_control/    # Mapeamento de Action Units (FACS) para keypoints 3D
│   ├── 04_instruct_avatar_nlp/    # Parser de comandos de direção cênica
│   ├── 05_audio2photoreal_dialogue/# Escuta ativa e acenos de cabeça (backchannel)
│   ├── 06_omnihuman_dual_system/  # Arquitetura de Sistema 1 x Sistema 2
│   └── 07_motion_diffusion_mdm/   # Amostragem estocástica DDIM e diversidade motora
└── laboratorio/                   # Pipeline completo de referência funcional
    ├── foto_realista_v2/          # Motor neural desacoplado (ditto_lab, compose, metrics)
    ├── output_v2/                 # Vídeos comparativos dos experimentos e gráficos
    ├── data/                      # Retrato fotográfico de teste em alta resolução
    ├── src/                       # Utilitários de áudio, FACS e exportação
    └── tests/                     # Testes automatizados do pipeline
```

---

## 🛠️ Começando a Rodar

### 1. Pré-requisitos
Recomenda-se ambiente virtual Python 3.10:
```bash
python3.10 -m venv .venv
source .venv/bin/activate
pip install -r laboratorio/requirements.txt
```

### 2. Pesos Pré-Treinados
Os pesos dos modelos neurais (~2.3 GB) são ignorados pelo repositório por excederem os limites do Git. Instruções para obtenção dos checkpoints estão em [laboratorio/foto_realista_v2/checkpoints/README.md](laboratorio/foto_realista_v2/checkpoints/README.md).

### 3. Rodando o Pipeline de Referência
```bash
cd laboratorio/foto_realista_v2

# Gerar trajetórias de movimento (rápido, segundos)
python experiments.py

# Renderizar os frames neurais (em lote com fila)
python render_queue.py fila.json

# Montar os vídeos finais comparativos
python compose.py e1 e2 e3 e4 e5 e6
```
