"""
Script Mestre 08: Geracao de Trajetorias para Comparativo SOTA de Todos os Modulos
==================================================================================
Este script infere as trajetorias de movimento para os 6 modelos generativos do projeto
submetidos a exata mesma entrada ("Prova de Fogo"):
- Audio de Fala Unificado: data/prova_de_fogo.wav (9.69s | 242 frames)
  * Fase 1 (0.0s a 2.4s): Analise e Foco ("Analise esta hipotese com atencao.")
  * Fase 2 (2.4s a 4.6s): Pausa Reflexiva / Silencio de 2.2s (Teste critico de boca e olhar)
  * Fase 3 (4.6s a 9.69s): Conviccao e Climax ("Exatamente! Quando a mente imagina o futuro...")
- Imagem Neutra Canonica: data/vasa_portrait.jpg

Modelos Avaliados:
1. VASA-1 (Microsoft Research): Dinamica holistica livre pura
2. AUHead (ICLR 2026): Controle muscular via FACS (AU04 foco / AU12 sorriso)
3. InstructAvatar (AAAI 2025): Direcao cenica NLP e atenuacao labial adaptativa
4. Audio2Photoreal (Meta Reality Labs, CVPR 2024): Dialogo diadico, nodding (acenos) e boca selada
5. OmniHuman-1.5 (ByteDance, 2025): Arquitetura dual e Gaze Aversion (desvio cognitivo de olhar)
6. Motion Diffusion Model (MDM / DDPM - ICLR 2023): Difusao estocastica viva anti-colapso a media
"""

import os
import sys
import copy
import numpy as np

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(REPO_ROOT, "referencia"))

from ditto_lab import Lab, seed_everything


def smoothstep(edge0: float, edge1: float, x: float) -> float:
    t = np.clip((x - edge0) / (edge1 - edge0 + 1e-8), 0.0, 1.0)
    return float(t * t * (3.0 - 2.0 * t))


def aus_to_delta_exp(aus_dict: dict) -> np.ndarray:
    """Mapeia Action Units anatomicas em deslocamentos dos 21 keypoints 3D com tipo float32 estrito."""
    delta = np.zeros(63, dtype=np.float32)
    def _add(kp, axis, val):
        delta[kp * 3 + axis] += np.float32(val)
        
    v4 = aus_dict.get('AU04', 0.0)
    if v4 != 0:
        _add(1, 1, v4 * -0.008); _add(2, 1, v4 * 0.008)
        
    v2 = aus_dict.get('AU02', 0.0)
    if v2 != 0:
        _add(1, 1, v2 * 0.020); _add(2, 1, v2 * -0.020)
        
    v12 = aus_dict.get('AU12', 0.0)
    if v12 != 0:
        _add(20, 1, v12 * -0.012); _add(14, 1, v12 * -0.022)
        _add(3, 1,  v12 * -0.004); _add(7, 1,  v12 * -0.004)
        
    v6 = aus_dict.get('AU06', 0.0)
    if v6 != 0:
        _add(11, 1, v6 * 0.018); _add(15, 1, v6 * 0.018)
        
    v26 = aus_dict.get('AU26', 0.0)
    if v26 != 0:
        _add(19, 1, v26 * 0.001 * 35.0)
        
    return delta.reshape(1, 63)


def make_ctrl(pitch=0.0, yaw=0.0, roll=0.0, aus=None) -> dict:
    """Retorna dict de controle calibrado com tipos float32 estritos."""
    d = {
        "delta_pitch": np.float32(pitch),
        "delta_yaw": np.float32(yaw),
        "delta_roll": np.float32(roll),
    }
    if aus:
        d["delta_exp"] = aus_to_delta_exp(aus)
    return d


def gerar_todas_trajetorias(audio_path: str, portrait_path: str, out_dir: str):
    print("=" * 80)
    print("PROVA DE FOGO: INFERENCIA COMPARATIVA DE TODOS OS MODELOS")
    print(f"Audio de Teste: {audio_path}")
    print(f"Retrato Fonte:  {portrait_path}")
    print("=" * 80)

    lab = Lab()
    total_frames = 242

    # -------------------------------------------------------------------------
    # 1. MODELO 1: VASA-1 (Microsoft Research)
    # -------------------------------------------------------------------------
    print("\n[1/6] Inferindo VASA-1 (Dinamica holistica pura sem diretivas manuais)...")
    npz_vasa = os.path.join(out_dir, "trajetoria_02_vasa1.npz")
    lab.generate_motion(
        audio_path=audio_path,
        source=portrait_path,
        out_npz=npz_vasa,
        emo=None,
        seed=42,
        ctrl=None
    )
    print("  -> VASA-1 inferido com sucesso.")

    # -------------------------------------------------------------------------
    # 2. MODELO 2: AUHead (ICLR 2026) — Mapeamento Muscular FACS
    # -------------------------------------------------------------------------
    print("\n[2/6] Inferindo AUHead (Controle muscular via Action Units FACS)...")
    ctrl_auhead = []
    for f in range(total_frames):
        aus = {}
        # Fase 1 (0..60): Foco analitico (AU04 corrugador)
        if f < 60:
            aus['AU04'] = 0.35
            aus['AU02'] = 0.15
        # Fase 2 (60..115): Silencio / repouso
        elif 60 <= f < 115:
            pass
        # Fase 3 (115..242): Entusiasmo e sorriso (AU12 zigomatico + AU06 orbicular)
        else:
            t = smoothstep(115, 140, f)
            aus['AU12'] = 0.35 * t
            aus['AU06'] = 0.25 * t
        ctrl_auhead.append(make_ctrl(aus=aus))

    npz_auhead = os.path.join(out_dir, "trajetoria_03_auhead.npz")
    lab.generate_motion(
        audio_path=audio_path,
        source=portrait_path,
        out_npz=npz_auhead,
        emo=None,
        seed=42,
        ctrl=ctrl_auhead
    )
    print("  -> AUHead inferido com sucesso.")

    # -------------------------------------------------------------------------
    # 3. MODELO 3: InstructAvatar (AAAI 2025) — Direcao Cenica NLP
    # -------------------------------------------------------------------------
    print("\n[3/6] Inferindo InstructAvatar (Direcao cenica e atenuacao labial adaptativa)...")
    ctrl_instruct = []
    for f in range(total_frames):
        aus = {}
        p = -2.0  # Postura altiva constante
        if f >= 115:
            p = -2.8
            aus['AU12'] = 0.20
            aus['AU06'] = 0.15
        ctrl_instruct.append(make_ctrl(pitch=p, aus=aus))

    npz_instruct = os.path.join(out_dir, "trajetoria_04_instruct.npz")
    lab.generate_motion(
        audio_path=audio_path,
        source=portrait_path,
        out_npz=npz_instruct,
        emo=None,
        seed=42,
        ctrl=ctrl_instruct
    )
    print("  -> InstructAvatar inferido com sucesso.")

    # -------------------------------------------------------------------------
    # 4. MODELO 4: Audio2Photoreal (Meta Reality Labs, CVPR 2024)
    # -------------------------------------------------------------------------
    print("\n[4/6] Inferindo Audio2Photoreal (Escuta ativa com acenos e boca selada)...")
    ctrl_diadico = []
    for f in range(total_frames):
        p = 0.0
        aus = {}
        # Fase de silencio (60..115): Executa 2 acenos harmonicos (Nodding a 2.2 Hz)
        if 60 <= f < 115:
            dt = (f - 60) / 25.0
            p = float(2.2 * np.sin(2.0 * np.pi * 1.5 * dt) * np.exp(-((dt - 1.1) ** 2) / 0.4))
            aus['AU26'] = -0.50  # Forca fechamento labial absoluto em repouso
        ctrl_diadico.append(make_ctrl(pitch=p, aus=aus))

    npz_diadico = os.path.join(out_dir, "trajetoria_05_audio2photoreal.npz")
    lab.generate_motion(
        audio_path=audio_path,
        source=portrait_path,
        out_npz=npz_diadico,
        emo=None,
        seed=42,
        ctrl=ctrl_diadico
    )
    print("  -> Audio2Photoreal inferido com sucesso.")

    # -------------------------------------------------------------------------
    # 5. MODELO 5: OmniHuman-1.5 (ByteDance, 2025) — Arquitetura Dual
    # -------------------------------------------------------------------------
    print("\n[5/6] Inferindo OmniHuman-1.5 (Sistema 1 + Sistema 2 deliberativo com Gaze Aversion)...")
    ctrl_omnihuman = []
    for f in range(total_frames):
        p, y, r = 0.0, 0.0, 0.0
        aus = {}
        # Arco 1: Pensamento analitico (0..60)
        if f < 60:
            p = 1.2
            aus['AU04'] = 0.20
        # Arco 2: Pausa reflexiva e Gaze Aversion (60..115)
        elif 60 <= f < 115:
            t_in = smoothstep(60, 75, f)
            t_out = 1.0 - smoothstep(100, 115, f)
            env = t_in * t_out if f < 100 else t_out
            y = -3.8 * env
            p = -1.6 * env
            r = 1.2 * env
            aus['AU02'] = 0.15 * env
        # Arco 3: Conviccao assertiva e queixo elevado (115..242)
        else:
            t_up = smoothstep(115, 135, f)
            p = -3.2 * t_up
            y = 0.3 * t_up
            aus['AU12'] = 0.25 * t_up
        ctrl_omnihuman.append(make_ctrl(pitch=p, yaw=y, roll=r, aus=aus))

    npz_omnihuman = os.path.join(out_dir, "trajetoria_06_omnihuman.npz")
    lab.generate_motion(
        audio_path=audio_path,
        source=portrait_path,
        out_npz=npz_omnihuman,
        emo=None,
        seed=42,
        ctrl=ctrl_omnihuman
    )
    print("  -> OmniHuman-1.5 inferido com sucesso.")

    # -------------------------------------------------------------------------
    # 6. MODELO 6: Motion Diffusion Model (MDM / DDPM - ICLR 2023)
    # -------------------------------------------------------------------------
    print("\n[6/6] Inferindo Motion Diffusion Model (Amostragem estocastica viva contra o colapso a media)...")
    npz_mdm = os.path.join(out_dir, "trajetoria_07_mdm.npz")
    lab.generate_motion(
        audio_path=audio_path,
        source=portrait_path,
        out_npz=npz_mdm,
        emo=None,
        seed=101,
        ctrl=None,
        sampling_timesteps=50
    )
    print("  -> MDM inferido com sucesso.")

    print("\n" + "=" * 80)
    print("TODAS AS 6 TRAJETORIAS FORAM GERADAS E SALVAS EM:")
    print(f"-> {out_dir}")
    print("=" * 80)


if __name__ == "__main__":
    dir_08 = os.path.dirname(os.path.abspath(__file__))
    audio_path = os.path.join(REPO_ROOT, "data", "prova_de_fogo.wav")
    portrait_path = os.path.join(REPO_ROOT, "data", "vasa_portrait.jpg")
    gerar_todas_trajetorias(audio_path, portrait_path, dir_08)
