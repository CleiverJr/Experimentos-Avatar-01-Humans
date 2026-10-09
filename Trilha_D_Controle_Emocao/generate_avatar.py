"""
Pipeline CLI Completo da Trilha D:
Recebe um Prompt e/ou Fala -> Gera o Áudio (TTS) -> Detecta Emoções -> Difunde o Movimento 3D -> Gera Visualizador com Som.
"""

import os
import sys
import argparse
import base64
import json
import time
import numpy as np
import matplotlib.pyplot as plt

# Garante inclusão de src no path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from src.tts_generator import SpeechSynthesizer
from src.audio_processor import AudioProcessor
from src.action_units import ActionUnitsSystem
from src.motion_diffusion import DDPMScheduler, TemporalMotionDenoiser, MotionDiffusionPipeline
from src.instruct_parser import InstructParser
from src.exporter import MotionExporter


def generate_avatar(prompt: str, speech_text: str = None, seed: int = 42, output_name: str = "avatar_custom"):
    start_time = time.time()
    
    # Se speech_text não foi passado, gera uma fala adequada ou usa o prompt
    if not speech_text:
        speech_text = prompt

    print("=" * 70)
    print("🎭 PIPELINE TRILHA D: PROMPT -> ÁUDIO -> EMOÇÕES -> MOVIMENTO 3D")
    print("=" * 70)
    print(f"📝 Prompt de Atuação: \"{prompt}\"")
    print(f"🗣️  Texto Falado:      \"{speech_text}\"")
    print(f"🎲 Semente (Seed):    {seed}")

    output_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "output"))
    os.makedirs(output_dir, exist_ok=True)

    # 1. GERAÇÃO DO ÁUDIO (TTS)
    print("\n[1/5] Sintetizando voz do avatar...")
    tts = SpeechSynthesizer(sample_rate=16000)
    wav_path = os.path.join(output_dir, f"{output_name}_audio.wav")
    audio_data, duration_sec = tts.synthesize(speech_text, wav_path)
    print(f"      ✓ Áudio gerado: {wav_path} ({duration_sec:.2f} segundos)")

    # 2. PROCESSAMENTO ACÚSTICO
    print("\n[2/5] Extraindo representações acústicas alinhadas por frame...")
    fps = 30.0
    audio_proc = AudioProcessor(sample_rate=16000, n_mels=80, fps=fps)
    audio_features = audio_proc.extract_features(audio_data)
    mel_spectrogram = audio_features["mel_spectrogram"]
    energy_rms = audio_features["energy_rms"]
    total_frames = audio_features["num_frames"]
    print(f"      ✓ Frames totais a {fps} FPS: {total_frames} frames")
    print(f"      ✓ Mel-Spectrogram: {mel_spectrogram.shape}, Energia RMS: min={np.min(energy_rms):.3f}, max={np.max(energy_rms):.3f}")

    # 3. DETECÇÃO DE EMOÇÕES E VIESES (INSTRUCTAVATAR / OMNIHUMAN)
    print("\n[3/5] Analisando semântica, emoções e intenção motora do prompt...")
    parser = InstructParser(embedding_dim=16)
    parsed = parser.parse_instruction(prompt)
    emotions = parsed["emotion_weights"]
    intensity = parsed["intensity"]
    head_bias = parsed["head_bias"]
    cond_vector = parsed["conditioning_vector"]
    
    print(f"      ✓ Emoções detectadas: {emotions}")
    print(f"      ✓ Intensidade emocional: {intensity:.2f}")
    print(f"      ✓ Vieses de pose de cabeça: Yaw={head_bias['yaw_deg']}°, Pitch={head_bias['pitch_deg']}°, Aceno={head_bias['nodding']}")

    # 4. SÍNTESE DE ACTION UNITS (FACS) E MODULAÇÃO DA FALA
    print("\n[4/5] Mapeando músculos faciais FACS e sincronia labial...")
    facs = ActionUnitsSystem(num_flame_exp=50)
    base_au = facs.blend_emotions(emotions)
    base_au_seq = np.tile(base_au, (total_frames, 1))
    
    # Modulação da mandíbula pela energia real da fala sintetizada + piscadas
    modulated_au = facs.modulate_with_speech(base_au_seq, energy_rms, blink_interval=45)
    
    flame_trajectories = []
    flame_exp_matrix = np.zeros((total_frames, 50), dtype=np.float32)
    flame_jaw_matrix = np.zeros((total_frames, 3), dtype=np.float32)
    for t in range(total_frames):
        ff = facs.au_to_flame(modulated_au[t])
        flame_trajectories.append(ff)
        flame_exp_matrix[t] = ff["expression_coefficients"]
        flame_jaw_matrix[t] = ff["jaw_rotation"]
    print(f"      ✓ 14 Action Units moduladas dinamicamente")
    print(f"      ✓ 50 coeficientes de deformação FLAME gerados")

    # 5. DIFUSÃO DE MOVIMENTO 3D DA CABEÇA (MOTION DIFFUSION / VASA-1)
    print("\n[5/5] Executando difusão estocástica de trajetória de cabeça (DDPM)...")
    scheduler = DDPMScheduler(num_timesteps=50)
    denoiser = TemporalMotionDenoiser(motion_dim=6, audio_dim=80, emo_dim=16, hidden_dim=64)
    pipeline = MotionDiffusionPipeline(denoiser, scheduler)
    
    # Amostragem reversa
    head_traj = pipeline.sample(mel_spectrogram, cond_vector, guidance_scale=2.0, seed=seed)
    # Injeta vieses de rotação de cabeça
    head_traj[:, 1] += head_bias["yaw_deg"]
    head_traj[:, 0] += head_bias["pitch_deg"]
    if head_bias["nodding"]:
        nod_wave = 4.0 * np.sin(np.linspace(0, 4 * np.pi, total_frames))
        head_traj[:, 0] += nod_wave
    print(f"      ✓ Trajetória contínua 3D gerada: {head_traj.shape}")

    # 6. EXPORTAÇÃO DOS ARQUIVOS
    exporter = MotionExporter(fps=fps)
    meta = {
        "user_prompt": prompt,
        "speech_text": speech_text,
        "emotions": emotions,
        "intensity": intensity,
        "head_bias": head_bias,
        "audio_duration_sec": duration_sec,
        "seed": seed
    }
    json_path = os.path.join(output_dir, f"{output_name}_animation.json")
    package = exporter.assemble_animation_package(head_traj, modulated_au, flame_trajectories, meta)
    exporter.save_json(package, json_path)

    npz_path = os.path.join(output_dir, f"{output_name}_animation.npz")
    exporter.save_npz(head_traj, modulated_au, flame_exp_matrix, flame_jaw_matrix, npz_path)

    # 7. GERAÇÃO DO DASHBOARD EM IMAGEM (PNG)
    png_path = os.path.join(output_dir, f"{output_name}_dashboard.png")
    generate_dashboard_plot(package, png_path)

    # 8. GERAÇÃO DO PLAYER INTERATIVO HTML COM ÁUDIO SINCRONIZADO
    with open(wav_path, "rb") as f_wav:
        wav_base64 = base64.b64encode(f_wav.read()).decode("utf-8")

    html_path = os.path.join(output_dir, f"{output_name}_player.html")
    generate_interactive_player(package, wav_base64, html_path)

    # Copia também para o diretório de artifacts do sistema para exibição imediata
    artifact_dir = "/Users/cleiver/.gemini/antigravity/brain/43ca0243-7920-487b-a12e-0e566e30e831"
    artifact_html = os.path.join(artifact_dir, "visualizador_avatar_audio.html")
    generate_interactive_player(package, wav_base64, artifact_html)

    elapsed = time.time() - start_time
    print("\n" + "=" * 70)
    print(f"✨ AVATAR GERADO COM SUCESSO EM {elapsed:.2f}s!")
    print(f"   🔊 Áudio Real WAV:     {wav_path}")
    print(f"   📊 Telemetria PNG:     {png_path}")
    print(f"   💾 Dados JSON e NPZ:   {json_path} | {npz_path}")
    print(f"   🎬 Player com Som:     {html_path}")
    print("=" * 70 + "\n")

    return {
        "wav_path": wav_path,
        "png_path": png_path,
        "json_path": json_path,
        "npz_path": npz_path,
        "html_path": html_path,
        "artifact_html": artifact_html,
        "metadata": meta,
        "total_frames": total_frames
    }


def generate_dashboard_plot(package: dict, output_png: str):
    """Gera gráfico PNG estilizado da animação gerada."""
    time_axis = np.array([f["timestamp"] for f in package["frames"]])
    yaw = np.array([f["head_pose"]["rotation_euler_deg"][1] for f in package["frames"]])
    pitch = np.array([f["head_pose"]["rotation_euler_deg"][0] for f in package["frames"]])
    roll = np.array([f["head_pose"]["rotation_euler_deg"][2] for f in package["frames"]])
    
    au_smile = np.array([f["facs_action_units"]["AU_07"] for f in package["frames"]])
    au_brow = np.array([f["facs_action_units"]["AU_00"] for f in package["frames"]])
    au_jaw = np.array([f["facs_action_units"]["AU_12"] for f in package["frames"]])
    au_blink = np.array([f["facs_action_units"]["AU_13"] for f in package["frames"]])

    plt.style.use('dark_background')
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 6), sharex=True)
    
    fig.suptitle(f"Avatar Synthesis: \"{package['metadata']['user_prompt']}\"", fontsize=12, color='#38bdf8', fontweight='bold')
    
    ax1.plot(time_axis, yaw, label="Yaw (Giro)", color="#38bdf8", lw=2)
    ax1.plot(time_axis, pitch, label="Pitch (Vertical)", color="#f43f5e", lw=2)
    ax1.plot(time_axis, roll, label="Roll (Lateral)", color="#eab308", lw=1.5, linestyle="--")
    ax1.set_ylabel("Pose da Cabeça (°)")
    ax1.grid(True, alpha=0.2)
    ax1.legend(loc="upper right", framealpha=0.3)

    ax2.plot(time_axis, au_smile, label="AU12 (Sorriso)", color="#22c55e", lw=2)
    ax2.plot(time_axis, au_brow, label="AU01 (Sobrancelha)", color="#a855f7", lw=2)
    ax2.plot(time_axis, au_jaw, label="AU26 (Abertura Mandíbula na Fala)", color="#f97316", lw=1.8)
    ax2.fill_between(time_axis, 0, au_blink, label="AU45 (Piscada)", color="#06b6d4", alpha=0.3)
    ax2.set_xlabel("Tempo (segundos)")
    ax2.set_ylabel("Ativação FACS")
    ax2.grid(True, alpha=0.2)
    ax2.legend(loc="upper right", framealpha=0.3)

    plt.tight_layout()
    plt.savefig(output_png, dpi=160)
    plt.close()


def generate_interactive_player(package: dict, wav_base64: str, output_html: str):
    """Gera o arquivo HTML com player 3D e áudio sincronizado."""
    frames_compact = []
    for f in package["frames"]:
        frames_compact.append({
            "t": f["timestamp"],
            "p": f["head_pose"]["rotation_euler_deg"][0],
            "y": f["head_pose"]["rotation_euler_deg"][1],
            "r": f["head_pose"]["rotation_euler_deg"][2],
            "smile": f["facs_action_units"]["AU_07"],
            "brow": f["facs_action_units"]["AU_00"],
            "jaw": f["facs_action_units"]["AU_12"],
            "blink": f["facs_action_units"]["AU_13"]
        })

    json_frames_str = json.dumps(frames_compact)
    meta = package["metadata"]
    emo_summary = ", ".join([f"{k.capitalize()}: {v*100:.0f}%" for k, v in meta["emotions"].items()])

    html_content = f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
  <meta charset="UTF-8">
  <title>Avatar 3D com Áudio Sincronizado - Trilha D</title>
  <script src="https://www.gstatic.com/antigravity/web/dev/tailwindcss.min.js"></script>
</head>
<body class="bg-transparent text-[var(--foreground)] antialiased p-3 select-none">
  <!-- Áudio real sintetizado embutido em Base64 -->
  <audio id="speechAudio" src="data:audio/wav;base64,{wav_base64}" preload="auto"></audio>

  <div class="bg-[var(--card)] text-[var(--foreground)] border border-[var(--border)] rounded-2xl p-4 shadow-xl max-w-4xl mx-auto">
    <!-- Header -->
    <div class="flex items-center justify-between pb-3 mb-3 border-b border-[var(--border)]">
      <div>
        <div class="flex items-center gap-2">
          <span class="text-xs font-semibold px-2 py-0.5 rounded-full bg-emerald-500/20 text-emerald-400 border border-emerald-500/30">Áudio + Expressão Sincronizados</span>
          <span class="text-xs text-[var(--muted-foreground)]">Trilha D: Maestro</span>
        </div>
        <h2 class="text-base font-bold text-[var(--foreground)] mt-1">"{meta['speech_text']}"</h2>
        <p class="text-xs text-[var(--muted-foreground)]">Emoções Detectadas: <span class="text-emerald-400 font-semibold">{emo_summary}</span> | Intensidade: <span class="font-mono text-sky-400">{meta['intensity']:.2f}x</span></p>
      </div>
      <div class="text-right">
        <span id="badgeBlink" class="text-xs font-mono px-2 py-0.5 rounded bg-emerald-500/20 text-emerald-400 border border-emerald-500/30">Olhos Abertos</span>
      </div>
    </div>

    <!-- Main Grid -->
    <div class="grid grid-cols-1 md:grid-cols-12 gap-4 items-center">
      <!-- 3D Canvas Viewport -->
      <div class="md:col-span-6 flex flex-col items-center justify-center bg-[var(--background)]/60 rounded-xl p-2 border border-[var(--border)]/70 relative overflow-hidden">
        <div class="absolute top-2 left-2 text-[11px] font-mono text-[var(--muted-foreground)] bg-[var(--card)]/80 px-2 py-0.5 rounded border border-[var(--border)]">
          Render 3D Sincronizado
        </div>
        <canvas id="avatarCanvas" width="340" height="250" class="w-full max-w-[340px] h-[230px]"></canvas>
      </div>

      <!-- Telemetry & Action Units -->
      <div class="md:col-span-6 flex flex-col justify-between h-full space-y-3">
        <!-- Pose Rígida 3D -->
        <div class="bg-[var(--background)]/40 p-2.5 rounded-lg border border-[var(--border)]">
          <div class="flex justify-between items-center mb-1">
            <span class="text-xs font-semibold text-sky-400">Pose de Cabeça 3D (Motion Diffusion)</span>
            <span class="text-[10px] font-mono text-[var(--muted-foreground)]">Ângulos Euler</span>
          </div>
          <div class="grid grid-cols-3 gap-2 text-center text-xs font-mono">
            <div class="bg-[var(--card)] p-1.5 rounded border border-[var(--border)]">
              <span class="text-[var(--muted-foreground)] block text-[10px]">Yaw (Giro)</span>
              <span id="valYaw" class="font-bold text-sky-400">0.0°</span>
            </div>
            <div class="bg-[var(--card)] p-1.5 rounded border border-[var(--border)]">
              <span class="text-[var(--muted-foreground)] block text-[10px]">Pitch (Vertical)</span>
              <span id="valPitch" class="font-bold text-rose-400">0.0°</span>
            </div>
            <div class="bg-[var(--card)] p-1.5 rounded border border-[var(--border)]">
              <span class="text-[var(--muted-foreground)] block text-[10px]">Roll (Lateral)</span>
              <span id="valRoll" class="font-bold text-amber-400">0.0°</span>
            </div>
          </div>
        </div>

        <!-- Action Units FACS -->
        <div class="bg-[var(--background)]/40 p-2.5 rounded-lg border border-[var(--border)] space-y-2">
          <div class="flex justify-between items-center">
            <span class="text-xs font-semibold text-emerald-400">Action Units FACS (AUHead)</span>
            <span class="text-[10px] font-mono text-[var(--muted-foreground)]">Ativação Muscular</span>
          </div>
          
          <div>
            <div class="flex justify-between text-xs mb-0.5">
              <span>AU12: Sorriso (Alegria)</span>
              <span id="txtAU12" class="font-mono text-emerald-400">0.00</span>
            </div>
            <div class="w-full bg-[var(--card)] h-1.5 rounded-full overflow-hidden">
              <div id="barAU12" class="bg-emerald-500 h-full rounded-full transition-all duration-75" style="width: 0%"></div>
            </div>
          </div>

          <div>
            <div class="flex justify-between text-xs mb-0.5">
              <span>AU01: Sobrancelhas (Surpresa)</span>
              <span id="txtAU01" class="font-mono text-purple-400">0.00</span>
            </div>
            <div class="w-full bg-[var(--card)] h-1.5 rounded-full overflow-hidden">
              <div id="barAU01" class="bg-purple-500 h-full rounded-full transition-all duration-75" style="width: 0%"></div>
            </div>
          </div>

          <div>
            <div class="flex justify-between text-xs mb-0.5">
              <span>AU26: Abertura Mandíbula (Sincronizada à Voz)</span>
              <span id="txtAU26" class="font-mono text-amber-400">0.00</span>
            </div>
            <div class="w-full bg-[var(--card)] h-1.5 rounded-full overflow-hidden">
              <div id="barAU26" class="bg-amber-500 h-full rounded-full transition-all duration-75" style="width: 0%"></div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Playback Controls Bar com Áudio -->
    <div class="mt-4 pt-3 border-t border-[var(--border)] flex flex-col gap-2">
      <div class="flex items-center gap-3">
        <button id="btnPlay" class="px-4 py-1.5 rounded-lg bg-emerald-500 text-slate-950 font-bold text-xs hover:bg-emerald-400 transition-colors flex items-center gap-1.5 shadow-md">
          <span id="playIcon">▶</span> <span id="playLabel">Ouvir & Assistir</span>
        </button>
        <button id="btnMute" class="px-2.5 py-1.5 rounded-lg bg-[var(--card)] border border-[var(--border)] text-xs font-mono hover:bg-[var(--card)]/80 transition-colors">
          🔊 Som Ativado
        </button>
        <input id="sliderFrame" type="range" min="0" max="{len(frames_compact) - 1}" value="0" class="flex-1 accent-emerald-500 cursor-pointer h-2 bg-[var(--border)] rounded-lg">
        <span id="txtTime" class="text-xs font-mono text-[var(--muted-foreground)] w-32 text-right">0.00s / {meta['audio_duration_sec']:.2f}s</span>
      </div>
    </div>
  </div>

  <script>
    const FRAMES_DATA = {json_frames_str};
    const totalDuration = {meta['audio_duration_sec']};
    const fps = 30.0;

    const audio = document.getElementById("speechAudio");
    const canvas = document.getElementById("avatarCanvas");
    const ctx = canvas.getContext("2d");

    const slider = document.getElementById("sliderFrame");
    const btnPlay = document.getElementById("btnPlay");
    const playIcon = document.getElementById("playIcon");
    const playLabel = document.getElementById("playLabel");
    const btnMute = document.getElementById("btnMute");
    const txtTime = document.getElementById("txtTime");
    const valYaw = document.getElementById("valYaw");
    const valPitch = document.getElementById("valPitch");
    const valRoll = document.getElementById("valRoll");
    const txtAU12 = document.getElementById("txtAU12");
    const barAU12 = document.getElementById("barAU12");
    const txtAU01 = document.getElementById("txtAU01");
    const barAU01 = document.getElementById("barAU01");
    const txtAU26 = document.getElementById("txtAU26");
    const barAU26 = document.getElementById("barAU26");
    const badgeBlink = document.getElementById("badgeBlink");

    let currentFrame = 0;

    const basePoints = [
      {{ x: -50, y: -70, z: -10 }}, {{ x: 0, y: -80, z: -5 }}, {{ x: 50, y: -70, z: -10 }},
      {{ x: -65, y: -20, z: 0 }},   {{ x: 65, y: -20, z: 0 }},
      {{ x: -60, y: 35, z: 10 }},   {{ x: 60, y: 35, z: 10 }},
      {{ x: 0, y: 75, z: 20 }},
      {{ x: -45, y: -35, z: 25 }}, {{ x: -30, y: -42, z: 28 }}, {{ x: -15, y: -38, z: 27 }},
      {{ x: 15, y: -38, z: 27 }}, {{ x: 30, y: -42, z: 28 }}, {{ x: 45, y: -35, z: 25 }},
      {{ x: -38, y: -22, z: 25 }}, {{ x: -28, y: -26, z: 27 }}, {{ x: -18, y: -22, z: 25 }}, {{ x: -28, y: -18, z: 27 }},
      {{ x: 18, y: -22, z: 25 }}, {{ x: 28, y: -26, z: 27 }}, {{ x: 38, y: -22, z: 25 }}, {{ x: 28, y: -18, z: 27 }},
      {{ x: 0, y: -20, z: 30 }}, {{ x: 0, y: 5, z: 42 }}, {{ x: -10, y: 15, z: 36 }}, {{ x: 10, y: 15, z: 36 }},
      {{ x: -28, y: 35, z: 28 }},
      {{ x: 0, y: 30, z: 34 }},
      {{ x: 28, y: 35, z: 28 }},
      {{ x: 0, y: 44, z: 34 }}
    ];

    function rotate3D(pt, pitchDeg, yawDeg, rollDeg) {{
      const p = (pitchDeg * Math.PI) / 180;
      const y = (yawDeg * Math.PI) / 180;
      const r = (rollDeg * Math.PI) / 180;

      let x1 = pt.x * Math.cos(y) + pt.z * Math.sin(y);
      let y1 = pt.y;
      let z1 = -pt.x * Math.sin(y) + pt.z * Math.cos(y);

      let x2 = x1;
      let y2 = y1 * Math.cos(p) - z1 * Math.sin(p);
      let z2 = y1 * Math.sin(p) + z1 * Math.cos(p);

      let x3 = x2 * Math.cos(r) - y2 * Math.sin(r);
      let y3 = x2 * Math.sin(r) + y2 * Math.cos(r);
      let z3 = z2;

      const fov = 280;
      const scale = fov / (fov + z3);
      return {{
        x: canvas.width / 2 + x3 * scale,
        y: canvas.height / 2 + y3 * scale
      }};
    }}

    function render() {{
      const f = FRAMES_DATA[currentFrame];
      ctx.clearRect(0, 0, canvas.width, canvas.height);

      valYaw.textContent = (f.y >= 0 ? "+" : "") + f.y.toFixed(1) + "°";
      valPitch.textContent = (f.p >= 0 ? "+" : "") + f.p.toFixed(1) + "°";
      valRoll.textContent = (f.r >= 0 ? "+" : "") + f.r.toFixed(1) + "°";

      txtAU12.textContent = f.smile.toFixed(2);
      barAU12.style.width = (f.smile * 100) + "%";

      txtAU01.textContent = f.brow.toFixed(2);
      barAU01.style.width = (f.brow * 100) + "%";

      txtAU26.textContent = f.jaw.toFixed(2);
      barAU26.style.width = (f.jaw * 100) + "%";

      slider.value = currentFrame;
      txtTime.textContent = f.t.toFixed(2) + "s / " + totalDuration.toFixed(2) + "s";

      if (f.blink > 0.4) {{
        badgeBlink.textContent = "Piscando (AU45)";
        badgeBlink.className = "text-xs font-mono px-2 py-0.5 rounded bg-cyan-500/20 text-cyan-400 border border-cyan-500/30";
      }} else {{
        badgeBlink.textContent = "Olhos Abertos";
        badgeBlink.className = "text-xs font-mono px-2 py-0.5 rounded bg-emerald-500/20 text-emerald-400 border border-emerald-500/30";
      }}

      const pts = basePoints.map(p => ({{ ...p }}));

      // Deformações FACS
      const browOffset = f.brow * 14;
      [8, 9, 10, 11, 12, 13].forEach(i => pts[i].y -= browOffset);

      const smileOffset = f.smile * 12;
      pts[22].x -= smileOffset * 0.5;
      pts[22].y -= smileOffset;
      pts[24].x += smileOffset * 0.5;
      pts[24].y -= smileOffset;

      const jawOffset = Math.max(0, (f.jaw - 0.22) * 40);
      pts[7].y += jawOffset * 0.8;
      pts[25].y += jawOffset;

      const proj = pts.map(pt => rotate3D(pt, f.p, f.y, f.r));

      // Cabeça
      ctx.strokeStyle = "rgba(56, 189, 248, 0.4)";
      ctx.lineWidth = 1.5;
      ctx.beginPath();
      ctx.moveTo(proj[0].x, proj[0].y);
      ctx.quadraticCurveTo(proj[1].x, proj[1].y, proj[2].x, proj[2].y);
      ctx.quadraticCurveTo(proj[4].x, proj[4].y, proj[6].x, proj[6].y);
      ctx.quadraticCurveTo(proj[7].x, proj[7].y, proj[5].x, proj[5].y);
      ctx.quadraticCurveTo(proj[3].x, proj[3].y, proj[0].x, proj[0].y);
      ctx.stroke();

      // Sobrancelhas
      ctx.strokeStyle = "#c084fc";
      ctx.lineWidth = 2.5;
      ctx.beginPath();
      ctx.moveTo(proj[8].x, proj[8].y);
      ctx.lineTo(proj[9].x, proj[9].y);
      ctx.lineTo(proj[10].x, proj[10].y);
      ctx.stroke();

      ctx.beginPath();
      ctx.moveTo(proj[11].x, proj[11].y);
      ctx.lineTo(proj[12].x, proj[12].y);
      ctx.lineTo(proj[13].x, proj[13].y);
      ctx.stroke();

      // Olhos
      ctx.strokeStyle = "#38bdf8";
      ctx.fillStyle = "#38bdf8";
      ctx.lineWidth = 1.8;
      if (f.blink > 0.5) {{
        ctx.beginPath();
        ctx.moveTo(proj[14].x, proj[14].y); ctx.lineTo(proj[16].x, proj[16].y);
        ctx.moveTo(proj[18].x, proj[18].y); ctx.lineTo(proj[20].x, proj[20].y);
        ctx.stroke();
      }} else {{
        ctx.beginPath();
        ctx.moveTo(proj[14].x, proj[14].y);
        ctx.quadraticCurveTo(proj[15].x, proj[15].y, proj[16].x, proj[16].y);
        ctx.quadraticCurveTo(proj[17].x, proj[17].y, proj[14].x, proj[14].y);
        ctx.stroke();
        ctx.beginPath();
        ctx.arc((proj[14].x + proj[16].x)/2, (proj[14].y + proj[16].y)/2, 2.5, 0, Math.PI * 2);
        ctx.fill();

        ctx.beginPath();
        ctx.moveTo(proj[18].x, proj[18].y);
        ctx.quadraticCurveTo(proj[19].x, proj[19].y, proj[20].x, proj[20].y);
        ctx.quadraticCurveTo(proj[21].x, proj[21].y, proj[18].x, proj[18].y);
        ctx.stroke();
        ctx.beginPath();
        ctx.arc((proj[18].x + proj[20].x)/2, (proj[18].y + proj[20].y)/2, 2.5, 0, Math.PI * 2);
        ctx.fill();
      }}

      // Nariz
      ctx.strokeStyle = "rgba(148, 163, 184, 0.7)";
      ctx.lineWidth = 2;
      ctx.beginPath();
      ctx.moveTo(proj[22].x, proj[22].y);
      ctx.lineTo(proj[23].x, proj[23].y);
      ctx.lineTo(proj[24].x, proj[24].y);
      ctx.stroke();

      // Boca (abre com o som!)
      ctx.strokeStyle = f.smile > 0.3 ? "#4ade80" : "#fbbf24";
      ctx.lineWidth = 2.2;
      ctx.beginPath();
      ctx.moveTo(proj[26].x, proj[26].y);
      ctx.quadraticCurveTo(proj[27].x, proj[27].y, proj[28].x, proj[28].y);
      ctx.quadraticCurveTo(proj[29].x, proj[29].y, proj[26].x, proj[26].y);
      ctx.closePath();
      ctx.stroke();
      if (jawOffset > 3) {{
        ctx.fillStyle = "rgba(251, 191, 36, 0.25)";
        ctx.fill();
      }}
    }}

    function syncWithAudio() {{
      if (!audio.paused) {{
        const targetFrame = Math.min(FRAMES_DATA.length - 1, Math.floor(audio.currentTime * fps));
        currentFrame = targetFrame;
        render();
        requestAnimationFrame(syncWithAudio);
      }} else {{
        playIcon.textContent = "▶";
        playLabel.textContent = "Ouvir & Assistir";
      }}
    }}

    btnPlay.addEventListener("click", () => {{
      if (audio.paused) {{
        if (currentFrame >= FRAMES_DATA.length - 1) {{
          currentFrame = 0;
          audio.currentTime = 0;
        }} else {{
          audio.currentTime = currentFrame / fps;
        }}
        audio.play();
        playIcon.textContent = "⏸";
        playLabel.textContent = "Pausar";
        requestAnimationFrame(syncWithAudio);
      }} else {{
        audio.pause();
        playIcon.textContent = "▶";
        playLabel.textContent = "Ouvir & Assistir";
      }}
    }});

    audio.addEventListener("ended", () => {{
      playIcon.textContent = "▶";
      playLabel.textContent = "Ouvir Novamente";
    }});

    slider.addEventListener("input", (e) => {{
      currentFrame = parseInt(e.target.value, 10);
      audio.currentTime = currentFrame / fps;
      render();
    }});

    btnMute.addEventListener("click", () => {{
      audio.muted = !audio.muted;
      btnMute.textContent = audio.muted ? "🔇 Mudo" : "🔊 Som Ativado";
    }});

    // Render inicial
    render();
  </script>
</body>
</html>
"""
    with open(output_html, "w", encoding="utf-8") as f:
        f.write(html_content)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Gera avatar 3D com áudio e emoções detectadas a partir de prompt.")
    parser.add_argument("--prompt", type=str, default="Fale com muita alegria e surpresa, olhando para a esquerda", help="Prompt com instruções de atuação e emoção.")
    parser.add_argument("--speech", type=str, default=None, help="Texto específico que o avatar deve falar. Se omitido, usa o prompt.")
    parser.add_argument("--seed", type=int, default=42, help="Semente para a difusão de movimento.")
    parser.add_argument("--name", type=str, default="avatar_custom", help="Nome base para os arquivos de saída.")

    args = parser.parse_args()
    generate_avatar(prompt=args.prompt, speech_text=args.speech, seed=args.seed, output_name=args.name)
