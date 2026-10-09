"""
Renderizador Neural: Motion Diffusion Model (MDM / DDPM) — Vídeo Demonstrativo MP4
===================================================================================
Referências:
- Paper: "Human Motion Diffusion Model" (Guy Tevet et al., ICLR 2023)
  * Link oficial: https://arxiv.org/abs/2209.14916
  * GitHub: https://github.com/GuyTevet/motion-diffusion-model
  * Arquivo local: Artigos/MDM_Motion_Diffusion.pdf
- Paper: "Denoising Diffusion Probabilistic Models" (Jonathan Ho et al., NeurIPS 2020)
  * Link oficial: https://arxiv.org/abs/2006.11239
  * GitHub: https://github.com/hojonathanho/diffusion
  * Arquivo local: Artigos/DDPM.pdf

Este script renderiza o vídeo final foto-realista gerado via difusão estocástica:
1. Carrega a trajetória cinemática (.npz) sintetizada pelo mdm_difusao_cinematica.py
2. Reutiliza as features neurais de aparência (avatar_state.pkl)
3. Deforma o volume 3D canônico e decodifica pixels foto-realistas via GPU MPS
4. Aplica legendas e telemetria dos conceitos fundamentais do MDM:
   - Denoising Schedule & Predição Direta de x̂_0
   - Resolução da ambiguidade "1-para-Muitos" (Sem colapso para a média estática)
   - Sincronia fonética labial estrita preservada
5. Muxa o áudio original em MP4 via FFmpeg.
"""

import os
import sys
import shutil
import argparse
import subprocess
import numpy as np
from PIL import Image, ImageDraw, ImageFont

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(REPO_ROOT, "referencia"))

from ditto_lab import Renderer, Lab


def aplicar_overlay_mdm(frame_path: str, frame_idx: int, total_frames: int, font_title, font_sub):
    """Insere barras informativas com métricas e telemetria do MDM em tempo real."""
    img = Image.open(frame_path).convert("RGB")
    W, H = img.size
    draw = ImageDraw.Draw(img, "RGBA")
    
    # 1. Barra Superior de Contexto
    header_h = 75
    draw.rectangle([(0, 0), (W, header_h)], fill=(15, 23, 42, 220))
    draw.text((25, 12), "Motion Diffusion Model (MDM / DDPM) — Tevet et al. (ICLR 2023)", fill=(56, 189, 248), font=font_title)
    
    # Legenda da fala dividida em 2 momentos
    if frame_idx < 145:
        # Primeiro momento: Explicando o problema da regressão à média
        draw.text((25, 42), "\"Modelos de regressão colapsam para a média estática...\"", fill=(248, 113, 113), font=font_sub)
    else:
        # Segundo momento: A solução da difusão de movimento
        draw.text((25, 42), "\"Com o MDM, a estocasticidade gera infinitas trajetórias vivas e naturais!\"", fill=(74, 222, 128), font=font_sub)
        
    # 2. Barra Inferior de Telemetria do MDM
    footer_h = 90
    y_footer = H - footer_h
    draw.rectangle([(0, y_footer), (W, H)], fill=(15, 23, 42, 235))
    
    # Badges conceituais
    if frame_idx < 145:
        draw.rectangle([(25, y_footer + 12), (370, y_footer + 42)], fill=(225, 29, 72, 230))
        draw.text((35, y_footer + 16), "DILEMA: REGRESSÃO À MÉDIA", fill=(255, 255, 255), font=font_sub)
        draw.text((390, y_footer + 16), "Modelos MSE colapsam poses válidas para uma média paralisada", fill=(254, 205, 211), font=font_sub)
        draw.text((25, y_footer + 54), "Problema 1-para-Muitos: uma frase falada admite infinitas poses de cabeça plausíveis", fill=(148, 163, 184), font=font_sub)
    else:
        draw.rectangle([(25, y_footer + 12), (370, y_footer + 42)], fill=(16, 185, 129, 230))
        draw.text((35, y_footer + 16), "SOLUÇÃO: DIFUSÃO ESTOCÁSTICA", fill=(255, 255, 255), font=font_sub)
        draw.text((390, y_footer + 16), "Amostragem Reversa DDPM: Cada ruído inicial gera um movimento vivo", fill=(209, 250, 229), font=font_sub)
        draw.text((25, y_footer + 54), "Predição Direta x̂_0 + Perda de Velocidade Cinemática (||Δx_0 - Δx̂_0||²)", fill=(148, 163, 184), font=font_sub)
        
    img.save(frame_path, quality=95)


def renderizar_mdm(
    npz_path: str,
    portrait_path: str,
    audio_path: str,
    out_mp4: str,
    num_frames: int = None,
    device: str = "mps"
):
    print("=" * 80)
    print("🎥 RENDERIZANDO VÍDEO FINAL DO MDM (MOTION DIFFUSION) VIA GPU MPS")
    print("=" * 80)
    
    dir_07 = os.path.dirname(npz_path)
    avatar_pkl = os.path.join(dir_07, "avatar_state.pkl")
    out_frames_dir = os.path.join(dir_07, "frames_mdm")
    os.makedirs(out_frames_dir, exist_ok=True)
    
    # 1. Reutilizar volume 3D pré-calculado para economizar tempo
    avatar_pkl_ref = os.path.join(REPO_ROOT, "Implementacoes", "05_audio2photoreal_dialogue", "avatar_state.pkl")
    if not os.path.exists(avatar_pkl) and os.path.exists(avatar_pkl_ref):
        print("\n[1/4] Reutilizando volume 3D de aparência pré-calculado...")
        shutil.copy2(avatar_pkl_ref, avatar_pkl)
    elif not os.path.exists(avatar_pkl):
        print("\n[1/4] Extraindo volume 3D de aparência...")
        lab = Lab()
        lab._setup(portrait_path, emo=None)
        lab.save_avatar_state(avatar_pkl)
    else:
        print("\n[1/4] Volume 3D de aparência pronto.")
        
    # 2. Renderizar os frames neurais
    m = np.load(npz_path, allow_pickle=True)
    total_frames = len(m["x_d"])
    end_frame = total_frames if num_frames is None else min(num_frames, total_frames)
    
    print(f"\n[2/4] Renderizando {end_frame} frames usando aceleração: [{device.upper()}]...")
    renderer = Renderer(device=device, bf16=True)
    renderer.render(
        avatar_pkl=avatar_pkl,
        motion_npz=npz_path,
        out_dir=out_frames_dir,
        start=0,
        end=end_frame,
        full=True
    )
    print("  ✅ Frames neurais sintetizados com sucesso!")
    
    # 3. Aplicar legendas e telemetria da difusão
    print("\n[3/4] Inserindo cartela com telemetria do MDM...")
    try:
        font_title = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 22)
        font_sub = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 17)
    except Exception:
        font_title = font_sub = ImageFont.load_default()
        
    for i in range(end_frame):
        frame_file = os.path.join(out_frames_dir, f"{i:05d}.jpg")
        if os.path.exists(frame_file):
            aplicar_overlay_mdm(frame_file, i, end_frame, font_title, font_sub)
            
    # 4. Compilar em MP4 com áudio sincronizado via FFmpeg
    print("\n[4/4] Montando vídeo MP4 com áudio sincronizado via FFmpeg...")
    duration = end_frame / 25.0
    
    cmd = [
        "ffmpeg", "-y",
        "-framerate", "25",
        "-i", os.path.join(out_frames_dir, "%05d.jpg"),
        "-ss", "0",
        "-t", str(duration),
        "-i", audio_path,
        "-c:v", "libx264",
        "-crf", "18",
        "-preset", "fast",
        "-pix_fmt", "yuv420p",
        "-c:a", "aac",
        "-b:a", "192k",
        "-shortest",
        out_mp4
    ]
    subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    
    # Limpar frames temporários
    shutil.rmtree(out_frames_dir, ignore_errors=True)
    
    print("\n" + "=" * 80)
    print(f"🎬 VÍDEO FINAL MDM GERADO COM SUCESSO:")
    print(f"   -> {out_mp4}")
    print(f"   (Duração: {duration:.2f}s | {end_frame} frames | Resolução: 1024x1024 | 25 FPS)")
    print("=" * 80)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--frames", type=int, default=None, help="Número de frames para renderizar")
    parser.add_argument("--device", type=str, default="mps", choices=["mps", "cpu"])
    args = parser.parse_args()
    
    dir_path = os.path.dirname(os.path.abspath(__file__))
    npz = os.path.join(dir_path, "trajetoria_mdm.npz")
    audio = os.path.join(REPO_ROOT, "data", "mdm_speech.wav")
    portrait = os.path.join(REPO_ROOT, "data", "vasa_portrait.jpg")
    saida = os.path.join(dir_path, "video_mdm.mp4")
    
    renderizar_mdm(
        npz_path=npz,
        portrait_path=portrait,
        audio_path=audio,
        out_mp4=saida,
        num_frames=args.frames,
        device=args.device
    )
