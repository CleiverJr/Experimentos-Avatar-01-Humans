"""
Script executável para renderizar vídeos foto-realistas MP4 a partir da foto real e áudio gerado.
Gera o avatar com pele, olhos, barba e dentes reais se movendo e falando em sincronia com a voz.
"""

import os
import sys
import json

sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))
from src.photoreal_renderer import PhotorealAvatarRenderer


def render_all_photoreal_videos():
    base_dir = os.path.abspath(os.path.dirname(__file__))
    portrait_path = os.path.join(base_dir, "data", "vasa_portrait.jpg")
    output_dir = os.path.join(base_dir, "output")
    os.makedirs(output_dir, exist_ok=True)

    renderer = PhotorealAvatarRenderer(portrait_path, target_size=512)

    # 1. Renderiza o VASA-1 Foto-Realista
    lab_json_path = os.path.join(base_dir, "laboratorio_sementes", "laboratorio_completo.json")
    with open(lab_json_path, "r", encoding="utf-8") as f:
        lab_data = json.load(f)

    vasa_frames = lab_data["vasa"]["frames"]
    vasa_wav = os.path.join(base_dir, "laboratorio_sementes", "audio", "vasa_speech.wav")
    vasa_mp4 = os.path.join(output_dir, "vasa1_avatar_realista.mp4")

    print("\n" + "=" * 70)
    print("🎬 [1/2] GERANDO VÍDEO FOTO-REALISTA VASA-1 (MICROSOFT RESEARCH)")
    print("=" * 70)
    renderer.render_video_with_audio(vasa_frames, vasa_wav, vasa_mp4, fps=30.0)

    # 2. Renderiza o teste personalizado do Cleiver ("Bem-vindos ao laboratório...")
    cleiver_json = os.path.join(output_dir, "meu_teste_animation.json")
    if os.path.exists(cleiver_json):
        with open(cleiver_json, "r", encoding="utf-8") as f:
            c_data = json.load(f)

        cleiver_frames = []
        for f in c_data["frames"]:
            cleiver_frames.append({
                "p": f["head_pose"]["rotation_euler_deg"][0],
                "y": f["head_pose"]["rotation_euler_deg"][1],
                "r": f["head_pose"]["rotation_euler_deg"][2],
                "smile": f["facs_action_units"]["AU_07"],
                "brow": f["facs_action_units"]["AU_00"],
                "jaw": f["facs_action_units"]["AU_12"],
                "blink": f["facs_action_units"]["AU_13"]
            })

        cleiver_wav = os.path.join(output_dir, "meu_teste_audio.wav")
        cleiver_mp4 = os.path.join(output_dir, "meu_teste_avatar_realista.mp4")

        print("\n" + "=" * 70)
        print("🎬 [2/2] GERANDO VÍDEO FOTO-REALISTA: 'MEU TESTE' (CLEIVER)")
        print("=" * 70)
        renderer.render_video_with_audio(cleiver_frames, cleiver_wav, cleiver_mp4, fps=30.0)

    print("\n✨ TODOS OS VÍDEOS FOTO-REALISTAS FORAM GERADOS COM SUCESSO!")
    print(f"   -> {vasa_mp4}")
    if os.path.exists(cleiver_json):
        print(f"   -> {cleiver_mp4}")


if __name__ == "__main__":
    render_all_photoreal_videos()
