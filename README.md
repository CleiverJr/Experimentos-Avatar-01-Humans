# 🧬 Experimentos Avatar 01 — Humans

Repositório de pesquisa, literatura científica e implementações práticas dedicadas à **síntese, animação e controle comportamental de avatares foto-realistas** a partir de áudio de fala e texto em linguagem natural.

O objetivo deste projeto é investigar e reimplementar manualmente os princípios dos principais modelos do estado da arte (SOTA), compreendendo a fundo o funcionamento matemático e arquitetural de cada um.

---

## 🔬 Literatura Científica (`Artigos/`)

O repositório reúne os papers seminais dos modelos estudados:

| Modelo | Paper de Referência | Conceito Chave |
| :--- | :--- | :--- |
| **VASA-1** | [VASA-1.pdf](Artigos/VASA-1.pdf) *(Microsoft Research, 2024)* | Dinâmica holística facial e pose de cabeça desacopladas da identidade em espaço latente 3D. |
| **AUHead** | [AUHead.pdf](Artigos/AUHead.pdf) *(ICLR 2026)* | Controle anatômico e muscular fisiológico baseado em Action Units do sistema FACS de Paul Ekman. |
| **InstructAvatar** | [InstructAvatar.pdf](Artigos/InstructAvatar.pdf) *(AAAI 2025)* | Modulação de estilo motor e emoções sutis via prompts de linguagem natural livre. |
| **Audio2Photoreal** | [Audio2Photoreal.pdf](Artigos/Audio2Photoreal.pdf) *(Meta Reality Labs, CVPR 2024)* | Comportamento em conversações diádicas (fala ativa + escuta reativa com acenos de cabeça). |
| **OmniHuman-1.5** | [OmniHuman-1.5.pdf](Artigos/OmniHuman-1.5.pdf) *(ByteDance, 2025)* | Arquitetura cognitiva dual: Sistema 1 reativo (fala e prosódia) e Sistema 2 deliberativo (planejamento via LLM). |
| **Motion Diffusion** | [MDM_Motion_Diffusion.pdf](Artigos/MDM_Motion_Diffusion.pdf) *(Tevet et al.)* & [DDPM.pdf](Artigos/DDPM.pdf) | Modelagem generativa estocástica resolvendo o problema 1-para-Muitos sem colapsar para a média. |
| **LivePortrait** | [LivePortrait.pdf](Artigos/LivePortrait.pdf) *(Guo et al., 2024)* | Espaço de movimento implícito baseado em 21 keypoints 3D com costura e retargeting suave. |

---

## 📂 Estrutura do Repositório

```
Experimentos-Avatar-01-Humans/
├── Artigos/                       # Papers em PDF referentes aos modelos estudados
├── data/                          # Retrato fotográfico neutro para testes
├── Implementacoes/                # Implementações manuais modelo por modelo
│   ├── 01_ditto_core/             # Núcleo geométrico, tensores x_s/x_d e Lab x Renderer
│   ├── 02_vasa1_audio_motion/     # Dinâmica holística e pose livre via áudio
│   ├── 03_auhead_facs_control/    # Mapeamento de Action Units (FACS) para keypoints 3D
│   ├── 04_instruct_avatar_nlp/    # Parser de comandos de direção cênica
│   ├── 05_audio2photoreal_dialogue/# Escuta ativa e acenos de cabeça (backchannel)
│   ├── 06_omnihuman_dual_system/  # Arquitetura de Sistema 1 x Sistema 2
│   └── 07_motion_diffusion_mdm/   # Amostragem estocástica DDIM e diversidade motora
├── referencia/                    # Código e configurações de suporte
│   ├── ditto_lab.py               # Módulo desacoplado de geração e renderização
│   ├── PATCHES_ditto_cpu.md       # Patches para execução em CPU/Apple Silicon (MPS)
│   └── checkpoints/               # Configurações e guia para obtenção dos modelos
├── requirements.txt               # Dependências do ambiente Python
└── README.md
```

---

## 🛠️ Como Configurar o Ambiente

```bash
# 1. Criar e ativar o ambiente virtual (Python 3.10)
python3.10 -m venv .venv
source .venv/bin/activate

# 2. Instalar dependências
pip install -r requirements.txt
```

Para instruções sobre os checkpoints pré-treinados, consulte [referencia/checkpoints/README.md](referencia/checkpoints/README.md).
