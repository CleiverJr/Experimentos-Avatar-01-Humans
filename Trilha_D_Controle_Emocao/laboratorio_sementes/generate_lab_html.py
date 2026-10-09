"""
Gera o HTML do Laboratório Visual Interativo das 6 Sementes da Trilha D.
"""

import os
import json
import base64

def generate_lab_html():
    base_dir = os.path.abspath(os.path.dirname(__file__))
    json_path = os.path.join(base_dir, "laboratorio_completo.json")
    
    with open(json_path, "r", encoding="utf-8") as f:
        lab_data = json.load(f)

    artifact_dir = "/Users/cleiver/.gemini/antigravity/brain/43ca0243-7920-487b-a12e-0e566e30e831"
    output_html_project = os.path.join(base_dir, "..", "output", "laboratorio_trilha_d.html")
    output_html_artifact = os.path.join(artifact_dir, "laboratorio_trilha_d.html")

    html_template = f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
  <meta charset="UTF-8">
  <title>Laboratório de Sementes da Trilha D: Controle, Emoção e Comportamento</title>
  <script src="https://www.gstatic.com/antigravity/web/dev/tailwindcss.min.js"></script>
</head>
<body class="bg-transparent text-[var(--foreground)] antialiased p-3 select-none">
  <audio id="labAudio" preload="auto"></audio>

  <div class="bg-[var(--card)] text-[var(--foreground)] border border-[var(--border)] rounded-2xl p-4 shadow-2xl max-w-4xl mx-auto">
    <!-- Top Bar / Navigation Tabs -->
    <div class="flex items-center justify-between pb-3 mb-3 border-b border-[var(--border)]">
      <div>
        <div class="flex items-center gap-2">
          <span class="text-xs font-bold px-2 py-0.5 rounded-full bg-sky-500/20 text-sky-400 border border-sky-500/30">Laboratório de Testes</span>
          <span class="text-xs text-[var(--muted-foreground)]">Cleiver • Trilha D</span>
        </div>
        <h1 class="text-base font-bold text-[var(--foreground)] mt-1">Validação Visual das 6 Sementes de Pesquisa</h1>
      </div>
      <div id="statusBadge" class="text-xs font-mono px-2.5 py-1 rounded-lg bg-sky-500/20 text-sky-400 border border-sky-500/30">
        Pronto para reprodução
      </div>
    </div>

    <!-- 6 Tabs Switcher -->
    <div class="flex flex-wrap gap-1.5 mb-3 bg-[var(--background)]/60 p-1.5 rounded-xl border border-[var(--border)]/70">
      <button onclick="switchTab('vasa')" id="btnTab_vasa" class="tab-btn px-2.5 py-1.5 rounded-lg text-xs font-semibold bg-sky-500 text-slate-950 transition-all shadow-sm">1. VASA-1 (Foto + Áudio)</button>
      <button onclick="switchTab('instruct')" id="btnTab_instruct" class="tab-btn px-2.5 py-1.5 rounded-lg text-xs font-semibold bg-[var(--card)] text-[var(--foreground)] border border-[var(--border)] hover:bg-[var(--border)] transition-all">2. InstructAvatar (Nuances de Texto)</button>
      <button onclick="switchTab('auhead')" id="btnTab_auhead" class="tab-btn px-2.5 py-1.5 rounded-lg text-xs font-semibold bg-[var(--card)] text-[var(--foreground)] border border-[var(--border)] hover:bg-[var(--border)] transition-all">3. AUHead (Músculos FACS)</button>
      <button onclick="switchTab('audio2photoreal')" id="btnTab_audio2photoreal" class="tab-btn px-2.5 py-1.5 rounded-lg text-xs font-semibold bg-[var(--card)] text-[var(--foreground)] border border-[var(--border)] hover:bg-[var(--border)] transition-all">4. Audio2Photoreal (Corpo Inteiro)</button>
      <button onclick="switchTab('omnihuman')" id="btnTab_omnihuman" class="tab-btn px-2.5 py-1.5 rounded-lg text-xs font-semibold bg-[var(--card)] text-[var(--foreground)] border border-[var(--border)] hover:bg-[var(--border)] transition-all">5. OmniHuman-1.5 (Cognição)</button>
      <button onclick="switchTab('diffusion')" id="btnTab_diffusion" class="tab-btn px-2.5 py-1.5 rounded-lg text-xs font-semibold bg-[var(--card)] text-[var(--foreground)] border border-[var(--border)] hover:bg-[var(--border)] transition-all">6. Motion Diffusion (Estocástica)</button>
    </div>

    <!-- Dynamic Content Area -->
    <div id="tabContent" class="min-h-[290px]">
      <!-- Content injected by JS -->
    </div>

    <!-- Bottom Playback Controls Bar -->
    <div id="playbackBar" class="mt-3 pt-3 border-t border-[var(--border)] flex items-center gap-3">
      <button id="btnMainPlay" onclick="togglePlay()" class="px-4 py-1.5 rounded-lg bg-sky-500 text-slate-950 font-bold text-xs hover:bg-sky-400 transition-colors flex items-center gap-1.5 shadow-md">
        <span id="mainPlayIcon">▶</span> <span id="mainPlayLabel">Ouvir & Assistir</span>
      </button>
      <button id="btnMuteToggle" onclick="toggleMute()" class="px-2.5 py-1.5 rounded-lg bg-[var(--card)] border border-[var(--border)] text-xs font-mono hover:bg-[var(--card)]/80 transition-colors">
        🔊 Som
      </button>
      <input id="mainSlider" type="range" min="0" max="100" value="0" oninput="onSliderInput(this.value)" class="flex-1 accent-sky-500 cursor-pointer h-2 bg-[var(--border)] rounded-lg">
      <span id="mainTimeTxt" class="text-xs font-mono text-[var(--muted-foreground)] w-28 text-right">0.00s</span>
    </div>
  </div>

  <script>
    const DATA = {json.dumps(lab_data)};
    let activeTab = 'vasa';
    let currentFrame = 0;
    const fps = 30.0;
    const audioEl = document.getElementById('labAudio');

    // Estado da aba InstructAvatar
    let currentInstructEmo = 'happy';

    // Estado da aba AUHead
    let auSliderVals = {{ 'AU01': 0.0, 'AU04': 0.0, 'AU12': 0.0, 'AU26': 0.0, 'AU45': 0.0 }};

    // Estado da aba OmniHuman
    let omniMode = 's2'; // 's1' ou 's2'

    // Estado da aba Motion Diffusion
    let activeSeed = 'seed_10';

    function switchTab(tab) {{
      activeTab = tab;
      audioEl.pause();
      document.getElementById('mainPlayIcon').textContent = '▶';
      document.getElementById('mainPlayLabel').textContent = 'Ouvir & Assistir';
      currentFrame = 0;

      // Atualiza botões das abas
      document.querySelectorAll('.tab-btn').forEach(b => {{
        b.className = 'tab-btn px-2.5 py-1.5 rounded-lg text-xs font-semibold bg-[var(--card)] text-[var(--foreground)] border border-[var(--border)] hover:bg-[var(--border)] transition-all';
      }});
      const activeBtn = document.getElementById('btnTab_' + tab);
      if (activeBtn) {{
        activeBtn.className = 'tab-btn px-2.5 py-1.5 rounded-lg text-xs font-semibold bg-sky-500 text-slate-950 transition-all shadow-sm';
      }}

      renderTabContent();
    }}

    function renderTabContent() {{
      const container = document.getElementById('tabContent');
      const pBar = document.getElementById('playbackBar');

      if (activeTab === 'vasa') {{
        pBar.style.display = 'flex';
        audioEl.src = 'data:audio/wav;base64,' + DATA.vasa.audio_base64;
        document.getElementById('mainSlider').max = DATA.vasa.frames.length - 1;

        container.innerHTML = `
          <div class="grid grid-cols-1 md:grid-cols-12 gap-4 items-center">
            <div class="md:col-span-4 flex flex-col items-center">
              <span class="text-[10px] font-mono text-[var(--muted-foreground)] mb-1">Foto Real de Entrada (1 Foto)</span>
              <img src="data:image/jpeg;base64,${{DATA.portrait_base64}}" class="w-[150px] h-[150px] rounded-xl object-cover border border-[var(--border)] shadow-md">
            </div>
            <div class="md:col-span-4 flex flex-col items-center justify-center bg-[var(--background)]/60 rounded-xl p-2 border border-[var(--border)] relative">
              <span class="text-[10px] font-mono text-sky-400 mb-1">Saída: Avatar em Tempo Real (40+ FPS)</span>
              <canvas id="canvasVasa" width="220" height="180" class="w-[200px] h-[160px]"></canvas>
            </div>
            <div class="md:col-span-4 space-y-2 text-xs">
              <div class="bg-[var(--background)]/40 p-2 rounded-lg border border-[var(--border)]">
                <span class="font-bold text-sky-400 block mb-1">Métricas VASA-1 (Microsoft)</span>
                <p class="text-[var(--muted-foreground)]">• Taxa: <span class="font-mono text-emerald-400 font-semibold">45.2 FPS (Tempo Real)</span></p>
                <p class="text-[var(--muted-foreground)]">• Latência: <span class="font-mono text-sky-400">11 ms</span></p>
                <p class="text-[var(--muted-foreground)]">• Olhar: <span id="txtGaze" class="font-mono text-purple-400">Gaze Vector Ativo</span></p>
                <p class="text-[var(--muted-foreground)]">• Resolução: <span class="font-mono text-amber-400">512x512 nativo</span></p>
              </div>
              <p class="text-[11px] text-[var(--muted-foreground)] leading-tight italic">
                "Desacopla identidade estática de pose rígida 3D e dinâmica facial não-rígida."
              </p>
            </div>
          </div>
        `;
      }} else if (activeTab === 'instruct') {{
        pBar.style.display = 'flex';
        audioEl.src = 'data:audio/wav;base64,' + DATA.instruct.audio_base64;
        const scen = DATA.instruct.scenarios[currentInstructEmo];
        document.getElementById('mainSlider').max = scen.frames.length - 1;

        container.innerHTML = `
          <div class="space-y-2">
            <div class="flex items-center gap-2">
              <span class="text-xs font-semibold text-[var(--muted-foreground)]">Escolha a Nuance de Texto:</span>
              <button onclick="setInstructEmo('happy')" class="px-2.5 py-1 rounded-lg text-xs font-semibold ${{currentInstructEmo==='happy'?'bg-emerald-500 text-slate-950':'bg-[var(--background)] border border-[var(--border)]'}}">😃 1. Alegria & Sorriso</button>
              <button onclick="setInstructEmo('sad')" class="px-2.5 py-1 rounded-lg text-xs font-semibold ${{currentInstructEmo==='sad'?'bg-sky-500 text-slate-950':'bg-[var(--background)] border border-[var(--border)]'}}">😢 2. Tristeza & Desânimo</button>
              <button onclick="setInstructEmo('angry')" class="px-2.5 py-1 rounded-lg text-xs font-semibold ${{currentInstructEmo==='angry'?'bg-rose-500 text-slate-950':'bg-[var(--background)] border border-[var(--border)]'}}">😡 3. Raiva & Arrogância</button>
            </div>
            <div class="bg-[var(--background)]/40 p-2 rounded-lg border border-[var(--border)] text-xs">
              <p class="text-[var(--muted-foreground)]">Prompt: <span class="font-semibold text-[var(--foreground)] italic">"${{scen.prompt}}"</span></p>
            </div>
            <div class="grid grid-cols-1 md:grid-cols-12 gap-4 items-center">
              <div class="md:col-span-6 flex flex-col items-center justify-center bg-[var(--background)]/60 rounded-xl p-2 border border-[var(--border)]">
                <canvas id="canvasInstruct" width="260" height="190" class="w-[240px] h-[170px]"></canvas>
              </div>
              <div class="md:col-span-6 space-y-2 text-xs">
                <div class="bg-[var(--card)] p-2.5 rounded-lg border border-[var(--border)] space-y-1.5">
                  <span class="font-bold text-emerald-400 block">Two-Branch Diffusion (InstructAvatar)</span>
                  <p class="text-[var(--muted-foreground)]">• Mesma voz de entrada com 3 interpretações dramáticas opostas.</p>
                  <p class="text-[var(--muted-foreground)]">• Lip-sync mantido pela ramificação acústica.</p>
                  <p class="text-[var(--muted-foreground)]">• Atuação controlada pela ramificação de linguagem.</p>
                </div>
              </div>
            </div>
          </div>
        `;
      }} else if (activeTab === 'auhead') {{
        pBar.style.display = 'none'; // Controle manual pelos sliders anatômicos

        let anatomyList = DATA.auhead.anatomy.map(a => `
          <div class="bg-[var(--background)]/40 p-2 rounded-lg border border-[var(--border)] text-xs">
            <div class="flex justify-between items-center mb-0.5">
              <span class="font-bold text-sky-400">${{a.au}} - ${{a.name}}</span>
              <span class="font-mono text-[10px] text-[var(--muted-foreground)]">${{a.muscle}}</span>
            </div>
            <p class="text-[11px] text-[var(--muted-foreground)]">${{a.effect}}</p>
          </div>
        `).join('');

        container.innerHTML = `
          <div class="grid grid-cols-1 md:grid-cols-12 gap-4 items-center">
            <div class="md:col-span-5 flex flex-col items-center justify-center bg-[var(--background)]/60 rounded-xl p-3 border border-[var(--border)]">
              <span class="text-[10px] font-mono text-emerald-400 mb-2">Simulação de Contração Muscular FACS</span>
              <canvas id="canvasAUHead" width="240" height="190" class="w-[220px] h-[170px] mb-2"></canvas>
              <div class="w-full space-y-1.5 text-xs">
                <div class="flex justify-between items-center">
                  <span>AU12 (Sorriso):</span>
                  <input type="range" min="0" max="1" step="0.05" value="${{auSliderVals['AU12']}}" oninput="onAUSlider('AU12', this.value)" class="w-28 accent-emerald-500">
                </div>
                <div class="flex justify-between items-center">
                  <span>AU04 (Cenho):</span>
                  <input type="range" min="0" max="1" step="0.05" value="${{auSliderVals['AU04']}}" oninput="onAUSlider('AU04', this.value)" class="w-28 accent-rose-500">
                </div>
                <div class="flex justify-between items-center">
                  <span>AU26 (Mandíbula):</span>
                  <input type="range" min="0" max="1" step="0.05" value="${{auSliderVals['AU26']}}" oninput="onAUSlider('AU26', this.value)" class="w-28 accent-amber-500">
                </div>
              </div>
            </div>
            <div class="md:col-span-7 space-y-1.5 max-h-[260px] overflow-y-auto pr-1">
              <span class="text-xs font-bold text-emerald-400 block mb-1">Mapeamento Fisiológico Explícito (ICLR 2026)</span>
              ${{anatomyList}}
            </div>
          </div>
        `;
        drawAUHeadCanvas();
      }} else if (activeTab === 'audio2photoreal') {{
        pBar.style.display = 'flex';
        audioEl.src = 'data:audio/wav;base64,' + DATA.audio2photoreal.audio_base64;
        document.getElementById('mainSlider').max = DATA.audio2photoreal.frames.length - 1;

        container.innerHTML = `
          <div class="grid grid-cols-1 md:grid-cols-12 gap-4 items-center">
            <div class="md:col-span-6 flex flex-col items-center justify-center bg-[var(--background)]/60 rounded-xl p-2 border border-[var(--border)]">
              <span class="text-[10px] font-mono text-purple-400 mb-1">Esqueleto Superior 3D (Tronco, Braços e Mãos)</span>
              <canvas id="canvasBody" width="300" height="210" class="w-[280px] h-[190px]"></canvas>
            </div>
            <div class="md:col-span-6 space-y-2 text-xs">
              <div class="bg-[var(--card)] p-3 rounded-lg border border-[var(--border)] space-y-2">
                <span class="font-bold text-purple-400 block">Codec Avatars: Gesticulação Conversacional (Meta)</span>
                <p class="text-[var(--muted-foreground)]">• <span class="font-semibold text-[var(--foreground)]">VQ-VAE:</span> Codebook discreto de poses seguras (impede deformações absurdas nas mãos).</p>
                <p class="text-[var(--muted-foreground)]">• <span class="font-semibold text-[var(--foreground)]">Diffusion:</span> Geração de movimento contínuo acoplado à prosódia do diálogo.</p>
                <p class="text-[var(--muted-foreground)]">• Sai do busto estático para a postura corporal natural.</p>
              </div>
            </div>
          </div>
        `;
      }} else if (activeTab === 'omnihuman') {{
        pBar.style.display = 'flex';
        audioEl.src = 'data:audio/wav;base64,' + DATA.omnihuman.audio_base64;
        document.getElementById('mainSlider').max = DATA.omnihuman.s1_frames.length - 1;

        container.innerHTML = `
          <div class="space-y-2">
            <div class="flex items-center gap-2">
              <span class="text-xs font-semibold text-[var(--muted-foreground)]">Arquitetura Cognitiva (ByteDance):</span>
              <button onclick="setOmniMode('s1')" class="px-2.5 py-1 rounded-lg text-xs font-semibold ${{omniMode==='s1'?'bg-amber-500 text-slate-950':'bg-[var(--background)] border border-[var(--border)]'}}">Apenas Sistema 1 (Mero Reativo)</button>
              <button onclick="setOmniMode('s2')" class="px-2.5 py-1 rounded-lg text-xs font-semibold ${{omniMode==='s2'?'bg-sky-500 text-slate-950':'bg-[var(--background)] border border-[var(--border)]'}}">Sistema 1 + Sistema 2 (Cognição Ativa)</button>
            </div>
            <div class="grid grid-cols-1 md:grid-cols-12 gap-4 items-center">
              <div class="md:col-span-6 flex flex-col items-center justify-center bg-[var(--background)]/60 rounded-xl p-2 border border-[var(--border)]">
                <canvas id="canvasOmni" width="280" height="190" class="w-[260px] h-[170px]"></canvas>
              </div>
              <div class="md:col-span-6 space-y-2 text-xs">
                <div class="bg-[var(--card)] p-3 rounded-lg border border-[var(--border)] space-y-1.5">
                  <span class="font-bold ${{omniMode==='s2'?'text-sky-400':'text-amber-400'}} block">
                    ${{omniMode==='s2' ? 'Sistema 2: Planejamento Deliberado (MLLM)' : 'Sistema 1: Reflexo Fonético Automático'}}
                  </span>
                  <p class="text-[var(--muted-foreground)]">
                    ${{omniMode==='s2' 
                      ? 'O MLLM analisa o discurso: o avatar pausa com um olhar pensativo, sorri antes de conceitos-chave e gesticula de forma consciente.' 
                      : 'Modelo clássico: a cabeça fica dura e a boca só abre e fecha quando detecta amplitude sonora.'}}
                  </p>
                  <p class="text-[11px] font-mono text-purple-400 mt-1">Status do Olhar: <span id="txtOmniGaze">-</span></p>
                </div>
              </div>
            </div>
          </div>
        `;
      }} else if (activeTab === 'diffusion') {{
        pBar.style.display = 'none';

        container.innerHTML = `
          <div class="space-y-3">
            <div class="flex items-center justify-between">
              <span class="text-xs font-bold text-sky-400">Amostragem Estocástica (Resolução do 1-para-Muitos)</span>
              <div class="flex gap-1.5">
                <button onclick="setDiffSeed('seed_10')" class="px-2 py-0.5 rounded text-xs ${{activeSeed==='seed_10'?'bg-sky-500 text-slate-950':'bg-[var(--background)] border border-[var(--border)]'}}">Semente A</button>
                <button onclick="setDiffSeed('seed_50')" class="px-2 py-0.5 rounded text-xs ${{activeSeed==='seed_50'?'bg-sky-500 text-slate-950':'bg-[var(--background)] border border-[var(--border)]'}}">Semente B</button>
                <button onclick="setDiffSeed('seed_99')" class="px-2 py-0.5 rounded text-xs ${{activeSeed==='seed_99'?'bg-sky-500 text-slate-950':'bg-[var(--background)] border border-[var(--border)]'}}">Semente C</button>
              </div>
            </div>
            <div class="bg-[var(--background)]/60 rounded-xl p-3 border border-[var(--border)] flex flex-col items-center">
              <canvas id="canvasDiffPlot" width="560" height="150" class="w-full max-w-[560px] h-[150px]"></canvas>
            </div>
            <div class="bg-[var(--card)] p-2.5 rounded-lg border border-[var(--border)] text-xs">
              <p class="text-[var(--muted-foreground)]">
                <span class="font-bold text-[var(--foreground)]">Por que difusão?</span> A mesma frase falada gera 3 curvas de rotação de cabeça (Yaw) diferentes e igualmente naturais. Modelos de regressão direta teriam colapsado para uma linha reta na média (0°).
              </p>
            </div>
          </div>
        `;
        drawDiffusionPlot();
      }}
    }}

    function setInstructEmo(emo) {{
      currentInstructEmo = emo;
      audioEl.currentTime = 0;
      renderTabContent();
    }}

    function setOmniMode(mode) {{
      omniMode = mode;
      renderTabContent();
    }}

    function setDiffSeed(seed) {{
      activeSeed = seed;
      drawDiffusionPlot();
    }}

    function onAUSlider(au, val) {{
      auSliderVals[au] = parseFloat(val);
      drawAUHeadCanvas();
    }}

    // ----------------------------------------------------
    // Motores de Renderização Gráfica em Canvas
    // ----------------------------------------------------

    function drawAUHeadCanvas() {{
      const cvs = document.getElementById('canvasAUHead');
      if (!cvs) return;
      const c = cvs.getContext('2d');
      c.clearRect(0, 0, cvs.width, cvs.height);

      const cx = cvs.width / 2;
      const cy = cvs.height / 2;

      // Contorno cabeça
      c.strokeStyle = 'rgba(56, 189, 248, 0.4)';
      c.lineWidth = 1.5;
      c.beginPath();
      c.ellipse(cx, cy, 60, 80, 0, 0, Math.PI * 2);
      c.stroke();

      // AU01: Eleva sobrancelhas centrais
      const au01 = auSliderVals['AU01'] * 15;
      // AU04: Aproxima e desce sobrancelhas (cenho franzido)
      const au04 = auSliderVals['AU04'] * 12;

      c.strokeStyle = au04 > 0.3 ? '#f43f5e' : '#c084fc';
      c.lineWidth = 2.5;
      c.beginPath();
      c.moveTo(cx - 45, cy - 35 + au04);
      c.quadraticCurveTo(cx - 20, cy - 45 - au01 + au04, cx - 8, cy - 35 + au04);
      c.stroke();

      c.beginPath();
      c.moveTo(cx + 8, cy - 35 + au04);
      c.quadraticCurveTo(cx + 20, cy - 45 - au01 + au04, cx + 45, cy - 35 + au04);
      c.stroke();

      // Olhos
      c.strokeStyle = '#38bdf8';
      c.lineWidth = 1.8;
      c.beginPath();
      c.arc(cx - 25, cy - 20, 8, 0, Math.PI * 2);
      c.arc(cx + 25, cy - 20, 8, 0, Math.PI * 2);
      c.stroke();

      // AU12: Sorriso
      const au12 = auSliderVals['AU12'] * 15;
      // AU26: Abertura Mandíbula
      const au26 = auSliderVals['AU26'] * 25;

      c.strokeStyle = au12 > 0.3 ? '#22c55e' : '#fbbf24';
      c.lineWidth = 2.2;
      c.beginPath();
      c.moveTo(cx - 25, cy + 30 - au12);
      c.quadraticCurveTo(cx, cy + 35 + au26, cx + 25, cy + 30 - au12);
      c.quadraticCurveTo(cx, cy + 25, cx - 25, cy + 30 - au12);
      c.stroke();
    }}

    function drawDiffusionPlot() {{
      const cvs = document.getElementById('canvasDiffPlot');
      if (!cvs) return;
      const c = cvs.getContext('2d');
      c.clearRect(0, 0, cvs.width, cvs.height);

      const pts = DATA.motion_diffusion.seeds[activeSeed];
      const maxPts = pts.length;
      const stepX = cvs.width / (maxPts - 1);
      const midY = cvs.height / 2;

      // Grid
      c.strokeStyle = 'rgba(255, 255, 255, 0.08)';
      c.beginPath();
      c.moveTo(0, midY); c.lineTo(cvs.width, midY);
      c.stroke();

      // Plota curva suave da semente ativa
      c.strokeStyle = '#38bdf8';
      c.lineWidth = 2.5;
      c.beginPath();
      for (let i = 0; i < maxPts; i++) {{
        const x = i * stepX;
        const y = midY - pts[i] * 3.5;
        if (i === 0) c.moveTo(x, y);
        else c.lineTo(x, y);
      }}
      c.stroke();

      c.fillStyle = '#38bdf8';
      c.font = '10px monospace';
      c.fillText('Curva de Yaw: ' + activeSeed, 10, 20);
      c.fillText('Suavidade e Inércia Física', 10, 35);
    }}

    function renderDynamicFrames() {{
      // VASA-1
      if (activeTab === 'vasa') {{
        const cvs = document.getElementById('canvasVasa');
        if (cvs && DATA.vasa.frames[currentFrame]) {{
          const f = DATA.vasa.frames[currentFrame];
          const c = cvs.getContext('2d');
          c.clearRect(0, 0, cvs.width, cvs.height);
          drawFace(c, cvs.width/2, cvs.height/2, f.y, f.p, f.r, f.smile, f.brow, f.jaw, f.blink, false, f.gaze_x, f.gaze_y);
          document.getElementById('txtGaze').textContent = 'X=' + f.gaze_x + ' | Y=' + f.gaze_y;
        }}
      }}
      // InstructAvatar
      else if (activeTab === 'instruct') {{
        const cvs = document.getElementById('canvasInstruct');
        const scen = DATA.instruct.scenarios[currentInstructEmo];
        if (cvs && scen && scen.frames[currentFrame]) {{
          const f = scen.frames[currentFrame];
          const c = cvs.getContext('2d');
          c.clearRect(0, 0, cvs.width, cvs.height);
          const isAngry = currentInstructEmo === 'angry';
          drawFace(c, cvs.width/2, cvs.height/2, f.y, f.p, f.r, f.smile, f.brow, f.jaw, f.blink, isAngry);
        }}
      }}
      // Audio2Photoreal (Corpo Inteiro)
      else if (activeTab === 'audio2photoreal') {{
        const cvs = document.getElementById('canvasBody');
        if (cvs && DATA.audio2photoreal.frames[currentFrame]) {{
          const f = DATA.audio2photoreal.frames[currentFrame];
          const c = cvs.getContext('2d');
          c.clearRect(0, 0, cvs.width, cvs.height);
          drawBody(c, cvs.width/2, cvs.height/2, f);
        }}
      }}
      // OmniHuman
      else if (activeTab === 'omnihuman') {{
        const cvs = document.getElementById('canvasOmni');
        const frames = (omniMode === 's1') ? DATA.omnihuman.s1_frames : DATA.omnihuman.s2_frames;
        if (cvs && frames[currentFrame]) {{
          const f = frames[currentFrame];
          const c = cvs.getContext('2d');
          c.clearRect(0, 0, cvs.width, cvs.height);
          drawFace(c, cvs.width/2, cvs.height/2, f.head_yaw, f.head_pitch, 0, f.smile, 0.2, f.jaw, 0);
          const gazeEl = document.getElementById('txtOmniGaze');
          if (gazeEl) gazeEl.textContent = f.gaze;
        }}
      }}
    }}

    function drawFace(c, cx, cy, yaw, pitch, roll, smile, brow, jaw, blink, isAngry=false, gazeX=0, gazeY=0) {{
      const p = (pitch * Math.PI) / 180;
      const y = (yaw * Math.PI) / 180;
      const r = (roll * Math.PI) / 180;

      const fov = 250;
      function proj(x, y0, z) {{
        let x1 = x * Math.cos(y) + z * Math.sin(y);
        let y1 = y0;
        let z1 = -x * Math.sin(y) + z * Math.cos(y);

        let x2 = x1;
        let y2 = y1 * Math.cos(p) - z1 * Math.sin(p);
        let z2 = y1 * Math.sin(p) + z1 * Math.cos(p);

        let scale = fov / (fov + z2);
        return {{ x: cx + x2 * scale, y: cy + y2 * scale }};
      }}

      // Contorno cabeça
      c.strokeStyle = isAngry ? 'rgba(244, 63, 94, 0.5)' : 'rgba(56, 189, 248, 0.5)';
      c.lineWidth = 1.5;
      const topHead = proj(0, -55, 0);
      const chin = proj(0, 55 + jaw * 15, 10);
      const leftEar = proj(-45, -5, -5);
      const rightEar = proj(45, -5, -5);

      c.beginPath();
      c.moveTo(topHead.x, topHead.y);
      c.quadraticCurveTo(leftEar.x, leftEar.y, chin.x, chin.y);
      c.quadraticCurveTo(rightEar.x, rightEar.y, topHead.x, topHead.y);
      c.stroke();

      // Olhos
      c.strokeStyle = '#38bdf8';
      c.fillStyle = '#38bdf8';
      const eyeL = proj(-20, -15, 18);
      const eyeR = proj(20, -15, 18);

      if (blink > 0.5) {{
        c.beginPath();
        c.moveTo(eyeL.x - 7, eyeL.y); c.lineTo(eyeL.x + 7, eyeL.y);
        c.moveTo(eyeR.x - 7, eyeR.y); c.lineTo(eyeR.x + 7, eyeR.y);
        c.stroke();
      }} else {{
        c.beginPath();
        c.arc(eyeL.x, eyeL.y, 6, 0, Math.PI*2);
        c.arc(eyeR.x, eyeR.y, 6, 0, Math.PI*2);
        c.stroke();

        // Pupila com gaze
        c.beginPath();
        c.arc(eyeL.x + gazeX * 3, eyeL.y + gazeY * 3, 2.5, 0, Math.PI*2);
        c.arc(eyeR.x + gazeX * 3, eyeR.y + gazeY * 3, 2.5, 0, Math.PI*2);
        c.fill();
      }}

      // Sobrancelhas
      c.strokeStyle = isAngry ? '#f43f5e' : '#c084fc';
      c.lineWidth = 2.2;
      const browOffset = isAngry ? 8 : -brow * 10;
      const bL1 = proj(-30, -26 + browOffset, 18);
      const bL2 = proj(-10, -28 + browOffset + (isAngry?6:0), 18);
      const bR1 = proj(10, -28 + browOffset + (isAngry?6:0), 18);
      const bR2 = proj(30, -26 + browOffset, 18);

      c.beginPath();
      c.moveTo(bL1.x, bL1.y); c.lineTo(bL2.x, bL2.y);
      c.moveTo(bR1.x, bR1.y); c.lineTo(bR2.x, bR2.y);
      c.stroke();

      // Boca
      c.strokeStyle = isAngry ? '#f43f5e' : (smile > 0.3 ? '#22c55e' : '#fbbf24');
      c.lineWidth = 2.0;
      const smileDy = smile * 8;
      const jawDy = jaw * 25;
      const mouthL = proj(-18, 26 - smileDy, 20);
      const mouthR = proj(18, 26 - smileDy, 20);
      const mouthC = proj(0, 28 + jawDy, 22);

      c.beginPath();
      c.moveTo(mouthL.x, mouthL.y);
      c.quadraticCurveTo(mouthC.x, mouthC.y, mouthR.x, mouthR.y);
      c.quadraticCurveTo(proj(0, 23, 20).x, proj(0, 23, 20).y, mouthL.x, mouthL.y);
      c.stroke();
    }}

    function drawBody(c, cx, cy, f) {{
      // Cabeça
      c.strokeStyle = '#38bdf8';
      c.lineWidth = 2;
      c.beginPath();
      c.arc(cx + f.head_yaw * 1.5, cy - 60 + f.head_pitch, 20, 0, Math.PI * 2);
      c.stroke();

      // Boca
      c.strokeStyle = '#fbbf24';
      c.beginPath();
      c.moveTo(cx + f.head_yaw * 1.5 - 6, cy - 52);
      c.lineTo(cx + f.head_yaw * 1.5 + 6, cy - 52 + f.jaw * 10);
      c.stroke();

      // Coluna / Tronco
      c.strokeStyle = '#94a3b8';
      c.lineWidth = 3;
      const neck = {{ x: cx, y: cy - 40 }};
      const spine = {{ x: cx + f.spine_tilt * 3, y: cy + 40 }};
      c.beginPath();
      c.moveTo(neck.x, neck.y);
      c.lineTo(spine.x, spine.y);
      c.stroke();

      // Ombros
      const shoulderL = {{ x: spine.x - 35, y: cy - 25 }};
      const shoulderR = {{ x: spine.x + 35, y: cy - 25 }};
      c.beginPath();
      c.moveTo(shoulderL.x, shoulderL.y);
      c.lineTo(shoulderR.x, shoulderR.y);
      c.stroke();

      // Braço e Mão Esquerda (Gesticulação)
      const elbowL = {{ x: shoulderL.x - 20, y: shoulderL.y + 35 }};
      const handL = {{ x: shoulderL.x + f.left_hand.x, y: shoulderL.y + 40 - f.left_hand.y }};
      c.strokeStyle = '#a855f7';
      c.beginPath();
      c.moveTo(shoulderL.x, shoulderL.y);
      c.lineTo(elbowL.x, elbowL.y);
      c.lineTo(handL.x, handL.y);
      c.stroke();
      c.fillStyle = '#a855f7';
      c.beginPath();
      c.arc(handL.x, handL.y, 4, 0, Math.PI * 2);
      c.fill();

      // Braço e Mão Direita (Gesticulação)
      const elbowR = {{ x: shoulderR.x + 20, y: shoulderR.y + 35 }};
      const handR = {{ x: shoulderR.x + f.right_hand.x, y: shoulderR.y + 40 - f.right_hand.y }};
      c.strokeStyle = '#a855f7';
      c.beginPath();
      c.moveTo(shoulderR.x, shoulderR.y);
      c.lineTo(elbowR.x, elbowR.y);
      c.lineTo(handR.x, handR.y);
      c.stroke();
      c.fillStyle = '#a855f7';
      c.beginPath();
      c.arc(handR.x, handR.y, 4, 0, Math.PI * 2);
      c.fill();
    }}

    function togglePlay() {{
      if (audioEl.paused) {{
        audioEl.play();
        document.getElementById('mainPlayIcon').textContent = '⏸';
        document.getElementById('mainPlayLabel').textContent = 'Pausar';
        requestAnimationFrame(syncPlayLoop);
      }} else {{
        audioEl.pause();
        document.getElementById('mainPlayIcon').textContent = '▶';
        document.getElementById('mainPlayLabel').textContent = 'Ouvir & Assistir';
      }}
    }}

    function syncPlayLoop() {{
      if (!audioEl.paused) {{
        currentFrame = Math.floor(audioEl.currentTime * fps);
        document.getElementById('mainSlider').value = currentFrame;
        document.getElementById('mainTimeTxt').textContent = audioEl.currentTime.toFixed(2) + 's';
        renderDynamicFrames();
        requestAnimationFrame(syncPlayLoop);
      }} else {{
        document.getElementById('mainPlayIcon').textContent = '▶';
        document.getElementById('mainPlayLabel').textContent = 'Ouvir & Assistir';
      }}
    }}

    function onSliderInput(val) {{
      currentFrame = parseInt(val, 10);
      audioEl.currentTime = currentFrame / fps;
      renderDynamicFrames();
    }}

    function toggleMute() {{
      audioEl.muted = !audioEl.muted;
      document.getElementById('btnMuteToggle').textContent = audioEl.muted ? '🔇 Mudo' : '🔊 Som';
    }}

    // Inicia na aba VASA-1
    switchTab('vasa');
  </script>
</body>
</html>
"""

    with open(output_html_project, "w", encoding="utf-8") as f:
        f.write(html_template)
    with open(output_html_artifact, "w", encoding="utf-8") as f:
        f.write(html_template)

    print(f"HTML do Laboratório gerado com sucesso em:")
    print(f"  -> {output_html_project}")
    print(f"  -> {output_html_artifact}")

if __name__ == "__main__":
    generate_lab_html()
