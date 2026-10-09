"""
Renderizador Neural: De Trajetória (.npz) para Vídeo MP4 (VASA-1)
=================================================================
Este script executa a segunda metade do pipeline:
1. Carrega a trajetória temporal (.npz) gerada pelo vasa1_gerador_dinamica.py
2. Carrega as features de aparência (avatar_state.pkl)
3. Deforma o volume 3D (WarpF3D) e sintetiza os pixels foto-realistas (DecodeF3D) usando GPU MPS
4. Monta o vídeo final MP4 com o áudio sincronizado via FFmpeg.
"""

import os
import sys
import argparse
import subprocess
import numpy as np

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(REPO_ROOT, "referencia"))

from ditto_lab import Renderer, Lab


def renderizar_vasa1(
    npz_path: str,
    portrait_path: str,
    audio_path: str,
    out_mp4: str,
    num_frames: int = None,
    device: str = "mps"
):
    print("=" * 70)
    print("🎥 RENDERIZANDO VÍDEO FINAL DO VASA-1 COM ACELERAÇÃO NEURAL")
    print("=" * 70)
    
    avatar_pkl = os.path.join(os.path.dirname(npz_path), "avatar_state.pkl")
    out_frames_dir = os.path.join(os.path.dirname(npz_path), "frames_vasa1")
    os.makedirs(out_frames_dir, exist_ok=True)
    
    # 1. Garantir que avatar_state.pkl existe
    if not os.path.exists(avatar_pkl):
        print("\n[1/3] Extraindo volume 3D de aparência da foto neutra...")
        lab = Lab()
        lab._setup(portrait_path, emo=None)
        lab.save_avatar_state(avatar_pkl)
    else:
        print("\n[1/3] Volume 3D de aparência já pronto.")
        
    # 2. Renderizar os frames neurais
    m = np.load(npz_path, allow_pickle=True)
    total_frames = len(m["x_d"])
    end_frame = total_frames if num_frames is None else min(num_frames, total_frames)
    
    print(f"\n[2/3] Renderizando {end_frame} frames usando dispositivo: [{device.upper()}]...")
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
    
    # 3. Compilar em MP4 com áudio usando FFmpeg
    print(f"\n[3/3] Montando vídeo MP4 com áudio sincronizado...")
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
        "-pix_fmt", "yuv420p",
        "-c:a", "aac",
        "-b:a", "192k",
        "-shortest",
        out_mp4
    ]
    
    subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    print(f"\n🎬 VÍDEO FINAL GERADO COM SUCESSO:")
    print(f"   -> {out_mp4}")
    print(f"   (Duração: {duration:.2f}s | {end_frame} frames | Resolução: 1024x1024 | 25 FPS)")
    print("=" * 70)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--frames", type=int, default=None, help="Número de frames para renderizar (ex: 75 para ~3s rápidos)")
    parser.add_argument("--device", type=str, default="mps", choices=["mps", "cpu"])
    args = parser.parse_args()
    
    dir_path = os.path.dirname(os.path.abspath(__file__))
    npz = os.path.join(dir_path, "trajetoria_vasa1.npz")
    audio = os.path.join(REPO_ROOT, "data", "vasa_speech.wav")
    portrait = os.path.join(REPO_ROOT, "data", "vasa_portrait.jpg")
    saida = os.path.join(dir_path, "video_vasa1.mp4")
    
    renderizar_vasa1(
        npz_path=npz,
        portrait_path=portrait,
        audio_path=audio,
        out_mp4=saida,
        num_frames=args.frames,
        device=args.device
    )
