"""
Renderizador Neural: InstructAvatar — Vídeo MP4 com Instrução de Direção Cênica
================================================================================
Este script executa a renderização do avatar foto-realista controlado por texto:
1. Carrega a trajetória temporal (.npz) gerada pelo instruct_avatar_parser.py
2. Reutiliza as features de aparência (avatar_state.pkl)
3. Deforma o volume 3D (WarpF3D) e decodifica pixels foto-realistas (DecodeF3D) via GPU MPS
4. Aplica um cabeçalho estético indicando a instrução textual recebida
5. Muxa o áudio original em MP4 sincronizado via FFmpeg.
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


def aplicar_overlay_instrucao(frame_path: str, instruction_text: str, font_title, font_sub):
    """Insere barra superior e inferior com os dados do comando cênico recebido."""
    img = Image.open(frame_path).convert("RGB")
    W, H = img.size
    draw = ImageDraw.Draw(img, "RGBA")
    
    # 1. Barra de Cabeçalho Superior
    header_h = 70
    draw.rectangle([(0, 0), (W, header_h)], fill=(15, 23, 42, 220))
    draw.text((25, 12), "InstructAvatar (AAAI 2025) — Controle Cênico por Texto", fill=(56, 189, 248), font=font_title)
    draw.text((25, 40), f"Comando: \"{instruction_text}\"", fill=(226, 232, 240), font=font_sub)
    
    # 2. Barra de Status Inferior
    footer_h = 50
    y_footer = H - footer_h
    draw.rectangle([(0, y_footer), (W, H)], fill=(15, 23, 42, 210))
    draw.text((25, y_footer + 15), "Two-Branch Diffusion: Sincronia Labial (HuBERT) + Atuação Cênica (CLIP)", fill=(148, 163, 184), font=font_sub)
    
    img.save(frame_path, quality=95)


def renderizar_instruct(
    npz_path: str,
    portrait_path: str,
    audio_path: str,
    out_mp4: str,
    instruction_text: str = "Fale com entusiasmo e expressividade calorosa, inclinando a cabeça para a direita e sorrindo com os olhos",
    num_frames: int = None,
    device: str = "mps"
):
    print("=" * 75)
    print("🎥 RENDERIZANDO VÍDEO FINAL DO InstructAvatar (AAAI 2025) VIA GPU NEURAL")
    print("=" * 75)
    
    dir_04 = os.path.dirname(npz_path)
    avatar_pkl = os.path.join(dir_04, "avatar_state.pkl")
    out_frames_dir = os.path.join(dir_04, "frames_instruct")
    os.makedirs(out_frames_dir, exist_ok=True)
    
    # 1. Reutilizar avatar_state.pkl dos módulos anteriores
    avatar_pkl_ref = os.path.join(REPO_ROOT, "Implementacoes", "03_auhead_facs_control", "avatar_state.pkl")
    if not os.path.exists(avatar_pkl) and os.path.exists(avatar_pkl_ref):
        print("\n[1/4] Reutilizando volume 3D de aparência pré-calculado...")
        shutil.copy2(avatar_pkl_ref, avatar_pkl)
    elif not os.path.exists(avatar_pkl):
        print("\n[1/4] Extraindo volume 3D de aparência da foto estática...")
        lab = Lab()
        lab._setup(portrait_path, emo=None)
        lab.save_avatar_state(avatar_pkl)
    else:
        print("\n[1/4] Volume 3D de aparência já carregado.")
        
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
    
    # 3. Aplicar legendas estéticas da instrução nos frames
    print("\n[3/4] Inserindo cartela cênica com a instrução do diretor...")
    try:
        font_title = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 22)
        font_sub = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 17)
    except Exception:
        font_title = font_sub = ImageFont.load_default()
        
    for i in range(end_frame):
        frame_file = os.path.join(out_frames_dir, f"{i:05d}.jpg")
        if os.path.exists(frame_file):
            aplicar_overlay_instrucao(frame_file, instruction_text, font_title, font_sub)
            
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
    
    print("\n" + "=" * 75)
    print(f"🎬 VÍDEO FINAL DO InstructAvatar GERADO COM SUCESSO:")
    print(f"   -> {out_mp4}")
    print(f"   (Duração: {duration:.2f}s | {end_frame} frames | Resolução: 1024x1024 | 25 FPS)")
    print("=" * 75)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--frames", type=int, default=None, help="Número de frames para renderizar")
    parser.add_argument("--device", type=str, default="mps", choices=["mps", "cpu"])
    parser.add_argument("--instruction", type=str, default="Fale com entusiasmo e expressividade calorosa, inclinando a cabeça para a direita e sorrindo com os olhos")
    args = parser.parse_args()
    
    dir_path = os.path.dirname(os.path.abspath(__file__))
    npz = os.path.join(dir_path, "trajetoria_instruct.npz")
    audio = os.path.join(REPO_ROOT, "data", "instruct_speech.wav")
    portrait = os.path.join(REPO_ROOT, "data", "vasa_portrait.jpg")
    saida = os.path.join(dir_path, "video_instruct.mp4")
    
    renderizar_instruct(
        npz_path=npz,
        portrait_path=portrait,
        audio_path=audio,
        out_mp4=saida,
        instruction_text=args.instruction,
        num_frames=args.frames,
        device=args.device
    )
