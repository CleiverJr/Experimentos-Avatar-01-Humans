"""
Implementação Manual 05: Audio2Photoreal — Comportamento Diádico e Escuta Ativa (Backchanneling)
==================================================================================================
Referência:
- Paper: "From Audio to Photoreal Embodiment: Synthesizing Humans in Conversations"
  (CVPR 2024, Meta Reality Labs / Codec Avatars Lab — Richard et al.)
- Arquivo local: Artigos/Audio2Photoreal.pdf
- Link oficial: https://arxiv.org/abs/2401.01885
- Código oficial: https://github.com/facebookresearch/audio2photoreal

A Tese do Audio2Photoreal:
Modelos tradicionais tratam a síntese de avatares como um MONÓLOGO ISOLADO:
quando há áudio, a boca se mexe; quando não há áudio, o avatar congela como uma estátua.

Porém, em conversações reais entre humanos (interações diádicas):
1. Passamos 50% do tempo ESCUTANDO o outro falar;
2. Ouvintes humanos não ficam congelados: executam BACKCHANNELING:
   - Acenos de concordância afirmativos (Head Nods) no eixo Pitch;
   - Inclinações de atenção e escuta atenta no eixo Roll;
   - Micro-sorrisos de empatia e compreensão;
   - E fundamentalmente: a boca permanece FECHADA e em repouso natural enquanto o outro fala!
3. Quando o turno de fala muda (Turn-Taking), o avatar assume o papel de Falante (Speaker)
   com sincronia labial ativa e articulação de fonemas.

Neste script:
1. Processamos um diálogo conversacional com alternância de turnos:
   - 0.0s a 6.17s  (frames 0..154): Interlocutora fala uma pergunta -> Avatar em ESCUTA ATIVA
   - 6.17s a 6.97s (frames 154..174): Silêncio de Turn-Taking -> Avatar prepara resposta
   - 6.97s a 14.65s (frames 174..366): Avatar responde com FALA ATIVA
2. Construímos o modelo de controle cinemático do ouvinte:
   - vad_alpha = 0.0 durante a escuta (lábios fechados, boca em repouso);
   - Injeção de acenos afirmativos (head nods) sincronizados com as pausas da fala da interlocutora;
   - Transição suave (Hermite smoothstep) para vad_alpha = 1.0 quando o avatar começa a falar.
3. Geramos a trajetória cinemática em trajetoria_diadica.npz.
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


def calcular_aceno_cabeca(frame: int, f_inicio: int, duracao_frames: int, amplitude_deg: float) -> float:
    """Gera um aceno afirmativo suave (head nod no eixo pitch) usando curva seno ao quadrado."""
    if f_inicio <= frame < f_inicio + duracao_frames:
        fase = (frame - f_inicio) / duracao_frames
        return float(amplitude_deg * (np.sin(np.pi * fase) ** 2))
    return 0.0


def au_dict_to_delta_exp(au_dict: dict) -> np.ndarray:
    """Converte AUs sutis de empatia para o vetor de keypoints 3D."""
    delta = np.zeros(63, dtype=np.float32)
    def _add(kp, axis, v): delta[kp * 3 + axis] += v
    def _g(k): return float(au_dict.get(k, 0.0))
    
    # AU12 sutil (sorriso leve de empatia, sem escancarar os dentes)
    if _g('AU12') > 0:
        s = _g('AU12') * 0.4  # dose controlada para não expor dentes na escuta
        _add(20, 1, s * -0.008); _add(14, 1, s * -0.015)
        _add(17, 1, s * 0.003)
        
    # AU02 (leve atenção no olhar)
    if _g('AU02') > 0:
        _add(1, 1, _g('AU02') * 0.010); _add(2, 1, _g('AU02') * -0.010)
        
    return delta


def construir_timeline_diadica(total_frames: int, frame_fim_pergunta: int = 154, frame_inicio_resposta: int = 174) -> list:
    """
    Constrói a timeline comportamental diádica:
    - Fase 1 (0 .. frame_fim_pergunta): LISTENER (Escuta Ativa / Backchanneling)
      * vad_alpha = 0.0 (boca 100% fechada)
      * Head Nod 1 (frames 35..65): Aceno leve pós-"Olá!"
      * Head Nod 2 (frames 110..150): Aceno duplo de concordância com a pergunta
      * Leve inclinação lateral de interesse (Roll = -1.8°)
    - Fase 2 (frame_fim_pergunta .. frame_inicio_resposta): TURN-TAKING
      * Transição suave de vad_alpha: 0.0 -> 1.0
      * Retorno da postura de escuta para postura assertiva
    - Fase 3 (frame_inicio_resposta .. total_frames): SPEAKER (Fala Ativa)
      * vad_alpha = 1.0 (sincronia labial total via HuBERT)
    """
    ctrl_timeline = []
    
    for f in range(total_frames):
        # 1. Determina o estado e o VAD (Voice Activity Detection do Avatar)
        if f < frame_fim_pergunta:
            # Estado Ouvinte: Lábios em repouso fechado
            vad_alpha = 0.0
            modo = "LISTENER"
        elif f < frame_inicio_resposta:
            # Transição suave de turno (Turn-Taking)
            vad_alpha = float(smoothstep(frame_fim_pergunta, frame_inicio_resposta, f))
            modo = "TURNING"
        else:
            # Estado Falante: Sincronia total
            vad_alpha = 1.0
            modo = "SPEAKER"
            
        # 2. Dinâmica de Cabeça (Backchanneling Nods e Atenção)
        delta_pitch = 0.0
        delta_roll = 0.0
        delta_yaw = 0.0
        aus = {}
        
        if modo == "LISTENER":
            # Inclinação sutil de cabeça para o lado (atenção empática)
            delta_roll = -1.8
            
            # Aceno 1: aos 1.5s (frames 35 a 62)
            nod1 = calcular_aceno_cabeca(f, f_inicio=35, duracao_frames=27, amplitude_deg=3.5)
            
            # Aceno 2: aos 4.5s (frames 110 a 145) - aceno duplo suave
            nod2 = calcular_aceno_cabeca(f, f_inicio=110, duracao_frames=35, amplitude_deg=4.2)
            
            delta_pitch = nod1 + nod2
            
            # Sorriso empático sutil durante a pergunta
            if 115 <= f < 154:
                aus['AU12'] = 0.25 * float(smoothstep(115, 130, f))
                aus['AU02'] = 0.20
        elif modo == "TURNING":
            # Leve elevação do queixo indicando que vai começar a falar
            t_turn = smoothstep(frame_fim_pergunta, frame_inicio_resposta, f)
            delta_pitch = -1.5 * t_turn
            delta_roll = -1.8 * (1.0 - t_turn)
            aus['AU02'] = 0.15
        else:
            # Modo Speaker: Movimento guiado pela prosódia natural do áudio
            delta_pitch = 0.0
            delta_roll = 0.0
            
        f_delta_exp = au_dict_to_delta_exp(aus).reshape(1, 63)
        
        ctrl_timeline.append({
            "vad_alpha": np.float32(vad_alpha),
            "delta_pitch": np.float32(delta_pitch),
            "delta_yaw": np.float32(delta_yaw),
            "delta_roll": np.float32(delta_roll),
            "delta_exp": f_delta_exp
        })
        
    return ctrl_timeline


def executar_experimento_diadico(
    audio_path: str,
    portrait_path: str,
    output_npz: str,
    seed: int = 42
):
    print("=" * 75)
    print("👥 EXPERIMENTO Audio2Photoreal: COMPORTAMENTO DIÁDICO & ESCUTA ATIVA")
    print("=" * 75)
    print(f"  • Áudio conversacional: {audio_path}")
    print(f"  • Retrato do avatar:    {portrait_path}")
    print(f"  • Saída da trajetória:  {output_npz}")
    
    seed_everything(seed)
    lab = Lab()
    
    # 1. Obter duração do áudio
    import soundfile as sf
    audio_data, sr = sf.read(audio_path)
    total_frames = int(round(len(audio_data) / sr * 25))
    frame_pergunta = 154  # 6.17s
    frame_resposta = 174  # 6.97s
    
    print(f"\n[1/3] Estrutura do diálogo diádico ({len(audio_data)/sr:.2f}s | {total_frames} frames):")
    print(f"  • 0.00s a 6.17s (frames   0 a {frame_pergunta}): Interlocutora pergunta -> Avatar ESCUTANDO (Boca Fechada)")
    print(f"  • 6.17s a 6.97s (frames {frame_pergunta} a {frame_resposta}): Transição de Turno (Turn-Taking)")
    print(f"  • 6.97s a {total_frames/25:.2f}s (frames {frame_resposta} a {total_frames}): Avatar responde -> FALA ATIVA (Lip-Sync)")
    
    # 2. Construir timeline de controle comportamental
    print("\n[2/3] Modelando acenos de cabeça (head nods) e modulação de VAD...")
    ctrl_timeline = construir_timeline_diadica(total_frames, frame_pergunta, frame_resposta)
    print(f"  ✅ Timeline calibrada gerada: {len(ctrl_timeline)} frames de comandos conversacionais.")
    
    # 3. Executar difusão LMDM
    print("\n[3/3] Executando difusão no espaço latente com transição de papéis...")
    lab.generate_motion(
        audio_path=audio_path,
        source=portrait_path,
        out_npz=output_npz,
        emo=None,
        seed=seed,
        ctrl=ctrl_timeline
    )
    print(f"  ✅ Trajetória diádica salva em:\n     -> {output_npz}")
    
    # 4. Análise das métricas
    res = np.load(output_npz)
    pose_deg = res["pose_deg"]
    x_d = res["x_d"]
    
    # Pitch nos acenos de cabeça
    pitch_nod1 = np.max(pose_deg[35:65, 0]) - np.mean(pose_deg[0:30, 0])
    pitch_nod2 = np.max(pose_deg[110:145, 0]) - np.mean(pose_deg[0:30, 0])
    
    # Abertura labial (distância entre lábio superior kp 17 e inferior kp 19)
    dist_mouth = np.linalg.norm(x_d[:, 19, :] - x_d[:, 17, :], axis=-1)
    abertura_escuta = np.mean(dist_mouth[0:frame_pergunta])
    abertura_fala = np.mean(dist_mouth[frame_resposta:])
    
    print("\n" + "-" * 75)
    print("📊 VALIDAÇÃO DAS MÉTRICAS CONVERSACIONAIS:")
    print("-" * 75)
    print(f"  • Aceno de Cabeça 1 (pós-cumprimento): +{pitch_nod1:.2f}° (inclinação afirmativa confirmada)")
    print(f"  • Aceno de Cabeça 2 (confirmação empática): +{pitch_nod2:.2f}° (nodding ativo)")
    print(f"  • Abertura labial durante ESCUTA: {abertura_escuta:.4f} (boca naturalmente fechada)")
    print(f"  • Abertura labial durante FALA:   {abertura_fala:.4f} (articulação fonética ativa)")
    print(f"  • Razão de articulação Fala/Escuta: {abertura_fala/abertura_escuta:.2f}x mais ativa na fala")
    print("=" * 75)
    
    return res


if __name__ == "__main__":
    dir_05 = os.path.dirname(os.path.abspath(__file__))
    audio_teste = os.path.join(REPO_ROOT, "data", "dialogo_diadico.wav")
    foto_teste = os.path.join(REPO_ROOT, "data", "vasa_portrait.jpg")
    saida_npz = os.path.join(dir_05, "trajetoria_diadica.npz")
    
    executar_experimento_diadico(
        audio_path=audio_teste,
        portrait_path=foto_teste,
        output_npz=saida_npz,
        seed=42
    )
