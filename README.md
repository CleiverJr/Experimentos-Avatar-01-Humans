# 🧬 Humans — Hub de Pesquisa e Laboratório de Humanos Virtuais

Repositório central de estudos, artigos e implementações práticas do projeto **Humans** (AKCIT / UFG). Este repositório concentra materiais de estudo teóricos (Visão Computacional, 3DGS, Modelos de Difusão) e o desenvolvimento prático da **Trilha D: Controle, Emoção e Comportamento de Avatares Foto-Realistas**.

---

## 🏛️ Contexto e Divisão de Papéis (AKCIT)

O projeto de humanos virtuais divide-se em quatro frentes sinérgicas:

```
[Áudio de Fala / Prompt Textual]
                │
                ▼
      ┌──────────────────┐
      │     TRILHA D     │ ◄─── Cleiver (Controle, Emoção e Comportamento)
      │ (O Titiriteiro)  │      • Motor gerador de pose 3D, FACS AUs e blendshapes
      └─────────┬────────┘
                │
                ├─────────────────────────────┬─────────────────────────────┐
                ▼                             ▼                             ▼
      ┌──────────────────┐          ┌──────────────────┐          ┌──────────────────┐
      │     TRILHA B     │          │     TRILHA C     │          │     TRILHA A     │
      │ (Arthur - 3D)    │          │ (Fernando - 3DGS)│          │ (Mateus - 2D)    │
      │ Malha FLAME/     │          │ GaussianAvatars  │          │ Síntese direta   │
      │ rigging facial   │          │ foto-realista    │          │ em pixel-space   │
      └──────────────────┘          └──────────────────┘          └──────────────────┘
```

---

## 📂 Estrutura do Repositório

```
Humans/
├── Artigos/                       # Papers e literatura base (3DGS, DDPM, Flow Matching, Instant-NGP)
├── Slides&Listas/                 # Apresentações, seminários e notas de estudo (NLP, Multimodal, Slides Trilha D)
├── Trilha_D_Controle_Emocao/      # Laboratório prático da Trilha D
│   ├── foto_realista_v2/          # Pipeline foto-realista com Ditto TalkingHead + controles da Trilha D
│   │   ├── ditto_lab.py           # Núcleo desacoplado: Lab (movimento) e Renderer (pixels)
│   │   ├── experiments.py         # Implementação dos experimentos das 6 sementes (E1 a E6)
│   │   ├── instruct_parser.py     # Parser de intenções dramáticas em linguagem natural
│   │   ├── compose.py             # Montagem e composição dos vídeos comparativos
│   │   ├── metrics.py             # Extração de métricas objetivas (MediaPipe, abertura de boca, AUC)
│   │   ├── PATCHES_ditto_cpu.md   # Patches e compatibilidade CPU/MPS (sem dependência de CUDA)
│   │   └── checkpoints/           # Estrutura e instruções de download dos modelos pré-treinados
│   ├── output_v2/                 # Vídeos comparativos finais (E0 a E6), métricas e dashboard HTML
│   ├── src/                       # Módulos legados e bibliotecas utilitárias da Trilha D
│   ├── tests/                     # Testes unitários e de integração
│   └── data/                      # Imagens de estúdio e amostras de teste
├── generate_html_deck.py          # Gerador do slide deck web interativo com vídeos embutidos
└── generate_pptx_deck.py          # Gerador da apresentação PowerPoint (.pptx)
```

---

## 🎭 Trilha D: As 6 Sementes Tecnológicas

A Trilha D investiga como transformar áudio (fala) e texto (direção cênica) em movimento expressivo sem depender de atores humanos em webcam frame a frame.

| Semente | Paper & Origem | Foco Conceitual | Como Reproduzido neste Repositório |
| :--- | :--- | :--- | :--- |
| **VASA-1** | Microsoft Research (2024) | Dinâmica holística e latente desacoplado | LMDM com HuBERT modelando pose e expressão sem controles manuais. |
| **AUHead** | ICLR (2026) | Controle anatômico via FACS de Ekman | Mapeamento `au_to_delta_exp`: AUs convertidas em deslocamento dos 21 keypoints 3D. |
| **InstructAvatar**| AAAI (2025) | Controle dramático via linguagem natural | `InstructParser` modulando pesos emocionais, AUs EMFACS e atitude de pose. |
| **Audio2Photoreal**| Meta Reality Labs, CVPR (2024) | Comportamento conversacional (diálogo) | Fala ativa e escuta atenta com acenos de cabeça (*backchannel*) nos picos de fala. |
| **OmniHuman-1.5** | ByteDance (2025) | Cognição Dual (Sistema 1 x Sistema 2) | Sistema 1 (reflexo reativo de fala) x Sistema 2 (plano de gestos deliberativo via LLM). |
| **Motion Diffusion**| Paradigma MDM / DDPM | Resolução do problema 1-para-Muitos | Invalidação de cache DDIM permitindo que 8 sementes gerem trajetórias motoras únicas. |

---

## 📊 Comparativo: Do Warping Delaunay (v1) ao Neural Talking Head (v2)

No teste inicial (`photoreal_renderer.py`), a deformação ocorria por malha geométrica 2D rígida (~45 pontos Delaunay). No pipeline v2 com **Ditto** (difusão latente no espaço LivePortrait + SPADE Decoder), o salto de qualidade foi mensurado objetivamente:

| Métrica (MediaPipe - 8s de áudio idêntico) | v1 (Delaunay Warping) | v2 (Ditto + Trilha D) | Ganho |
| :--- | :---: | :---: | :---: |
| **Amplitude da Boca (dp abertura normalizada)** | 0,0004 | **0,040** | **~100× maior** |
| **AUC Fala / Silêncio (0.5 = aleatório)** | 0,35 | **0,78** | **Correlação real** |
| **Boca na Fala ÷ Boca no Silêncio** | 0,8× | **5,1×** | **Articulação visível** |
| **Movimento da Cabeça (dp em px, 512p)** | 1,4 px | **3,5 px** | **Dinâmica natural** |
| **Piscadas por Minuto** | 0 | **7,5** | **Olhar vivo** |

---

## 🚀 Como Executar

### 1. Ambiente
Recomenda-se Python 3.10:
```bash
python3.10 -m venv .venv
source .venv/bin/activate
pip install -r Trilha_D_Controle_Emocao/requirements.txt
```

### 2. Pesos e Modelos
Consulte [Trilha_D_Controle_Emocao/foto_realista_v2/checkpoints/README.md](file:///Users/cleiver/Documents/Estudos/Humans/Trilha_D_Controle_Emocao/foto_realista_v2/checkpoints/README.md) para baixar os checkpoints do Hugging Face.

### 3. Executando os Experimentos
```bash
cd Trilha_D_Controle_Emocao/foto_realista_v2

# 1. Gerar trajetórias de movimento (rápido, segundos)
python experiments.py

# 2. Renderizar frames neurais a partir dos .npz
python render_queue.py fila.json

# 3. Compor os vídeos finais
python compose.py e1 e2 e3 e4 e5 e6
```

---

## 📖 Roteiro de Estudos e Implementação Manual

Para reimplementar cada componente do zero de forma didática, siga a sequência documentada:
1. **Guia 01 & 02:** Entendimento do espaço latente do LivePortrait, HuBERT e LMDM.
2. **Guia 03:** Separação do gerador de movimento (`.npz`) do sintetizador de pixels.
3. **Guia 05:** E1 VASA-1 — Dinâmica holística gerada por áudio.
4. **Guia 06:** E3 AUHead — Anatomia facial, calibração manual de AUs e FACS.
5. **Guia 07:** E2 InstructAvatar — Integração de NLP com modulação de AUs.
6. **Guia 08:** E4 Audio2Photoreal — Detecção de envelopes acústicos e acenos de escuta ativa.
7. **Guia 09:** E5 OmniHuman-1.5 — Planejamento semântico de gestos via LLM (Sistema 2).
8. **Guia 10:** E6 Motion Diffusion — Amostragem estocástica e controle de ruído DDIM.
