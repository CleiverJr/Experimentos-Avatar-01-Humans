"""
Renderizador Mestre 08: Montagem da Grade Comparativa 2x3 de Todos os Modelos SOTA
==================================================================================
Este script renderiza e compoe o mosaico de video comparativo em resolucao 1920x1370:
- Linha 1: [VASA-1] | [AUHead FACS] | [InstructAvatar NLP]
- Linha 2: [Audio2Photoreal] | [OmniHuman-1.5] | [Motion Diffusion MDM]

Para cada frame:
1. Aplica cabecalho superior sincronizado com o audio da "Prova de Fogo"
2. Em cada celula: tarjas com identificacao do modelo e telemetria comportamental
3. Monta o video final MP4 com o audio original unificado
4. Gera GIF animado de alta fidelidade para demonstracao instantanea no README
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


# Configuracao dos 6 modelos na grade 2x3
CONFIG_MODELOS = [
    {
        "id": "vasa1",
        "nome": "VASA-1 (Microsoft, 2024)",
        "sub": "Dinamica Holistica Livre por Audio",
        "npz": "trajetoria_02_vasa1.npz",
        "pos": (0, 0),  # linha 0, col 0
        "fase1": "Prosodia pura: fala neutra direta",
        "fase2": "Sem audio: boca semi-aberta (sem VAD)",
        "fase3": "Movimento padrao sem controle dirigido"
    },
    {
        "id": "auhead",
        "nome": "AUHead (ICLR 2026)",
        "sub": "Controle Muscular Anatomico FACS",
        "npz": "trajetoria_03_auhead.npz",
        "pos": (0, 1),  # linha 0, col 1
        "fase1": "AU04 (0.85): Cenho franzido & foco analitico",
        "fase2": "Relaxamento muscular da glabela",
        "fase3": "AU12 (0.85) + AU06: Grande sorriso Duchenne"
    },
    {
        "id": "instruct",
        "nome": "InstructAvatar (AAAI 2025)",
        "sub": "Direcao Cenica NLP & Oclusao Labial",
        "npz": "trajetoria_04_instruct.npz",
        "pos": (0, 2),  # linha 0, col 2
        "fase1": "Postura altiva: Queixo elevado (Pitch -4.5 deg)",
        "fase2": "Silencio: Labios selados (vad_alpha=0)",
        "fase3": "Presenca cenica ereta (Pitch -5.5 deg)"
    },
    {
        "id": "audio2photoreal",
        "nome": "Audio2Photoreal (Meta, CVPR)",
        "sub": "Conversacao Diadica & Backchanneling",
        "npz": "trajetoria_05_audio2photoreal.npz",
        "pos": (1, 0),  # linha 1, col 0
        "fase1": "Turno de fala inicial ativo",
        "fase2": "Escuta Ativa: 2 Acenos (+5.5 deg) & Boca Selada",
        "fase3": "Retomada suave de turno conversacional"
    },
    {
        "id": "omnihuman",
        "nome": "OmniHuman-1.5 (ByteDance, 2025)",
        "sub": "Arquitetura Dual (Sistema 1 + Sistema 2)",
        "npz": "trajetoria_06_omnihuman.npz",
        "pos": (1, 1),  # linha 1, col 1
        "fase1": "Sistema 2: Pensamento concentrado (Pitch +2.5 deg)",
        "fase2": "Gaze Aversion deliberativo: Yaw -9 deg, Pitch -3.5 deg",
        "fase3": "Conviccao: Foco frontal direto e queixo alto"
    },
    {
        "id": "mdm",
        "nome": "Motion Diffusion (MDM, ICLR)",
        "sub": "Difusao Estocastica (Anti-Colapso a Media)",
        "npz": "trajetoria_07_mdm.npz",
        "pos": (1, 2),  # linha 1, col 2
        "fase1": "DDPM Sampling: Cinematica viva anti-colapso",
        "fase2": "Dinamica postural organica continua",
        "fase3": "Rica amplitude angular livre da media"
    }
]


def renderizar_grade(out_dir: str, audio_path: str, portrait_path: str, num_frames: int = None, device: str = "mps"):
    print("=" * 80)
    print("INICIANDO RENDERIZACAO DA GRADE COMPARATIVA 2x3 (TODOS OS MODELOS SOTA)")
    print(f"Aceleracao de Hardware: [{device.upper()}] (Apple Silicon GPU)")
    print("=" * 80)

    avatar_pkl = os.path.join(out_dir, "avatar_state.pkl")
    avatar_ref = os.path.join(REPO_ROOT, "Implementacoes", "05_audio2photoreal_dialogue", "avatar_state.pkl")
    if not os.path.exists(avatar_pkl) and os.path.exists(avatar_ref):
        shutil.copy2(avatar_ref, avatar_pkl)
    elif not os.path.exists(avatar_pkl):
        lab = Lab()
        lab._setup(portrait_path, emo=None)
        lab.save_avatar_state(avatar_pkl)

    renderer = Renderer(device=device, bf16=True)
    total_frames = 242 if num_frames is None else num_frames

    # 1. Renderizar cada modelo individualmente em pasta temporaria redimensionada
    print("\n[Etapa 1/3] Renderizando frames neurais para cada um dos 6 modelos...")
    pastas_modelos = {}
    for mod in CONFIG_MODELOS:
        mid = mod["id"]
        npz_file = os.path.join(out_dir, mod["npz"])
        temp_dir = os.path.join(out_dir, f"temp_{mid}")
        os.makedirs(temp_dir, exist_ok=True)
        pastas_modelos[mid] = temp_dir
        
        print(f"  -> Renderizando {total_frames} frames para: {mod['nome']}...")
        renderer.render(
            avatar_pkl=avatar_pkl,
            motion_npz=npz_file,
            out_dir=temp_dir,
            start=0,
            end=total_frames,
            full=True
        )

    # 2. Composicao do Mosaico 2x3 com Telemetria e Badges
    print("\n[Etapa 2/3] Compondo grade comparativa 2x3 (1920x1370) com telemetria...")
    dir_mestre = os.path.join(out_dir, "frames_mestre")
    os.makedirs(dir_mestre, exist_ok=True)

    try:
        font_main = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 24)
        font_sub = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 17)
        font_badge_title = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 19)
        font_badge_desc = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 15)
    except Exception:
        font_main = font_sub = font_badge_title = font_badge_desc = ImageFont.load_default()

    grid_w, grid_h = 1920, 1370
    cell_w, cell_h = 640, 640
    header_h = 90

    for i in range(total_frames):
        canvas = Image.new("RGB", (grid_w, grid_h), (15, 23, 42))
        draw = ImageDraw.Draw(canvas, "RGBA")

        # --- CABECALHO GERAL ---
        draw.rectangle([(0, 0), (grid_w, header_h)], fill=(10, 15, 30, 240))
        draw.text((30, 12), "PROVA DE FOGO: COMPARATIVO SOTA DE SINTESE E CONTROLE DE AVATARES", fill=(56, 189, 248), font=font_main)

        # Subtitulo da fase atual do audio
        if i < 60:
            txt_audio = "\"Analise esta hipotese com atencao.\"  |  [FASE 1: CONCENTRACAO & FOCO ANALITICO]"
            cor_audio = (226, 232, 240)
        elif 60 <= i < 115:
            txt_audio = "\"(pausa de 2.2s em silencio reflexivo)\"  |  [FASE 2: PROVA CRITICA DE BOCA E OLHAR]"
            cor_audio = (251, 191, 36)
        else:
            txt_audio = "\"Exatamente! Quando a mente imagina o futuro...\"  |  [FASE 3: CLIMAX & CONVICCAO ASSERTIVA]"
            cor_audio = (74, 222, 128)
        draw.text((30, 48), txt_audio, fill=cor_audio, font=font_sub)

        # --- COMPOSICAO DOS 6 MODELOS ---
        for mod in CONFIG_MODELOS:
            mid = mod["id"]
            row, col = mod["pos"]
            x_off = col * cell_w
            y_off = header_h + row * cell_h

            frame_img_path = os.path.join(pastas_modelos[mid], f"{i:05d}.jpg")
            if os.path.exists(frame_img_path):
                fimg = Image.open(frame_img_path).convert("RGB")
                fimg_resized = fimg.resize((cell_w, cell_h), Image.Resampling.LANCZOS)
                canvas.paste(fimg_resized, (x_off, y_off))

            # 1. Tarja Superior da Celula (Identificacao do Modelo)
            draw.rectangle([(x_off, y_off), (x_off + cell_w, y_off + 52)], fill=(15, 23, 42, 215))
            draw.text((x_off + 15, y_off + 6), mod["nome"], fill=(255, 255, 255), font=font_badge_title)
            draw.text((x_off + 15, y_off + 29), mod["sub"], fill=(148, 163, 184), font=font_badge_desc)

            # 2. Tarja Inferior da Celula (Telemetria do Comportamento Atual)
            if i < 60:
                txt_status = mod["fase1"]
                cor_status_bg = (30, 41, 59, 220)
                cor_txt = (226, 232, 240)
            elif 60 <= i < 115:
                txt_status = mod["fase2"]
                # Destaque especial para os modelos que respondem ativamente ao silencio
                if mid in ["omnihuman", "audio2photoreal", "instruct"]:
                    cor_status_bg = (180, 83, 9, 230) if mid != "audio2photoreal" else (16, 185, 129, 230)
                    cor_txt = (255, 255, 255)
                else:
                    cor_status_bg = (71, 85, 105, 210)
                    cor_txt = (203, 213, 225)
            else:
                txt_status = mod["fase3"]
                cor_status_bg = (15, 118, 110, 225) if mid in ["omnihuman", "auhead", "mdm"] else (30, 41, 59, 220)
                cor_txt = (255, 255, 255)

            draw.rectangle([(x_off, y_off + cell_h - 48), (x_off + cell_w, y_off + cell_h)], fill=cor_status_bg)
            draw.text((x_off + 15, y_off + cell_h - 36), txt_status, fill=cor_txt, font=font_badge_desc)

            # Borda sutil de divisao
            draw.rectangle([(x_off, y_off), (x_off + cell_w, y_off + cell_h)], outline=(51, 65, 85, 180), width=1)

        # Salvar frame composto
        canvas.save(os.path.join(dir_mestre, f"{i:05d}.jpg"), quality=94)

    # 3. Compilacao do Video Final MP4 via FFmpeg
    print("\n[Etapa 3/3] Compilando video MP4 final com audio sincronizado...")
    out_mp4 = os.path.join(out_dir, "video_comparativo_mestre.mp4")
    duration = total_frames / 25.0

    cmd_mp4 = [
        "ffmpeg", "-y",
        "-framerate", "25",
        "-i", os.path.join(dir_mestre, "%05d.jpg"),
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
    subprocess.run(cmd_mp4, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    print(f"  ✅ Video final compilado com sucesso:\n     -> {out_mp4}")

    # 4. Gerar GIF animado otimizado para o README
    print("\nGerando GIF animado para o README...")
    out_gif = os.path.join(out_dir, "demo_comparativo_mestre.gif")
    vf = "fps=12,scale=720:-1:flags=lanczos,split[s0][s1];[s0]palettegen=max_colors=128[p];[s1][p]paletteuse=dither=bayer:bayer_scale=3"
    cmd_gif = [
        "ffmpeg", "-y",
        "-ss", "0", "-t", str(min(duration, 9.6)),
        "-i", out_mp4,
        "-vf", vf,
        out_gif
    ]
    subprocess.run(cmd_gif, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    gif_size = os.path.getsize(out_gif) / (1024 * 1024)
    print(f"  ✅ GIF comparativo gerado ({gif_size:.2f} MB):\n     -> {out_gif}")

    # 5. Limpeza de pastas temporarias
    print("\nLimpando caches temporarios de frames...")
    shutil.rmtree(dir_mestre, ignore_errors=True)
    for p in pastas_modelos.values():
        shutil.rmtree(p, ignore_errors=True)
    if os.path.exists(avatar_pkl):
        os.remove(avatar_pkl)

    print("\n" + "=" * 80)
    print("PROVA DE FOGO CONCLUIDA COM SUCESSO TOTAL!")
    print(f"Video MP4: {out_mp4}")
    print(f"Demo GIF:  {out_gif}")
    print("=" * 80)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--frames", type=int, default=None, help="Numero de frames para teste rapido")
    parser.add_argument("--device", type=str, default="mps", choices=["mps", "cpu"])
    args = parser.parse_args()

    dir_08 = os.path.dirname(os.path.abspath(__file__))
    audio_path = os.path.join(REPO_ROOT, "data", "prova_de_fogo.wav")
    portrait_path = os.path.join(REPO_ROOT, "data", "vasa_portrait.jpg")

    renderizar_grade(
        out_dir=dir_08,
        audio_path=audio_path,
        portrait_path=portrait_path,
        num_frames=args.frames,
        device=args.device
    )
