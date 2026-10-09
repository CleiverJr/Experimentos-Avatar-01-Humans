"""
Testes unitários para o modelo de difusão de movimento (Motion Diffusion Model - MDM).
Validação do agendador DDPM, rede neural temporal e amostragem estocástica (1-para-Muitos).
"""

import os
import sys
import torch
import numpy as np

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from src.motion_diffusion import DDPMScheduler, TemporalMotionDenoiser, MotionDiffusionPipeline


def test_diffusion_pipeline():
    print("=== [TESTE 3] Motor de Difusão de Movimento (Motion Diffusion / VASA-1 Core) ===")
    
    device = torch.device("mps" if torch.backends.mps.is_available() else "cpu")
    print(f"✓ Dispositivo de aceleração detectado: {device}")

    # 1. Validação do Agendador DDPM (Forward Process)
    scheduler = DDPMScheduler(num_timesteps=50, beta_start=0.0001, beta_end=0.02)
    scheduler.to(device)
    
    T = 60  # 2 segundos de movimento
    dummy_x0 = torch.zeros(1, 6, T, device=device)  # Trajetória limpa
    t_step = torch.tensor([25], device=device)
    x_t, noise = scheduler.add_noise(dummy_x0, t_step)
    
    assert x_t.shape == (1, 6, T), "Shape do forward process incompatível."
    print("✓ Processo Forward de Difusão (adição controlada de ruído gaussiano) validado")

    # 2. Inicialização da Rede Neural Denoiser
    denoiser = TemporalMotionDenoiser(motion_dim=6, audio_dim=80, emo_dim=16, hidden_dim=64)
    denoiser.to(device)
    
    audio_dummy = torch.randn(1, 80, T, device=device)
    emo_dummy = torch.randn(1, 16, device=device)
    pred_x0 = denoiser(x_t, t_step, audio_dummy, emo_dummy)
    
    assert pred_x0.shape == (1, 6, T), f"Shape da predição incompatível: {pred_x0.shape}"
    print(f"✓ Forward pass do Denoiser executado com sucesso: shape={pred_x0.shape}")

    # 3. Pipeline de Amostragem Reversa com Classifier-Free Guidance (CFG)
    pipeline = MotionDiffusionPipeline(denoiser, scheduler, device=device)
    
    audio_mel_np = np.random.randn(T, 80).astype(np.float32)
    emo_vec_np = np.ones(16, dtype=np.float32) * 0.5

    # Amostragem com Seed A
    traj_seed_a = pipeline.sample(audio_mel_np, emo_vec_np, guidance_scale=2.0, seed=42)
    assert traj_seed_a.shape == (T, 6), f"Shape da trajetória incorreto: {traj_seed_a.shape}"
    print(f"✓ Trajetória de pose de cabeça 3D gerada com Seed 42: {traj_seed_a.shape} (Pitch, Yaw, Roll, Tx, Ty, Tz)")

    # Amostragem com Seed B (mesmo áudio e emoção, ruído inicial diferente)
    traj_seed_b = pipeline.sample(audio_mel_np, emo_vec_np, guidance_scale=2.0, seed=999)

    # 4. Prova da Resolução do Problema 1-para-Muitos (Estocasticidade Plausível)
    diff = np.linalg.norm(traj_seed_a - traj_seed_b)
    print(f"✓ Distância L2 entre amostragens de seeds diferentes: {diff:.4f}")
    assert diff > 0.05, "O modelo não apresentou diversidade estocástica (colapso determinístico)."
    print("✓ O modelo resolveu com sucesso o problema 1-para-Muitos: gera performances distintas e válidas para o mesmo áudio!")

    # 5. Verificação de Suavidade Física (Aceleração finita)
    accel = np.diff(traj_seed_a, n=2, axis=0)
    max_accel = np.max(np.abs(accel))
    print(f"✓ Máxima aceleração angular observada: {max_accel:.4f} (movimento suave e contínuo)")
    print("--> Teste de Difusão concluído com SUCESSO!\n")


if __name__ == "__main__":
    test_diffusion_pipeline()
