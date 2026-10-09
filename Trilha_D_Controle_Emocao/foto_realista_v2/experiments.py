"""
Gera o MOVIMENTO (difusão + controles da Trilha D) de todos os experimentos.
A renderização é feita depois (ditto_lab.py render), possivelmente em paralelo.

Cada experimento salva:
  runs/<exp>/<variante>.npz   -> keypoints x_s/x_d por frame + pose/expressão geradas
  runs/<exp>/<variante>.json  -> linha do tempo dos controles (para legendas e gráficos)
"""
import os
import sys
import json
import pickle
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "trilha"))
from ditto_lab import Lab, au_to_delta_exp, emo_vector, EMO_NAMES, FPS
from instruct_parser import InstructParser   # parser de instruções da própria Trilha D

AUD = "/home/claude/w/aud"
SRC = "/home/claude/w/in/portrait.jpg"
RUNS = "/home/claude/w/lab/runs"
BASE_PITCH = 2.0          # o Ditto aplica +2° de pitch por padrão (overall_ctrl_info)
AUS = ["AU01", "AU02", "AU04", "AU06", "AU12", "AU15", "AU26", "AU43"]

# Protótipos EMFACS (Ekman & Friesen) restritos às AUs que o renderer controla
EMO_AU = {
    "Happy":    {"AU06": 0.7, "AU12": 0.85},
    "Sad":      {"AU01": 0.9, "AU04": 0.45, "AU15": 0.9},
    "Angry":    {"AU04": 1.0, "AU06": 0.35, "AU15": 0.25},
    "Surprise": {"AU01": 0.8, "AU02": 1.0, "AU26": 0.35},
    "Fear":     {"AU01": 0.9, "AU02": 0.6, "AU04": 0.5, "AU26": 0.2},
    "Disgust":  {"AU04": 0.6, "AU15": 0.5},
    "Contempt": {"AU12": 0.3},
    "Neutral":  {},
}
PARSER2DITTO = {"happy": "Happy", "sad": "Sad", "angry": "Angry", "surprised": "Surprise",
                "fear": "Fear", "disgusted": "Disgust", "skeptical": "Contempt", "neutral": "Neutral"}


def smooth_env(t, a, b, ramp=0.3):
    """envelope 0..1 com subida/descida suave (smoothstep) em [a, b]"""
    def ss(x):
        x = np.clip(x, 0, 1)
        return x * x * (3 - 2 * x)
    return ss((t - a) / ramp) * (1 - ss((t - b) / ramp))


def n_frames(wav):
    import soundfile as sf
    x, sr = sf.read(wav)
    return int(np.ceil(len(x) / sr * FPS))


def build_ctrl(N, au_tracks=None, pitch=None, yaw=None, roll=None):
    """au_tracks: {AU: array N}; pitch/yaw/roll: arrays N (graus, somados à pose gerada)."""
    ctrl, tl = [], []
    for i in range(N):
        au = {k: float(v[i]) for k, v in (au_tracks or {}).items()}
        d = {"delta_exp": au_to_delta_exp(au)[None],
             "delta_pitch": BASE_PITCH + (float(pitch[i]) if pitch is not None else 0.0),
             "delta_yaw": float(yaw[i]) if yaw is not None else 0.0,
             "delta_roll": float(roll[i]) if roll is not None else 0.0}
        ctrl.append(d)
        tl.append({"t": round(i / FPS, 3), "au": {k: round(v, 3) for k, v in au.items()},
                   "dpitch": round(d["delta_pitch"] - BASE_PITCH, 2), "dyaw": round(d["delta_yaw"], 2),
                   "droll": round(d["delta_roll"], 2)})
    return ctrl, tl


def save_tl(path, tl, **extra):
    with open(path, "w", encoding="utf-8") as f:
        json.dump({"fps": FPS, "frames": tl, **extra}, f, ensure_ascii=False)


# ---------------------------------------------------------------------------
def exp_vasa(lab):
    """VASA-1: foto + áudio -> dinâmica holística (lábios, olhar, piscadas, pose) por difusão.
    Sem nenhum controle explícito: tudo vem do LMDM condicionado no áudio."""
    out = f"{RUNS}/E1_vasa"; os.makedirs(out, exist_ok=True)
    for name, wav in [("nova_voz", f"{AUD}/vasa.wav"), ("audio_antigo", f"{AUD}/old_vasa_8s.wav")]:
        N = n_frames(wav)
        ctrl, tl = build_ctrl(N)
        lab.generate_motion(wav, SRC, f"{out}/{name}.npz", emo=None, seed=0, ctrl=ctrl)
        save_tl(f"{out}/{name}.json", tl, audio=wav)


def exp_instruct(lab):
    """InstructAvatar: mesma fala, instruções de texto diferentes.
    Texto -> InstructParser (código da Trilha D) -> (rótulo de emoção do Ditto + perfil de AUs + viés de pose)."""
    out = f"{RUNS}/E2_instruct"; os.makedirs(out, exist_ok=True)
    wav = f"{AUD}/instruct.wav"; N = n_frames(wav); t = np.arange(N) / FPS
    parser = InstructParser()
    instr = {
        "neutro": "Fale de forma natural, olhando para a câmera",
        "alegre": "Fale com muita alegria e um sorriso, olhando para a esquerda",
        "triste": "Fale com tristeza profunda, desanimado, cabeça para baixo",
        "raiva":  "Fale com muita raiva, irritado, olhando para a direita",
        "surpreso": "Fale muito surpreso, chocado com a notícia",
    }
    meta = {}
    for name, text in instr.items():
        p = parser.parse_instruction(text)
        inten = min(p["intensity"] / 1.5, 1.0) if p["intensity"] >= 1 else p["intensity"]
        weights = {PARSER2DITTO[k]: v for k, v in p["emotion_weights"].items()}
        emo = emo_vector(weights)
        env = smooth_env(t, 0.0, t[-1] + 1, ramp=0.5)
        aus = {}
        for e, w in weights.items():
            for au, v in EMO_AU[e].items():
                aus[au] = aus.get(au, 0) + v * w * inten
        tracks = {au: env * v for au, v in aus.items()}
        hb = p["head_bias"]
        # convenção: "esquerda" = esquerda do avatar
        yaw = env * (-hb["yaw_deg"] * 0.8)
        pitch = env * (-hb["pitch_deg"] * 0.8)    # pitch positivo do parser = olhar para cima
        if hb.get("nodding"):
            pitch = pitch + 3 * np.sin(2 * np.pi * 1.2 * t) * env
        ctrl, tl = build_ctrl(N, tracks, pitch=pitch, yaw=yaw)
        lab.generate_motion(wav, SRC, f"{out}/{name}.npz", emo=emo, seed=7, ctrl=ctrl)
        meta[name] = {"instrucao": text, "emotion_weights": p["emotion_weights"], "intensity": p["intensity"],
                      "head_bias": hb, "ditto_emo": dict(zip(EMO_NAMES, emo[0].round(3).tolist())),
                      "aus": {k: round(v, 3) for k, v in aus.items()}}
        save_tl(f"{out}/{name}.json", tl, audio=wav, **meta[name])
    json.dump(meta, open(f"{out}/instrucoes.json", "w"), ensure_ascii=False, indent=1)


def exp_auhead(lab):
    """AUHead: controle anatômico explícito por Action Units (FACS), sincronizado com a fala."""
    out = f"{RUNS}/E3_auhead"; os.makedirs(out, exist_ok=True)
    wav = f"{AUD}/auhead2.wav"; N = n_frames(wav); t = np.arange(N) / FPS
    seg = json.load(open(f"{AUD}/auhead2_segments.json"))
    # segmentos: 0 frase introdutória | 1 sorriso | 2 sobrancelhas | 3 testa franzida | 4 olhos | 5 mandíbula
    hold = 0.75
    tracks = {au: np.zeros(N) for au in AUS}
    def on(i, au, v, extra_hold=hold):
        a, b = seg[i]
        tracks[au] += v * smooth_env(t, a - 0.1, b + extra_hold, ramp=0.25)
    on(1, "AU12", 1.0); on(1, "AU06", 0.8)
    on(2, "AU01", 0.7); on(2, "AU02", 1.0)
    on(3, "AU04", 1.0)
    a, b = seg[4]
    tracks["AU43"] += smooth_env(t, b + 0.05, b + 0.55, ramp=0.12)      # fecha os olhos depois de dizer "os olhos"
    on(5, "AU26", 0.8, extra_hold=0.4)
    tracks = {k: np.clip(v, 0, 1.2) for k, v in tracks.items()}
    ctrl, tl = build_ctrl(N, tracks)
    lab.generate_motion(wav, SRC, f"{out}/au_timeline.npz", emo=None, seed=11, ctrl=ctrl)
    save_tl(f"{out}/au_timeline.json", tl, audio=wav, segments=seg,
            labels=["Introdução", "AU12+AU06 (sorriso de Duchenne)", "AU01+AU02 (sobrancelhas)",
                    "AU04 (corrugador)", "AU43 (olhos fechados)", "AU26 (mandíbula)"])


def exp_conversa(lab):
    """Audio2Photoreal: comportamento conversacional (falar E escutar).
    Turno 1 fala -> turno 2 escuta o interlocutor (acenos de backchannel nos picos de energia da voz
    dele + sorriso leve + leve giro para o interlocutor) -> turno 3 responde."""
    import soundfile as sf
    out = f"{RUNS}/E4_conversa"; os.makedirs(out, exist_ok=True)
    wav = f"{AUD}/conv_avatar.wav"; N = n_frames(wav); t = np.arange(N) / FPS
    seg = json.load(open(f"{AUD}/conv_segments.json"))
    # energia da voz do interlocutor por frame
    x, sr = sf.read(f"{AUD}/conv_partner.wav")
    hop = sr // FPS
    en = np.array([np.sqrt(np.mean(x[i * hop:(i + 1) * hop] ** 2)) if i * hop < len(x) else 0 for i in range(N)])
    en = np.convolve(en, np.ones(5) / 5, mode="same")
    listen = smooth_env(t, seg["b"][0] - 0.2, seg["b"][1] + 0.1, ramp=0.4)
    # acenos: detecta picos de ênfase (máximos locais acima do percentil 80, separados >0.9 s)
    thr = np.percentile(en[en > 0], 80) if (en > 0).any() else 1
    peaks, last = [], -99
    for i in range(2, N - 2):
        if en[i] > thr and en[i] == en[i - 2:i + 3].max() and t[i] - last > 0.9 and listen[i] > 0.5:
            peaks.append(i); last = t[i]
    nod = np.zeros(N)
    for p in peaks:
        nod += 4.5 * np.exp(-0.5 * ((t - t[p] - 0.15) / 0.12) ** 2)     # aceno ≈ 0,3 s
    pitch = -nod
    yaw = -6.0 * listen                                                   # vira um pouco para o interlocutor
    tracks = {"AU12": 0.35 * listen + 0.55 * smooth_env(t, seg["a2"][0], seg["a2"][0] + 1.2, 0.3),
              "AU06": 0.3 * listen + 0.4 * smooth_env(t, seg["a2"][0], seg["a2"][0] + 1.2, 0.3),
              "AU02": 0.5 * smooth_env(t, seg["a1"][0] + 1.6, seg["a1"][1], 0.2)}   # sobrancelha na pergunta
    ctrl, tl = build_ctrl(N, tracks, pitch=pitch, yaw=yaw)
    emo = np.stack([emo_vector({"Happy": 0.7, "Neutral": 0.3})[0] if ti >= seg["a2"][0] else emo_vector({"Neutral": 1})[0]
                    for ti in t])
    lab.generate_motion(wav, SRC, f"{out}/conversa.npz", emo=emo, seed=5, ctrl=ctrl)
    save_tl(f"{out}/conversa.json", tl, audio=f"{AUD}/conv_mix.wav", segments=seg,
            nods=[round(float(t[p]), 2) for p in peaks])


def exp_omni(lab):
    """OmniHuman-1.5: Sistema 1 (reativo, só áudio) vs Sistema 1 + Sistema 2 (plano deliberado
    a partir do SIGNIFICADO da fala). O plano abaixo foi escrito por um LLM (Claude) lendo a
    transcrição — é o papel do MLLM no OmniHuman-1.5."""
    out = f"{RUNS}/E5_omnihuman"; os.makedirs(out, exist_ok=True)
    wav = f"{AUD}/omni.wav"; N = n_frames(wav); t = np.arange(N) / FPS
    s = json.load(open(f"{AUD}/omni_segments.json"))
    # S1
    ctrl, tl = build_ctrl(N)
    lab.generate_motion(wav, SRC, f"{out}/s1_reativo.npz", emo=None, seed=3, ctrl=ctrl)
    save_tl(f"{out}/s1_reativo.json", tl, audio=wav)
    # S2 — plano
    a1, b1 = s["omni_1"]; a2, b2 = s["omni_2"]; a3, b3 = s["omni_3"]; a4, b4 = s["omni_4"]
    plan = [
        {"t": [a1, a2 - 0.15], "texto": "Deixa eu pensar...", "intencao": "buscar memória / hesitar",
         "acao": "olhar para cima e para o lado, testa levemente franzida, pausa sem fala"},
        {"t": [a2, b2], "texto": "Acho que a melhor parte foi o controle de emoção.", "intencao": "opinião positiva",
         "acao": "aceno afirmativo em 'melhor parte', sorriso"},
        {"t": [a3, b3], "texto": "Mas, sinceramente, ainda falta bastante...", "intencao": "ressalva / honestidade",
         "acao": "inclina a cabeça em 'sinceramente', sobrancelhas de preocupação, balança a cabeça em 'falta bastante'"},
        {"t": [a4, b4 + 0.4], "texto": "Vamos continuar testando!", "intencao": "encerramento animado",
         "acao": "flash de sobrancelha, sorriso aberto, aceno"},
    ]
    think = smooth_env(t, a1 + 0.1, a2 - 0.25, ramp=0.35)
    pitch = 7.0 * think
    yaw = 10.0 * think
    roll = np.zeros(N)
    # aceno em "melhor parte" (~35% da frase 2) e no fim
    tn = a2 + 0.35 * (b2 - a2)
    pitch += -4.0 * np.exp(-0.5 * ((t - tn) / 0.13) ** 2) - 3.0 * np.exp(-0.5 * ((t - tn - 0.38) / 0.12) ** 2)
    # "sinceramente": inclinação lateral
    roll += 5.0 * smooth_env(t, a3 + 0.3, a3 + 1.6, ramp=0.3)
    # "ainda falta bastante": balançar a cabeça (não)
    shake = smooth_env(t, a3 + 1.7, b3, ramp=0.25)
    yaw += 4.5 * np.sin(2 * np.pi * 1.7 * (t - a3)) * shake
    # final: aceno animado
    tf = a4 + 0.3
    pitch += -4.0 * np.exp(-0.5 * ((t - tf) / 0.13) ** 2)
    tracks = {
        "AU04": 0.45 * think + 0.35 * smooth_env(t, a3 + 0.3, b3, 0.3),
        "AU01": 0.55 * smooth_env(t, a3 + 0.3, b3, 0.3),
        "AU12": 0.75 * smooth_env(t, a2 + 0.2, b2 + 0.2, 0.35) + 0.95 * smooth_env(t, a4 - 0.1, b4 + 0.8, 0.3),
        "AU06": 0.5 * smooth_env(t, a2 + 0.2, b2 + 0.2, 0.35) + 0.7 * smooth_env(t, a4 - 0.1, b4 + 0.8, 0.3),
        "AU02": 0.8 * smooth_env(t, a4 - 0.15, a4 + 0.35, 0.12),
        "AU15": 0.35 * smooth_env(t, a3 + 1.7, b3, 0.3),
    }
    emo = []
    for ti in t:
        if a2 <= ti < b2 + 0.3 or ti >= a4 - 0.1:
            emo.append(emo_vector({"Happy": 0.8, "Neutral": 0.2})[0])
        else:
            emo.append(emo_vector({"Neutral": 1.0})[0])
    ctrl, tl = build_ctrl(N, tracks, pitch=pitch, yaw=yaw, roll=roll)
    lab.generate_motion(wav, SRC, f"{out}/s2_deliberado.npz", emo=np.stack(emo), seed=3, ctrl=ctrl)
    save_tl(f"{out}/s2_deliberado.json", tl, audio=wav, plano=plan)
    json.dump(plan, open(f"{out}/plano_sistema2.json", "w"), ensure_ascii=False, indent=1)


def exp_mdm(lab):
    """Motion Diffusion: mesma frase, sementes diferentes -> movimentos diferentes e plausíveis
    (o problema é 1-para-muitos; regressão colapsaria para a média)."""
    out = f"{RUNS}/E6_mdm"; os.makedirs(out, exist_ok=True)
    wav = f"{AUD}/mdm.wav"; N = n_frames(wav)
    for sd in [0, 1, 2, 3, 4, 5, 6, 7]:
        ctrl, tl = build_ctrl(N)
        lab.generate_motion(wav, SRC, f"{out}/seed{sd}.npz", emo=None, seed=sd, ctrl=ctrl)
        save_tl(f"{out}/seed{sd}.json", tl, audio=wav)


if __name__ == "__main__":
    which = sys.argv[1:] or ["vasa", "instruct", "auhead", "conversa", "omni", "mdm"]
    lab = Lab(threads=2)
    fns = {"vasa": exp_vasa, "instruct": exp_instruct, "auhead": exp_auhead,
           "conversa": exp_conversa, "omni": exp_omni, "mdm": exp_mdm}
    for w in which:
        print(">>", w, flush=True)
        fns[w](lab)
    lab.save_avatar_state(f"{RUNS}/avatar.pkl")
    print("OK")
