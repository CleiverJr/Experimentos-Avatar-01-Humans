# 03. Protocolo de Comunicação e Interface Inter-Trilhas

Para que o trabalho da Trilha D se integre perfeitamente com os modelos das Trilhas B e C, definimos uma especificação de dados aberta e padronizada.

---

## 1. Esquema do Pacote de Saída da Trilha D

Cada frame de animação gerado pela Trilha D para uma taxa padrão de **30 FPS** (ou 60 FPS) contém os seguintes vetores numéricos:

```json
{
  "version": "1.0.0",
  "fps": 30.0,
  "total_frames": 90,
  "duration_seconds": 3.0,
  "frames": [
    {
      "frame_idx": 0,
      "timestamp": 0.0,
      "head_pose": {
        "rotation_euler_deg": [2.5, -4.1, 0.8],
        "rotation_6d": [0.99, 0.01, 0.05, 0.02, 0.98, -0.04],
        "translation_cam": [0.01, -0.02, 0.45]
      },
      "facs_action_units": {
        "AU01_inner_brow_raiser": 0.15,
        "AU02_outer_brow_raiser": 0.10,
        "AU04_brow_lowerer": 0.05,
        "AU06_cheek_raiser": 0.65,
        "AU12_lip_corner_puller": 0.70,
        "AU25_lips_part": 0.45,
        "AU26_jaw_drop": 0.30,
        "AU45_blink": 0.0
      },
      "flame_parameters": {
        "expression_coefficients": [0.24, -0.11, 0.85, "... (50 valores)"],
        "jaw_rotation_axis_angle": [0.18, 0.0, 0.0],
        "eyeballs_rotation": [0.02, -0.05, 0.0, 0.02, -0.05, 0.0]
      }
    }
  ]
}
```

---

## 2. Como as Outras Trilhas Consomem Estes Dados

### Para o Fernando (Trilha C - 3D Gaussian Splatting / GaussianAvatars)
1. **Pose Global:** Usa `rotation_6d` (ou Euler) e `translation_cam` para posicionar o nó raiz do modelo 3DGS no espaço de câmera do renderizador.
2. **Deformação Facial:** Alimenta diretamente o vetor `expression_coefficients` e `jaw_rotation_axis_angle` nas funções de deformação das Gaussianas presas à malha FLAME (baseado em LBS - Linear Blend Skinning).
3. **Olhar:** Usa `eyeballs_rotation` para rodar as gaussianas correspondentes à íris/córnea.

### Para o Arthur (Trilha B - Malha / Rigging / FLAME)
1. Aplica a função de malha FLAME padrão:
   $$M(\beta, \theta, \psi) = \text{LBS}(T_P(\beta, \theta, \psi), J(\beta), \mathbf{w}, \mathcal{W})$$
   Onde $\psi$ é a expressão gerada pela Trilha D, e $\theta$ inclui a pose da cabeça e da mandíbula.
2. Como a malha do Arthur já possui os blendshapes corretos, a Trilha D garante compatibilidade anatômica nativa.

### Para o Mateus (Trilha A - Vídeo 2D)
1. Se o Mateus estiver usando modelos como LivePortrait ou SadTalker, ele pode consumir diretamente a trajetória de `head_pose` e `facs_action_units` para alimentar os mapas de deformação (warp/flow fields) da imagem de referência.
