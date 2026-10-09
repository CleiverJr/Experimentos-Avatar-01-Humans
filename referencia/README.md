# 🛠️ Código de Referência

Esta pasta contém o código e utilitários de referência técnica para a execução do motor neural (LivePortrait / Ditto):

* **`ditto_lab.py`**: Classe de referência que isola a geração de movimento (LMDM em `.npz`) da síntese de pixels (WarpF3D + DecodeF3D).
* **`PATCHES_ditto_cpu.md`**: Instruções e patches para rodar o Ditto sem placas NVIDIA (CPU com `bfloat16` ou Mac com `mps`).
* **`checkpoints/`**: Configurações de inferência (`ditto_cfg/`) e guia de download dos pesos no Hugging Face.
