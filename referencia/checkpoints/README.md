# Checkpoints do Ditto e Piper TTS

Esta pasta armazena os pesos e checkpoints neurais necessários para executar a inferência e a renderização foto-realista da Trilha D.
Os arquivos binários pesados (`.pth`, `.onnx`, `.task`) são ignorados pelo Git devido ao seu tamanho (~2.3 GB).

## 1. Estrutura Esperada

```
checkpoints/
├── ditto_cfg/
│   ├── v0.4_hubert_cfg_pytorch.pkl
│   └── v0.4_hubert_cfg_cpu.pkl
├── ditto_pytorch/
│   ├── models/
│   │   ├── appearance_extractor.pth
│   │   ├── motion_extractor.pth
│   │   ├── lmdm_v0.4_hubert.pth
│   │   ├── warp_network.pth
│   │   ├── decoder.pth
│   │   └── stitch_network.pth
│   └── aux_models/
│       ├── hubert_streaming_fix_kv.onnx
│       ├── landmark203.onnx
│       ├── det_10g.onnx
│       ├── 2d106det.onnx
│       └── face_landmarker.task
└── piper/
    ├── pt_BR-faber-medium.onnx
    └── pt_BR-faber-medium.onnx.json
```

## 2. Como Obter os Pesos

1. **Ditto (TalkingHead):**
   - Repositório Hugging Face: [digital-avatar/ditto-talkinghead](https://huggingface.co/digital-avatar/ditto-talkinghead)
   - Baixe as pastas `ditto_pytorch/` e `ditto_cfg/`.

2. **Piper TTS (Voz Faber pt-BR):**
   - Baixe o modelo `pt_BR-faber-medium.onnx` e seu `.json` da biblioteca oficial do Piper TTS:
     [rhasspy/piper](https://github.com/rhasspy/piper/releases).
