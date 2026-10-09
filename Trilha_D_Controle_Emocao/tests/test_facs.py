"""
Testes unitários para o sistema FACS, Action Units e conversão FLAME (Trilha D).
"""

import os
import sys
import numpy as np

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from src.action_units import ActionUnitsSystem, EMO_FACS_MAP


def test_facs_pipeline():
    print("=== [TESTE 2] Sistema FACS (Action Units) e Compatibilidade FLAME ===")
    facs = ActionUnitsSystem(num_flame_exp=50)

    # 1. Validação de perfil emocional canônico (Alegria)
    happy_au = facs.get_au_vector("happy", intensity=1.0)
    idx_au12 = facs.au_to_idx["AU12"]  # Lip Corner Puller (Sorriso)
    idx_au06 = facs.au_to_idx["AU06"]  # Cheek Raiser
    assert happy_au[idx_au12] > 0.5, "AU12 deveria estar ativo para 'happy'."
    assert happy_au[idx_au06] > 0.5, "AU06 deveria estar ativo para 'happy'."
    print(f"✓ Perfil de 'happy': AU12={happy_au[idx_au12]:.2f}, AU06={happy_au[idx_au06]:.2f}")

    # 2. Interpolação de emoções (ex: 60% feliz + 40% surpreso)
    blended = facs.blend_emotions({"happy": 0.6, "surprised": 0.4})
    idx_au01 = facs.au_to_idx["AU01"]  # Inner Brow Raiser (Surpresa)
    print(f"✓ Emoção combinada (60% feliz, 40% surpreso): AU12={blended[idx_au12]:.2f}, AU01={blended[idx_au01]:.2f}")
    assert blended[idx_au12] > 0.3 and blended[idx_au01] > 0.2

    # 3. Modulação temporal com áudio e piscadas
    T = 90  # 3 segundos a 30 FPS
    base_seq = np.tile(blended, (T, 1))
    dummy_energy = np.sin(np.linspace(0, 3 * np.pi, T)) ** 2
    modulated_seq = facs.modulate_with_speech(base_seq, dummy_energy, blink_interval=45)

    idx_au26 = facs.au_to_idx["AU26"]  # Jaw Drop
    idx_au45 = facs.au_to_idx["AU45"]  # Blink
    assert np.max(modulated_seq[:, idx_au26]) > 0.3, "AU26 deveria abrir durante a fala."
    assert np.max(modulated_seq[:, idx_au45]) > 0.8, "AU45 deveria disparar piscada."
    print("✓ Modulação de fala (AU26 mandíbula) e piscadas fisiológicas (AU45) validadas")

    # 4. Conversão para parâmetros FLAME (50 coeficientes de expressão + rotação de mandíbula)
    flame_out = facs.au_to_flame(modulated_seq[10])
    exp_coefs = flame_out["expression_coefficients"]
    jaw_rot = flame_out["jaw_rotation"]

    assert exp_coefs.shape == (50,), f"Shape de FLAME exp incorreto: {exp_coefs.shape}"
    assert jaw_rot.shape == (3,), f"Shape de FLAME jaw incorreto: {jaw_rot.shape}"
    print(f"✓ Conversão para FLAME: 50 coeficientes de expressão gerados, Jaw Rotation X={jaw_rot[0]:.3f} rad")
    print("--> Teste de FACS e FLAME concluído com SUCESSO!\n")


if __name__ == "__main__":
    test_facs_pipeline()
