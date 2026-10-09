# Trilha D: experimentos foto-realistas v2 (Ditto + controles da Trilha D)

Esta pasta substitui o `src/photoreal_renderer.py` (warping Delaunay com cerca de 45 pontos posicionados à mão) por um **talking head neural de verdade**. Os controles da Trilha D (emoção, Action Units e pose) agora dirigem um renderizador que articula a boca, os dentes, as pálpebras e a cabeça.

## Por que o teste antigo ficava ruim

- `photoreal_renderer.py` não usa nenhum modelo: desloca triângulos de uma malha fixa sobre a foto. A abertura da mandíbula virava **3 a 5 px** de deslocamento em 512 px, então a boca quase não se mexia.
- Na métrica com MediaPipe, a amplitude da abertura da boca no vídeo antigo é **cerca de 100 vezes menor** que no novo. O AUC fala/silêncio do vídeo antigo fica abaixo de 0,5, ou seja, a boca nem acompanha os trechos com voz. Os números estão em `E0_metricas_antes_x_depois.png`.
- Os demais testes do laboratório usavam um avatar desenhado em canvas.

## O que mudou

| Antes | Agora |
|---|---|
| Malha Delaunay fixa sobre a foto | **Ditto** (Ant Group, ACM MM 2025): difusão no espaço de movimento do LivePortrait, com warping 3D de features e decoder SPADE |
| Movimento sintético (senoides + DDPM 1D sem treino) | **LMDM** treinado: áudio (HuBERT) → pose + expressão, com olhar e piscadas |
| Voz do `say` do macOS | **Piper TTS pt-BR (faber, masculina)**, combinando com o rosto |
| Avatar desenhado | A própria foto de estúdio (1024×1024), colada de volta com máscara suave |

## Mapa sementes → experimento

| Semente | O que foi testado | Como |
|---|---|---|
| **VASA-1** | áudio → dinâmica holística | LMDM do Ditto (mesma ideia do VASA: difusão num espaço latente que separa identidade, pose e expressão). O VASA-1 não tem pesos públicos. |
| **InstructAvatar** | texto controla a emoção | `InstructParser` (código da Trilha D) → rótulo de emoção do Ditto + perfil de AUs (protótipos EMFACS) + viés de pose |
| **AUHead** | controle anatômico por FACS | `au_to_delta_exp`: cada AU vira um deslocamento dos 21 keypoints implícitos 3D (calibrado visualmente nesta foto) |
| **Audio2Photoreal** | comportamento em conversa | falar e escutar: acenos de backchannel nos picos de ênfase da outra voz, sorriso e giro para o interlocutor |
| **OmniHuman-1.5** | Sistema 1 × Sistema 2 | S1 = só áudio. S2 = plano de gestos escrito por um LLM a partir da transcrição (pensar, concordar, ressalvar, animar) |
| **Motion Diffusion** | 1-para-muitos | mesma frase com 8 sementes; a semente passou a controlar de fato o ruído do DDIM (o Ditto original o deixava fixo em cache) |

## Limitações (honestas)

- **VASA-1 e OmniHuman-1.5** não têm pesos públicos. Os experimentos reproduzem a *ideia* de cada um com um modelo aberto equivalente.
- **Corpo e gestos de mão** (Audio2Photoreal e OmniHuman): o retrato não mostra mãos e o Ditto anima só a cabeça. O experimento de conversa cobre o comportamento de cabeça e rosto. Gestos de corpo exigem um modelo de vídeo (por exemplo OmniAvatar ou EchoMimicV2) e GPU.
- O rótulo de emoção do Ditto muda pouco a expressão sozinho. A emoção legível vem da camada de AUs, e isso também é um resultado do experimento.
- Tudo foi renderizado em **CPU**, a cerca de 3 s por frame (bf16). Numa GPU o Ditto roda em tempo real.

## Como rodar

1. `git clone https://github.com/antgroup/ditto-talkinghead` e baixar de `huggingface.co/digital-avatar/ditto-talkinghead` a pasta `ditto_pytorch/` e o `ditto_cfg/v0.4_hubert_cfg_pytorch.pkl`.
2. Aplicar os ajustes para rodar sem CUDA, descritos em `PATCHES_ditto_cpu.md`.
3. `python experiments.py` gera o movimento de todos os experimentos (rápido) em `runs/`.
4. `python render_queue.py fila.json` renderiza os frames (lento).
5. `python compose.py e1 e1_antes_depois e2 e3 e4 e5 e6` monta os vídeos finais.
6. `python metrics.py video.mp4` calcula as métricas objetivas: abertura da boca, AUC fala/silêncio, movimento de cabeça e piscadas.

No Mac (M-series) dá para trocar `device: cpu` por `mps` no cfg. Deve ficar bem mais rápido.

## Arquivos

- `ditto_lab.py`: núcleo (geração de movimento + controles, renderização separada, AU → keypoints)
- `experiments.py`: definição dos 6 experimentos
- `compose.py`, `charts.py`, `metrics.py`: vídeos finais, gráficos e métricas
- `runs/*/*.npz`: trajetórias de movimento (keypoints, pose, expressão) por experimento, para exportar às Trilhas B/C
- `runs/*/*.json`: linha do tempo dos controles (AUs, pose) e o plano do Sistema 2

## Pesos (já nesta pasta)

`checkpoints/` tem tudo o que o código precisa, já na estrutura do Ditto:

```
checkpoints/
├── ditto_cfg/            v0.4_hubert_cfg_pytorch.pkl (original) e v0.4_hubert_cfg_cpu.pkl (device=cpu)
├── ditto_pytorch/models/      appearance_extractor, motion_extractor, lmdm_v0.4_hubert, warp_network, decoder, stitch_network (.pth)
├── ditto_pytorch/aux_models/  hubert_streaming_fix_kv.onnx, landmark203.onnx, det_10g.onnx, 2d106det.onnx, face_landmarker.task
└── piper/                pt_BR-faber-medium.onnx (+ .json), a voz pt-BR
```

Para usar: clone o repositório do Ditto, aplique `PATCHES_ditto_cpu.md` e aponte `DITTO_DIR` para o clone, com
`ln -s <esta pasta>/checkpoints <clone>/checkpoints`. A voz: `echo "texto" | piper -m checkpoints/piper/pt_BR-faber-medium.onnx -f saida.wav` (`pip install piper-tts`).
