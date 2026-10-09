"""
Renderizador Neural: OmniHuman-1.5 — Vídeo MP4 com Visualização dos Sistemas 1 e 2
====================================================================================
Este script renderiza a simulação da mente ativa do avatar sob a arquitetura dual:
1. Carrega a trajetória (.npz) gerada pelo omnihuman_sistema_dual.py
2. Reutiliza as features de aparência (avatar_state.pkl)
3. Deforma o volume e decodifica pixels foto-realistas via GPU MPS
4. Aplica legendas dinâmicas indicando os estados dos Sistemas 1 e 2 em tempo real:
   - [ARCO 1]: Pensamento analítico / introspecção
   - [ARCO 2]: Pausa reflexiva e desvio cognitivo de olhar (Gaze Aversion)
   - [ARCO 3]: Iluminação, convicção assertiva e ênfases motoras
5. Muxa o áudio reflexivo em MP4 via FFmpeg.
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


def aplicar_overlay_omnihuman(frame_path: str, frame_idx: int, font_title, font_sub):
    """Insere barras com o monitoramento dos Sistemas 1 e 2 em tempo real."""
    img = Image.open(frame_path).convert("RGB")
    W, H = img.size
    draw = ImageDraw.Draw(img, "RGBA")
    
    # 1. Barra Superior de Contexto
    header_h = 75
    draw.rectangle([(0, 0), (W, header_h)], fill=(15, 23, 42, 220))
    draw.text((25, 12), "OmniHuman-1.5 (ByteDance, 2025) — Arquitetura Cognitiva Dual", fill=(56, 189, 248), font=font_title)
    
    # 2. Barra Inferior de Monitoramento dos Sistemas
    footer_h = 85
    y_footer = H - footer_h
    draw.rectangle([(0, y_footer), (W, H)], fill=(15, 23, 42, 230))
    
    if frame_idx < 105:
        # Arco 1: Pensamento analítico
        draw.text((25, 42), "\"Muitos acreditavam que a inteligência artificial seria apenas cálculo...\"", fill=(226, 232, 240), font=font_sub)
        
        draw.rectangle([(25, y_footer + 12), (320, y_footer + 42)], fill=(79, 70, 229, 230))
        draw.text((35, y_footer + 16), "SISTEMA 2: ANALÍTICO", fill=(255, 255, 255), font=font_sub)
        draw.text((340, y_footer + 16), "Postura compenetrada & foco analítico concentrado", fill=(224, 231, 255), font=font_sub)
        draw.text((25, y_footer + 52), "Sistema 1: Fonação reflexa HuBERT com fechamento natural de lábios", fill=(148, 163, 184), font=font_sub)
        
    elif 105 <= frame_idx < 165:
        # Arco 2: Desvio cognitivo de olhar (Gaze Aversion)
        draw.text((25, 42), "\"Mas quando pensamos na mente humana... (pausa reflexiva)\"", fill=(251, 191, 36), font=font_sub)
        
        draw.rectangle([(25, y_footer + 12), (360, y_footer + 42)], fill=(217, 119, 6, 230))
        draw.text((35, y_footer + 16), "SISTEMA 2: GAZE AVERSION", fill=(255, 255, 255), font=font_sub)
        draw.text((380, y_footer + 16), "Desvio do olhar para a memória interna de trabalho", fill=(254, 243, 199), font=font_sub)
        draw.text((25, y_footer + 52), "Simulação de mente ativa pensando e assimilando a ideia", fill=(203, 213, 225), font=font_sub)
        
    else:
        # Arco 3: Iluminação e Convicção
        draw.text((25, 42), "\"percebemos que o segredo está em planejar e imaginar o futuro!\"", fill=(74, 222, 128), font=font_sub)
        
        draw.rectangle([(25, y_footer + 12), (340, y_footer + 42)], fill=(16, 185, 129, 230))
        draw.text((35, y_footer + 16), "SISTEMA 2: CONVICÇÃO", fill=(255, 255, 255), font=font_sub)
        draw.text((360, y_footer + 16), "Queixo elevado, olhar frontal firme & ênfases motoras", fill=(209, 250, 229), font=font_sub)
        draw.text((25, y_footer + 52), "Acoplamento perfeito: o avatar pensa, expressa convicção e articula", fill=(148, 163, 184), font=font_sub)
        
    img.save(frame_path, quality=95)


def renderizar_omnihuman(
    npz_path: str,
    portrait_path: str,
    audio_path: str,
    out_mp4: str,
    num_frames: int = None,
    device: str = "mps"
):
    print("=" * 75)
    print("🎥 RENDERIZANDO VÍDEO FINAL DO OmniHuman-1.5 VIA GPU MPS")
    print("=" * 75)
    
    dir_06 = os.path.dirname(npz_path)
    avatar_pkl = os.path.join(dir_06, "avatar_state.pkl")
    out_frames_dir = os.path.join(dir_06, "frames_omnihuman")
    os.makedirs(out_frames_dir, exist_ok=True)
    
    # 1. Reutilizar avatar_state.pkl
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
    
    # 3. Aplicar legendas e badges cognitivos
    print("\n[3/4] Inserindo cartela com monitoramento dos Sistemas 1 e 2...")
    try:
        font_title = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 22)
        font_sub = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 17)
    except Exception:
        font_title = font_sub = ImageFont.load_default()
        
    for i in range(end_frame):
        frame_file = os.path.join(out_frames_dir, f"{i:05d}.jpg")
        if os.path.exists(frame_file):
            aplicar_overlay_omnihuman(frame_file, i, font_title, font_sub)
            
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
    print(f"🎬 VÍDEO FINAL OmniHuman-1.5 GERADO COM SUCESSO:")
    print(f"   -> {out_mp4}")
    print(f"   (Duração: {duration:.2f}s | {end_frame} frames | Resolução: 1024x1024 | 25 FPS)")
    print("=" * 75)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--frames", type=int, default=None, help="Número de frames para renderizar")
    parser.add_argument("--device", type=str, default="mps", choices=["mps", "cpu"])
    args = parser.parse_args()
    
    dir_path = os.path.dirname(os.path.abspath(__file__))
    npz = os.path.join(dir_path, "trajetoria_omnihuman.npz")
    audio = os.path.join(REPO_ROOT, "data", "omnihuman_speech.wav")
    portrait = os.path.join(REPO_ROOT, "data", "vasa_portrait.jpg")
    saida = os.path.join(dir_path, "video_omnihuman.mp4")
    
    renderizar_omnihuman(
        npz_path=npz,
        portrait_path=portrait,
        audio_path=audio,
        out_mp4=saida,
        num_frames=args.frames,
        device=args.device
    )
