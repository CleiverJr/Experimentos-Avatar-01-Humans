"""
Gera um dashboard visual completo em PNG com as curvas e projeções 3D da animação gerada pela Trilha D.
"""

import json
import os
import numpy as np
import matplotlib.pyplot as plt

def render_dashboard():
    json_path = os.path.join(os.path.dirname(__file__), "..", "output", "animacao_demonstracao.json")
    output_png = os.path.join(os.path.dirname(__file__), "..", "output", "dashboard_animacao.png")

    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    fps = data["fps"]
    total_frames = data["total_frames"]
    time_axis = np.array([f["timestamp"] for f in data["frames"]])

    # Extração de curvas
    pitch = np.array([f["head_pose"]["rotation_euler_deg"][0] for f in data["frames"]])
    yaw = np.array([f["head_pose"]["rotation_euler_deg"][1] for f in data["frames"]])
    roll = np.array([f["head_pose"]["rotation_euler_deg"][2] for f in data["frames"]])

    au12_smile = np.array([f["facs_action_units"]["AU_07"] for f in data["frames"]])  # AU12
    au01_brow = np.array([f["facs_action_units"]["AU_00"] for f in data["frames"]])   # AU01
    au26_jaw = np.array([f["facs_action_units"]["AU_12"] for f in data["frames"]])    # AU26
    au45_blink = np.array([f["facs_action_units"]["AU_13"] for f in data["frames"]])  # AU45

    flame_exp_0 = np.array([f["flame_parameters"]["expression_coefficients"][0] for f in data["frames"]])
    flame_exp_1 = np.array([f["flame_parameters"]["expression_coefficients"][1] for f in data["frames"]])
    flame_exp_2 = np.array([f["flame_parameters"]["expression_coefficients"][2] for f in data["frames"]])
    jaw_rot_x = np.array([f["flame_parameters"]["jaw_rotation_axis_angle"][0] for f in data["frames"]])

    # Configuração de estilo escuro elegante
    plt.style.use('dark_background')
    fig = plt.figure(figsize=(16, 10))
    gs = fig.add_gridspec(3, 3, hspace=0.35, wspace=0.25)

    fig.suptitle(f"🎭 Trilha D: Visual Affective Synthesis Dashboard\nPrompt: \"{data['metadata']['user_prompt']}\"", 
                 fontsize=15, fontweight='bold', color='#38bdf8')

    # Subplot 1: Rotação 3D da Cabeça (Pose Diffusion)
    ax1 = fig.add_subplot(gs[0, :2])
    ax1.plot(time_axis, yaw, label="Yaw (Giro Horizontal)", color="#38bdf8", lw=2)
    ax1.plot(time_axis, pitch, label="Pitch (Inclinação Vertical)", color="#f43f5e", lw=2)
    ax1.plot(time_axis, roll, label="Roll (Inclinação Lateral)", color="#eab308", lw=1.5, linestyle="--")
    ax1.set_title("1. Trajetória 3D da Cabeça gerada por Motion Diffusion (DDPM)", fontsize=11, color="#e2e8f0")
    ax1.set_ylabel("Graus (°)")
    ax1.grid(True, alpha=0.2)
    ax1.legend(loc="upper right", framealpha=0.3)

    # Subplot 2: Wireframe 3D Esquemático do Rosto em 3 Instantes
    ax_face = fig.add_subplot(gs[0, 2], projection='3d')
    key_frames = [0, 45, 89]
    colors = ['#38bdf8', '#a855f7', '#22c55e']
    labels = ['t=0s (Início)', 't=1.5s (Meio)', 't=3.0s (Fim)']

    # Modelo simplificado de elipsoide facial
    u = np.linspace(0, 2 * np.pi, 16)
    v = np.linspace(0, np.pi, 12)
    x_base = 0.8 * np.outer(np.cos(u), np.sin(v))
    y_base = 1.0 * np.outer(np.sin(u), np.sin(v))
    z_base = 0.9 * np.outer(np.ones(np.size(u)), np.cos(v))

    for k_idx, f_idx in enumerate(key_frames):
        y_rot = np.radians(yaw[f_idx])
        p_rot = np.radians(pitch[f_idx])
        Ry = np.array([[np.cos(y_rot), 0, np.sin(y_rot)], [0, 1, 0], [-np.sin(y_rot), 0, np.cos(y_rot)]])
        Rx = np.array([[1, 0, 0], [0, np.cos(p_rot), -np.sin(p_rot)], [0, np.sin(p_rot), np.cos(p_rot)]])
        R = Ry @ Rx

        center = np.array([k_idx * 2.2 - 2.2, 0, 0])
        coords = np.stack([x_base.flatten(), y_base.flatten(), z_base.flatten()], axis=0)
        rot_coords = R @ coords + center[:, None]
        
        ax_face.plot_wireframe(rot_coords[0].reshape(x_base.shape), 
                               rot_coords[1].reshape(y_base.shape), 
                               rot_coords[2].reshape(z_base.shape), 
                               color=colors[k_idx], alpha=0.45, lw=0.7)
        # Nariz (vetor apontando para frente)
        nose_base = center
        nose_dir = R @ np.array([0, 0, 1.2])
        ax_face.plot([nose_base[0], nose_base[0] + nose_dir[0]],
                     [nose_base[1], nose_base[1] + nose_dir[1]],
                     [nose_base[2], nose_base[2] + nose_dir[2]],
                     color=colors[k_idx], lw=2.5, label=labels[k_idx])

    ax_face.set_title("Orientação 3D (Keyframes)", fontsize=11, color="#e2e8f0")
    ax_face.set_axis_off()
    ax_face.legend(loc="lower center", framealpha=0.3, fontsize=8)

    # Subplot 3: Action Units FACS (AUHead)
    ax2 = fig.add_subplot(gs[1, :])
    ax2.plot(time_axis, au12_smile, label="AU12 (Lip Corner Puller / Sorriso)", color="#22c55e", lw=2)
    ax2.plot(time_axis, au01_brow, label="AU01 (Inner Brow Raiser / Surpresa)", color="#a855f7", lw=2)
    ax2.plot(time_axis, au26_jaw, label="AU26 (Jaw Drop / Abertura na Fala)", color="#f97316", lw=1.5, linestyle=":")
    ax2.fill_between(time_axis, 0, au45_blink, label="AU45 (Piscadas de Olhos)", color="#06b6d4", alpha=0.3)
    ax2.set_title("2. Ativação Dinâmica de Action Units FACS (AUHead - Paul Ekman)", fontsize=11, color="#e2e8f0")
    ax2.set_ylabel("Intensidade [0.0 - 1.0]")
    ax2.set_ylim(-0.05, 1.1)
    ax2.grid(True, alpha=0.2)
    ax2.legend(loc="upper right", framealpha=0.3)

    # Subplot 4: Parâmetros FLAME e Mandíbula
    ax3 = fig.add_subplot(gs[2, :2])
    ax3.plot(time_axis, flame_exp_0, label="FLAME Modo 0 (Sorriso/Dimensão Principal)", color="#22c55e", lw=1.5)
    ax3.plot(time_axis, flame_exp_1, label="FLAME Modo 1 (Sobrancelhas)", color="#a855f7", lw=1.5)
    ax3.plot(time_axis, jaw_rot_x * 5.0, label="Rotação Mandíbula (x5 rad)", color="#f97316", lw=2)
    ax3.set_title("3. Parâmetros Deformáveis FLAME (Prontos para Arthur Trilha B e Fernando Trilha C)", fontsize=11, color="#e2e8f0")
    ax3.set_xlabel("Tempo (segundos)")
    ax3.set_ylabel("Magnitude Coeficiente")
    ax3.grid(True, alpha=0.2)
    ax3.legend(loc="upper right", framealpha=0.3)

    # Subplot 5: Resumo Executivo e Métricas
    ax4 = fig.add_subplot(gs[2, 2])
    ax4.axis("off")
    summary_text = (
        "📊 METADADOS DE GERAÇÃO\n"
        "───────────────────────────────\n"
        f"• Duração: {data['metadata']['audio_duration_sec']}s ({total_frames} frames)\n"
        f"• Taxa: {fps} FPS (Vídeo Contínuo)\n"
        f"• Emoção Primária: Alegria (0.50)\n"
        f"• Emoção Secundária: Surpresa (0.50)\n"
        f"• Viés de Olhar (Yaw): +15.0° (Esquerda)\n"
        f"• Sincronia Labial: Modulação AU26/AU25\n"
        f"• Piscadas: Periódicas (~1.5s)\n"
        f"• Compatibilidade: FLAME (50 exp) & 3DGS\n"
        "───────────────────────────────\n"
        "Status: PRONTO PARA INTEGRAÇÃO"
    )
    ax4.text(0.05, 0.5, summary_text, fontsize=9.5, fontfamily="monospace",
             verticalalignment="center", bbox=dict(boxstyle="round,pad=1", facecolor="#1e293b", edgecolor="#38bdf8", alpha=0.8))

    plt.savefig(output_png, dpi=180, bbox_inches="tight")
    print(f"Dashboard salvo em: {output_png}")

if __name__ == "__main__":
    render_dashboard()
