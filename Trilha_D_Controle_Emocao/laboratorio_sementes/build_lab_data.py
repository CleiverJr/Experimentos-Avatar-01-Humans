"""
Gera os dados e parâmetros pré-calculados para cada um dos 6 testes do Laboratório da Trilha D.
"""

import os
import sys
import json
import base64
import numpy as np

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.audio_processor import AudioProcessor
from src.action_units import ActionUnitsSystem
from src.motion_diffusion import DDPMScheduler, TemporalMotionDenoiser, MotionDiffusionPipeline
from src.instruct_parser import InstructParser


def build_laboratory_data():
    base_dir = os.path.abspath(os.path.dirname(__file__))
    audio_dir = os.path.join(base_dir, "audio")
    output_json = os.path.join(base_dir, "laboratorio_completo.json")

    fps = 30.0
    audio_proc = AudioProcessor(sample_rate=16000, n_mels=80, fps=fps)
    parser = InstructParser()
    facs = ActionUnitsSystem(num_flame_exp=50)

    scheduler = DDPMScheduler(num_timesteps=50)
    denoiser = TemporalMotionDenoiser(motion_dim=6, audio_dim=80, emo_dim=16, hidden_dim=64)
    diff_pipeline = MotionDiffusionPipeline(denoiser, scheduler)

    # 1. Carrega foto real em Base64 para o VASA-1
    img_path = os.path.join(base_dir, "..", "data", "vasa_portrait.jpg")
    with open(img_path, "rb") as f_img:
        portrait_b64 = base64.b64encode(f_img.read()).decode("utf-8")

    # ----------------------------------------------------
    # TESTE 1: VASA-1 (Foto Estática + Áudio -> Dinâmica Holística)
    # ----------------------------------------------------
    print("[1/6] Processando teste VASA-1...")
    vasa_wav = os.path.join(audio_dir, "vasa_speech.wav")
    vasa_audio = audio_proc.load_audio(vasa_wav)
    vasa_feat = audio_proc.extract_features(vasa_audio)
    T_vasa = vasa_feat["num_frames"]

    with open(vasa_wav, "rb") as f:
        vasa_audio_b64 = base64.b64encode(f.read()).decode("utf-8")

    # Dinâmica VASA: fala natural, cabeça oscilando sutilmente, olhar ativo
    vasa_parsed = parser.parse_instruction("Fale de forma natural, amigável e expressiva, olhando para a câmera")
    vasa_head = diff_pipeline.sample(vasa_feat["mel_spectrogram"], vasa_parsed["conditioning_vector"], seed=101)
    
    # Action units com modulação da fala
    vasa_base_au = facs.blend_emotions({"happy": 0.35, "neutral": 0.65})
    vasa_au_seq = facs.modulate_with_speech(np.tile(vasa_base_au, (T_vasa, 1)), vasa_feat["energy_rms"], blink_interval=40)

    vasa_frames = []
    for t in range(T_vasa):
        vasa_frames.append({
            "t": round(t / fps, 3),
            "p": round(float(vasa_head[t, 0]), 2),
            "y": round(float(vasa_head[t, 1]), 2),
            "r": round(float(vasa_head[t, 2]), 2),
            "gaze_x": round(float(np.sin(t * 0.1) * 0.4), 2),
            "gaze_y": round(float(np.cos(t * 0.08) * 0.2), 2),
            "smile": round(float(vasa_au_seq[t, facs.au_to_idx["AU12"]]), 3),
            "brow": round(float(vasa_au_seq[t, facs.au_to_idx["AU01"]]), 3),
            "jaw": round(float(vasa_au_seq[t, facs.au_to_idx["AU26"]]), 3),
            "blink": round(float(vasa_au_seq[t, facs.au_to_idx["AU45"]]), 3)
        })

    # ----------------------------------------------------
    # TESTE 2: InstructAvatar (3 Nuances Dramáticas para a Mesma Voz)
    # ----------------------------------------------------
    print("[2/6] Processando teste InstructAvatar (3 nuances de texto)...")
    inst_wav = os.path.join(audio_dir, "instruct_speech.wav")
    inst_audio = audio_proc.load_audio(inst_wav)
    inst_feat = audio_proc.extract_features(inst_audio)
    T_inst = inst_feat["num_frames"]

    with open(inst_wav, "rb") as f:
        inst_audio_b64 = base64.b64encode(f.read()).decode("utf-8")

    prompts = {
        "happy": "Fale com extrema alegria, entusiasmo e sorriso rasgado, olhando para a esquerda",
        "sad": "Fale com tristeza profunda, desânimo, cabeça baixa e olhar caído",
        "angry": "Fale com muita raiva, arrogância e desdém, sobrancelhas arqueadas e olhando para a direita"
    }

    instruct_scenarios = {}
    for emo_key, p_text in prompts.items():
        parsed = parser.parse_instruction(p_text)
        head_t = diff_pipeline.sample(inst_feat["mel_spectrogram"], parsed["conditioning_vector"], seed=42)
        head_t[:, 1] += parsed["head_bias"]["yaw_deg"]
        head_t[:, 0] += parsed["head_bias"]["pitch_deg"]
        
        base_au = facs.blend_emotions(parsed["emotion_weights"])
        mod_au = facs.modulate_with_speech(np.tile(base_au, (T_inst, 1)), inst_feat["energy_rms"], blink_interval=50)

        f_list = []
        for t in range(T_inst):
            f_list.append({
                "t": round(t / fps, 3),
                "p": round(float(head_t[t, 0]), 2),
                "y": round(float(head_t[t, 1]), 2),
                "r": round(float(head_t[t, 2]), 2),
                "smile": round(float(mod_au[t, facs.au_to_idx["AU12"]]), 3),
                "brow": round(float(mod_au[t, facs.au_to_idx["AU01"]]), 3),
                "brow_down": round(float(mod_au[t, facs.au_to_idx["AU04"]]), 3),
                "jaw": round(float(mod_au[t, facs.au_to_idx["AU26"]]), 3),
                "blink": round(float(mod_au[t, facs.au_to_idx["AU45"]]), 3)
            })
        instruct_scenarios[emo_key] = {
            "prompt": p_text,
            "emotions": parsed["emotion_weights"],
            "intensity": parsed["intensity"],
            "frames": f_list
        }

    # ----------------------------------------------------
    # TESTE 3: AUHead (Dissecação Anatômica FACS)
    # ----------------------------------------------------
    print("[3/6] Processando teste AUHead (Músculos FACS Isolados)...")
    # Tabela anatômica com os músculos reais de Paul Ekman
    facs_anatomy = [
        {"au": "AU01", "name": "Inner Brow Raiser", "muscle": "Músculo Frontal (porção medial)", "effect": "Eleva a parte interna das sobrancelhas (expressão de surpresa ou súplica)"},
        {"au": "AU04", "name": "Brow Lowerer", "muscle": "Músculo Corrugador do Supercílio", "effect": "Abaixa e aproxima as sobrancelhas, criando rugas verticais (raiva ou concentração)"},
        {"au": "AU06", "name": "Cheek Raiser", "muscle": "Músculo Orbicular dos Olhos (porção orbital)", "effect": "Eleva as bochechas e estreita os olhos (o sorriso Duchenne genuíno)"},
        {"au": "AU12", "name": "Lip Corner Puller", "muscle": "Músculo Zigomático Maior", "effect": "Puxa os cantos dos lábios para cima e para trás (sorriso)"},
        {"au": "AU15", "name": "Lip Corner Depressor", "muscle": "Músculo Depressor do Ângulo da Boca", "effect": "Puxa os cantos dos lábios para baixo (tristeza ou desânimo)"},
        {"au": "AU26", "name": "Jaw Drop", "muscle": "Músculo Masseter e Mandíbula", "effect": "Abaixa a mandíbula para articulação de vogais abertas"},
        {"au": "AU45", "name": "Blink", "muscle": "Músculo Orbicular dos Olhos (porção palpebral)", "effect": "Fechamento fisiológico e reflexo das pálpebras"}
    ]

    # ----------------------------------------------------
    # TESTE 4: Audio2Photoreal (Corpo Inteiro e Gesticulação)
    # ----------------------------------------------------
    print("[4/6] Processando teste Audio2Photoreal (Corpo Inteiro)...")
    conv_wav = os.path.join(audio_dir, "conversation_speech.wav")
    conv_audio = audio_proc.load_audio(conv_wav)
    conv_feat = audio_proc.extract_features(conv_audio)
    T_conv = conv_feat["num_frames"]

    with open(conv_wav, "rb") as f:
        conv_audio_b64 = base64.b64encode(f.read()).decode("utf-8")

    # Síntese das juntas 3D do corpo superior (tronco, ombros, cotovelos, mãos)
    body_frames = []
    for t in range(T_conv):
        timestamp = t / fps
        energy = float(conv_feat["energy_rms"][t])
        
        # Dinâmica das mãos sincronizada com a energia da fala (gesticulação conversacional)
        left_hand_y = np.sin(timestamp * 3.5) * (15 + energy * 60)
        left_hand_x = -35 + np.cos(timestamp * 2.2) * (10 + energy * 30)
        right_hand_y = np.cos(timestamp * 3.0) * (20 + energy * 70)
        right_hand_x = 35 + np.sin(timestamp * 2.5) * (10 + energy * 35)

        # Inclinação de tronco
        spine_tilt = np.sin(timestamp * 1.2) * 4.0

        body_frames.append({
            "t": round(timestamp, 3),
            "spine_tilt": round(float(spine_tilt), 2),
            "left_hand": {"x": round(float(left_hand_x), 1), "y": round(float(left_hand_y), 1)},
            "right_hand": {"x": round(float(right_hand_x), 1), "y": round(float(right_hand_y), 1)},
            "head_pitch": round(float(np.sin(timestamp * 2.8) * 3.0), 1),
            "head_yaw": round(float(np.sin(timestamp * 1.5) * 8.0), 1),
            "jaw": round(float(np.clip(energy * 4.0, 0.1, 0.8)), 2)
        })

    # ----------------------------------------------------
    # TESTE 5: OmniHuman-1.5 (Sistema 1 vs Sistema 2)
    # ----------------------------------------------------
    print("[5/6] Processando teste OmniHuman-1.5 (Cognição Sistema 1 + 2)...")
    # Comparativo:
    # Sistema 1 (Reativo simples): a cabeça não se mexe quase nada, apenas abre a boca quando tem som
    # Sistema 2 (Cognitivo): antecipa pausas com olhar para cima, gesticula com ênfase nas palavras-chave
    omni_s1_frames = []
    omni_s2_frames = []
    for t in range(T_vasa):
        ts = t / fps
        energy = float(vasa_feat["energy_rms"][t])
        
        # Sistema 1: Busto quase imóvel, só boca mexendo de forma mecânica
        omni_s1_frames.append({
            "t": round(ts, 3),
            "head_yaw": 0.0,
            "head_pitch": 0.0,
            "jaw": round(float(energy * 2.5), 2),
            "smile": 0.0,
            "gaze": "Fixo"
        })

        # Sistema 2: Cognição ativa!
        # Em t ~ 2.0s a 3.0s: momento de reflexão (olha para cima, sorri antecipando ideia)
        is_thinking = (1.8 <= ts <= 3.2)
        pitch_cog = 8.0 if is_thinking else float(np.sin(ts * 2.0) * 4.0)
        yaw_cog = -12.0 if is_thinking else float(np.cos(ts * 1.5) * 7.0)
        smile_cog = 0.55 if not is_thinking else 0.2
        gaze_cog = "Desviado (Pensando)" if is_thinking else "Conectado com o ouvinte"

        omni_s2_frames.append({
            "t": round(ts, 3),
            "head_yaw": round(float(yaw_cog), 1),
            "head_pitch": round(float(pitch_cog), 1),
            "jaw": round(float(energy * 3.5), 2),
            "smile": round(float(smile_cog), 2),
            "gaze": gaze_cog
        })

    # ----------------------------------------------------
    # TESTE 6: Motion Diffusion (Denoising Steps & 3 Sementes)
    # ----------------------------------------------------
    print("[6/6] Processando teste Motion Diffusion (Denoising & Sementes)...")
    # Gera 3 trajetórias com o mesmo áudio e seeds diferentes
    seed_a = diff_pipeline.sample(vasa_feat["mel_spectrogram"][:60], vasa_parsed["conditioning_vector"], seed=10)
    seed_b = diff_pipeline.sample(vasa_feat["mel_spectrogram"][:60], vasa_parsed["conditioning_vector"], seed=50)
    seed_c = diff_pipeline.sample(vasa_feat["mel_spectrogram"][:60], vasa_parsed["conditioning_vector"], seed=99)

    diffusion_seeds = {
        "seed_10": [round(float(v), 2) for v in seed_a[:, 1]], # Yaw
        "seed_50": [round(float(v), 2) for v in seed_b[:, 1]],
        "seed_99": [round(float(v), 2) for v in seed_c[:, 1]],
        "timestamps": [round(t / fps, 3) for t in range(60)]
    }

    # Salva tudo no JSON central
    lab_data = {
        "portrait_base64": portrait_b64,
        "vasa": {
            "audio_base64": vasa_audio_b64,
            "duration": round(T_vasa / fps, 2),
            "frames": vasa_frames
        },
        "instruct": {
            "audio_base64": inst_audio_b64,
            "duration": round(T_inst / fps, 2),
            "scenarios": instruct_scenarios
        },
        "auhead": {
            "anatomy": facs_anatomy
        },
        "audio2photoreal": {
            "audio_base64": conv_audio_b64,
            "duration": round(T_conv / fps, 2),
            "frames": body_frames
        },
        "omnihuman": {
            "audio_base64": vasa_audio_b64,
            "duration": round(T_vasa / fps, 2),
            "s1_frames": omni_s1_frames,
            "s2_frames": omni_s2_frames
        },
        "motion_diffusion": {
            "seeds": diffusion_seeds
        }
    }

    with open(output_json, "w", encoding="utf-8") as f:
        json.dump(lab_data, f)

    print(f"\n✓ Laboratório completo compilado com sucesso em: {output_json}")


if __name__ == "__main__":
    build_laboratory_data()
