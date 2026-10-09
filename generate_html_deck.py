"""
Gera a apresentação de slides interativa em HTML com reprodução de vídeos MP4 e áudio embutidos.
"""

import os
import base64

def generate_html_deck():
    base_dir = os.path.abspath(os.path.dirname(__file__))
    output_html_project = os.path.join(base_dir, "Slides", "apresentacao_slides_interativa.html")
    artifact_dir = "/Users/cleiver/.gemini/antigravity/brain/43ca0243-7920-487b-a12e-0e566e30e831"
    output_html_artifact = os.path.join(artifact_dir, "apresentacao_slides_interativa.html")

    # Lê imagens e vídeos em base64
    portrait_path = os.path.join(base_dir, "Trilha_D_Controle_Emocao", "data", "vasa_portrait.jpg")
    dash_path = os.path.join(base_dir, "Trilha_D_Controle_Emocao", "output", "dashboard_animacao.png")
    v_cleiver_path = os.path.join(base_dir, "Trilha_D_Controle_Emocao", "output", "meu_teste_avatar_realista.mp4")

    with open(portrait_path, "rb") as f:
        img_b64 = base64.b64encode(f.read()).decode("utf-8")
    with open(dash_path, "rb") as f:
        dash_b64 = base64.b64encode(f.read()).decode("utf-8")
    with open(v_cleiver_path, "rb") as f:
        v1_b64 = base64.b64encode(f.read()).decode("utf-8")

    html_content = f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
  <meta charset="UTF-8">
  <title>Apresentação: Trilha D - Controle, Emoção e Comportamento</title>
  <script src="https://www.gstatic.com/antigravity/web/dev/tailwindcss.min.js"></script>
  <style>
    .slide {{ display: none; }}
    .slide.active {{ display: flex; }}
  </style>
</head>
<body class="bg-slate-950 text-slate-100 antialiased min-h-screen flex flex-col justify-between p-4 select-none">
  <!-- Top Bar -->
  <header class="flex justify-between items-center max-w-6xl mx-auto w-full pb-3 border-b border-slate-800">
    <div class="flex items-center gap-2">
      <span class="text-xs font-bold px-2 py-0.5 rounded-full bg-sky-500/20 text-sky-400 border border-sky-500/30">PROJETO HUMANS • AKCIT</span>
      <span class="text-xs text-slate-400">Trilha D: Controle, Emoção e Comportamento</span>
    </div>
    <div class="text-xs font-mono text-slate-400">
      Slide <span id="currentSlideNum" class="text-sky-400 font-bold">1</span> / <span id="totalSlidesNum">8</span>
    </div>
  </header>

  <!-- Slide Container -->
  <main class="flex-1 max-w-6xl mx-auto w-full my-4 flex items-center justify-center">
    
    <!-- SLIDE 1: CAPA -->
    <div class="slide active flex-col items-center justify-center text-center p-8 bg-slate-900 border border-slate-800 rounded-3xl shadow-2xl w-full max-w-4xl">
      <span class="text-xs font-bold px-3 py-1 rounded-full bg-sky-500/20 text-sky-400 border border-sky-500/30 mb-4">SEMINÁRIO DE ALINHAMENTO</span>
      <h1 class="text-4xl font-extrabold text-white mb-3">Trilha D: Controle, Emoção e Comportamento</h1>
      <p class="text-lg text-slate-300 max-w-2xl mb-8">Síntese Autônoma de Movimento Facial e Corporal a partir de Áudio e Texto (Sem Pose Explícita)</p>
      <div class="flex items-center gap-4 text-xs font-mono bg-slate-950 px-4 py-2 rounded-xl border border-slate-800">
        <span class="text-emerald-400 font-semibold">Pesquisador: Cleiver</span>
        <span class="text-slate-600">•</span>
        <span class="text-slate-400">Outubro 2026</span>
        <span class="text-slate-600">•</span>
        <span class="text-sky-400">AKCIT / UFG</span>
      </div>
    </div>

    <!-- SLIDE 2: ONDE ME ENCAIXO NO GRUPO? -->
    <div class="slide flex-col p-8 bg-slate-900 border border-slate-800 rounded-3xl shadow-2xl w-full">
      <span class="text-xs font-bold text-sky-400 mb-1">ECOSSISTEMA DO PROJETO HUMANS</span>
      <h2 class="text-2xl font-bold text-white mb-6">O Papel da Trilha D: O Titiriteiro (O Maestro)</h2>
      <div class="grid grid-cols-4 gap-4 mb-6">
        <div class="bg-slate-950 p-4 rounded-2xl border border-slate-800">
          <span class="text-xs font-bold text-sky-400 block mb-2">Trilha A (Mateus)</span>
          <p class="text-sm font-semibold text-white mb-1">Vídeo 2D Direto</p>
          <p class="text-xs text-slate-400">Foto + Áudio -> Vídeo 2D (SadTalker, EMO, LivePortrait)</p>
        </div>
        <div class="bg-slate-950 p-4 rounded-2xl border border-slate-800">
          <span class="text-xs font-bold text-purple-400 block mb-2">Trilha B (Arthur)</span>
          <p class="text-sm font-semibold text-white mb-1">Avatar 3D de 1 Foto</p>
          <p class="text-xs text-slate-400">Malha FLAME/SMPL-X e Rigging automático (A 'Marionete')</p>
        </div>
        <div class="bg-slate-950 p-4 rounded-2xl border border-slate-800">
          <span class="text-xs font-bold text-amber-400 block mb-2">Trilha C (Fernando)</span>
          <p class="text-sm font-semibold text-white mb-1">Cabeças 3DGS</p>
          <p class="text-xs text-slate-400">Gaussianas presas na malha deformável (A 'Pele 3D')</p>
        </div>
        <div class="bg-emerald-950/40 p-4 rounded-2xl border-2 border-emerald-500 shadow-lg">
          <span class="text-xs font-bold text-emerald-400 block mb-2">Trilha D (Cleiver) ★</span>
          <p class="text-sm font-semibold text-white mb-1">Controle & Emoção</p>
          <p class="text-xs text-slate-300">Gera o movimento 3D, piscadas e atuação a partir do áudio e texto.</p>
        </div>
      </div>
      <div class="bg-slate-950 p-3 rounded-xl border border-slate-800 text-xs text-slate-300 flex items-center gap-2">
        <span class="text-emerald-400 font-bold">Por que existo?</span>
        Sem a Trilha D, a malha do Arthur e as Gaussianas do Fernando ficam completamente paralisadas (boneco de cera) ou dependem de um ator humano gravando webcam frame a frame.
      </div>
    </div>

    <!-- SLIDE 3: AS 6 SEMENTES SOTA -->
    <div class="slide flex-col p-8 bg-slate-900 border border-slate-800 rounded-3xl shadow-2xl w-full">
      <span class="text-xs font-bold text-sky-400 mb-1">REVISÃO BIBLIOGRÁFICA</span>
      <h2 class="text-2xl font-bold text-white mb-4">As 6 Sementes da Trilha D: A Vanguarda do Estado da Arte</h2>
      <div class="grid grid-cols-2 gap-3 text-xs">
        <div class="bg-slate-950 p-3 rounded-xl border border-slate-800">
          <span class="font-bold text-sky-400">1. Motion Diffusion Models (MDM) • Motor Matemático</span>
          <p class="text-slate-300 mt-1">Resolve o problema 1-para-Muitos. Gera curvas suaves de rotação de cabeça sem colapso para a média.</p>
        </div>
        <div class="bg-slate-950 p-3 rounded-xl border border-slate-800">
          <span class="font-bold text-emerald-400">2. VASA-1 (Microsoft, 2024) • Tempo Real 40+ FPS</span>
          <p class="text-slate-300 mt-1">Desacopla identidade estática, pose de cabeça e dinâmica facial holística em espaço latente a 512x512.</p>
        </div>
        <div class="bg-slate-950 p-3 rounded-xl border border-slate-800">
          <span class="font-bold text-purple-400">3. InstructAvatar (AAAI 2025) • Direção por Texto</span>
          <p class="text-slate-300 mt-1">Two-Branch Diffusion: a voz mantém lip-sync perfeito enquanto prompts de texto livres modulam a atuação.</p>
        </div>
        <div class="bg-slate-950 p-3 rounded-xl border border-slate-800">
          <span class="font-bold text-amber-400">4. AUHead (ICLR 2026) • Anatomia FACS (Paul Ekman)</span>
          <p class="text-slate-300 mt-1">Passa pela contração dos músculos faciais reais (Action Units), garantindo controle cirúrgico sem caixas-pretas.</p>
        </div>
        <div class="bg-slate-950 p-3 rounded-xl border border-slate-800">
          <span class="font-bold text-sky-400">5. Audio2Photoreal (Meta, CVPR 2024) • Corpo Inteiro</span>
          <p class="text-slate-300 mt-1">Expande do busto para corpo inteiro e gesticulação de mãos em diálogos de 2 pessoas (VQ-VAE + Difusão).</p>
        </div>
        <div class="bg-slate-950 p-3 rounded-xl border border-slate-800">
          <span class="font-bold text-emerald-400">6. OmniHuman-1.5 (ByteDance, 2025) • Cognição Dual</span>
          <p class="text-slate-300 mt-1">Sistema 1 (reflexo reativo rápido) + Sistema 2 (planejamento deliberado via MLLM) para avatar com intenção.</p>
        </div>
      </div>
    </div>

    <!-- SLIDE 4: O DESAFIO 1-PARA-MUITOS -->
    <div class="slide flex-col p-8 bg-slate-900 border border-slate-800 rounded-3xl shadow-2xl w-full">
      <span class="text-xs font-bold text-rose-400 mb-1">O DESAFIO FUNDAMENTAL</span>
      <h2 class="text-2xl font-bold text-white mb-6">Por que Modelos Tradicionais de Regressão Falham?</h2>
      <div class="grid grid-cols-2 gap-6">
        <div class="bg-slate-950 p-5 rounded-2xl border border-rose-500/40">
          <h3 class="text-base font-bold text-rose-400 mb-3">O Problema do 1-para-Muitos</h3>
          <p class="text-xs text-slate-300 leading-relaxed mb-3">
            Para uma mesma frase, existem infinitas variações válidas de movimento de cabeça (inclinar +15° à esquerda, -15° à direita, ou assentir).
          </p>
          <p class="text-xs text-slate-300 leading-relaxed mb-3">
            <span class="text-rose-400 font-semibold">Colapso para a Média:</span> Redes determinísticas com perda MSE tentam adivinhar a média de todos os movimentos possíveis. A média é zero.
          </p>
          <div class="bg-rose-500/10 p-2.5 rounded-lg border border-rose-500/30 text-xs text-rose-300 font-semibold">
            Resultado: Cabeça congelada ou tremores robóticos ("efeito ventríloquo").
          </div>
        </div>

        <div class="bg-slate-950 p-5 rounded-2xl border border-emerald-500/40">
          <h3 class="text-base font-bold text-emerald-400 mb-3">A Solução por Difusão Estocástica (DDPM)</h3>
          <p class="text-xs text-slate-300 leading-relaxed mb-3">
            Em vez de prever um valor pontual médio, o modelo aprende a <span class="text-emerald-400 font-semibold">distribuição real de trajetórias humanas</span>.
          </p>
          <p class="text-xs text-slate-300 leading-relaxed mb-3">
            Parte de ruído gaussiano puro e realiza o <span class="text-emerald-400 font-semibold">denoising temporal</span> condicionado no espectrograma de áudio e no vetor de intenção.
          </p>
          <div class="bg-emerald-500/10 p-2.5 rounded-lg border border-emerald-500/30 text-xs text-emerald-300 font-semibold">
            Resultado Provado: 2 sementes aleatórias com o mesmo áudio geram 2 atuações distintas e naturais (L2 = 0.1194).
          </div>
        </div>
      </div>
    </div>

    <!-- SLIDE 5: RESULTADOS EXPERIMENTAIS DO PIPELINE -->
    <div class="slide flex-col p-8 bg-slate-900 border border-slate-800 rounded-3xl shadow-2xl w-full">
      <span class="text-xs font-bold text-sky-400 mb-1">VALIDAÇÃO EMPÍRICA</span>
      <h2 class="text-2xl font-bold text-white mb-4">Pipeline Operacional Implementado e Testado</h2>
      <div class="grid grid-cols-12 gap-4 items-center">
        <div class="col-span-7 bg-slate-950 p-2 rounded-2xl border border-slate-800">
          <img src="data:image/png;base64,{dash_b64}" class="w-full rounded-xl">
        </div>
        <div class="col-span-5 space-y-2 text-xs">
          <div class="bg-slate-950 p-3 rounded-xl border border-slate-800">
            <span class="font-bold text-sky-400 block mb-1">Métricas de Execução no Mac</span>
            <p class="text-slate-300">• Hardware: <span class="font-mono text-emerald-400">Apple Silicon MPS (Metal)</span></p>
            <p class="text-slate-300">• Tempo de Difusão: <span class="font-mono text-sky-400 font-bold">0.10s (~900 FPS)</span></p>
            <p class="text-slate-300">• Taxa de Vídeo: <span class="font-mono text-purple-400">30.0 FPS Sincronizado</span></p>
          </div>
          <div class="bg-slate-950 p-3 rounded-xl border border-slate-800 space-y-1">
            <span class="font-bold text-emerald-400 block mb-1">Camadas de Síntese</span>
            <p class="text-slate-300">1. Áudio: Log-Mel 80 canais + Energia RMS + Pitch F0</p>
            <p class="text-slate-300">2. Músculos: 14 Action Units FACS com piscadas</p>
            <p class="text-slate-300">3. FLAME: 50 coeficientes de expressão + mandíbula</p>
            <p class="text-slate-300">4. Formato: Exportação limpa em .JSON e .NPZ</p>
          </div>
        </div>
      </div>
    </div>

    <!-- SLIDE 6: DA MATEMÁTICA AO FOTO-REALISMO -->
    <div class="slide flex-col p-8 bg-slate-900 border border-slate-800 rounded-3xl shadow-2xl w-full">
      <span class="text-xs font-bold text-emerald-400 mb-1">FIDELIDADE VISUAL</span>
      <h2 class="text-2xl font-bold text-white mb-4">Do Esquemático ao Foto-Realismo: Foto Real Ganha Vida</h2>
      <div class="grid grid-cols-12 gap-5 items-center">
        <div class="col-span-4 flex flex-col items-center">
          <img src="data:image/jpeg;base64,{img_b64}" class="w-[200px] h-[200px] rounded-2xl object-cover border-2 border-slate-800 shadow-xl">
          <span class="text-[11px] font-mono text-slate-400 mt-2">Foto Estática Original (1024x1024)</span>
        </div>
        <div class="col-span-8 bg-slate-950 p-5 rounded-2xl border border-slate-800 space-y-2 text-xs">
          <h3 class="text-sm font-bold text-emerald-400 mb-2">Deformação Afim Densa (Delaunay Mesh Warping)</h3>
          <p class="text-slate-300 leading-relaxed">
            • <span class="font-semibold text-white">Preservação Total de Identidade:</span> Os poros da pele, barba e iluminação do estúdio são preservados pixel a pixel.
          </p>
          <p class="text-slate-300 leading-relaxed">
            • <span class="font-semibold text-white">Cavidade Bucal Real:</span> Quando a energia da voz abre a mandíbula (AU26), é sintetizada a sombra interna e dentes superiores translúcidos, sem cortes retos.
          </p>
          <p class="text-slate-300 leading-relaxed">
            • <span class="font-semibold text-white">Rotação 3D com Paralaxe:</span> Nariz e olhos movem mais rápido que as orelhas ao girar (Yaw/Pitch), dando sensação tridimensional crível.
          </p>
          <p class="text-slate-300 leading-relaxed">
            • <span class="font-semibold text-white">Piscadas Naturais:</span> As pálpebras descem com a textura da própria pele do sujeito em intervalos biológicos.
          </p>
        </div>
      </div>
    </div>

    <!-- SLIDE 7: DEMONSTRAÇÃO PRÁTICA EM VÍDEO -->
    <div class="slide flex-col p-8 bg-slate-900 border border-slate-800 rounded-3xl shadow-2xl w-full">
      <span class="text-xs font-bold text-sky-400 mb-1">DEMONSTRAÇÃO AO VIVO</span>
      <h2 class="text-2xl font-bold text-white mb-3">Vídeo Foto-Realista Gerado na Prática (Com Som)</h2>
      <div class="grid grid-cols-12 gap-5 items-center">
        <div class="col-span-6 flex justify-center bg-black/80 p-2 rounded-2xl border border-slate-800">
          <video class="w-[300px] h-[260px] rounded-xl object-contain shadow-2xl" controls autoplay loop playsinline>
            <source src="data:video/mp4;base64,{v1_b64}" type="video/mp4">
          </video>
        </div>
        <div class="col-span-6 space-y-2 text-xs">
          <div class="bg-slate-950 p-3 rounded-xl border border-slate-800">
            <span class="text-xs font-bold text-emerald-400 block mb-1">Experimento: "Meu Teste"</span>
            <p class="text-slate-300 mb-1"><span class="text-slate-400">Prompt:</span> <span class="italic text-white">"Fale com muita alegria e entusiasmo, olhando para a esquerda"</span></p>
            <p class="text-slate-300 mb-2"><span class="text-slate-400">Fala:</span> <span class="font-semibold text-sky-300">"Bem-vindos ao laboratório de humanos virtuais da nossa equipe!"</span></p>
            <div class="space-y-1 text-slate-400 text-[11px] border-t border-slate-800 pt-2">
              <p>✓ Rotação: <span class="text-emerald-400 font-mono">Yaw = +15.0° (vira à esquerda)</span></p>
              <p>✓ Expressão: <span class="text-emerald-400 font-mono">AU12 (sorriso alegre)</span></p>
              <p>✓ Sincronia Labial: <span class="text-emerald-400 font-mono">Mandíbula abre nas sílabas</span></p>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- SLIDE 8: INTERFACE COM O RESTO DO GRUPO -->
    <div class="slide flex-col p-8 bg-slate-900 border border-slate-800 rounded-3xl shadow-2xl w-full">
      <span class="text-xs font-bold text-purple-400 mb-1">INTEGRAÇÃO INTER-TRILHAS</span>
      <h2 class="text-2xl font-bold text-white mb-5">O Que a Trilha D Entrega para o Resto do Grupo?</h2>
      <div class="grid grid-cols-3 gap-4 text-xs">
        <div class="bg-slate-950 p-4 rounded-2xl border border-amber-500/40">
          <span class="text-amber-400 font-bold block mb-2">Para o Fernando (Trilha C - 3DGS)</span>
          <p class="text-slate-300 leading-relaxed mb-2">• Rotação 6D contínua da cabeça no espaço de câmera.</p>
          <p class="text-slate-300 leading-relaxed mb-2">• 50 coeficientes de deformação FLAME frame a frame.</p>
          <div class="bg-amber-500/10 p-2 rounded text-[11px] text-amber-300">
            -> Move as Gaussianas 3D sem precisar de ator na webcam!
          </div>
        </div>

        <div class="bg-slate-950 p-4 rounded-2xl border border-purple-500/40">
          <span class="text-purple-400 font-bold block mb-2">Para o Arthur (Trilha B - Malha)</span>
          <p class="text-slate-300 leading-relaxed mb-2">• Rotação dos ossos do pescoço e translação.</p>
          <p class="text-slate-300 leading-relaxed mb-2">• Rotação de mandíbula (Jaw Drop em radianos).</p>
          <div class="bg-purple-500/10 p-2 rounded text-[11px] text-purple-300">
            -> Puxa os ossos da marionete 3D com física realista!
          </div>
        </div>

        <div class="bg-slate-950 p-4 rounded-2xl border border-sky-500/40">
          <span class="text-sky-400 font-bold block mb-2">Para o Mateus (Trilha A - 2D)</span>
          <p class="text-slate-300 leading-relaxed mb-2">• Trajetórias latentes e de pose de cabeça.</p>
          <p class="text-slate-300 leading-relaxed mb-2">• Sinais de Action Units para mapas de fluxo.</p>
          <div class="bg-sky-500/10 p-2 rounded text-[11px] text-sky-300">
            -> Elimina a cabeça dura em modelos 2D!
          </div>
        </div>
      </div>
    </div>

  </main>

  <!-- Navigation Controls -->
  <footer class="flex justify-between items-center max-w-6xl mx-auto w-full pt-3 border-t border-slate-800 text-xs">
    <div class="text-slate-500">
      Use as setas <span class="font-mono bg-slate-900 px-1.5 py-0.5 rounded border border-slate-800">←</span> e <span class="font-mono bg-slate-900 px-1.5 py-0.5 rounded border border-slate-800">→</span> para navegar
    </div>
    <div class="flex gap-2">
      <button id="btnPrev" onclick="changeSlide(-1)" class="px-4 py-2 rounded-xl bg-slate-900 border border-slate-800 text-slate-300 hover:bg-slate-800 font-semibold transition-all">← Anterior</button>
      <button id="btnNext" onclick="changeSlide(1)" class="px-5 py-2 rounded-xl bg-sky-500 text-slate-950 font-bold hover:bg-sky-400 transition-all shadow-md">Próximo →</button>
    </div>
  </footer>

  <script>
    let currentSlide = 0;
    const slides = document.querySelectorAll('.slide');
    const totalSlides = slides.length;
    document.getElementById('totalSlidesNum').textContent = totalSlides;

    function showSlide(idx) {{
      slides.forEach((s, i) => {{
        if (i === idx) s.classList.add('active');
        else s.classList.remove('active');
      }});
      currentSlide = idx;
      document.getElementById('currentSlideNum').textContent = idx + 1;
      document.getElementById('btnPrev').disabled = (idx === 0);
      document.getElementById('btnPrev').style.opacity = (idx === 0) ? '0.5' : '1.0';
    }}

    function changeSlide(delta) {{
      let next = currentSlide + delta;
      if (next >= 0 && next < totalSlides) {{
        showSlide(next);
      }}
    }}

    document.addEventListener('keydown', (e) => {{
      if (e.key === 'ArrowRight' || e.key === ' ') changeSlide(1);
      if (e.key === 'ArrowLeft') changeSlide(-1);
    }});

    showSlide(0);
  </script>
</body>
</html>
"""

    with open(output_html_project, "w", encoding="utf-8") as f:
        f.write(html_content)
    with open(output_html_artifact, "w", encoding="utf-8") as f:
        f.write(html_content)

    print(f"Deck interativo HTML gerado com sucesso em:")
    print(f"  -> {output_html_project}")
    print(f"  -> {output_html_artifact}")

if __name__ == "__main__":
    generate_html_deck()
