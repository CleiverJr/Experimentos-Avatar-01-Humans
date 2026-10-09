"""
Métricas objetivas simples de qualidade de talking head (sem precisar de pesos externos):
  - abertura da boca por frame (MediaPipe FaceMesh: distância lábio interno sup/inf
    normalizada pela distância entre os cantos externos dos olhos)
  - amplitude de articulação = desvio-padrão da abertura (boca "parada" -> ~0)
  - sincronia labial = maior correlação de Pearson entre abertura da boca e envelope RMS
    do áudio, buscando defasagem em ±4 frames (±160 ms); reporta a defasagem
  - movimento de cabeça = desvio-padrão da posição do nariz (px na escala 512) e rotação 2D
  - piscadas = nº de mínimos da abertura dos olhos abaixo de 50% da mediana
"""
import sys
import json
import subprocess
import numpy as np
import cv2


def read_frames(video, size=512):
    cap = cv2.VideoCapture(video)
    fps = cap.get(cv2.CAP_PROP_FPS)
    frames = []
    while True:
        ok, f = cap.read()
        if not ok:
            break
        frames.append(f)
    return frames, fps


def audio_rms(video_or_wav, fps, n):
    import soundfile as sf
    tmp = "/tmp/_m_audio.wav"
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", video_or_wav, "-ac", "1", "-ar", "16000", tmp], check=True)
    x, sr = sf.read(tmp)
    hop = sr / fps
    return np.array([np.sqrt(np.mean(x[int(i * hop):int((i + 1) * hop)] ** 2)) if int(i * hop) < len(x) else 0.0
                     for i in range(n)])


def analyze(video, audio=None):
    import mediapipe as mp
    frames, fps = read_frames(video)
    fm = mp.solutions.face_mesh.FaceMesh(static_image_mode=False, max_num_faces=1, refine_landmarks=True)
    mouth, eye, nose, ang = [], [], [], []
    for f in frames:
        h, w = f.shape[:2]
        r = fm.process(cv2.cvtColor(f, cv2.COLOR_BGR2RGB))
        if not r.multi_face_landmarks:
            mouth.append(np.nan); eye.append(np.nan); nose.append([np.nan, np.nan]); ang.append(np.nan)
            continue
        L = np.array([[p.x * w, p.y * h] for p in r.multi_face_landmarks[0].landmark])
        iod = np.linalg.norm(L[33] - L[263])
        mouth.append(np.linalg.norm(L[13] - L[14]) / iod)
        eye.append((np.linalg.norm(L[159] - L[145]) + np.linalg.norm(L[386] - L[374])) / (2 * iod))
        s = 512.0 / max(h, w)
        nose.append(L[1] * s)
        v = L[263] - L[33]
        ang.append(np.degrees(np.arctan2(v[1], v[0])))
    mouth, eye, nose, ang = map(np.array, (mouth, eye, nose, ang))
    rms = audio_rms(audio or video, fps, len(frames))
    k = np.ones(3) / 3                      # suavização leve (120 ms) nos dois sinais
    m = np.convolve(np.nan_to_num(mouth - np.nanmean(mouth)), k, mode="same")
    a = np.convolve(rms - rms.mean(), k, mode="same")
    best = (-1, 0)
    for lag in range(-4, 5):
        if lag >= 0:
            x, y = m[lag:], a[:len(a) - lag]
        else:
            x, y = m[:lag], a[-lag:]
        if x.std() > 1e-9 and y.std() > 1e-9:
            c = float(np.corrcoef(x, y)[0, 1])
            if c > best[0]:
                best = (c, lag)
    # concordância fala/silêncio: a boca abre quando há voz e fecha no silêncio?
    rs = np.convolve(rms, np.ones(5) / 5, mode="same")
    vad = rs > 0.12 * rs.max()
    mm = np.nan_to_num(mouth)
    pos, neg = mm[vad], mm[~vad]
    if len(pos) and len(neg):
        from scipy.stats import mannwhitneyu
        auc = float(mannwhitneyu(pos, neg).statistic / (len(pos) * len(neg)))
        ratio = float(pos.mean() / max(neg.mean(), 1e-6))
    else:
        auc, ratio = float("nan"), float("nan")
    med = np.nanmedian(eye)
    blinks = 0
    below = False
    for e in eye:
        if not np.isnan(e) and e < 0.5 * med and not below:
            blinks += 1; below = True
        elif not np.isnan(e) and e > 0.7 * med:
            below = False
    res = {
        "video": video, "frames": len(frames), "fps": fps,
        "face_detected_pct": float(100 * np.mean(~np.isnan(mouth))),
        "mouth_open_mean": float(np.nanmean(mouth)), "mouth_open_std": float(np.nanstd(mouth)),
        "mouth_open_p95": float(np.nanpercentile(mouth, 95)),
        "speech_silence_auc": round(auc, 3), "mouth_speech_over_silence": round(ratio, 2),
        "lipsync_corr": round(best[0], 3), "lipsync_lag_frames": best[1],
        "head_pos_std_px": float(np.nanmean(np.nanstd(nose, axis=0))),
        "head_roll_std_deg": float(np.nanstd(ang)),
        "blinks": blinks, "blinks_per_min": blinks / (len(frames) / fps) * 60,
    }
    return res, {"mouth": mouth.tolist(), "rms": rms.tolist(), "eye": eye.tolist()}


if __name__ == "__main__":
    out = []
    for v in sys.argv[1:]:
        r, _ = analyze(v)
        out.append(r)
        print(json.dumps(r, ensure_ascii=False))
