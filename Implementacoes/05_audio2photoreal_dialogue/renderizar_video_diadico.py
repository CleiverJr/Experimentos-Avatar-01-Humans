"""
Renderizador Neural: Audio2Photoreal — Vídeo MP4 de Diálogo Diádico com Escuta Ativa
======================================================================================
Este script renderiza o vídeo da interação conversacional de duas vias:
1. Carrega a trajetória temporal (.npz) gerada pelo audio2photoreal_diadico.py
2. Reutiliza o volume de aparência (avatar_state.pkl)
3. Deforma e sintetiza os pixels foto-realistas via GPU MPS
4. Aplica legendas e badges dinâmicos de estado conversacional:
   - [ESCUTA ATIVA / BACKCHANNELING]: Lábios fechados e acenos de concordância
   - [TRANSIÇÃO DE TURNO / TURN-TAKING]: Preparação da resposta
   - [FALA ATIVA / SPEAKER]: Sincronia labial plena
5. Muxa o áudio do diálogo diádico em MP4 via FFmpeg.
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


def aplicar_overlay_diadico(frame_path: str, frame_idx: int, font_title, font_sub):
    """Insere barras de diálogo e badges indicando o papel conversacional em cada instante."""
    img = Image.open(frame_path).convert("RGB")
    W, H = img.size
    draw = ImageDraw.Draw(img, "RGBA")
    
    # 1. Barra Superior de Contexto
    header_h = 75
    draw.rectangle([(0, 0), (W, header_h)], fill=(15, 23, 42, 220))
    draw.text((25, 12), "Audio2Photoreal (CVPR 2024 / Meta) — Dinâmica Diádica", fill=(56, 189, 248), font=font_title)
    
    # 2. Status e Falas Conforme a Fase
    footer_h = 85
    y_footer = H - footer_h
    
    if frame_idx < 154:
        # Fase 1: Interlocutora falando / Avatar escutando
        draw.text((25, 42), "Interlocutora: \"Olá! Você conseguiu implementar o controle facial...?\"", fill=(244, 114, 182), font=font_sub)
        
        # Badge Inferior de Escuta Ativa
        draw.rectangle([(0, y_footer), (W, H)], fill=(15, 23, 42, 230))
        draw.rectangle([(25, y_footer + 12), (320, y_footer + 42)], fill=(13, 148, 136, 230))
        draw.text((35, y_footer + 16), "MODO: ESCUTA ATIVA", fill=(255, 255, 255), font=font_sub)
        draw.text((340, y_footer + 16), "Acenos afirmativos (Backchanneling) & Lábios Fechados", fill=(204, 251, 241), font=font_sub)
        draw.text((25, y_footer + 52), "Sem congelar a cabeça — postura empática e atenta", fill=(148, 163, 184), font=font_sub)
        
    elif 154 <= frame_idx < 174:
        # Fase 2: Turn-Taking
        draw.text((25, 42), "Transição de Turno (Silêncio respiratório de assimilação)", fill=(203, 213, 225), font=font_sub)
        
        draw.rectangle([(0, y_footer), (W, H)], fill=(30, 41, 59, 230))
        draw.rectangle([(25, y_footer + 12), (360, y_footer + 42)], fill=(217, 119, 6, 230))
        draw.text((35, y_footer + 16), "TRANSIÇÃO (TURN-TAKING)", fill=(255, 255, 255), font=font_sub)
        draw.text((380, y_footer + 16), "Avatar assimila a pergunta e prepara a fala", fill=(254, 243, 199), font=font_sub)
        draw.text((25, y_footer + 52), "Elevação sutil de queixo e ativação de VAD", fill=(203, 213, 225), font=font_sub)
        
    else:
        # Fase 3: Avatar falando
        draw.text((25, 42), "Avatar: \"Sim! Implementamos o VASA-1, o AUHead e o InstructAvatar.\"", fill=(74, 222, 128), font=font_sub)
        
        draw.rectangle([(0, y_footer), (W, H)], fill=(15, 23, 42, 230))
        draw.rectangle([(25, y_footer + 12), (300, y_footer + 42)], fill=(37, 99, 235, 230))
        draw.text((35, y_footer + 16), "MODO: FALA ATIVA", fill=(255, 255, 255), font=font_sub)
        draw.text((320, y_footer + 16), "Sincronia labial total (HuBERT) & Articulação fonética", fill=(191, 219, 254), font=font_sub)
        draw.text((25, y_footer + 52), "Movimento motor assertivo acompanhando a prosódia", fill=(148, 163, 184), font=font_sub)
        
    img.save(frame_path, quality=95)


def renderizar_diadico(
    npz_path: str,
    portrait_path: str,
    audio_path: str,
    out_mp4: str,
    num_frames: int = None,
    device: str = "mps"
):
    print("=" * 75)
    print("🎥 RENDERIZANDO VÍDEO CONVERSACIONAL DO Audio2Photoreal VIA GPU MPS")
    print("=" * 75)
    
    dir_05 = os.path.dirname(npz_path)
    avatar_pkl = os.path.join(dir_05, "avatar_state.pkl")
    out_frames_dir = os.path.join(dir_05, "frames_diadico")
    os.makedirs(out_frames_dir, exist_ok=True)
    
    # 1. Reutilizar avatar_state.pkl
    avatar_pkl_ref = os.path.join(REPO_ROOT, "Implementacoes", "04_instruct_avatar_nlp", "avatar_state.pkl")
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
    
    # 3. Aplicar legendas estéticas da interação diádica
    print("\n[3/4] Inserindo cartela conversacional com estados de escuta e fala...")
    try:
        font_title = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 22)
        font_sub = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 17)
    except Exception:
        font_title = font_sub = ImageFont.load_default()
        
    for i in range(end_frame):
        frame_file = os.path.join(out_frames_dir, f"{i:05d}.jpg")
        if os.path.exists(frame_file):
            aplicar_overlay_diadico(frame_file, i, font_title, font_sub)
            
    # 4. Compilar em MP4 com áudio sincronizado via FFmpeg
    print("\n[4/4] Montando vídeo MP4 com diálogo diádico sincronizado via FFmpeg...")
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
    print(f"🎬 VÍDEO FINAL Audio2Photoreal GERADO COM SUCESSO:")
    print(f"   -> {out_mp4}")
    print(f"   (Duração: {duration:.2f}s | {end_frame} frames | Resolução: 1024x1024 | 25 FPS)")
    print("=" * 75)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--frames", type=int, default=None, help="Número de frames para renderizar")
    parser.add_argument("--device", type=str, default="mps", choices=["mps", "cpu"])
    args = parser.parse_args()
    
    dir_path = os.path.dirname(os.path.abspath(__file__))
    npz = os.path.join(dir_path, "trajetoria_diadica.npz")
    audio = os.path.join(REPO_ROOT, "data", "dialogo_diadico.wav")
    portrait = os.path.join(REPO_ROOT, "data", "vasa_portrait.jpg")
    saida = os.path.join(dir_path, "video_diadico.mp4")
    
    renderizar_diadico(
        npz_path=npz,
        portrait_path=portrait,
        audio_path=audio,
        out_mp4=saida,
        num_frames=args.frames,
        device=args.device
    )
