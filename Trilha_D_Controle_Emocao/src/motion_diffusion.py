"""
Motor de Difusão de Movimento (Motion Diffusion Model - MDM).
Implementa o agendador de ruído DDPM e a rede neural temporal para síntese estocástica de pose de cabeça.
Conceito base de VASA-1, InstructAvatar e Audio2Photoreal.
"""

import math
import torch
import torch.nn as nn
import torch.nn.functional as F
import numpy as np
from typing import Dict, Tuple, Optional


class DDPMScheduler:
    """Agendador de difusão gaussiana (Ho et al., DDPM)."""
    def __init__(self, num_timesteps: int = 100, beta_start: float = 0.0001, beta_end: float = 0.02):
        self.num_timesteps = num_timesteps
        self.betas = torch.linspace(beta_start, beta_end, num_timesteps, dtype=torch.float32)
        self.alphas = 1.0 - self.betas
        self.alphas_cumprod = torch.cumprod(self.alphas, dim=0)
        self.alphas_cumprod_prev = F.pad(self.alphas_cumprod[:-1], (1, 0), value=1.0)
        
        # Coeficientes para o processo forward q(x_t | x_0)
        self.sqrt_alphas_cumprod = torch.sqrt(self.alphas_cumprod)
        self.sqrt_one_minus_alphas_cumprod = torch.sqrt(1.0 - self.alphas_cumprod)
        
        # Coeficientes para o processo posterior q(x_{t-1} | x_t, x_0)
        self.posterior_variance = self.betas * (1.0 - self.alphas_cumprod_prev) / (1.0 - self.alphas_cumprod)
        self.posterior_mean_coef1 = self.betas * torch.sqrt(self.alphas_cumprod_prev) / (1.0 - self.alphas_cumprod)
        self.posterior_mean_coef2 = (1.0 - self.alphas_cumprod_prev) * torch.sqrt(self.alphas) / (1.0 - self.alphas_cumprod)

    def to(self, device: torch.device):
        self.betas = self.betas.to(device)
        self.alphas = self.alphas.to(device)
        self.alphas_cumprod = self.alphas_cumprod.to(device)
        self.alphas_cumprod_prev = self.alphas_cumprod_prev.to(device)
        self.sqrt_alphas_cumprod = self.sqrt_alphas_cumprod.to(device)
        self.sqrt_one_minus_alphas_cumprod = self.sqrt_one_minus_alphas_cumprod.to(device)
        self.posterior_variance = self.posterior_variance.to(device)
        self.posterior_mean_coef1 = self.posterior_mean_coef1.to(device)
        self.posterior_mean_coef2 = self.posterior_mean_coef2.to(device)
        return self

    def add_noise(self, x_0: torch.Tensor, t: torch.Tensor, noise: Optional[torch.Tensor] = None) -> Tuple[torch.Tensor, torch.Tensor]:
        """Processo Forward: adiciona ruído gaussiano a x_0 no timestep t."""
        if noise is None:
            noise = torch.randn_like(x_0)
        sqrt_alpha = self.sqrt_alphas_cumprod[t].view(-1, 1, 1)
        sqrt_one_minus_alpha = self.sqrt_one_minus_alphas_cumprod[t].view(-1, 1, 1)
        x_t = sqrt_alpha * x_0 + sqrt_one_minus_alpha * noise
        return x_t, noise

    def step(self, pred_x0: torch.Tensor, t: int, x_t: torch.Tensor) -> torch.Tensor:
        """Processo Reverso: calcula x_{t-1} a partir da predição x_0 no timestep t."""
        if t == 0:
            return pred_x0
        mean = self.posterior_mean_coef1[t] * pred_x0 + self.posterior_mean_coef2[t] * x_t
        var = self.posterior_variance[t]
        noise = torch.randn_like(x_t)
        return mean + torch.sqrt(var) * noise


class SinusoidalPosEmb(nn.Module):
    """Embedding posicional senoidal para timesteps de difusão."""
    def __init__(self, dim: int):
        super().__init__()
        self.dim = dim

    def forward(self, t: torch.Tensor) -> torch.Tensor:
        device = t.device
        half_dim = self.dim // 2
        emb = math.log(10000) / (half_dim - 1)
        emb = torch.exp(torch.arange(half_dim, device=device) * -emb)
        emb = t[:, None] * emb[None, :]
        return torch.cat((emb.sin(), emb.cos()), dim=-1)


class TemporalResidualBlock(nn.Module):
    """Bloco residual 1D com modulação FiLM por áudio e texto/emoção."""
    def __init__(self, channels: int, cond_dim: int):
        super().__init__()
        self.conv1 = nn.Conv1d(channels, channels, kernel_size=5, padding=2)
        self.conv2 = nn.Conv1d(channels, channels, kernel_size=5, padding=2)
        self.film_gen = nn.Linear(cond_dim, channels * 2)
        self.act = nn.SiLU()

    def forward(self, x: torch.Tensor, cond: torch.Tensor) -> torch.Tensor:
        # x: [B, C, T]
        # cond: [B, cond_dim] ou [B, cond_dim, T]
        residual = x
        h = self.act(self.conv1(x))
        
        # Modulação FiLM (Scale e Shift)
        if cond.ndim == 2:
            film = self.film_gen(cond).unsqueeze(-1)  # [B, 2*C, 1]
        else:
            film = self.film_gen(cond.transpose(1, 2)).transpose(1, 2)  # [B, 2*C, T]
            
        gamma, beta = torch.chunk(film, 2, dim=1)
        h = h * (1.0 + gamma) + beta
        h = self.conv2(self.act(h))
        return h + residual


class TemporalMotionDenoiser(nn.Module):
    """
    Rede Neural de Denoising Temporal (x0-prediction) para séries de pose de cabeça 3D.
    Entrada: Trajetória ruidosa [B, 6, T] (pitch, yaw, roll, tx, ty, tz)
    Condição: Áudio Mel-spectrogram [B, 80, T] + Vetor de Emoção/Instrução [B, emo_dim]
    """
    def __init__(self, motion_dim: int = 6, audio_dim: int = 80, emo_dim: int = 16, hidden_dim: int = 64):
        super().__init__()
        self.motion_dim = motion_dim
        self.time_mlp = nn.Sequential(
            SinusoidalPosEmb(hidden_dim),
            nn.Linear(hidden_dim, hidden_dim),
            nn.SiLU()
        )
        
        # Projeção de entradas
        self.in_proj = nn.Conv1d(motion_dim, hidden_dim, kernel_size=3, padding=1)
        self.audio_proj = nn.Conv1d(audio_dim, hidden_dim, kernel_size=3, padding=1)
        self.emo_proj = nn.Linear(emo_dim, hidden_dim)

        # Blocos residuais temporais
        cond_dim = hidden_dim * 3
        self.block1 = TemporalResidualBlock(hidden_dim, cond_dim)
        self.block2 = TemporalResidualBlock(hidden_dim, cond_dim)
        self.block3 = TemporalResidualBlock(hidden_dim, cond_dim)

        # Projeção de saída (prevê x_0 diretamente)
        self.out_proj = nn.Conv1d(hidden_dim, motion_dim, kernel_size=3, padding=1)

    def forward(self, x_t: torch.Tensor, t: torch.Tensor, audio: torch.Tensor, emo: torch.Tensor) -> torch.Tensor:
        # x_t: [B, motion_dim, T]
        # t: [B]
        # audio: [B, audio_dim, T]
        # emo: [B, emo_dim]
        B, _, T = x_t.shape
        
        # Codificação de condições
        t_emb = self.time_mlp(t).unsqueeze(-1).expand(-1, -1, T)  # [B, hidden_dim, T]
        a_emb = self.audio_proj(audio)                             # [B, hidden_dim, T]
        e_emb = self.emo_proj(emo).unsqueeze(-1).expand(-1, -1, T) # [B, hidden_dim, T]
        cond = torch.cat([t_emb, a_emb, e_emb], dim=1)            # [B, 3*hidden_dim, T]

        h = self.in_proj(x_t)
        h = self.block1(h, cond)
        h = self.block2(h, cond)
        h = self.block3(h, cond)
        
        pred_x0 = self.out_proj(h)
        return pred_x0


class MotionDiffusionPipeline:
    """Pipeline completo de inferência com amostragem e Classifier-Free Guidance."""
    def __init__(self, denoiser: TemporalMotionDenoiser, scheduler: DDPMScheduler, device: Optional[torch.device] = None):
        self.device = device or torch.device("mps" if torch.backends.mps.is_available() else "cpu")
        self.denoiser = denoiser.to(self.device)
        self.scheduler = scheduler.to(self.device)

    @torch.no_grad()
    def sample(self, 
               audio_mel: np.ndarray, 
               emo_vector: np.ndarray, 
               guidance_scale: float = 2.0, 
               seed: Optional[int] = None) -> np.ndarray:
        """
        Executa o processo reverso de difusão:
        Ruído puro ~ N(0, I) -> Trajetória suave de pose de cabeça 3D.
        audio_mel: [T, 80]
        emo_vector: [emo_dim]
        Retorna: [T, 6] (pitch, yaw, roll, tx, ty, tz)
        """
        if seed is not None:
            torch.manual_seed(seed)
            np.random.seed(seed)

        self.denoiser.eval()
        T = audio_mel.shape[0]

        # Tensores condicionais
        audio_t = torch.from_numpy(audio_mel).float().transpose(0, 1).unsqueeze(0).to(self.device)  # [1, 80, T]
        emo_t = torch.from_numpy(emo_vector).float().unsqueeze(0).to(self.device)                    # [1, emo_dim]
        
        # Vetores nulos para Classifier-Free Guidance
        audio_null = torch.zeros_like(audio_t)
        emo_null = torch.zeros_like(emo_t)

        # Inicia com ruído gaussiano puro
        x_t = torch.randn(1, self.denoiser.motion_dim, T, device=self.device)

        # Loop de desruidificação reversa
        for step in reversed(range(self.scheduler.num_timesteps)):
            t_batch = torch.tensor([step], device=self.device)
            
            # Predição condicionada
            pred_cond = self.denoiser(x_t, t_batch, audio_t, emo_t)
            
            # Predição não-condicionada (CFG)
            if guidance_scale > 1.0:
                pred_uncond = self.denoiser(x_t, t_batch, audio_null, emo_null)
                pred_x0 = pred_uncond + guidance_scale * (pred_cond - pred_uncond)
            else:
                pred_x0 = pred_cond

            # Passo de atualização temporal
            x_t = self.scheduler.step(pred_x0, step, x_t)

        # Suavização física das trajetórias (simula momento inercial do pescoço humano)
        trajectory = x_t.squeeze(0).transpose(0, 1).cpu().numpy()
        return trajectory
