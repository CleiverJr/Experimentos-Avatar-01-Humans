"""
Monta os vídeos finais de cada experimento (legendas, painéis lado a lado, barras de AU,
linha do tempo do plano do Sistema 2...). Lê os frames renderizados (runs/<exp>/<var>/*.jpg).
"""
import os
import sys
import json
import glob
import subprocess
import numpy as np
from PIL import Image, ImageDraw, ImageFont

RUNS = "/home/claude/w/lab/runs"
OUT = "/home/claude/w/final"
AUD = "/home/claude/w/aud"
FPS = 25
FD = "/usr/share/fonts/opentype/inter/"
BG = (17, 18, 20)
FG = (238, 238, 236)
MUTED = (150, 152, 158)
ACC = (255, 176, 59)
ACC2 = (94, 201, 255)
os.makedirs(OUT, exist_ok=True)


def font(sz, w="Medium"):
    return ImageFont.truetype(FD + f"Inter-{w}.otf", sz)


def frames(d):
    return sorted(glob.glob(f"{RUNS}/{d}/*.jpg"))


FACE_BOX = (232, 16, 808, 592)   # recorte quadrado 576 px em volta da cabeça (foto 1024)


def face(path, size):
    im = Image.open(path).convert("RGB").crop(FACE_BOX)
    return im.resize((size, size), Image.LANCZOS)


class Writer:
    def __init__(self, path, w, h, audio, fps=FPS, crf=18):
        self.path = path
        self.p = subprocess.Popen(
            ["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{w}x{h}", "-r", str(fps),
             "-i", "-", "-i", audio, "-map", "0:v", "-map", "1:a", "-c:v", "libx264", "-preset", "medium",
             "-crf", str(crf), "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "160k", "-shortest",
             "-movflags", "+faststart", path], stdin=subprocess.PIPE)

    def write(self, im):
        self.p.stdin.write(np.asarray(im.convert("RGB"), dtype=np.uint8).tobytes())

    def close(self):
        self.p.stdin.close()
        self.p.wait()
        print("->", self.path)


def text_wrap(draw, txt, f, maxw):
    words, lines, cur = txt.split(), [], ""
    for w in words:
        t = (cur + " " + w).strip()
        if draw.textlength(t, font=f) <= maxw:
            cur = t
        else:
            lines.append(cur); cur = w
    if cur:
        lines.append(cur)
    return lines


def header(draw, W, title, sub, h=96):
    draw.rectangle([0, 0, W, h], fill=BG)
    draw.text((28, 18), title, font=font(30, "SemiBold"), fill=FG)
    draw.text((28, 58), sub, font=font(19, "Regular"), fill=MUTED)


def footer_note(draw, W, H, txt):
    draw.text((28, H - 30), txt, font=font(15, "Regular"), fill=(110, 112, 118))


def subtitle(draw, x, y, w, txt, sz=24):
    f = font(sz, "Medium")
    lines = text_wrap(draw, txt, f, w - 40)
    for i, l in enumerate(lines):
        tw = draw.textlength(l, font=f)
        tx = x + (w - tw) / 2
        ty = y + i * (sz + 8)
        draw.rounded_rectangle([tx - 12, ty - 4, tx + tw + 12, ty + sz + 6], 6, fill=(0, 0, 0))
        draw.text((tx, ty), l, font=f, fill=FG)


SRC_NOTE = "Avatar: foto única 1024×1024 • Renderizador/difusão: Ditto (Ant Group, ACM MM 2025) • Voz: Piper TTS pt-BR • Controles: Trilha D"


# ---------------------------------------------------------------------------
def e1():
    fr = frames("E1_vasa/nova_voz")
    S = 960
    W, H = S, S + 96 + 40
    w = Writer(f"{OUT}/E1_VASA1_audio_para_dinamica_holistica.mp4", W, H, f"{AUD}/vasa.wav")
    for p in fr:
        im = Image.new("RGB", (W, H), BG)
        im.paste(face(p, S), (0, 96))
        full = Image.open(p).convert("RGB").resize((220, 220), Image.LANCZOS)
        im.paste(full, (W - 236, 96 + S - 236))
        d = ImageDraw.Draw(im)
        d.rectangle([W - 237, 96 + S - 237, W - 16, 96 + S - 16], outline=(255, 255, 255))
        header(d, W, "E1 · VASA-1 — áudio → dinâmica facial holística",
               "Sem controle manual: lábios, olhar, piscadas e pose vêm da difusão condicionada na voz")
        footer_note(d, W, H, "Foto única • Difusão no espaço de movimento + warping neural 3D: Ditto • Voz: Piper TTS pt-BR")
        w.write(im)
    w.close()


def e1_antes_depois():
    old = "/mnt/user-data/uploads/Humans/Trilha_D_Controle_Emocao/output/vasa1_avatar_realista.mp4"
    tmp = "/tmp/old_frames"
    os.makedirs(tmp, exist_ok=True)
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", old, "-t", "8", "-r", "25", f"{tmp}/%05d.png"], check=True)
    of = sorted(glob.glob(f"{tmp}/*.png"))
    nf = frames("E1_vasa/audio_antigo")
    S = 600
    W, H = 2 * S + 3 * 24, S + 96 + 70 + 40
    w = Writer(f"{OUT}/E0_antes_x_depois.mp4", W, H, f"{AUD}/old_vasa_8s.wav")
    n = min(len(of), len(nf))
    for i in range(n):
        im = Image.new("RGB", (W, H), BG)
        d = ImageDraw.Draw(im)
        header(d, W, "Antes × depois — mesmo áudio, mesma foto",
               "Esquerda: renderizador antigo (warping Delaunay com ~45 pontos fixos). Direita: Ditto (difusão + warping neural 3D)")
        o = Image.open(of[i]).convert("RGB")       # 512x512 do vídeo antigo, foto inteira
        o = o.crop((116, 8, 404, 296)).resize((S, S), Image.LANCZOS)  # mesmo enquadramento do rosto
        im.paste(o, (24, 110))
        im.paste(face(nf[i], S), (48 + S, 110))
        d.text((24, 110 + S + 14), "ANTES — boca praticamente imóvel", font=font(22, "SemiBold"), fill=(255, 120, 110))
        d.text((48 + S, 110 + S + 14), "DEPOIS — articulação real, dentes, olhar, piscadas", font=font(22, "SemiBold"), fill=(120, 230, 150))
        footer_note(d, W, H, "Áudio: os primeiros 8 s de laboratorio_sementes/audio/vasa_speech.wav (o mesmo do teste antigo)")
        w.write(im)
    w.close()


def e2():
    meta = json.load(open(f"{RUNS}/E2_instruct/instrucoes.json"))
    names = ["neutro", "alegre", "triste", "raiva", "surpreso"]
    F = {k: frames(f"E2_instruct/{k}") for k in names}
    S = 384
    W = 5 * S + 6 * 16
    H = 96 + S + 150 + 40
    w = Writer(f"{OUT}/E2_InstructAvatar_texto_controla_emocao.mp4", W, H, f"{AUD}/instruct.wav")
    n = min(len(v) for v in F.values())
    for i in range(n):
        im = Image.new("RGB", (W, H), BG)
        d = ImageDraw.Draw(im)
        header(d, W, "E2 · InstructAvatar — mesma voz, instruções de texto diferentes",
               "Texto → InstructParser (Trilha D) → rótulo de emoção do Ditto + perfil de Action Units + viés de pose")
        for j, k in enumerate(names):
            x = 16 + j * (S + 16)
            im.paste(face(F[k][i], S), (x, 104))
            d.text((x, 104 + S + 10), k.upper(), font=font(20, "Bold"), fill=ACC)
            for li, l in enumerate(text_wrap(d, "“" + meta[k]["instrucao"] + "”", font(16, "Regular"), S)[:4]):
                d.text((x, 104 + S + 38 + li * 21), l, font=font(16, "Regular"), fill=FG)
            aus = ", ".join(f"{a} {v:.1f}" for a, v in meta[k]["aus"].items()) or "sem AUs extras"
            d.text((x, 104 + S + 124), aus, font=font(13, "Regular"), fill=MUTED)
        footer_note(d, W, H, SRC_NOTE)
        w.write(im)
    w.close()


def bar(d, x, y, w, h, v, label, col):
    d.rounded_rectangle([x, y, x + w, y + h], 5, fill=(40, 42, 46))
    vv = float(np.clip(v, 0, 1))
    if vv > 0.01:
        d.rounded_rectangle([x, y, x + int(w * vv), y + h], 5, fill=col)
    d.text((x, y - 22), label, font=font(15, "Medium"), fill=FG if vv > 0.05 else MUTED)


AU_DESC = {"AU01": "AU01 levantador interno da sobrancelha", "AU02": "AU02 levantador externo da sobrancelha",
           "AU04": "AU04 abaixador da sobrancelha", "AU06": "AU06 levantador da bochecha",
           "AU12": "AU12 puxador do canto dos lábios", "AU15": "AU15 depressor do canto dos lábios",
           "AU26": "AU26 queda da mandíbula", "AU43": "AU43 olhos fechados"}


def e3():
    tl = json.load(open(f"{RUNS}/E3_auhead/au_timeline.json"))
    fr = frames("E3_auhead/au_timeline")
    S = 720
    PW = 420
    W, H = S + PW + 48, S + 96 + 60
    w = Writer(f"{OUT}/E3_AUHead_controle_por_action_units.mp4", W, H, f"{AUD}/auhead2.wav")
    segs, labels = tl["segments"], tl["labels"]
    for i, p in enumerate(fr):
        t = i / FPS
        im = Image.new("RGB", (W, H), BG)
        d = ImageDraw.Draw(im)
        header(d, W, "E3 · AUHead — controle anatômico por Action Units (FACS)",
               "Cada AU vira um deslocamento dos keypoints implícitos 3D; a boca continua sincronizada com a fala")
        im.paste(face(p, S), (16, 104))
        au = tl["frames"][min(i, len(tl["frames"]) - 1)]["au"]
        x0 = S + 40
        for j, k in enumerate(["AU01", "AU02", "AU04", "AU06", "AU12", "AU15", "AU26", "AU43"]):
            bar(d, x0, 150 + j * 74, PW - 30, 18, au.get(k, 0), AU_DESC[k], ACC2 if k != "AU26" else ACC)
        cur = next((labels[j] for j, (a, b) in enumerate(segs) if a - 0.1 <= t <= b + 0.8), "")
        if cur:
            subtitle(d, 16, 104 + S - 70, S, cur, 24)
        footer_note(d, W, H, "Mapeamento AU → keypoints calibrado visualmente nesta foto (ver E3_au_calibracao.png). " + "Renderizador: Ditto")
        w.write(im)
    w.close()


def e4():
    tl = json.load(open(f"{RUNS}/E4_conversa/conversa.json"))
    seg = tl["segments"]
    fr = frames("E4_conversa/conversa")
    import soundfile as sf
    xp, sr = sf.read(f"{AUD}/conv_partner.wav")
    S = 720
    PW = 480
    W, H = S + PW + 48, S + 96 + 60
    w = Writer(f"{OUT}/E4_Audio2Photoreal_conversa_falar_e_escutar.mp4", W, H, f"{AUD}/conv_mix.wav")
    lines = {"a1": "Avatar: “E então, como foram os testes com o modelo novo?”",
             "b": "Interlocutor: “Funcionaram muito bem. A boca finalmente acompanha a fala, e a cabeça se mexe de um jeito natural.”",
             "a2": "Avatar: “Que ótimo! Então vamos preparar a apresentação para a equipe.”"}
    nods = tl["nods"]
    for i, p in enumerate(fr):
        t = i / FPS
        im = Image.new("RGB", (W, H), BG)
        d = ImageDraw.Draw(im)
        header(d, W, "E4 · Audio2Photoreal — comportamento em conversa (falar e escutar)",
               "Enquanto escuta: acenos nos picos de ênfase da outra voz, sorriso leve e giro em direção ao interlocutor")
        im.paste(face(p, S), (16, 104))
        state = "FALANDO" if any(seg[k][0] <= t <= seg[k][1] for k in ("a1", "a2")) else ("ESCUTANDO" if seg["b"][0] - 0.2 <= t <= seg["b"][1] + 0.2 else "")
        if state:
            col = (120, 230, 150) if state == "FALANDO" else ACC2
            d.rounded_rectangle([32, 120, 32 + 170, 160], 8, fill=(0, 0, 0))
            d.ellipse([44, 132, 60, 148], fill=col)
            d.text((70, 128), state, font=font(20, "Bold"), fill=col)
        x0 = S + 40
        d.text((x0, 120), "Interlocutor (só voz)", font=font(20, "SemiBold"), fill=FG)
        # forma de onda do interlocutor (janela de 4 s centrada no tempo atual)
        cy, ww, hh = 240, PW - 30, 110
        d.rectangle([x0, cy - hh / 2, x0 + ww, cy + hh / 2], outline=(50, 52, 56))
        win = 4.0
        for k in range(ww):
            tt = t - win / 2 + win * k / ww
            if 0 <= tt < len(xp) / sr:
                a = int(tt * sr); seg_ = xp[a:a + int(sr * win / ww) + 1]
                amp = float(np.abs(seg_).max()) if len(seg_) else 0
                d.line([x0 + k, cy - min(amp * 1.6, 1.0) * hh * 0.45, x0 + k, cy + min(amp * 1.6, 1.0) * hh * 0.45], fill=ACC2 if tt <= t else (70, 90, 110))
        d.line([x0 + ww / 2, cy - hh / 2, x0 + ww / 2, cy + hh / 2], fill=FG)
        # marcadores de aceno
        d.text((x0, 320), "Acenos de escuta (backchannel)", font=font(17, "Medium"), fill=MUTED)
        T = len(fr) / FPS
        d.line([x0, 360, x0 + ww, 360], fill=(60, 62, 66), width=2)
        for k, (a, b) in seg.items():
            d.rectangle([x0 + ww * a / T, 352, x0 + ww * b / T, 368], fill=(120, 230, 150) if k != "b" else ACC2)
        for nt in nods:
            xx = x0 + ww * nt / T
            d.polygon([(xx, 376), (xx - 7, 390), (xx + 7, 390)], fill=ACC)
        d.line([x0 + ww * t / T, 340, x0 + ww * t / T, 396], fill=FG, width=2)
        cur = next((lines[k] for k in ("a1", "b", "a2") if seg[k][0] - 0.1 <= t <= seg[k][1] + 0.3), "")
        if cur:
            for li, l in enumerate(text_wrap(d, cur, font(20, "Regular"), PW - 30)):
                d.text((x0, 440 + li * 28), l, font=font(20, "Regular"), fill=FG)
        d.text((x0, 104 + S - 70), "Limitação: o retrato não mostra mãos/braços,", font=font(15, "Regular"), fill=MUTED)
        d.text((x0, 104 + S - 48), "então gestos de corpo não são sintetizados aqui.", font=font(15, "Regular"), fill=MUTED)
        footer_note(d, W, H, SRC_NOTE)
        w.write(im)
    w.close()


def e5():
    tl2 = json.load(open(f"{RUNS}/E5_omnihuman/s2_deliberado.json"))
    plan = tl2["plano"]
    f1, f2 = frames("E5_omnihuman/s1_reativo"), frames("E5_omnihuman/s2_deliberado")
    S = 600
    W, H = 2 * S + 3 * 24, S + 96 + 190 + 40
    w = Writer(f"{OUT}/E5_OmniHuman15_sistema1_x_sistema2.mp4", W, H, f"{AUD}/omni.wav")
    n = min(len(f1), len(f2))
    for i in range(n):
        t = i / FPS
        im = Image.new("RGB", (W, H), BG)
        d = ImageDraw.Draw(im)
        header(d, W, "E5 · OmniHuman-1.5 — Sistema 1 (reflexo) × Sistema 1 + Sistema 2 (deliberação)",
               "S2: um LLM leu a transcrição e planejou gestos com intenção (pensar, concordar, ressalvar, animar)")
        im.paste(face(f1[i], S), (24, 104))
        im.paste(face(f2[i], S), (48 + S, 104))
        d.text((24, 104 + S + 12), "SISTEMA 1 — só áudio (reativo)", font=font(21, "Bold"), fill=MUTED)
        d.text((48 + S, 104 + S + 12), "SISTEMA 1 + SISTEMA 2 — plano semântico", font=font(21, "Bold"), fill=ACC)
        cur = next((p for p in plan if p["t"][0] - 0.1 <= t <= p["t"][1] + 0.3), None)
        y = 104 + S + 50
        if cur:
            d.text((48 + S, y), "“" + cur["texto"] + "”", font=font(19, "SemiBold"), fill=FG)
            d.text((48 + S, y + 30), "intenção: " + cur["intencao"], font=font(17, "Regular"), fill=ACC2)
            for li, l in enumerate(text_wrap(d, "ação: " + cur["acao"], font(17, "Regular"), S)[:3]):
                d.text((48 + S, y + 56 + li * 23), l, font=font(17, "Regular"), fill=FG)
        footer_note(d, W, H, SRC_NOTE + " • mesma semente de difusão nos dois lados")
        w.write(im)
    w.close()


def e6():
    seeds = [4, 6, 7]
    F = {s: frames(f"E6_mdm/seed{s}") for s in seeds}
    S = 560
    W, H = 3 * S + 4 * 16, S + 96 + 60 + 40
    w = Writer(f"{OUT}/E6_MotionDiffusion_mesma_frase_3_sementes.mp4", W, H, f"{AUD}/mdm.wav")
    n = min(len(v) for v in F.values())
    for i in range(n):
        im = Image.new("RGB", (W, H), BG)
        d = ImageDraw.Draw(im)
        header(d, W, "E6 · Motion Diffusion — o problema 1-para-muitos",
               "Mesma frase, mesmo áudio, sementes de ruído diferentes → três movimentos diferentes e plausíveis")
        for j, s in enumerate(seeds):
            x = 16 + j * (S + 16)
            im.paste(face(F[s][i], S), (x, 104))
            d.text((x, 104 + S + 12), f"semente {s}", font=font(22, "Bold"), fill=ACC)
        footer_note(d, W, H, SRC_NOTE)
        w.write(im)
    # repete 2x para ficar mais fácil comparar
    w.close()


if __name__ == "__main__":
    for name in sys.argv[1:]:
        globals()[name]()
