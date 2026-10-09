# 🔬 Laboratório de Referência: Animação e Controle Foto-Realista de Avatares

Este laboratório contém a implementação de referência ponta a ponta desenvolvida para animar retratos fotográficos de alta fidelidade (1024x1024) a partir de áudio e texto com controle anatômico e comportamental.

---

## 🏛️ Visão Geral da Arquitetura

O pipeline é estruturado em quatro etapas de processamento:

```
[Áudio de Fala (16 kHz)] + [Instrução de Texto (Prompt)]
                        │
                        ▼
┌─────────────────────────────────────────────────────────────┐
│ 1. Frontend e Extração de Features                          │
│    • HuBERT (ONNX): Representação acústica densa (N, 1024)  │
│    • Parser de Linguagem: Intenção dramática, pose e AUs    │
└──────────────────────────────┬──────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────┐
│ 2. Modelo de Difusão de Movimento (LMDM)                    │
│    • 50 passos DDIM em janelas temporais de 80 frames       │
│    • Gera pose de cabeça (66 bins), translação e expressão  │
└──────────────────────────────┬──────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────┐
│ 3. Injeção de Controles Anatômicos e Comportamentais        │
│    • FACS Action Units (Paul Ekman) -> delta_exp            │
│    • Rotação e viés de pose (delta_pitch, delta_yaw)        │
│    • Dinâmica de escuta ativa (acenos e backchannel)        │
└──────────────────────────────┬──────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────┐
│ 4. Síntese Neural de Alta Fidelidade (SPADE + LivePortrait) │
│    • WarpF3D: Deformação do volume denso de features 3D     │
│    • DecodeF3D: Síntese de dentes, língua, lábios e pele    │
│    • PutBack: Recomposição na foto original com blending    │
└─────────────────────────────────────────────────────────────┘
```

---

## 📂 Estrutura de Pastas

* **`foto_realista_v2/`**: O motor neural atual baseado no espaço latente do Ditto/LivePortrait rodando com aceleração CPU/bf16 ou MPS:
  * `ditto_lab.py`: Núcleo desacoplado que divide a geração em **Lab** (movimento rápido em `.npz`) e **Renderer** (processamento de imagem).
  * `experiments.py`: Roteiro dos experimentos das sementes (E1 a E6).
  * `instruct_parser.py`: Parser semântico de instruções dramáticas.
  * `compose.py` e `metrics.py`: Montagem de vídeos comparativos e métricas objetivas (MediaPipe, abertura de boca, AUC).
  * `PATCHES_ditto_cpu.md`: Adaptações para execução fora de clusters NVIDIA (compatível com macOS).
* **`output_v2/`**: Vídeos finais comparativos em MP4 (H.264/AAC), gráficos de trajetórias e o painel `laboratorio_trilha_d_v2.html`.
* **`data/`**: Amostras de retratos de estúdio em alta resolução (`vasa_portrait.jpg`).
* **`src/`**: Utilitários auxiliares de áudio, FACS e exportação.
* **`tests/`**: Testes automatizados do pipeline.
