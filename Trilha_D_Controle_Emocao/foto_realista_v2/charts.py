"""Gráficos estáticos (PNG) para o laboratório e para slides."""
import json
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager

for f in ["Inter-Regular.otf", "Inter-Medium.otf", "Inter-SemiBold.otf"]:
    font_manager.fontManager.addfont("/usr/share/fonts/opentype/inter/" + f)
plt.rcParams.update({
    "font.family": "Inter", "font.size": 11, "axes.edgecolor": "#c9c8c2", "axes.labelcolor": "#52514e",
    "xtick.color": "#52514e", "ytick.color": "#52514e", "axes.spines.top": False, "axes.spines.right": False,
    "axes.grid": True, "grid.color": "#ecebe6", "grid.linewidth": 0.8, "figure.facecolor": "#fcfcfb",
    "axes.facecolor": "#fcfcfb", "axes.titleweight": "semibold", "axes.titlesize": 13, "axes.titlecolor": "#0b0b0b",
})
S1, S2, S3, MUT = "#2a78d6", "#eb6834", "#1baf7a", "#b9b8b1"
RUNS = "/home/claude/w/lab/runs"
OUT = "/home/claude/w/final"


def mdm(chosen=(4, 6, 7)):
    P = {s: np.load(f"{RUNS}/E6_mdm/seed{s}.npz")["pose_deg"] for s in range(8)}
    t = np.arange(len(P[0])) / 25
    fig, axes = plt.subplots(2, 1, figsize=(10, 6), sharex=True)
    for ax, k, name in zip(axes, [1, 0], ["Yaw (giro lateral), graus", "Pitch (inclinação vertical), graus"]):
        for s in range(8):
            if s not in chosen:
                ax.plot(t, P[s][:, k], color=MUT, lw=1.2, zorder=1)
        for s, c in zip(chosen, [S1, S2, S3]):
            ax.plot(t, P[s][:, k], color=c, lw=2, zorder=3, label=f"semente {s}")
            pass  # legenda cobre a identidade
        ax.set_ylabel(name)
    axes[0].set_title("Mesma frase, 8 sementes de difusão: trajetórias diferentes e plausíveis", loc="left")
    axes[0].legend(loc="upper left", frameon=False, ncol=3)
    axes[1].set_xlabel("tempo (s)")
    fig.text(0.01, 0.005, "Cinza: as outras 5 sementes. Pose gerada pelo LMDM do Ditto, antes dos controles.", color="#52514e", fontsize=9)
    fig.tight_layout(rect=(0, 0.02, 0.97, 1))
    fig.savefig(f"{OUT}/E6_trajetorias_8_sementes.png", dpi=150)


def before_after(m_old, m_new):
    fig, axes = plt.subplots(1, 2, figsize=(10, 3.6))
    labels = ["Antes\n(warping Delaunay)", "Depois\n(Ditto)"]
    for ax, key, title, fmt in [
        (axes[0], "mouth_open_std", "Amplitude de articulação da boca\n(desvio-padrão da abertura, normalizada)", "{:.4f}"),
        (axes[1], "speech_silence_auc", "Boca abre na fala e fecha no silêncio?\n(AUC; 0,5 = acaso)", "{:.2f}"),
    ]:
        v = [m_old[key], m_new[key]]
        ax.grid(axis="x", visible=False); ax.set_axisbelow(True)
        b = ax.bar(labels, v, color=[MUT, S1], width=0.55)
        for r, val in zip(b, v):
            ax.annotate(fmt.format(val), (r.get_x() + r.get_width() / 2, r.get_height()), xytext=(0, 4),
                        textcoords="offset points", ha="center", fontsize=11, color="#0b0b0b")
        ax.set_title(title, loc="left", fontsize=11)
        if key == "speech_silence_auc":
            ax.axhline(0.5, color="#52514e", lw=1, ls="--")
            ax.set_ylim(0, 1)
    fig.tight_layout()
    fig.savefig(f"{OUT}/E0_metricas_antes_x_depois.png", dpi=150)


def au_timeline():
    tl = json.load(open(f"{RUNS}/E3_auhead/au_timeline.json"))
    fr = tl["frames"]
    t = np.array([f["t"] for f in fr])
    aus = ["AU12", "AU06", "AU01", "AU02", "AU04", "AU43", "AU26"]
    cols = ["#2a78d6", "#eb6834", "#1baf7a", "#eda100", "#e87ba4", "#008300", "#4a3aa7"]
    fig, axes = plt.subplots(len(aus), 1, figsize=(10, 6.5), sharex=True)
    for ax, a, c in zip(axes, aus, cols):
        v = np.array([f["au"].get(a, 0) for f in fr])
        ax.fill_between(t, 0, v, color=c, alpha=0.85, lw=0)
        ax.set_ylim(0, 1.1); ax.set_yticks([])
        ax.set_ylabel(a, rotation=0, ha="right", va="center", fontsize=10, color="#0b0b0b")
        ax.grid(False)
    for a, b in tl["segments"]:
        for ax in axes:
            ax.axvspan(a, b, color="#ecebe6", zorder=0)
    axes[0].set_title("E3 · Intensidade de cada Action Unit ao longo da fala (faixas cinza = trechos com voz)", loc="left")
    axes[-1].set_xlabel("tempo (s)")
    fig.tight_layout()
    fig.savefig(f"{OUT}/E3_timeline_action_units.png", dpi=150)


if __name__ == "__main__":
    import sys
    for n in sys.argv[1:]:
        if n == "before_after":
            m = [json.loads(l) for l in open(f"{OUT}/metricas.jsonl")]
            before_after(m[0], m[1])
        else:
            globals()[n]()
