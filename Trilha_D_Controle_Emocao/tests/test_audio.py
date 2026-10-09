"""
Testes unitários para o processador de áudio acústico (Trilha D).
"""

import os
import sys
import numpy as np

# Adiciona pasta raiz ao sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from src.audio_processor import AudioProcessor


def test_audio_pipeline():
    print("=== [TESTE 1] Processamento Acústico e Extração de Features ===")
    processor = AudioProcessor(sample_rate=16000, n_mels=80, fps=30.0)

    # 1. Gerar fala sintética calibrada (3 segundos)
    duration = 3.0
    speech = processor.generate_synthetic_speech(duration_sec=duration, base_f0=130.0)
    assert len(speech) == int(16000 * duration), "Tamanho do áudio sintético incorreto."
    print(f"✓ Fala sintética gerada: {len(speech)} amostras ({duration}s a 16kHz)")

    # 2. Extração de características
    features = processor.extract_features(speech)
    mel = features["mel_spectrogram"]
    energy = features["energy_rms"]
    f0 = features["pitch_f0"]
    num_frames = features["num_frames"]

    print(f"✓ Frames visuais gerados a 30 FPS: {num_frames} frames")
    print(f"✓ Shape do Log-Mel Spectrogram: {mel.shape} (Esperado: [{num_frames}, 80])")
    assert mel.shape == (num_frames, 80), "Dimensão do espectrograma Mel incompatível."
    assert energy.shape == (num_frames,), "Dimensão do envelope de energia incompatível."
    assert f0.shape == (num_frames,), "Dimensão de pitch F0 incompatível."

    # 3. Validação de faixas de valores
    assert not np.isnan(mel).any(), "Valores NaN encontrados no Mel-spectrogram."
    assert np.all(energy >= 0.0), "Energia não pode ser negativa."
    print(f"✓ Média de energia RMS: {np.mean(energy):.4f}")
    print(f"✓ Pitch F0 medido (min/médio/max): {np.min(f0):.1f}Hz / {np.mean(f0[f0 > 0]):.1f}Hz / {np.max(f0):.1f}Hz")
    print("--> Teste de áudio concluído com SUCESSO!\n")


if __name__ == "__main__":
    test_audio_pipeline()
