"""
Experimento Comparativo: VASA-1 vs AUHead (Lado a Lado)
=========================================================
Objetivo:
Comparar o comportamento expressivo e emocional de dois paradigmas:
1. VASA-1 (Microsoft Research, 2024):
   - Movimento derivado exclusivamente da prosódia do áudio de fala (HuBERT)
   - Dinâmica holística natural de pose e lábios, mas com face neutra/sem controle muscular explícito.
2. AUHead (ICLR 2026):
   - O mesmo áudio de fala, porém com injeção cirúrgica de Action Units FACS (Paul Ekman)
   - Transição dinâmica de emoções contrastantes:
     * Fase 1: RAIVA (AU04 - Corrugador/Cenho franzido + AU07 - Olhar tenso + AU15 - Cantos caídos)
     * Fase 2: TRANSIÇÃO (Relaxamento fisiológico via interpolação cúbica Hermite/Smoothstep)
     * Fase 3: FELICIDADE (AU12 - Zigomático maior/Sorriso aberto + AU06 - Olhar de Duchenne)

Saída:
Vídeo comparativo em tela dividida (Split-Screen 2048x1024) com áudio sincronizado:
-> Implementacoes/03_auhead_facs_control/video_comparativo_vasa_vs_auhead.mp4
"""

import os
import sys
import shutil
import subprocess
import numpy as np
from PIL import Image, ImageDraw, ImageFont

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(REPO_ROOT, "referencia"))

from ditto_lab import Lab, Renderer, seed_everything


def smoothstep(edge0: float, edge1: float, x: float) -> float:
    t = np.clip((x - edge0) / (edge1 - edge0 + 1e-8), 0.0, 1.0)
    return t * t * (3.0 - 2.0 * t)


def au_to_delta_exp(au_dict: dict) -> np.ndarray:
    """Converte intensidades de AUs FACS em delta_exp de 21 keypoints 3D."""
    delta = np.zeros(63, dtype=np.float32)
    
    def _add(kp: int, axis: int, value: float):
        delta[kp * 3 + axis] += value
        
    def _get(key: str) -> float:
        return float(au_dict.get(key, 0.0))

    # --- RAIVA: AU04 (Corrugador), AU07 (Tensão ocular), AU15 (Cantos labiais) ---
    val_au04 = _get('AU04')
    if val_au04 > 0:
        _add(1, 1, val_au04 * -0.012)  # Sobrancelhas descem
        _add(2, 1, val_au04 * 0.012)
        _add(1, 0, val_au04 * -0.007)  # Aproximam-se no centro
        _add(2, 0, val_au04 * 0.007)

    val_au07 = _get('AU07')
    if val_au07 > 0:
        _add(11, 1, val_au07 * 0.015)  # Olhos se estreitam em tensão
        _add(15, 1, val_au07 * 0.015)
        _add(13, 1, val_au07 * -0.005)
        _add(16, 1, val_au07 * -0.005)

    val_au15 = _get('AU15')
    if val_au15 > 0:
        _add(20, 1, val_au15 * 0.012)  # Cantos da boca descem
        _add(14, 1, val_au15 * 0.022)
        _add(17, 1, val_au15 * -0.007)

    # --- FELICIDADE: AU12 (Zigomático), AU06 (Olhar Duchenne), AU02 (Frontal) ---
    val_au12 = _get('AU12')
    if val_au12 > 0:
        s = val_au12 * 1.2
        _add(20, 1, s * -0.014)  # Cantos da boca sobem em sorriso aberto
        _add(14, 1, s * -0.024)
        _add(17, 1, s * 0.008)
        _add(3, 1,  s * -0.005)
        _add(7, 1,  s * -0.005)

    val_au06 = _get('AU06')
    if val_au06 > 0:
        c = val_au06 * 0.45
        _add(11, 1, c * 0.018)  # Bochechas sobem comprimindo pálpebras
        _add(15, 1, c * 0.018)
        _add(13, 1, c * -0.008)
        _add(16, 1, c * -0.008)

    val_au02 = _get('AU02')
    if val_au02 > 0:
        _add(1, 1, val_au02 * 0.012)  # Elevação sutil receptiva
        _add(2, 1, val_au02 * -0.012)

    return delta


def construir_timeline_comparativa(total_frames: int) -> list:
    """
    Timeline com duas emoções antagônicas:
    - Frames 0 a 75 (0.0s a 3.0s):   "Primeiro eu sinto muita raiva e indignação!" -> RAIVA
    - Frames 75 a 100 (3.0s a 4.0s): Transição / Pausa respiratória
    - Frames 100 a 191 (4.0s a 7.6s): "Mas agora, eu fico completamente feliz e aliviado." -> FELICIDADE
    """
    ctrl_list = []
    for f in range(total_frames):
        au = {}
        if f < 75:
            # Fase 1: Raiva Plena
            subida = smoothstep(0, 15, f)
            au['AU04'] = 0.90 * subida  # Corrugador (cenho)
            au['AU07'] = 0.40 * subida  # Tensão ocular
            au['AU15'] = 0.35 * subida  # Cantos caídos
        elif 75 <= f < 100:
            # Transição: Desativa raiva, prepara sorriso
            fator_descida = 1.0 - smoothstep(75, 100, f)
            au['AU04'] = 0.90 * fator_descida
            au['AU07'] = 0.40 * fator_descida
            au['AU15'] = 0.35 * fator_descida
        else:
            # Fase 2: Felicidade Radiante (Sorriso Duchenne)
            fator_subida = smoothstep(100, 125, f)
            au['AU12'] = 0.95 * fator_subida  # Zigomático (sorriso)
            au['AU06'] = 0.75 * fator_subida  # Olhar de Duchenne
            au['AU02'] = 0.25 * fator_subida  # Sobrancelhas suaves
            
        delta = au_to_delta_exp(au)
        ctrl_list.append({"delta_exp": delta.reshape(1, 63)})
        
    return ctrl_list


def criar_frame_comparativo(img_vasa_path: str, img_auhead_path: str, frame_idx: int, font_title, font_sub) -> Image.Image:
    """Combina os dois frames lado a lado com barras de título e legendas anatômicas."""
    im_v = Image.open(img_vasa_path).convert("RGB")
    im_a = Image.open(img_auhead_path).convert("RGB")
    
    W, H = im_v.size  # 1024, 1024
    comp = Image.new("RGB", (W * 2, H), color=(10, 12, 16))
    comp.paste(im_v, (0, 0))
    comp.paste(im_a, (W, 0))
    
    draw = ImageDraw.Draw(comp, "RGBA")
    
    # 1. Linha divisória vertical
    draw.rectangle([(W - 2, 0), (W + 2, H)], fill=(255, 255, 255, 180))
    
    # 2. Faixa de Cabeçalho Superior
    header_h = 70
    draw.rectangle([(0, 0), (W, header_h)], fill=(15, 23, 42, 230))
    draw.rectangle([(W, 0), (W * 2, header_h)], fill=(16, 37, 66, 230))
    
    draw.text((30, 20), "VASA-1: Áudio Puro (Sem Controle FACS)", fill=(240, 240, 240), font=font_title)
    draw.text((W + 30, 20), "AUHead: Controle Anatômico FACS (ICLR 2026)", fill=(56, 189, 248), font=font_title)
    
    # 3. Badges Inferiores de Estado Emocional
    footer_h = 75
    y_footer = H - footer_h - 20
    
    # Lado VASA-1: sempre sem controle muscular adicional
    draw.rectangle([(30, y_footer), (W - 30, y_footer + footer_h)], fill=(15, 23, 42, 220), outline=(100, 116, 139, 255), width=2)
    draw.text((50, y_footer + 15), "ESTADO: Neutro / Prosódia de Fala Pura", fill=(203, 213, 225), font=font_sub)
    draw.text((50, y_footer + 42), "Apenas sincronia labial — face inexpressiva", fill=(148, 163, 184), font=font_sub)
    
    # Lado AUHead: muda conforme a fase
    if frame_idx < 75:
        # Fase Raiva
        draw.rectangle([(W + 30, y_footer), (W * 2 - 30, y_footer + footer_h)], fill=(69, 10, 10, 230), outline=(239, 68, 68, 255), width=2)
        draw.text((W + 50, y_footer + 15), "EMOÇÃO: RAIVA & INDIGNAÇÃO", fill=(254, 202, 202), font=font_title)
        draw.text((W + 50, y_footer + 45), "AU04 (Corrugador/Cenho) + AU07 (Tensão Ocular) + AU15", fill=(252, 165, 165), font=font_sub)
    elif 75 <= frame_idx < 100:
        # Fase Transição
        draw.rectangle([(W + 30, y_footer), (W * 2 - 30, y_footer + footer_h)], fill=(30, 41, 59, 230), outline=(148, 163, 184, 255), width=2)
        draw.text((W + 50, y_footer + 15), "TRANSIÇÃO: Relaxamento Muscular (Smoothstep)", fill=(241, 245, 249), font=font_title)
        draw.text((W + 50, y_footer + 45), "Interpolação cúbica de Hermite entre estados", fill=(203, 213, 225), font=font_sub)
    else:
        # Fase Felicidade
        draw.rectangle([(W + 30, y_footer), (W * 2 - 30, y_footer + footer_h)], fill=(6, 78, 59, 230), outline=(34, 197, 94, 255), width=2)
        draw.text((W + 50, y_footer + 15), "EMOÇÃO: FELICIDADE & ALÍVIO", fill=(187, 247, 208), font=font_title)
        draw.text((W + 50, y_footer + 45), "AU12 (Zigomático/Sorriso) + AU06 (Olhos de Duchenne)", fill=(134, 239, 172), font=font_sub)
        
    return comp


def executar_comparativo():
    print("=" * 75)
    print("🔬 EXPERIMENTO COMPARATIVO LADO A LADO: VASA-1 vs AUHead (RAIVA & FELICIDADE)")
    print("=" * 75)
    
    dir_03 = os.path.dirname(os.path.abspath(__file__))
    audio_path = os.path.join(REPO_ROOT, "data", "comparativo_speech.wav")
    portrait_path = os.path.join(REPO_ROOT, "data", "vasa_portrait.jpg")
    
    npz_vasa = os.path.join(dir_03, "trajetoria_vasa1_comp.npz")
    npz_auhead = os.path.join(dir_03, "trajetoria_auhead_comp.npz")
    avatar_pkl = os.path.join(dir_03, "avatar_state.pkl")
    
    dir_frames_vasa = os.path.join(dir_03, "frames_vasa1_comp")
    dir_frames_auhead = os.path.join(dir_03, "frames_auhead_comp")
    dir_frames_side = os.path.join(dir_03, "frames_comparativo_side")
    
    out_mp4 = os.path.join(dir_03, "video_comparativo_vasa_vs_auhead.mp4")
    
    # 1. Inicializar Lab e preparar semente
    seed_everything(42)
    lab = Lab()
    
    import soundfile as sf
    audio_data, sr = sf.read(audio_path)
    total_frames = int(round(len(audio_data) / sr * 25))
    print(f"\n[1/5] Áudio de teste: {len(audio_data)/sr:.2f}s ({total_frames} frames @ 25 FPS)")
    
    # 2. Gerar Trajetória VASA-1 (ctrl=None, áudio puro)
    print("\n[2/5] Gerando trajetória do VASA-1 (sem controle muscular FACS)...")
    lab.generate_motion(
        audio_path=audio_path,
        source=portrait_path,
        out_npz=npz_vasa,
        emo=None,
        seed=42,
        ctrl=None
    )
    print(f"  ✅ Trajetória VASA-1 salva em: {os.path.basename(npz_vasa)}")
    
    # 3. Gerar Trajetória AUHead (com injeção da timeline de AUs)
    print("\n[3/5] Gerando trajetória do AUHead (com timeline muscular Raiva -> Felicidade)...")
    ctrl_timeline = construir_timeline_comparativa(total_frames)
    lab.generate_motion(
        audio_path=audio_path,
        source=portrait_path,
        out_npz=npz_auhead,
        emo=None,
        seed=42,
        ctrl=ctrl_timeline
    )
    print(f"  ✅ Trajetória AUHead salva em: {os.path.basename(npz_auhead)}")
    
    # 4. Renderizar ambos os modelos na GPU (Apple Silicon MPS)
    print(f"\n[4/5] Renderizando {total_frames} frames de cada modelo usando GPU MPS...")
    renderer = Renderer(device="mps", bf16=True)
    
    print("  -> Renderizando VASA-1...")
    renderer.render(
        avatar_pkl=avatar_pkl,
        motion_npz=npz_vasa,
        out_dir=dir_frames_vasa,
        start=0,
        end=total_frames,
        full=True
    )
    
    print("  -> Renderizando AUHead...")
    renderer.render(
        avatar_pkl=avatar_pkl,
        motion_npz=npz_auhead,
        out_dir=dir_frames_auhead,
        start=0,
        end=total_frames,
        full=True
    )
    print("  ✅ Ambos os conjuntos de frames foram sintetizados com sucesso!")
    
    # 5. Composição Lado a Lado (Split-Screen com Anotações)
    print("\n[5/5] Compondo split-screen lado a lado com legendas científicas...")
    os.makedirs(dir_frames_side, exist_ok=True)
    
    try:
        font_title = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 26)
        font_sub = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 20)
    except Exception:
        font_title = font_sub = ImageFont.load_default()
        
    for i in range(total_frames):
        p_v = os.path.join(dir_frames_vasa, f"{i:05d}.jpg")
        p_a = os.path.join(dir_frames_auhead, f"{i:05d}.jpg")
        
        comp_img = criar_frame_comparativo(p_v, p_a, i, font_title, font_sub)
        comp_img.save(os.path.join(dir_frames_side, f"{i:05d}.jpg"), quality=95)
        
    print("  ✅ 191 frames compostos em 2048x1024.")
    
    # 6. Compilar Vídeo MP4 Final com Áudio via FFmpeg
    print("\n🎬 Montando vídeo MP4 final com áudio sincronizado via FFmpeg...")
    cmd = [
        "ffmpeg", "-y",
        "-framerate", "25",
        "-i", os.path.join(dir_frames_side, "%05d.jpg"),
        "-i", audio_path,
        "-c:v", "libx264",
        "-crf", "19",
        "-preset", "fast",
        "-pix_fmt", "yuv420p",
        "-c:a", "aac",
        "-b:a", "192k",
        "-shortest",
        out_mp4
    ]
    subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    
    # 7. Limpeza dos diretórios de frames intermediários para poupar espaço
    print("\n🧹 Limpando pastas temporárias de frames para manter o repositório limpo...")
    shutil.rmtree(dir_frames_vasa, ignore_errors=True)
    shutil.rmtree(dir_frames_auhead, ignore_errors=True)
    shutil.rmtree(dir_frames_side, ignore_errors=True)
    
    print("\n" + "=" * 75)
    print(f"🎉 VÍDEO COMPARATIVO GERADO COM SUCESSO:")
    print(f"   -> {out_mp4}")
    print(f"   Resolução: 2048x1024 | Duração: {total_frames/25:.2f}s ({total_frames} frames @ 25 FPS)")
    print("=" * 75)


if __name__ == "__main__":
    executar_comparativo()
