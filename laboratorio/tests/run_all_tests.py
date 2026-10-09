"""
Suíte unificada de testes e demonstração ponta-a-ponta (End-to-End) da Trilha D.
Executa os testes e gera um pacote de animação exportável para as Trilhas B (Arthur) e C (Fernando).
"""

import os
import sys
import time
import numpy as np

# Garante que tanto a raiz do projeto quanto a pasta tests estejam no path
root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
tests_dir = os.path.abspath(os.path.dirname(__file__))
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)
if tests_dir not in sys.path:
    sys.path.insert(0, tests_dir)

try:
    from tests.test_audio import test_audio_pipeline
    from tests.test_facs import test_facs_pipeline
    from tests.test_diffusion import test_diffusion_pipeline
    from tests.test_instruct import test_instruct_pipeline
except ModuleNotFoundError:
    from test_audio import test_audio_pipeline
    from test_facs import test_facs_pipeline
    from test_diffusion import test_diffusion_pipeline
    from test_instruct import test_instruct_pipeline

from src.audio_processor import AudioProcessor
from src.action_units import ActionUnitsSystem
from src.motion_diffusion import DDPMScheduler, TemporalMotionDenoiser, MotionDiffusionPipeline
from src.instruct_parser import InstructParser
from src.exporter import MotionExporter


def run_end_to_end_demo():
    print("=" * 70)
    print("🎬 EXECUÇÃO PONTA-A-PONTA: ÁUDIO + TEXTO -> MOVIMENTO 3D COMPLETO")
    print("=" * 70)

    start_time = time.time()
    output_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "output"))
    os.makedirs(output_dir, exist_ok=True)

    # 1. Configurações
    fps = 30.0
    duration_sec = 3.0
    total_frames = int(fps * duration_sec)
    prompt = "Fale com muita alegria e surpresa, olhando levemente para a esquerda"

    print(f"\n1. Entrada Textual do Usuário:")
    print(f"   -> \"{prompt}\"")

    # 2. Interpretação Semântica (InstructAvatar / OmniHuman)
    parser = InstructParser(embedding_dim=16)
    parsed_instruct = parser.parse_instruction(prompt)
    emo_weights = parsed_instruct["emotion_weights"]
    intensity = parsed_instruct["intensity"]
    head_bias = parsed_instruct["head_bias"]
    cond_vec = parsed_instruct["conditioning_vector"]
    print(f"   ✓ Emoções inferidas: {emo_weights}")
    print(f"   ✓ Fator de intensidade: {intensity:.2f}")
    print(f"   ✓ Viés espacial: Yaw={head_bias['yaw_deg']}°")

    # 3. Processamento Acústico (VASA-1 / Audio2Photoreal Audio Frontend)
    print(f"\n2. Processamento do Sinal de Áudio ({duration_sec}s):")
    audio_proc = AudioProcessor(sample_rate=16000, n_mels=80, fps=fps)
    speech = audio_proc.generate_synthetic_speech(duration_sec=duration_sec, base_f0=140.0)
    features = audio_proc.extract_features(speech)
    mel = features["mel_spectrogram"]  # [T, 80]
    energy = features["energy_rms"]    # [T]
    print(f"   ✓ Espectrograma Mel extraído: {mel.shape} (80 canais por frame)")
    print(f"   ✓ Energia acústica RMS mapeada para {len(energy)} frames")

    # 4. Modelação Facial Anatômica (AUHead & FLAME)
    print(f"\n3. Síntese de Action Units e Parâmetros FLAME:")
    facs = ActionUnitsSystem(num_flame_exp=50)
    blended_au = facs.blend_emotions(emo_weights)
    base_au_seq = np.tile(blended_au, (total_frames, 1))
    
    # Modulação de fala e piscadas
    modulated_au = facs.modulate_with_speech(base_au_seq, energy, blink_interval=45)
    
    # Conversão para FLAME
    flame_trajectories = []
    flame_exp_matrix = np.zeros((total_frames, 50), dtype=np.float32)
    flame_jaw_matrix = np.zeros((total_frames, 3), dtype=np.float32)
    for t in range(total_frames):
        flame_frame = facs.au_to_flame(modulated_au[t])
        flame_trajectories.append(flame_frame)
        flame_exp_matrix[t] = flame_frame["expression_coefficients"]
        flame_jaw_matrix[t] = flame_frame["jaw_rotation"]

    print(f"   ✓ Action Units FACS moduladas: {modulated_au.shape} (inclui sincronia labial e piscadas)")
    print(f"   ✓ Coeficientes de expressão FLAME calculados: {flame_exp_matrix.shape}")

    # 5. Difusão de Movimento 3D da Cabeça (Motion Diffusion Models)
    print(f"\n4. Difusão Estocástica de Trajetória da Cabeça (Pose 3D):")
    scheduler = DDPMScheduler(num_timesteps=50)
    denoiser = TemporalMotionDenoiser(motion_dim=6, audio_dim=80, emo_dim=16, hidden_dim=64)
    pipeline = MotionDiffusionPipeline(denoiser, scheduler)
    
    # Amostragem reversa
    head_trajectory = pipeline.sample(mel, cond_vec, guidance_scale=2.0, seed=42)
    
    # Aplicação do viés do prompt (ex: virar à esquerda)
    head_trajectory[:, 1] += head_bias["yaw_deg"]  # Adiciona viés de Yaw
    print(f"   ✓ Trajetória 3D desruidificada: {head_trajectory.shape} (Pitch, Yaw, Roll, Tx, Ty, Tz)")

    # 6. Exportação Padronizada para as Trilhas B (Arthur) e C (Fernando)
    print(f"\n5. Empacotamento e Exportação Inter-Trilhas:")
    exporter = MotionExporter(fps=fps)
    metadata = {
        "user_prompt": prompt,
        "emotions": emo_weights,
        "intensity": intensity,
        "audio_duration_sec": duration_sec,
        "generator": "Trilha D - Motion Diffusion & FACS Pipeline"
    }

    # Salva JSON
    json_path = os.path.join(output_dir, "animacao_demonstracao.json")
    package = exporter.assemble_animation_package(head_trajectory, modulated_au, flame_trajectories, metadata)
    exporter.save_json(package, json_path)
    print(f"   ✓ Arquivo JSON gerado: {json_path}")

    # Salva NPZ
    npz_path = os.path.join(output_dir, "animacao_demonstracao.npz")
    exporter.save_npz(head_trajectory, modulated_au, flame_exp_matrix, flame_jaw_matrix, npz_path)
    print(f"   ✓ Arquivo binário compactado NPZ gerado: {npz_path}")

    elapsed = time.time() - start_time
    print("\n" + "=" * 70)
    print(f"✨ DEMONSTRAÇÃO CONCLUÍDA COM SUCESSO EM {elapsed:.2f} SEGUNDOS!")
    print(f"   Total de frames renderizáveis: {total_frames} frames a {fps} FPS")
    print(f"   Dados prontos para o Arthur (Trilha B - Malha) e Fernando (Trilha C - 3DGS)")
    print("=" * 70 + "\n")


def main():
    print("\n" + "#" * 70)
    print("  INICIANDO BATERIA DE TESTES DA TRILHA D (CONTROLE, EMOÇÃO E COMPORTAMENTO)")
    print("#" * 70 + "\n")

    # Executa testes unitários individuais
    test_audio_pipeline()
    test_facs_pipeline()
    test_diffusion_pipeline()
    test_instruct_pipeline()

    # Executa a demonstração integrada completa
    run_end_to_end_demo()


if __name__ == "__main__":
    main()
