"""
Testes unitários para o analisador de instruções de texto (InstructAvatar / OmniHuman).
"""

import os
import sys
import numpy as np

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from src.instruct_parser import InstructParser


def test_instruct_pipeline():
    print("=== [TESTE 4] Controle por Linguagem Natural (InstructAvatar / OmniHuman) ===")
    parser = InstructParser(embedding_dim=16)

    # 1. Teste de instrução composta em português
    prompt_1 = "Fale com muita raiva e olhe para a esquerda balançando a cabeça afirmativo"
    res_1 = parser.parse_instruction(prompt_1)
    
    print(f"Instrução: \"{prompt_1}\"")
    print(f"✓ Emoções detectadas: {res_1['emotion_weights']}")
    print(f"✓ Intensidade calculada: {res_1['intensity']} (esperado >= 1.5)")
    print(f"✓ Vieses espaciais de cabeça: {res_1['head_bias']}")
    
    assert "angry" in res_1["emotion_weights"], "Deveria detectar 'angry'."
    assert res_1["intensity"] >= 1.5, "Deveria detectar alta intensidade ('muita')."
    assert res_1["head_bias"]["yaw_deg"] > 0, "Deveria virar para a esquerda (yaw positivo)."
    assert res_1["head_bias"]["nodding"] is True, "Deveria detectar aceno afirmativo."

    # 2. Teste de instrução em inglês com tom alegre e contido
    prompt_2 = "Speak lightly happy and look up"
    res_2 = parser.parse_instruction(prompt_2)
    
    print(f"\nInstrução: \"{prompt_2}\"")
    print(f"✓ Emoções detectadas: {res_2['emotion_weights']}")
    print(f"✓ Intensidade calculada: {res_2['intensity']} (esperado <= 0.8)")
    print(f"✓ Vieses espaciais de cabeça: {res_2['head_bias']}")
    
    assert "happy" in res_2["emotion_weights"], "Deveria detectar 'happy'."
    assert res_2["intensity"] <= 0.8, "Deveria detectar baixa intensidade ('lightly')."
    assert res_2["head_bias"]["pitch_deg"] > 0, "Deveria olhar para cima (pitch positivo)."

    # 3. Validação do vetor de condicionamento contínuo para o Denoiser
    cond_vec = res_1["conditioning_vector"]
    assert cond_vec.shape == (16,), f"Shape do vetor de condicionamento incorreto: {cond_vec.shape}"
    assert not np.isnan(cond_vec).any(), "Vetor de condicionamento contém NaN."
    print(f"✓ Vetor de condicionamento gerado com 16 dimensões: {cond_vec[:5]}...")
    print("--> Teste de Instruções concluído com SUCESSO!\n")


if __name__ == "__main__":
    test_instruct_pipeline()
