# Ajustes no Ditto para rodar sem GPU NVIDIA

O código oficial assume CUDA. Para rodar em CPU (e, com pequenas mudanças, em MPS), aplicamos:

1. **cfg**: carregar `v0.4_hubert_cfg_pytorch.pkl`, trocar recursivamente todo `device: cuda` por `cpu` e salvar como `v0.4_hubert_cfg_cpu.pkl`.
2. **autocast** (`core/models/{motion_extractor,appearance_extractor,warp_network,decoder}.py`): o código usa `torch.autocast(..., dtype=float16, enabled=True)`, que falha em CPU. Troque por:
   ```python
   torch.autocast(device_type=self.device[:4],
                  dtype=(torch.float16 if self.device[:4]=="cuda" else torch.bfloat16),
                  enabled=(self.device[:4]=="cuda" or os.environ.get("DITTO_BF16")=="1"))
   ```
   Com `DITTO_BF16=1`, warp + decoder ficam cerca de 2× mais rápidos em CPU com AVX512-BF16, com PSNR de 54 dB em relação ao fp32 (visualmente idêntico).
3. **LMDM** (`core/utils/load_model.py`, `create_model`): repassar o `device` para o módulo `LMDM`, que tem `device='cuda'` como padrão:
   ```python
   if module_name == "LMDM":
       kwargs["device"] = device
   model = module(**kwargs)
   ```
4. **Semente da difusão** (`ditto_lab.py`): o `LMDM.setup()` sorteia o ruído de cada passo DDIM uma única vez e o guarda em cache. Por isso trocar a semente não mudava nada (diferença máxima de 0,0005°). Antes de cada geração, zeramos `sampling_timesteps` e chamamos `setup()` de novo, já com a semente aplicada.
5. Dependência extra: `einops`, e `mediapipe==0.10.14` para o landmarker de 478 pontos.
