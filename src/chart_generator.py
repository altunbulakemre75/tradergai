import io
import matplotlib.pyplot as plt
import numpy as np
from wordcloud import WordCloud

def generate_gauge(score: int, title: str = "Piyasa Duyarlılığı") -> io.BytesIO:
    """
    Üretilen skor (0-100) için görsel bir ibre (gauge) oluşturur.
    """
    fig, ax = plt.subplots(figsize=(6, 3), subplot_kw={'projection': 'polar'})
    
    # Arka plan renkleri (Kırmızıdan Yeşile)
    colors = ['#ff4b4b', '#ffa500', '#2ecc71']
    values = [0, 33, 66, 100]
    
    # Yarım daire ayarı
    ax.set_theta_zero_location("W")
    ax.set_theta_direction(-1)
    ax.set_thetamax(180)
    ax.set_thetagrids([])
    ax.set_yticklabels([])
    ax.spines['polar'].set_visible(False)

    # Renk dilimleri
    for i in range(len(colors)):
        start = np.deg2rad(values[i] * 1.8)
        end = np.deg2rad(values[i+1] * 1.8)
        ax.barh(1, end - start, left=start, color=colors[i], height=0.5, align='edge', alpha=0.8)

    # İbre (Pointer)
    pos = np.deg2rad(score * 1.8)
    ax.annotate("", xy=(pos, 1.1), xytext=(0, 0),
                arrowprops=dict(arrowstyle="wedge,tail_width=0.5", color="black", lw=2))
    
    # Orta nokta
    ax.plot(0, 0, color="black", marker="o", markersize=10)

    # Metinler
    plt.title(f"{title} (%{score})", fontsize=14, pad=20, fontweight='bold')
    plt.text(np.deg2rad(0), 1.3, "Ayı (Negatif)", horizontalalignment='center', fontsize=10)
    plt.text(np.deg2rad(180), 1.3, "Boğa (Pozitif)", horizontalalignment='center', fontsize=10)

    buf = io.BytesIO()
    plt.savefig(buf, format='png', bbox_inches='tight', transparent=True)
    plt.close(fig)
    buf.seek(0)
    return buf

def generate_wordcloud(keywords: list[str]) -> io.BytesIO | None:
    """
    Anahtar kelimelerden bir kelime bulutu görseli oluşturur.
    """
    if not keywords:
        return None
        
    text = " ".join(keywords)
    wordcloud = WordCloud(
        width=800, height=400,
        background_color='white',
        colormap='viridis',
        max_words=50
    ).generate(text)

    fig, ax = plt.subplots(figsize=(10, 5))
    ax.imshow(wordcloud, interpolation='bilinear')
    ax.axis("off")
    
    buf = io.BytesIO()
    plt.savefig(buf, format='png', bbox_inches='tight')
    plt.close(fig)
    buf.seek(0)
    return buf
