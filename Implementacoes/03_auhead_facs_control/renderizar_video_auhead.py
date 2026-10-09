"""
Renderizador Neural: De Trajetória FACS (.npz) para Vídeo MP4 (AUHead)
=======================================================================
Este script executa a renderização do avatar foto-realista sob controle de Action Units:
1. Carrega a trajetória temporal (.npz) com modulações FACS gerada pelo auhead_facs_mapeador.py
2. Carrega ou reutiliza as features de aparência (avatar_state.pkl)
3. Executa a deformação do volume 3D (WarpF3D) e decodificação neural (DecodeF3D) via GPU MPS
4. Monta o vídeo final MP4 com o áudio narrado sincronizado via FFmpeg.
"""

import os
import sys
import shutil
import argparse
import subprocess
import numpy as np

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(REPO_ROOT, "referencia"))

from ditto_lab import Renderer, Lab


def renderizar_auhead(
    npz_path: str,
    portrait_path: str,
    audio_path: str,
    out_mp4: str,
    num_frames: int = None,
    device: str = "mps"
):
    print("=" * 70)
    print("🎥 RENDERIZANDO VÍDEO FINAL DO AUHead (FACS) COM ACELERAÇÃO NEURAL")
    print("=" * 70)
    
    dir_03 = os.path.dirname(npz_path)
    avatar_pkl = os.path.join(dir_03, "avatar_state.pkl")
    out_frames_dir = os.path.join(dir_03, "frames_auhead")
    os.makedirs(out_frames_dir, exist_ok=True)
    
    # 1. Reutilizar avatar_state.pkl do módulo 02 se existir para evitar recálculo
    avatar_pkl_02 = os.path.join(REPO_ROOT, "Implementacoes", "02_vasa1_audio_motion", "avatar_state.pkl")
    if not os.path.exists(avatar_pkl) and os.path.exists(avatar_pkl_02):
        print("\n[1/3] Reutilizando volume 3D de aparência pré-calculado do módulo 02...")
        shutil.copy2(avatar_pkl_02, avatar_pkl)
    elif not os.path.exists(avatar_pkl):
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
    print(f"\n[3/3] Montando vídeo MP4 com áudio sincronizado via FFmpeg...")
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
    print(f"\n🎬 VÍDEO FINAL AUHead GERADO COM SUCESSO:")
    print(f"   -> {out_mp4}")
    print(f"   (Duração: {duration:.2f}s | {end_frame} frames | Resolução: 1024x1024 | 25 FPS)")
    print("=" * 70)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--frames", type=int, default=None, help="Número de frames para renderizar (ex: 100 para teste rápido)")
    parser.add_argument("--device", type=str, default="mps", choices=["mps", "cpu"])
    args = parser.parse_args()
    
    dir_path = os.path.dirname(os.path.abspath(__file__))
    npz = os.path.join(dir_path, "trajetoria_auhead.npz")
    audio = os.path.join(REPO_ROOT, "data", "auhead_speech.wav")
    portrait = os.path.join(REPO_ROOT, "data", "vasa_portrait.jpg")
    saida = os.path.join(dir_path, "video_auhead.mp4")
    
    renderizar_auhead(
        npz_path=npz,
        portrait_path=portrait,
        audio_path=audio,
        out_mp4=saida,
        num_frames=args.frames,
        device=args.device
    )
