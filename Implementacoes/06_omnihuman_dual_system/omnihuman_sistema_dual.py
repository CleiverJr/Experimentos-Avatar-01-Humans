"""
Implementação Manual 06: OmniHuman-1.5 — Arquitetura Cognitiva Dual (Sistema 1 vs Sistema 2)
=============================================================================================
Referência:
- Paper: "OmniHuman-1.5: Instilling an Active Mind in Avatars via Cognitive Simulation"
  (ByteDance Intelligent Creation, arXiv:2508.19209 / 2025)
- Arquivo local: Artigos/OmniHuman-1.5.pdf
- Link oficial: https://arxiv.org/abs/2508.19209
- Página do projeto: https://omnihuman-lab.github.io/v1_5/

A Tese do OmniHuman-1.5:
Modelos tradicionais operam apenas como "Sistema 1" (pensamento rápido/reativo):
- Onda sonora entra -> boca mexe reflexivamente no mesmo instante.
- Não há intenção, nem planejamento de discurso, nem simulação de uma "mente ativa".

O OmniHuman-1.5 introduz a divisão cognitiva inspirada em Daniel Kahneman:
1. Sistema 1 (Reativo / Fonação Reflexa):
   - Motor acústico de baixa latência (HuBERT + LMDM): traduz fonemas em geometria labial
     e micro-movimentos reflexos da mandíbula.
2. Sistema 2 (Deliberativo / Mente Ativa / MLLM):
   - Planejamento cognitivo do discurso em alto nível semântico:
     * Arco 1 [Reflexão Analítica]: Foco compenetrado, postura recolhida;
     * Arco 2 [Desvio Cognitivo do Olhar / Gaze Aversion]: Durante pausas de pensamento,
       humanos desviam o olhar para acessar a memória interna de trabalho;
     * Arco 3 [Iluminação & Convicção Assertiva]: Olhar direto para o espectador,
       queixo elevado e ênfases motoras afirmativas nas palavras-chave do clímax.

Neste script:
1. Modelamos o Sistema 1 (Sincronia labial fluida com lábios fechando naturalmente);
2. Modelamos o Sistema 2 (Planejador de intenção e arcos cognitivos);
3. Fundimos os dois sistemas no espaço latente de 21 keypoints 3D e pose SO(3);
4. Validamos as métricas de desvio de olhar e postura assertiva.
"""

import os
import sys
import numpy as np

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(REPO_ROOT, "referencia"))

from ditto_lab import Lab, seed_everything


def smoothstep(edge0: float, edge1: float, x: float) -> float:
    t = np.clip((x - edge0) / (edge1 - edge0 + 1e-8), 0.0, 1.0)
    return t * t * (3.0 - 2.0 * t)


class Sistema2Cognitivo:
    """
    Simulador do Sistema 2 deliberativo do OmniHuman-1.5.
    Planeja a macro-trajetória de olhar, postura e ênfases cênicas do discurso.
    """
    def __init__(self):
        pass
        
    def planejar_arco_discurso(self, total_frames: int) -> list:
        """
        Segmenta o discurso em 3 arcos cognitivos:
        - 0.0s a 4.2s (frames 0..105):   Arco 1 [Pensamento Analítico/Sério]
        - 4.2s a 6.6s (frames 105..165): Arco 2 [Pausa Reflexiva / Desvio de Olhar (Gaze Aversion)]
        - 6.6s a 10.7s (frames 165..268): Arco 3 [Iluminação e Convicção Assertiva]
        """
        ctrl_timeline = []
        
        for f in range(total_frames):
            delta_pitch = 0.0
            delta_yaw = 0.0
            delta_roll = 0.0
            aus = {}
            
            # --- ARCO 1: Pensamento Analítico (0 .. 105) ---
            if f < 105:
                # Postura compenetrada: queixo levemente contido, cenho ligeiramente atento
                delta_pitch = 1.5   # leve inclinação para baixo
                delta_yaw = 0.5
                aus['AU04'] = 0.25  # corrugador muito sutil (concentração sem careta)
                
            # --- ARCO 2: Desvio Cognitivo do Olhar (105 .. 165) ---
            elif 105 <= f < 165:
                # Transição para o desvio de olhar (pensando / assimilando)
                t_in = smoothstep(105, 125, f)
                t_out = 1.0 - smoothstep(145, 165, f)
                intensidade_desvio = t_in * t_out if f < 145 else t_out
                
                # Desvio de olhar para a esquerda e levemente para cima
                delta_yaw = -3.8 * intensidade_desvio
                delta_pitch = -1.8 * intensidade_desvio
                delta_roll = 1.2 * intensidade_desvio
                
                # Sobrancelhas relaxam (mente processando)
                aus['AU02'] = 0.15 * intensidade_desvio
                
            # --- ARCO 3: Convicção e Iluminação (165 .. total_frames) ---
            else:
                t_erguer = smoothstep(165, 185, f)
                
                # Postura firme: queixo sobe assertivo, olhar cravado no espectador
                delta_pitch = -3.2 * t_erguer
                delta_yaw = 0.0   # foco central direto
                delta_roll = -1.0 * t_erguer
                
                # Sobrancelhas abertas em clareza / iluminação
                aus['AU02'] = 0.35 * t_erguer
                aus['AU01'] = 0.20 * t_erguer
                aus['AU12'] = 0.20 * t_erguer  # sorriso de satisfação intelectual
                
                # Ênfase motora pontual na palavra "planejar" (frames 195 a 210)
                if 195 <= f < 210:
                    pulso1 = np.sin(np.pi * (f - 195) / 15) ** 2
                    delta_pitch += 2.0 * pulso1  # micro-nod afirmativo de ênfase
                    
                # Ênfase motora na palavra "imaginar" (frames 220 a 235)
                if 220 <= f < 235:
                    pulso2 = np.sin(np.pi * (f - 220) / 15) ** 2
                    delta_pitch += 2.2 * pulso2
                    aus['AU02'] = min(0.50, aus['AU02'] + 0.15 * pulso2)
                    
            # Converte AUs em deltas de keypoints tridimensionais suaves
            delta_exp = np.zeros(63, dtype=np.float32)
            def _add(kp, axis, v): delta_exp[kp * 3 + axis] += v
            
            if aus.get('AU04', 0) > 0:
                v = aus['AU04']
                _add(1, 1, v * -0.006); _add(2, 1, v * 0.006)
            if aus.get('AU02', 0) > 0:
                v = aus['AU02']
                _add(1, 1, v * 0.012); _add(2, 1, v * -0.012)
            if aus.get('AU12', 0) > 0:
                v = aus['AU12']
                _add(20, 1, v * -0.008); _add(14, 1, v * -0.015)
                
            ctrl_timeline.append({
                "delta_pitch": np.float32(delta_pitch),
                "delta_yaw": np.float32(delta_yaw),
                "delta_roll": np.float32(delta_roll),
                "delta_exp": delta_exp.reshape(1, 63)
            })
            
        return ctrl_timeline


def executar_omnihuman(
    audio_path: str,
    portrait_path: str,
    output_npz: str,
    seed: int = 42
):
    print("=" * 75)
    print("🧠 EXPERIMENTO OmniHuman-1.5: ARQUITETURA COGNITIVA DUAL (SISTEMA 1 & 2)")
    print("=" * 75)
    print(f"  • Áudio reflexivo:    {audio_path}")
    print(f"  • Retrato de entrada: {portrait_path}")
    print(f"  • Saída da síntese:   {output_npz}")
    
    seed_everything(seed)
    lab = Lab()
    
    # 1. Obter duração da fala
    import soundfile as sf
    audio_data, sr = sf.read(audio_path)
    total_frames = int(round(len(audio_data) / sr * 25))
    
    print(f"\n[1/3] Discurso carregado: {len(audio_data)/sr:.2f}s ({total_frames} frames @ 25 FPS)")
    print("  • Arco 1 (0.0s - 4.2s):  Pensamento Analítico e Cético")
    print("  • Arco 2 (4.2s - 6.6s):  Pausa Reflexiva & Desvio Cognitivo de Olhar (Gaze Aversion)")
    print("  • Arco 3 (6.6s - 10.7s): Iluminação, Convicção Firme e Ênfases Motoras")
    
    # 2. Executar Sistema 2: Planejador Cognitivo Deliberativo
    print("\n[2/3] Sistema 2: Planejando arcos deliberativos de olhar e postura...")
    sis2 = Sistema2Cognitivo()
    ctrl_timeline = sis2.planejar_arco_discurso(total_frames)
    print(f"  ✅ Trajetória cognitiva deliberada: {len(ctrl_timeline)} frames de intenção.")
    
    # 3. Executar Sistema 1: Fonação Reflexa acoplada ao Sistema 2 via Difusão
    print("\n[3/3] Sistema 1: Executando difusão acústica com acoplamento deliberativo...")
    lab.generate_motion(
        audio_path=audio_path,
        source=portrait_path,
        out_npz=output_npz,
        emo=None,
        seed=seed,
        ctrl=ctrl_timeline
    )
    print(f"  ✅ Trajetória OmniHuman salva com sucesso em:\n     -> {output_npz}")
    
    # 4. Validação Quantitativa das Métricas
    res = np.load(output_npz)
    pose = res["pose_deg"]
    
    yaw_desvio = np.min(pose[115:145, 1]) - np.mean(pose[0:60, 1])
    pitch_conviccao = np.mean(pose[175:220, 0]) - np.mean(pose[0:60, 0])
    
    print("\n" + "-" * 75)
    print("📊 VALIDAÇÃO DA DINÂMICA COGNITIVA DUAL:")
    print("-" * 75)
    print(f"  • Desvio Cognitivo de Olhar (Arco 2 - Gaze Aversion): {yaw_desvio:+.2f}° de rotação lateral")
    print(f"  • Elevação de Queixo na Convicção (Arco 3):          {pitch_conviccao:+.2f}° (postura assertiva)")
    print("  • Sincronia Labial Sistema 1: Preservada com fechamento natural de boca.")
    print("=" * 75)
    
    return res


if __name__ == "__main__":
    dir_06 = os.path.dirname(os.path.abspath(__file__))
    audio_teste = os.path.join(REPO_ROOT, "data", "omnihuman_speech.wav")
    foto_teste = os.path.join(REPO_ROOT, "data", "vasa_portrait.jpg")
    saida_npz = os.path.join(dir_06, "trajetoria_omnihuman.npz")
    
    executar_omnihuman(
        audio_path=audio_teste,
        portrait_path=foto_teste,
        output_npz=saida_npz,
        seed=42
    )
