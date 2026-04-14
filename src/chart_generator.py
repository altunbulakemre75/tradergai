from __future__ import annotations

import io

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches


def generate_gauge(score: int, title: str = "") -> io.BytesIO:
    fig, ax = plt.subplots(figsize=(5, 2.8))
    fig.patch.set_facecolor("#0f0f1a")
    ax.set_facecolor("#0f0f1a")
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 5)
    ax.axis("off")

    # Arka plan bar (gri)
    bar_y = 1.8
    bar_h = 0.7
    ax.add_patch(mpatches.FancyBboxPatch(
        (0.5, bar_y), 9, bar_h,
        boxstyle="round,pad=0.1",
        facecolor="#2a2a3a", edgecolor="none"
    ))

    # Renkli dolgu
    filled_w = score / 100 * 9
    if score < 35:
        color = "#e74c3c"
    elif score < 60:
        color = "#f39c12"
    else:
        color = "#2ecc71"

    if filled_w > 0:
        ax.add_patch(mpatches.FancyBboxPatch(
            (0.5, bar_y), filled_w, bar_h,
            boxstyle="round,pad=0.1",
            facecolor=color, edgecolor="none", alpha=0.9
        ))

    # Skor yazısı (ortada, büyük)
    ax.text(5, 3.5, f"{score}", ha="center", va="center",
            fontsize=36, fontweight="bold", color="white")
    ax.text(5, 2.8, "/ 100", ha="center", va="center",
            fontsize=11, color="#888888")

    # Etiketler
    ax.text(0.5, bar_y - 0.4, "Negatif", ha="left", va="top",
            fontsize=8, color="#e74c3c")
    ax.text(9.5, bar_y - 0.4, "Pozitif", ha="right", va="top",
            fontsize=8, color="#2ecc71")

    # Başlık (sadece ticker adı)
    if title:
        ax.text(5, 4.6, title, ha="center", va="center",
                fontsize=12, fontweight="bold", color="white")

    buf = io.BytesIO()
    plt.savefig(buf, format="png", bbox_inches="tight",
                facecolor=fig.get_facecolor(), dpi=110)
    plt.close(fig)
    buf.seek(0)
    return buf
