# 🗺️ Poster Build Guide
## "Indonesia Pakai AI — Tapi Belum Siap"
### Data Visualization Poster — Full Technical Brief

---

## 1. Data Sources

Semua data sudah ada di notebook `Dataset_Correlation.ipynb` kamu. Berikut mapping dataset ke grafik:

### Dataset 1 — `final_global_country_ai_dataset.csv`
```
URL: https://drive.google.com/uc?id=1XbMG2fAOWLSwfuQQqb6w0IIruWDk6RyI
```

Kolom yang dipakai:

| Kolom | Dipakai di Grafik |
|---|---|
| `country` | Semua grafik (join key) |
| `ai_overall_score` | Grafik 1 — Bubble size |
| `ai_talent` | Grafik 2 — Stacked bar |
| `ai_infrastructure` | Grafik 2 — Stacked bar |
| `ai_government_strategy` | Grafik 1 — Bar dot · Grafik 2 — Stacked bar |
| `ai_research` | Grafik 2 — Stacked bar |
| `ai_development` | Grafik 2 — Stacked bar |
| `ai_commercial` | Grafik 2 — Stacked bar |
| `gdp_per_capita` | Grafik 1 — Arc band width |
| `internet_usage_pct` | Grafik 1 — Bar secondary |
| `rank_ai_overall` | Hook callout |

### Dataset 2 — `trend_country_year_2020_2024.csv`
```
URL: https://drive.google.com/uc?id=1Z3x2Q5CSSvcfjIQaehZJ7jEGO7TEQFTX
```
Tidak dipakai langsung di poster — sudah teragregasi di dataset 1.

### Dataset 3 — `fitped_dataset1.csv`
```
URL: https://drive.google.com/uc?id=1BIy4219xU8GKhmgZzk1WQ04QiEBa35oy
```

Kolom yang dipakai (agregasi mean per konstruk):

| Konstruk | Kolom raw | Mean (paper) |
|---|---|---|
| AI Literacy | L1–L5 | 3.99 |
| AI Readiness | RE1–RE6 | 3.78 |
| AI Anxiety | A1–A5 | 2.58 (inverted di radar) |
| Career Motivation | CM1–CM4 | 3.67 |
| Behavioural Intention | BI1–BI5 | 3.76 |
| Confidence | C1–C5 | 3.58 |
| Relevance of AI | R1–R6 | 3.80 |

---

## 2. Library yang Dibutuhkan

```python
pip install matplotlib numpy pandas scipy

# Semua sudah tersedia di Google Colab default
# Tidak perlu install tambahan
```

| Library | Dipakai untuk |
|---|---|
| `matplotlib.pyplot` | Semua grafik |
| `matplotlib.gridspec` | Layout multi-panel poster |
| `matplotlib.patches.PathPatch` | Arc flow / bezier bands |
| `matplotlib.path.Path` | Custom bezier curves untuk arc |
| `numpy` | Kalkulasi posisi arc, radar angles |
| `pandas` | Load dan filter data |
| `scipy.stats` | Opsional — kalau mau tambah regression line di scatter |

---

## 3. Struktur File

```
poster_project/
│
├── poster_main.py          ← script utama, jalankan ini
├── data/
│   ├── (otomatis load dari Google Drive via URL)
└── output/
    └── poster_ai_indonesia.png   ← hasil output
```

---

## 4. Layout Poster

Ukuran canvas: **24 × 52 inch** @ 150 dpi = 3600 × 7800 px

```
fig = plt.figure(figsize=(24, 52), facecolor='#0F172A')

GridSpec height ratios:
  [3.0]  →  Section 1: Hook
  [24.0] →  Section 2: Arc + Bar + Bubble (3 kolom)
  [14.0] →  Section 3: Stacked Bar Pilar
  [14.0] →  Section 4: 3x Radar + Insight cards
  [3.5]  →  Section 5: CTA + Footer
```

---

## 5. Section-by-Section Build Guide

---

### SECTION 1 — HOOK

**Tujuan:** Ciptakan pertanyaan di kepala pembaca sebelum mereka melihat satu grafik pun.

**Yang ditampilkan:**
```
[Kalimat kontras besar]
"Indonesia pakai AI lebih banyak dari Jerman —
 tapi rank AI-nya 47 tingkat di bawahnya."

[3 stat cards horizontal]
  9/100           #39              9 Juta
AI Score      Global Rank      Tech workers
                               dibutuhkan 2030
```

**Data source:** Hardcoded dari hasil analisis notebook (tidak perlu kalkulasi ulang).

**Teknik:** `ax.text()` dengan `transform=ax.transAxes` — tidak perlu chart sama sekali.

---

### SECTION 2 — ARC FLOW + BAR + BUBBLE

**Ini adalah highlight section — 3 kolom paralel, ukuran 46% dari total tinggi poster.**

---

#### Kolom Kiri — Arc Proportional Flow

**Konsep:** Mirip poster plastic waste. Setiap negara = satu arc band. Lebar band proporsional terhadap GDP per capita. Dikelompokkan per region sebagai label di sisi kiri.

**Data yang dipakai:**
```python
df['gdp_per_capita']  # lebar arc
df['country']         # label di ujung kanan arc
df['region']          # grouping label kiri
```

**Teknik — Custom Bezier Arc:**
```python
from matplotlib.patches import PathPatch
from matplotlib.path import Path

def draw_arc_band(ax, y_center, band_height, gdp_value, max_gdp,
                  color, x_start=0, x_end=8):
    """
    Gambar satu arc band untuk satu negara.
    Lebar band = proporsional terhadap gdp_value / max_gdp
    """
    # Lebar arc di sisi kanan (proporsional)
    arc_width = (gdp_value / max_gdp) * (x_end - x_start)

    # 4 control points untuk bezier
    y_top = y_center + band_height / 2
    y_bot = y_center - band_height / 2
    cx    = (x_start + x_end) / 2

    verts = [
        (x_start, y_bot),
        (cx, y_bot), (cx, y_bot), (x_end, y_bot),   # bottom curve
        (x_end, y_top),
        (cx, y_top), (cx, y_top), (x_start, y_top),  # top curve
        (x_start, y_bot),
    ]
    codes = [Path.MOVETO,
             Path.CURVE4, Path.CURVE4, Path.CURVE4,
             Path.LINETO,
             Path.CURVE4, Path.CURVE4, Path.CURVE4,
             Path.CLOSEPOLY]

    ax.add_patch(PathPatch(
        Path(verts, codes),
        facecolor=color, edgecolor='none', alpha=0.75, zorder=2
    ))

    # Label GDP di dalam band (jika cukup lebar)
    if gdp_value > 5000:
        gdp_k = gdp_value / 1000
        ax.text(x_end * 0.6, y_center,
                f'${gdp_k:.0f}k',
                color='white', fontsize=8, fontweight='bold',
                ha='center', va='center', zorder=3)
```

**Negara yang ditampilkan (30 negara):**
```python
# Top 12 AI score
TOP12 = df.nlargest(12, 'ai_overall_score')['country'].tolist()

# ASEAN
ASEAN = ['Malaysia', 'Thailand', 'Indonesia', 'Vietnam', 'Philippines']

# GDP peers Indonesia (GDP mirip ~$3k–$7k)
PEERS = ['Brazil', 'India', 'Colombia', 'Egypt', 'Morocco', 'Nigeria', 'Mexico']

SELECTED = list(dict.fromkeys(TOP12 + ASEAN + PEERS))
```

**Sorting:** Dalam setiap region, negara diurutkan dari GDP tertinggi ke terendah (arc terluar = GDP terbesar).

**Highlight Indonesia:**
```python
COUNTRY_COLORS = {
    'Indonesia'    : '#E24B4A',   # merah — HANYA Indonesia
    'Singapore'    : '#378ADD',   # biru
    'Brazil'       : '#1D9E75',   # hijau
    'India'        : '#E8A838',   # amber
    # lainnya      : warna region (muted)
}
```

**Region label di kiri:**
```python
REGION_COLORS = {
    'Asia'    : '#7C3AED',
    'Europe'  : '#0891B2',
    'Americas': '#059669',
    'Africa'  : '#D97706',
}
```

---

#### Kolom Tengah — Bar Chart: Gov Strategy + Internet Dot

**Tujuan:** Tunjukkan bahwa GDP mirip bukan berarti Gov Strategy mirip. Ini differentiator yang menjelaskan gap AI score.

**Data yang dipakai:**
```python
df['ai_government_strategy']  # bar utama
df['internet_usage_pct']      # secondary dot
```

**Teknik:**
```python
# Untuk setiap negara (satu row per negara, aligned dengan arc):
ax.barh(y_center, row['ai_government_strategy'],
        height=0.55, color=country_color, alpha=0.88)

# Internet sebagai dot overlay (normalisasi 0-100)
ax.scatter(row['internet_usage_pct'], y_center,
           s=28, color='#FBBF24', zorder=5)

# Label angka
ax.text(row['ai_government_strategy'] + 1, y_center,
        f"{int(row['ai_government_strategy'])}",
        color='white', fontsize=7.5, va='center')
```

**Annotasi wajib (callout Indonesia):**
```python
# Di baris Indonesia, tambah annotation box
ax.annotate(
    "Gov Strategy = 19\n(Finland = 39 · India = 55)",
    xy=(19, idn_y),
    xytext=(55, idn_y + 3),
    color='#FBBF24',
    arrowprops=dict(arrowstyle='->', color='#FBBF24', lw=1.2),
    bbox=dict(boxstyle='round,pad=0.3', fc='#1E293B', ec='#FBBF24', lw=0.8),
    fontsize=7.5
)
```

---

#### Kolom Kanan — Bubble: AI Score

**Tujuan:** Visual penutup — ukuran bubble langsung komunikasikan posisi AI negara tanpa perlu baca angka.

**Data yang dipakai:**
```python
df['ai_overall_score']  # → radius bubble
```

**Teknik:**
```python
max_score = df['ai_overall_score'].max()

for i, row in dfs.iterrows():
    radius = (row['ai_overall_score'] / max_score) * 0.44 + 0.05
    circle = plt.Circle((0, y_center), radius,
                         color=country_color, alpha=0.82)
    ax.add_patch(circle)
    # Angka di dalam bubble
    ax.text(0, y_center, f"{int(row['ai_overall_score'])}",
            color='white', fontsize=7.5, fontweight='bold',
            ha='center', va='center')
```

---

### SECTION 3 — STACKED BAR: AI PILLAR DISTRIBUTION

**Tujuan:** Tunjukkan bahwa Indonesia tidak tertinggal di semua pilar — hanya di Gov Strategy dan Research. Ini mempertegas argumen bahwa masalahnya bukan kapasitas tapi kebijakan.

**Data yang dipakai:**
```python
PILLARS = [
    'ai_talent',
    'ai_infrastructure',
    'ai_government_strategy',
    'ai_research',
    'ai_development',
    'ai_commercial'
]
```

**Pilihan negara untuk section ini (lebih selektif — 12-15 negara):**
```python
# Hanya tampilkan:
# - Top 5 AI score
# - Indonesia
# - 3–4 GDP peers Indonesia (India, Brazil, Colombia)
# - 2–3 negara ASEAN (Singapore, Malaysia, Vietnam)
SUBSET = ['United States', 'China', 'Singapore', 'United Kingdom', 'Germany',
          'Finland', 'India', 'Brazil', 'Malaysia', 'Vietnam', 'Indonesia',
          'Colombia', 'Nigeria']
```

**Teknik:**
```python
PIL_COLORS = ['#818CF8','#38BDF8','#34D399','#FBBF24','#F472B6','#FB923C']

for i, row in dfs.iterrows():
    left = 0
    for col, pc in zip(PILLARS, PIL_COLORS):
        ax.barh(y_center, row[col], height=0.6,
                left=left, color=pc, alpha=0.88)
        left += row[col]
```

**Highlight Indonesia:**
```python
# Tambah border merah tipis di seluruh baris Indonesia
ax.barh(idn_y, 105, height=0.72, left=0,
        color='none', edgecolor='#E24B4A', lw=1.2, zorder=5)
```

**Legend pilar** ditempatkan di bagian atas section sebagai color swatch horizontal.

---

### SECTION 4 — RADAR CHART (3x Berdampingan)

**Tujuan:** Tunjukkan kondisi kesiapan mahasiswa Indonesia dibandingkan kondisi ideal dan negara maju. Polygon yang "penyok" di Confidence dan Readiness adalah visual metafora utama.

**Data yang dipakai:**
```python
# Dari fitped_dataset1.csv — agregasi mean per konstruk
# Hitung dengan:
fitped_means = df_fp.groupby('Country')[konstruk_columns].mean()
idn_means    = fitped_means.loc['Indonesia']
```

**6 axis radar yang digunakan:**
```python
AXES = {
    'AI Literacy'  : mean_L,        # L1-L5 avg
    'Readiness'    : mean_RE,        # RE1-RE6 avg
    'Relevance'    : mean_R,         # R1-R6 avg
    'Confidence'   : mean_C,         # C1-C5 avg
    'Intent'       : mean_BI,        # BI1-BI5 avg
    'Low Anxiety'  : 5 - mean_A,     # INVERTED: rendah anxiety = bagus
}
```

**3 radar yang digambar:**
```
Radar 1 — Indonesia (merah)
Radar 2 — Negara maju di dataset (biru) — ambil mean negara Eropa di FITPED
Radar 3 — Kondisi ideal (abu putus-putus) — set semua axis = 4.3
```

**Teknik:**
```python
import numpy as np

def draw_radar(ax, values, labels, color, fill_alpha=0.25, lw=2, ls='-'):
    N      = len(labels)
    angles = np.linspace(0, 2*np.pi, N, endpoint=False).tolist()
    vals   = values + [values[0]]
    a      = angles + [angles[0]]

    ax.set_facecolor('#0F172A')
    ax.set_theta_offset(np.pi / 2)
    ax.set_theta_direction(-1)
    ax.set_ylim(0, 5)
    ax.set_xticks(angles)
    ax.set_xticklabels(labels, fontsize=8, color='#94A3B8')
    ax.set_yticks([1, 2, 3, 4, 5])
    ax.set_yticklabels([])
    ax.grid(color='#475569', lw=0.4, alpha=0.4)

    ax.plot(a, vals, color=color, lw=lw, ls=ls)
    ax.fill(a, vals, color=color, alpha=fill_alpha)
```

**Insight cards (di sebelah kanan 3 radar):**
```
┌─────────────────────────────────────┐
│  TAHU soal AI          3.99/5  ✓   │
│  TIDAK TAKUT AI        2.58/5  ✓   │
│  TIDAK PERCAYA DIRI    3.58/5  ✗   │  ← highlight ini
│  NIAT TINGGI pakai AI  3.76/5  ✓   │
└─────────────────────────────────────┘
```

```python
# Setiap card = FancyBboxPatch + 2 text elements
ax.add_patch(FancyBboxPatch(
    (x, y), width, height,
    boxstyle="round,pad=0.01",
    facecolor='#1E293B', edgecolor=color, lw=0.8
))
ax.text(x+0.08, y+mid, label, color='#94A3B8', fontsize=9)
ax.text(x+0.88, y+mid, value, color=color, fontsize=9,
        fontweight='bold', ha='right')
```

---

### SECTION 5 — CALL TO ACTION

**Tujuan:** Tutup dengan solusi yang terukur. Bukan opini — tunjukkan angka target yang konkret.

**Yang ditampilkan:**
```
[Kalimat kuat]
"Masalahnya bukan uang. Bukan talenta. Bukan internet."

[Target konkret]
"Gov. Strategy: 19 → 39 = proyeksi naik dari rank #39 ke #16 dunia"
"India dengan GDP lebih rendah dari Indonesia, Gov Strategy 55 = rank #12"

[Footer sumber]
Tortoise Global AI Index 2024 · UNDP HDR 2023 · World Bank 2023 · FITPED 2024 (n=1,205)
```

---

## 6. Color System

### Per Entitas (konsisten di SEMUA grafik)
```python
COLORS = {
    'Indonesia' : '#E24B4A',   # merah — EKSKLUSIF, tidak dipakai entitas lain
    'Singapore' : '#378ADD',
    'Brazil'    : '#1D9E75',
    'India'     : '#E8A838',
    'Others'    : '#475569',   # muted slate
}
```

### Per Region (untuk arc flow grouping)
```python
REGION_COLORS = {
    'Asia'    : '#7C3AED',
    'Europe'  : '#0891B2',
    'Americas': '#059669',
    'Africa'  : '#D97706',
}
```

### Per Pilar AI (untuk stacked bar)
```python
PILLAR_COLORS = {
    'Talent'         : '#818CF8',
    'Infrastructure' : '#38BDF8',
    'Gov. Strategy'  : '#34D399',
    'Research'       : '#FBBF24',
    'Development'    : '#F472B6',
    'Commercial'     : '#FB923C',
}
```

### UI
```python
BG       = '#0F172A'   # background utama
PANEL_BG = '#1E293B'   # background card/callout
TEXT     = '#F1F5F9'   # teks utama
TEXT_DIM = '#94A3B8'   # teks sekunder/label
ACCENT   = '#FBBF24'   # kuning — untuk callout/annotation
```

---

## 7. Typography

```python
plt.rcParams.update({
    'font.family'     : 'sans-serif',
    'font.size'       : 10,
    'figure.facecolor': '#0F172A',
})

# Ukuran teks per elemen:
# Judul poster        : fontsize=32, fontweight='bold'
# Section titles      : fontsize=13, fontstyle='italic', color=TEXT_DIM
# Big number HOOK     : fontsize=28, fontweight='bold'
# Label negara        : fontsize=8.5 (highlight) / 7.0 (others)
# Angka di dalam chart: fontsize=7.5, fontweight='bold'
# Anotasi callout     : fontsize=7.5
# Footer              : fontsize=7.5, color=MUTED
```

---

## 8. Checklist Sebelum Final Export

- [ ] Indonesia berwarna merah di **semua** 5 section
- [ ] Arc band Indonesia terlihat jelas (warna berbeda dari region color)
- [ ] Anotasi Gov Strategy callout muncul tepat di baris Indonesia
- [ ] 3 radar ukurannya sama persis
- [ ] Insight cards radar readable dari jarak normal (fontsize min 8.5)
- [ ] Legend pilar tersedia dan mudah dibaca
- [ ] Footer sumber lengkap: 4 dataset + tahun
- [ ] Test print: simpan juga sebagai PDF untuk output A2

---

## 9. Export

```python
# Preview (Colab)
plt.savefig('poster_ai_indonesia.png',
            dpi=150, bbox_inches='tight',
            facecolor='#0F172A', edgecolor='none')

# Print-ready (A2)
plt.savefig('poster_ai_indonesia_print.pdf',
            dpi=300, bbox_inches='tight',
            facecolor='#0F172A', edgecolor='none',
            format='pdf')

plt.show()
```

---

## 10. Urutan Build yang Disarankan

```
1. Setup figure dan GridSpec dulu — pastikan proporsi benar
2. Build Section 1 (Hook) — paling cepat, verify layout
3. Build Arc Flow (kolom kiri Section 2) — yang paling kompleks, kerjakan duluan
4. Build Bar + Bubble (kolom tengah dan kanan Section 2)
5. Build Stacked Bar Section 3
6. Build Radar Section 4
7. Build CTA Section 5
8. Final pass: warna, font size, spacing, anotasi
9. Export PNG preview → cek di layar → Export PDF
```

---

*Sumber data: Tortoise Global AI Index 2024 · UNDP Human Development Report 2023 · World Bank Internet Penetration 2023 · FITPED Cross-National AI Education Survey 2024 (n=1,205)*