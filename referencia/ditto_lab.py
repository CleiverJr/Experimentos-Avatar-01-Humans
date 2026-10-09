"""
ditto_lab.py — Trilha D: núcleo dos experimentos foto-realistas.

Separa os experimentos em dois estágios:
  1) MOVIMENTO (barato): áudio (+ emoção / instrução / AUs / pose) -> trajetória de movimento
     no espaço de keypoints implícitos do LivePortrait (pitch, yaw, roll, t, exp[21x3]),
     gerada pelo LMDM (Latent Motion Diffusion Model) do Ditto. É aqui que vivem os
     controles da Trilha D. O resultado é salvo em .npz (motion) — é isso que seria
     exportado para as Trilhas B/C.
  2) RENDERIZAÇÃO (cara): warp 3D das features de aparência + decoder SPADE -> 512x512,
     colado de volta na foto original. Pode ser dividido em fatias de frames e rodado em
     paralelo (outra máquina), porque só depende do .npz + estado do avatar.

Base: Ditto (Ant Group, ACM MM 2025) — https://github.com/antgroup/ditto-talkinghead
"""
import os
import sys
import math
import copy
import pickle
import random
import argparse

import numpy as np

DITTO_DIR = os.environ.get("DITTO_DIR", os.path.join(os.path.dirname(os.path.abspath(__file__)), "ditto_repo"))
sys.path.insert(0, DITTO_DIR)

EMO_NAMES = ['Angry', 'Disgust', 'Fear', 'Happy', 'Neutral', 'Sad', 'Surprise', 'Contempt']
FPS = 25


def seed_everything(seed):
    import torch
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)


# ---------------------------------------------------------------------------
# Controle facial explícito: Action Units (FACS) -> deslocamentos de keypoints
# implícitos do LivePortrait (exp: 21 keypoints x 3 eixos).
# Coeficientes adaptados do editor de expressões do LivePortrait
# (comunidade ComfyUI-AdvancedLivePortrait), reescritos em termos de AUs.
# Unidade de cada AU: intensidade FACS normalizada 0..1 (≈ A..E).
# ---------------------------------------------------------------------------
def _add(exp, kp, axis, v):
    exp[kp * 3 + axis] += v


def au_to_delta_exp(au: dict) -> np.ndarray:
    """au: {'AU01':0..1, 'AU02', 'AU04', 'AU06', 'AU12', 'AU15', 'AU26', 'AU43'} -> delta exp (63,)"""
    e = np.zeros(63, dtype=np.float32)
    g = lambda k: float(au.get(k, 0.0))

    # AU12 lip corner puller (zigomático maior) — sorriso
    s = g('AU12') * 1.1
    _add(e, 20, 1, s * -0.01); _add(e, 14, 1, s * -0.02)
    _add(e, 17, 1, s * 0.0065); _add(e, 17, 2, s * 0.003)
    _add(e, 13, 1, s * -0.00275); _add(e, 16, 1, s * -0.00275)
    _add(e, 3, 1, s * -0.0035); _add(e, 7, 1, s * -0.0035)

    # AU15 lip corner depressor — cantos para baixo (tristeza): sorriso negativo
    d = g('AU15') * 0.45
    _add(e, 20, 1, d * 0.01); _add(e, 14, 1, d * 0.02)
    _add(e, 17, 1, d * -0.0065); _add(e, 3, 1, d * 0.0035); _add(e, 7, 1, d * 0.0035)

    # AU02 outer brow raiser (frontal lateral) — sobrancelhas inteiras sobem (calibrado visualmente)
    r = g('AU02')
    _add(e, 1, 1, r * 0.02); _add(e, 2, 1, r * -0.02)

    # AU01 inner brow raiser (frontal medial) — cantos internos sobem (súplica/tristeza)
    i1 = g('AU01')
    _add(e, 1, 0, i1 * 0.012); _add(e, 2, 0, i1 * -0.012)

    # AU04 brow lowerer (corrugador) — sobrancelhas descem, franze a glabela
    l4 = g('AU04')
    _add(e, 1, 1, l4 * -0.008); _add(e, 2, 1, l4 * 0.008)

    # AU06 cheek raiser (orbicular, porção orbital) e AU43 eyes closed — pálpebras
    c = g('AU06') * 0.3 + g('AU43')
    _add(e, 11, 1, c * 0.018); _add(e, 15, 1, c * 0.018)
    _add(e, 13, 1, c * -0.005); _add(e, 16, 1, c * -0.005)

    # AU26 jaw drop extra (o áudio já move a mandíbula; isto é um viés)
    m = g('AU26') * 40.0
    _add(e, 19, 1, m * 0.001); _add(e, 19, 2, m * 0.0001); _add(e, 17, 1, m * -0.0001)
    return e


def emo_vector(weights: dict) -> np.ndarray:
    """{'Happy':0.7,'Neutral':0.3} -> vetor 8-d no formato do Ditto (distribuição)."""
    v = np.zeros(8, dtype=np.float32)
    for k, w in weights.items():
        v[EMO_NAMES.index(k)] += w
    if v.sum() <= 0:
        v[4] = 1
    v = v / v.sum()
    # o Ditto foi treinado com distribuições "suaves" (softmax de logits) — suaviza um pouco
    return (0.9 * v + 0.1 / 8).astype(np.float32)[None]  # [1, 8]


# ---------------------------------------------------------------------------
class Lab:
    def __init__(self, threads=None):
        import torch
        if threads:
            torch.set_num_threads(threads)
        from stream_pipeline_offline import StreamSDK
        cfg = os.path.join(DITTO_DIR, "checkpoints/ditto_cfg/v0.4_hubert_cfg_cpu.pkl")
        root = os.path.join(DITTO_DIR, "checkpoints/ditto_pytorch")
        self.sdk = StreamSDK(cfg, root)

    def _setup(self, source, emo, sampling_timesteps=50, extra=None):
        sdk = self.sdk
        kw = dict(sampling_timesteps=sampling_timesteps)
        if emo is not None:
            kw['emo'] = emo
        if extra:
            kw.update(extra)
        tmp = "/tmp/_ditto_dummy.mp4"
        sdk.setup(source, tmp, **kw)
        # só queremos os componentes: encerra as threads do pipeline de streaming
        sdk.stop_event.set()
        for t in sdk.thread_list:
            t.join()
        try:
            sdk.writer.close()
        except Exception:
            pass

    def generate_motion(self, audio_path, source, out_npz, emo=4, seed=0,
                        ctrl=None, overall_ctrl=None, sampling_timesteps=50,
                        extra_setup=None, meta=None):
        """ctrl: lista (len N) de dicts por frame com delta_pitch/delta_yaw/delta_roll/delta_exp."""
        import librosa
        from core.atomic_components.motion_stitch import bin66_to_degree
        sdk = self.sdk
        seed_everything(seed)
        extra = dict(extra_setup or {})
        if overall_ctrl is not None:
            extra["overall_ctrl_info"] = overall_ctrl
        self._setup(source, emo, sampling_timesteps, extra)

        audio, _ = librosa.core.load(audio_path, sr=16000)
        N = math.ceil(len(audio) / 16000 * FPS)
        sdk.setup_Nd(N_d=N)
        seed_everything(seed)
        # O LMDM do Ditto sorteia o ruído de cada passo DDIM uma única vez (cache em setup()).
        # Para que a semente realmente controle a amostra, regeneramos esse ruído aqui.
        lm = sdk.audio2motion.lmdm.model
        lm.sampling_timesteps = None
        lm.setup(sampling_timesteps)

        aud_feat = sdk.wav2feat.wav2feat(audio)
        cond_all = sdk.condition_handler(aud_feat, 0)
        a2m = sdk.audio2motion
        L, valid = a2m.seq_frames, a2m.valid_clip_len
        n = len(cond_all)
        idx, res = 0, None
        while idx < n:
            c = cond_all[idx:idx + L][None]
            if c.shape[1] < L:
                c = np.concatenate([c, np.stack([c[:, -1]] * (L - c.shape[1]), 1)], 1)
            res = a2m(c, res)
            idx += valid
        res = res[:, :n]
        res = a2m._smo(res, 0, res.shape[1])
        x_d_list = a2m.cvt_fmt(res)

        self.last = dict(x_d_list=x_d_list[:N], audio=audio_path, seed=seed, N=N, meta=meta)
        return self.stitch(ctrl, out_npz, meta)

    def stitch(self, ctrl, out_npz, meta=None):
        """Aplica os controles (pose/AUs) sobre o último movimento gerado pela difusão."""
        from core.atomic_components.motion_stitch import bin66_to_degree
        sdk = self.sdk
        x_d_list, N = self.last["x_d_list"], self.last["N"]
        sdk.motion_stitch.d0 = None
        sdk.motion_stitch.idx = 0
        sdk.motion_stitch.fade_dst = None
        si = sdk.source_info
        nsrc = len(si["x_s_info_lst"])
        X_s, X_d, pose_raw, exp_raw = [], [], [], []
        for i, x_d_info in enumerate(x_d_list[:N]):
            fidx = i % nsrc
            k = {}
            base = sdk._get_ctrl_info(i)  # fade in/out do próprio SDK
            k.update(base)
            if ctrl is not None and i < len(ctrl):
                k.update(ctrl[i])
            pose_raw.append([float(bin66_to_degree(x_d_info[a]).item()) for a in ("pitch", "yaw", "roll")])
            exp_raw.append(x_d_info["exp"].reshape(-1).copy())
            x_s, x_d = sdk.motion_stitch(si["x_s_info_lst"][fidx], copy.deepcopy(x_d_info), **k)
            X_s.append(np.asarray(x_s).reshape(-1, 3))
            X_d.append(np.asarray(x_d).reshape(-1, 3))

        np.savez_compressed(
            out_npz,
            x_s=np.stack(X_s).astype(np.float32),
            x_d=np.stack(X_d).astype(np.float32),
            pose_deg=np.array(pose_raw, dtype=np.float32),   # pose gerada pela difusão (antes dos controles)
            exp=np.stack(exp_raw).astype(np.float32),        # expressão gerada (63)
            fps=FPS, audio=self.last["audio"], seed=self.last["seed"],
            emo=np.asarray(sdk.condition_handler.emo_lst, dtype=np.float32),
            meta=np.array(repr(meta or {})),
        )
        return out_npz

    def save_avatar_state(self, out_pkl):
        si = self.sdk.source_info
        st = {
            "f_s": [np.asarray(f) for f in si["f_s_lst"]],
            "img_rgb": si["img_rgb_lst"],
            "M_c2o": si["M_c2o_lst"],
        }
        with open(out_pkl, "wb") as f:
            pickle.dump(st, f)


# ---------------------------------------------------------------------------
class Renderer:
    """Só warp + decoder + putback. Leve o suficiente para rodar em outra máquina."""
    def __init__(self, threads=None, bf16=False, device=None):
        import torch
        if threads:
            torch.set_num_threads(threads)
        if device is None:
            device = "mps" if torch.backends.mps.is_available() else "cpu"
        self.device = device
        from core.atomic_components.warp_f3d import WarpF3D
        from core.atomic_components.decode_f3d import DecodeF3D
        from core.atomic_components.putback import PutBack
        root = os.path.join(DITTO_DIR, "checkpoints/ditto_pytorch/models")
        self.warp = WarpF3D({"model_path": os.path.join(root, "warp_network.pth"), "device": self.device})
        self.dec = DecodeF3D({"model_path": os.path.join(root, "decoder.pth"), "device": self.device})
        self.putback = PutBack()
        self.bf16 = bf16

    def render(self, avatar_pkl, motion_npz, out_dir, start=0, end=None, full=True):
        import torch
        import cv2
        os.makedirs(out_dir, exist_ok=True)
        with open(avatar_pkl, "rb") as f:
            st = pickle.load(f)
        m = np.load(motion_npz, allow_pickle=True)
        x_s_all, x_d_all = m["x_s"], m["x_d"]
        N = len(x_d_all)
        end = N if end is None else min(end, N)
        nsrc = len(st["f_s"])
        ctx = torch.autocast("cpu", dtype=torch.bfloat16) if (self.bf16 and self.device == "cpu") else _null()
        for i in range(start, end):
            p = os.path.join(out_dir, f"{i:05d}.jpg")
            if os.path.exists(p):
                continue
            fi = i % nsrc
            with ctx, torch.no_grad():
                f3d = self.warp(st["f_s"][fi], x_s_all[i][None], x_d_all[i][None])
                img = self.dec(f3d)
            if full:
                img = self.putback(st["img_rgb"][fi], img, st["M_c2o"][fi])
            cv2.imwrite(p, cv2.cvtColor(np.ascontiguousarray(img), cv2.COLOR_RGB2BGR), [cv2.IMWRITE_JPEG_QUALITY, 95])
        return out_dir


class _null:
    def __enter__(self):
        return self

    def __exit__(self, *a):
        return False


def mux(frames_dir, audio, out_mp4, fps=FPS, crf=17):
    cmd = (f'ffmpeg -loglevel error -y -framerate {fps} -i "{frames_dir}/%05d.jpg" -i "{audio}" '
           f'-map 0:v -map 1:a -c:v libx264 -preset slow -crf {crf} -pix_fmt yuv420p -c:a aac -b:a 160k -shortest "{out_mp4}"')
    assert os.system(cmd) == 0, cmd
    return out_mp4


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=["render"])
    ap.add_argument("--avatar")
    ap.add_argument("--motion")
    ap.add_argument("--out")
    ap.add_argument("--start", type=int, default=0)
    ap.add_argument("--end", type=int, default=None)
    ap.add_argument("--threads", type=int, default=None)
    ap.add_argument("--bf16", action="store_true")
    a = ap.parse_args()
    if a.cmd == "render":
        Renderer(a.threads, a.bf16).render(a.avatar, a.motion, a.out, a.start, a.end)
