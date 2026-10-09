# 🎭 Trilha D: Controle, Emoção e Comportamento
**Pesquisador Responsável:** Cleiver  
**Contexto do Grupo:** Projeto Humans (Modelagem, Animação e Renderização de Humanos Virtuais)  
**Objetivo Central:** Síntese de movimento autônomo, expressividade emocional e comportamento dinâmico a partir de **áudio e texto, sem depender de pose explícita (webcam ou captura de movimento pré-gravada)**.

---

## 🧭 O Papel da Trilha D no Ecossistema Humans

No desenvolvimento de humanos digitais foto-realistas, as responsabilidades se dividem em quatro pilares interconectados:

```
[Áudio / Texto] ─────────► [TRILHA D: Cleiver] ─── (Pose 3D, FLAME, AUs) ───┐
                            (O Titiriteiro / Maestro)                      │
                                                                           ▼
[Foto Única] ─────────────► [TRILHA B: Arthur] ──── (Malha / Rigging) ──► [TRILHA C: Fernando] ──► [Vídeo 3DGS]
                             (A Marionete / Geometria)                    (A Pele / 3DGS Animável)
                                                                           ▲
[Foto Única + Áudio] ─────► [TRILHA A: Mateus] ───────────────────────────┴─► [Vídeo 2D Direto]
                             (Síntese Direta 2D Pixel-Space)
```

* **Arthur (Trilha B):** Constrói a geometria 3D da cabeça/corpo a partir de uma foto (malha FLAME/SMPL-X com rigging).
* **Fernando (Trilha C):** Anexa Gaussianas 3D à malha e faz a renderização foto-realista em tempo real (GaussianAvatars).
* **Mateus (Trilha A):** Explora síntese direta em espaço de pixel 2D (LivePortrait, SadTalker, EMO).
* **Cleiver (Trilha D):** É o **motor motor e comportamental**. Sem a Trilha D, a malha do Arthur e as Gaussianas do Fernando ficam completamente imóveis (um manequim estático), a menos que um humano fique gravando seu próprio rosto na webcam. A Trilha D gera as trajetórias de rotação da cabeça, as microexpressões faciais, as piscadas de olhos e os gestos corporais diretamente do som da voz e de instruções textuais.

---

## 🔬 Dissecção das Sementes de Pesquisa

### 1. VASA-1 (Microsoft Research, 2024)
* **Tema:** *Visual Affective Skills in Avatar* (Habilidades Visuais Afetivas).
* **Inovação Nuclear:** Desacoplamento radical em um **espaço latente facial holístico**. Em vez de prever pixels diretamente a partir do áudio, o VASA-1 comprime o vídeo em um espaço latente que separa:
  1. *Identidade Estática* (aparência da pessoa);
  2. *Pose Rígida da Cabeça* (Euler angles + translação 3D);
  3. *Dinâmica Facial Não-Rígida* (expressão, abertura de boca, micro-movimentos).
* **Motor Generativo:** Um *Diffusion Transformer* modela a distribuição temporal das dinâmicas faciais e da pose da cabeça condicionado pelo áudio de fala.
* **Controle:** Permite injetar sinais adicionais como vetor de olhar (*gaze*), distância da câmera e *offsets* de humor. Capaz de gerar vídeos 512x512 a mais de 40 FPS em tempo real.

### 2. InstructAvatar (AAAI 2025)
* **Tema:** *Text-Guided Emotion and Motion Control for Avatar Generation*.
* **Inovação Nuclear:** Controle da expressividade via **linguagem natural** granular. Enquanto modelos anteriores aceitavam apenas categorias engessadas ("alegre" ou "bravo"), o InstructAvatar interpreta instruções detalhadas (ex: *"fale com uma mistura de euforia e surpresa"*, *"levante as sobrancelhas e incline a cabeça à esquerda"*).
* **Arquitetura:** Gerador de difusão de duas ramificações (*two-branch diffusion*):
  * *Ramificação Temporal-Acústica:* Alinhada com os fonemas do áudio para lip-sync perfeito;
  * *Ramificação Semântico-Instrucional:* Condicionada em embeddings de texto (via LLM/CLIP) para modular o estilo motor e a carga afetiva.

### 3. AUHead (ICLR 2026)
* **Tema:** *Realistic Emotional Talking Head Generation via Action Units Control*.
* **Inovação Nuclear:** Uso explícito do **FACS (Facial Action Coding System)** de Paul Ekman como representação intermediária transparente e fisicamente interpretável.
* **Arquitetura em 2 Etapas:**
  * *Etapa 1 (Cognição):* Um modelo de áudio-linguagem (ALM) processa a fala usando uma cadeia de raciocínio (*Emotion-then-AU Chain-of-Thought*) para derivar a ativação temporal de cada músculo facial individual (AU1, AU2, AU4, AU12, AU25, AU26, etc.).
  * *Etapa 2 (Síntese Contornada):* Um modelo de difusão renderiza a dinâmica facial condicionado rigorosamente na trajetória dessas Action Units, garantindo que expressões sutis (como um micro-sorriso assimétrico ou franzir de cenho) sejam respeitadas.

### 4. Audio2Photoreal (CVPR 2024 - Meta Reality Labs)
* **Tema:** *From Audio to Photoreal Embodiment: Synthesizing Humans in Conversations*.
* **Inovação Nuclear:** Expansão para o **corpo inteiro** e gesticulação natural em diálogos conversacionais diádicos.
* **Abordagem Híbrida (VQ-VAE + Diffusion):**
  * O movimento corporal tem posturas plausíveis de baixa frequência (braços cruzados, mãos em repouso) e gestos expressivos de alta frequência (enfatizar uma palavra com as mãos, balançar o tronco).
  * O trabalho utiliza um *Vector-Quantized VAE (VQ-VAE)* para aprender um catálogo (*codebook*) discreto de poses humanas anatomicamente estáveis, e aplica **modelos de difusão** para interpolar trajetórias contínuas e detalhes vibrantes a partir do áudio.

### 5. OmniHuman-1.5 (ByteDance, 2025)
* **Tema:** *Instilling an Active Mind in Avatars via Cognitive Simulation*.
* **Inovação Nuclear:** Arquitetura inspirada na teoria cognitiva de **Sistema 1 e Sistema 2** (Daniel Kahneman):
  * *Sistema 1 (Reativo/Rápido):* Reflexos motores de curto prazo — sincronismo fonema-lábio e oscilações prosódicas imediatas guiadas pelo sinal acústico.
  * *Sistema 2 (Deliberado/Lento):* Um MLLM (Multimodal Large Language Model) analisa o significado semântico do discurso, o tópico da conversa e o arco narrativo para planejar gestos conscientes (ex: hesitar antes de responder, olhar para o teto para lembrar de algo, abrir os braços para acolher uma ideia).
* Esses dois sistemas alimentam um *Diffusion Transformer* unificado para gerar uma performance humana completa e convincente.

### 6. Motion Diffusion Models (MDM)
* **Tema:** Paradigma generativo estocástico para séries temporais de movimento humano.
* **Por que Difusão?** O problema do mapeamento fala-movimento é **1-para-Muitos** (*one-to-many*). Uma frase pode ser dita com infinitas variações de inclinação de cabeça e piscadas. Modelos de regressão direta (L1/L2 loss) colapsam para a média (resultando em cabeças engessadas e sem vida).
* **Princípio:** O modelo aprende a reverter um processo de difusão gaussiana, transformando trajetórias ruidosas em curvas motoras suaves, realistas e diversificadas, condicionadas por atenção cruzada (*cross-attention*) em vetores de áudio e texto.

---

## 🛠️ Estrutura Deste Repositório de Testes

```
Trilha_D_Controle_Emocao/
├── README.md                           # Este documento
├── requirements.txt                    # Dependências do projeto
├── docs/                               # Documentação detalhada e especificações
│   ├── 01_panorama_trilha_d.md
│   ├── 02_analise_sementes.md
│   └── 03_protocolo_comunicacao_trilhas.md
├── src/                                # Módulos de código e protótipos funcionais
│   ├── audio_processor.py              # Extração acústica (Log-Mel, Envelopes, F0)
│   ├── action_units.py                 # Sistema FACS, Action Units e Blendshapes FLAME
│   ├── motion_diffusion.py             # Implementação funcional de Difusão Temporal 1D
│   ├── instruct_parser.py              # Mapeador de instruções em texto para condicionamento
│   └── exporter.py                     # Gerador de pacotes para o Fernando (3DGS) e Arthur (FLAME)
└── tests/                              # Baterias de validação executáveis
    ├── test_audio.py
    ├── test_facs.py
    ├── test_diffusion.py
    ├── test_instruct.py
    └── run_all_tests.py                # Execução ponta a ponta integrada
```

---

## 🚀 Como Executar os Testes

Com o ambiente Python ativado:

```bash
# Executar a suíte de testes integrada completa
python tests/run_all_tests.py
```
