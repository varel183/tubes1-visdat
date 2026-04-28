"""
poster_main.py
"Indonesia Pakai AI — Tapi Belum Siap"
Data Visualization Poster — Sankey Flow Edition
"""

import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from matplotlib.patches import PathPatch, FancyBboxPatch, Circle
from matplotlib.path import Path
import warnings
warnings.filterwarnings('ignore')

# ══════════════════════════════════════════
# 0.  COLOR SYSTEM
# ══════════════════════════════════════════
BG       = '#0D1B2E'
PANEL_BG = '#1E293B'
TEXT     = '#F1F5F9'
TEXT_DIM = '#94A3B8'
ACCENT   = '#FBBF24'
MUTED    = '#334155'

COUNTRY_COLORS = {
    'Indonesia'     : '#E24B4A',
    'Singapore'     : '#5B9BD5',
    'Brazil'        : '#1D9E75',
    'India'         : '#E8A838',
    'United States' : '#60A5FA',
    'China'         : '#F87171',
    'Germany'       : '#A78BFA',
    'United Kingdom': '#34D399',
    'France'        : '#FB923C',
    'Finland'       : '#38BDF8',
    'Japan'         : '#F9A8D4',
    'South Korea'   : '#86EFAC',
    'Canada'        : '#67E8F9',
    'Australia'     : '#FCD34D',
}

REGION_COLORS = {
    'Asia'     : '#7C3AED',
    'Europe'   : '#0891B2',
    'Americas' : '#059669',
    'Africa'   : '#D97706',
    'Oceania'  : '#BE185D',
    'Others'   : '#475569',
}

PIL_COLORS = ['#818CF8','#38BDF8','#34D399','#FBBF24','#F472B6','#FB923C']
PILLARS    = ['ai_talent','ai_infrastructure','ai_government_strategy',
              'ai_research','ai_development','ai_commercial']
PIL_LABELS = ['Talent','Infrastructure','Gov. Strategy','Research','Development','Commercial']

plt.rcParams.update({
    'font.family'     : 'DejaVu Sans',
    'font.size'       : 10,
    'figure.facecolor': BG,
    'axes.facecolor'  : BG,
    'text.color'      : TEXT,
})

# ══════════════════════════════════════════
# 1.  LOAD DATA
# ══════════════════════════════════════════
print("Loading datasets...")

URL1 = "https://drive.google.com/uc?id=1XbMG2fAOWLSwfuQQqb6w0IIruWDk6RyI&export=download"
URL3 = "https://drive.google.com/uc?id=1BIy4219xU8GKhmgZzk1WQ04QiEBa35oy&export=download"

df    = pd.read_csv(URL1)
df_fp = pd.read_csv(URL3)

print("Columns AI:", df.columns.tolist())

df.columns    = df.columns.str.strip().str.lower().str.replace(' ', '_')
df_fp.columns = df_fp.columns.str.strip().str.lower().str.replace(' ', '_')

# ── Region assignment ─────────────────────────────────────────
REGION_MAP = {
    'United States':'Americas','Canada':'Americas','Mexico':'Americas',
    'Brazil':'Americas','Colombia':'Americas','Argentina':'Americas',
    'China':'Asia','Japan':'Asia','South Korea':'Asia','India':'Asia',
    'Singapore':'Asia','Malaysia':'Asia','Thailand':'Asia','Indonesia':'Asia',
    'Vietnam':'Asia','Philippines':'Asia','Taiwan':'Asia',
    'United Kingdom':'Europe','Germany':'Europe','France':'Europe',
    'Finland':'Europe','Sweden':'Europe','Netherlands':'Europe',
    'Spain':'Europe','Italy':'Europe','Poland':'Europe','Denmark':'Europe',
    'Norway':'Europe','Switzerland':'Europe',
    'Nigeria':'Africa','Egypt':'Africa','Morocco':'Africa','South Africa':'Africa',
    'Australia':'Oceania','New Zealand':'Oceania',
}
if 'region' not in df.columns:
    df['region'] = df['country'].map(REGION_MAP).fillna('Others')

# ── Selected countries (30) ───────────────────────────────────
TOP12    = df.nlargest(12, 'ai_overall_score')['country'].tolist()
ASEAN    = ['Malaysia','Thailand','Indonesia','Vietnam','Philippines']
PEERS    = ['Brazil','India','Colombia','Egypt','Morocco','Nigeria','Mexico']
SELECTED = list(dict.fromkeys(TOP12 + ASEAN + PEERS))
SELECTED = [c for c in SELECTED if c in df['country'].values]

dfs = df[df['country'].isin(SELECTED)].copy()

# Sort: region order (Africa last so Asia/Europe/Americas up top), then GDP desc within region
REGION_ORDER = ['Americas','Asia','Europe','Africa','Oceania','Others']
dfs['_rord'] = dfs['region'].map({r:i for i,r in enumerate(REGION_ORDER)}).fillna(99)
dfs = dfs.sort_values(['_rord','gdp_per_capita'], ascending=[True,False]).reset_index(drop=True)

n = len(dfs)

# ── FITPED means (paper-reported) ────────────────────────────
RADAR_LABELS = ['AI Literacy','Readiness','Relevance','Confidence','Intent','Low Anxiety']
idn_radar    = [3.99, 3.78, 3.80, 3.58, 3.76, 5 - 2.58]
adv_radar    = [4.22, 4.05, 4.18, 4.10, 4.12, 5 - 1.85]
ideal_radar  = [4.3] * 6

print("Data ready. N countries:", n)

# ══════════════════════════════════════════
# 2.  FIGURE + GRIDSPEC
# ══════════════════════════════════════════
fig = plt.figure(figsize=(24, 52), facecolor=BG)
gs_main = gridspec.GridSpec(
    5, 1,
    height_ratios=[2.8, 24.0, 14.0, 14.0, 3.2],
    hspace=0.03,
    figure=fig,
    left=0.03, right=0.97,
    top=0.99, bottom=0.01
)

def clean_ax(ax, keep_y=False):
    ax.set_facecolor(BG)
    ax.set_xticks([])
    if not keep_y:
        ax.set_yticks([])
    for sp in ax.spines.values():
        sp.set_visible(False)

def get_color(country, region=''):
    return COUNTRY_COLORS.get(country, REGION_COLORS.get(region, MUTED))

# ══════════════════════════════════════════
# SECTION 1 — HOOK
# ══════════════════════════════════════════
ax_hook = fig.add_subplot(gs_main[0])
clean_ax(ax_hook)

ax_hook.text(0.5, 0.84,
    'Indonesia pakai AI lebih banyak dari Jerman —',
    transform=ax_hook.transAxes, ha='center', va='center',
    fontsize=30, fontweight='bold', color=TEXT)
ax_hook.text(0.5, 0.60,
    'tapi rank AI-nya 47 tingkat di bawahnya.',
    transform=ax_hook.transAxes, ha='center', va='center',
    fontsize=30, fontweight='bold', color='#E24B4A')

cards = [
    ('9/100',  'AI Score',                  0.18),
    ('#39',    'Global Rank',               0.50),
    ('9 Juta', 'Tech workers needed 2030',  0.82),
]
for val, lbl, xp in cards:
    ax_hook.text(xp, 0.28, val,
        transform=ax_hook.transAxes, ha='center', va='center',
        fontsize=28, fontweight='bold', color=ACCENT)
    ax_hook.text(xp, 0.08, lbl,
        transform=ax_hook.transAxes, ha='center', va='center',
        fontsize=9.5, color=TEXT_DIM)

# ══════════════════════════════════════════
# SECTION 2 — SANKEY + BAR + BUBBLE
# ══════════════════════════════════════════
gs2 = gridspec.GridSpecFromSubplotSpec(
    1, 3, subplot_spec=gs_main[1],
    width_ratios=[6, 3, 2], wspace=0.01
)
ax_sk  = fig.add_subplot(gs2[0])   # Sankey
ax_bar = fig.add_subplot(gs2[1])   # Gov Strategy bars
ax_bub = fig.add_subplot(gs2[2])   # AI Score bubbles

for ax in (ax_sk, ax_bar, ax_bub):
    clean_ax(ax)

# ── Sankey geometry ───────────────────────────────────────────
# Y-axis: 0 at bottom, n+1 at top. Right side: uniform rows.
ROW_H      = 0.72   # row height on right side
REGION_GAP = 1.60   # gap between region blocks on LEFT side

# Right-side y-centers (evenly spaced, same order as dfs)
right_yc = np.arange(n, 0, -1, dtype=float)        # n, n-1, ..., 1
right_yb = right_yc - ROW_H / 2
right_yt = right_yc + ROW_H / 2

# Left-side: stack proportionally by GDP within each region
regions_in_order = []
for r in dfs['region'].tolist():
    if r not in regions_in_order:
        regions_in_order.append(r)

n_regions    = len(regions_in_order)
total_span   = n + 1.0                                   # matches right-side span
gap_budget   = n_regions * REGION_GAP
band_budget  = total_span - gap_budget                   # total height for actual bands
total_gdp    = dfs['gdp_per_capita'].sum()
dfs['left_h'] = (dfs['gdp_per_capita'] / total_gdp) * band_budget

# Walk region by region from top
left_yc_list = []
left_yb_list = []
left_yt_list = []

cur = total_span  # start at top
for reg in regions_in_order:
    mask = dfs['region'] == reg
    for idx in dfs[mask].index:
        h   = dfs.loc[idx, 'left_h']
        top = cur
        bot = cur - h
        left_yt_list.append(top)
        left_yb_list.append(bot)
        left_yc_list.append((top + bot) / 2)
        cur = bot
    cur -= REGION_GAP

dfs['left_yt'] = left_yt_list
dfs['left_yb'] = left_yb_list
dfs['left_yc'] = left_yc_list

# ── Sankey draw function ───────────────────────────────────────
def draw_sankey(ax, yl_bot, yl_top, yr_bot, yr_top, xl, xr, color, alpha=0.72):
    """
    Draw one Sankey band using two cubic bezier curves (top & bottom edges)
    and vertical lines at left and right walls.
    """
    cx1 = xl + (xr - xl) * 0.38
    cx2 = xl + (xr - xl) * 0.62

    verts = [
        (xl,  yl_bot),
        (cx1, yl_bot), (cx2, yr_bot), (xr, yr_bot),  # bottom edge →
        (xr,  yr_top),
        (cx2, yr_top), (cx1, yl_top), (xl, yl_top),  # top edge ←
        (xl,  yl_bot),
    ]
    codes = [
        Path.MOVETO,
        Path.CURVE4, Path.CURVE4, Path.CURVE4,
        Path.LINETO,
        Path.CURVE4, Path.CURVE4, Path.CURVE4,
        Path.CLOSEPOLY,
    ]
    ax.add_patch(PathPatch(Path(verts, codes),
                           facecolor=color, edgecolor='none',
                           alpha=alpha, zorder=2))

# Axis limits (same coordinate system for Sankey, bar, bubble)
Y_MIN = 0
Y_MAX = n + 1.2

XL = 0.0
XR = 8.5

ax_sk.set_xlim(-2.5, XR + 2.0)
ax_sk.set_ylim(Y_MIN, Y_MAX)

# ── Draw all Sankey bands ─────────────────────────────────────
for i, (_, row) in enumerate(dfs.iterrows()):
    c = get_color(row['country'], row['region'])
    draw_sankey(ax_sk,
                yl_bot=row['left_yb'], yl_top=row['left_yt'],
                yr_bot=right_yb[i],   yr_top=right_yt[i],
                xl=XL, xr=XR,
                color=c)

# ── Region labels on LEFT ─────────────────────────────────────
# Compute mid-y for each region block (on LEFT side)
for reg in regions_in_order:
    reg_mask = dfs['region'] == reg
    if not reg_mask.any():
        continue
    top_y = dfs.loc[reg_mask, 'left_yt'].max()
    bot_y = dfs.loc[reg_mask, 'left_yb'].min()
    mid_y = (top_y + bot_y) / 2
    rc    = REGION_COLORS.get(reg, MUTED)

    # Horizontal bracket line along left wall
    ax_sk.plot([XL, XL], [bot_y, top_y], color=rc, lw=2.5, alpha=0.9, zorder=5)

    # Region label to the left
    ax_sk.text(-0.4, mid_y, reg.upper(),
               va='center', ha='right', fontsize=9,
               fontweight='bold', color=rc, zorder=6)


# ── GDP labels inside wide bands (left side) ─────────────────
for i, (_, row) in enumerate(dfs.iterrows()):
    bh = row['left_yt'] - row['left_yb']
    if bh > 0.55 and row['gdp_per_capita'] > 5000:
        gdp_k = row['gdp_per_capita'] / 1000
        c = get_color(row['country'], row['region'])
        ax_sk.text(XL + (XR - XL)*0.15, row['left_yc'],
                   f"${gdp_k:.0f}k",
                   color='white', fontsize=7, fontweight='bold',
                   ha='center', va='center', zorder=4)

# ── Country labels on RIGHT of Sankey ─────────────────────────
for i, (_, row) in enumerate(dfs.iterrows()):
    c  = get_color(row['country'], row['region'])
    fs = 8.5 if row['country'] == 'Indonesia' else 7.0
    fw = 'bold' if row['country'] == 'Indonesia' else 'normal'
    ax_sk.text(XR + 0.15, right_yc[i], row['country'],
               va='center', ha='left', fontsize=fs, fontweight=fw,
               color='#E24B4A' if row['country'] == 'Indonesia' else TEXT_DIM)

# Section column title
ax_sk.text((XL + XR)/2, Y_MAX - 0.05, 'GDP PER CAPITA (width of band)',
           ha='center', va='top', fontsize=9, fontstyle='italic',
           color=TEXT_DIM, fontweight='bold')

# ── BAR: Gov Strategy + Internet dot ─────────────────────────
ax_bar.set_xlim(0, 108)
ax_bar.set_ylim(Y_MIN, Y_MAX)

idn_y = None
for i, (_, row) in enumerate(dfs.iterrows()):
    y  = right_yc[i]
    c  = get_color(row['country'], row['region'])
    gs_val = float(row.get('ai_government_strategy', 0) or 0)
    iu_val = float(row.get('internet_usage_pct',      0) or 0)

    ax_bar.barh(y, gs_val, height=ROW_H * 0.78, color=c, alpha=0.88, zorder=2)
    ax_bar.scatter(iu_val, y, s=22, color=ACCENT, zorder=5)
    ax_bar.text(gs_val + 1.2, y, f"{int(gs_val)}",
                color=TEXT_DIM, fontsize=6.5, va='center')

    if row['country'] == 'Indonesia':
        idn_y   = y
        idn_gs  = gs_val

if idn_y is not None:
    ax_bar.annotate(
        f"Gov Strategy = {int(idn_gs)}\n(Finland=39 · India=55)",
        xy=(idn_gs, idn_y),
        xytext=(68, idn_y + 4),
        color=ACCENT,
        arrowprops=dict(arrowstyle='->', color=ACCENT, lw=1.1),
        bbox=dict(boxstyle='round,pad=0.3', fc=PANEL_BG, ec=ACCENT, lw=0.8),
        fontsize=7.5, zorder=6
    )

ax_bar.text(54, Y_MAX - 0.05, 'GOV. STRATEGY SCORE',
            ha='center', va='top', fontsize=9,
            fontstyle='italic', color=TEXT_DIM, fontweight='bold')

# Internet dot legend
ax_bar.scatter([], [], s=22, color=ACCENT, label='Internet usage %')
leg = ax_bar.legend(loc='lower right', fontsize=7, framealpha=0.3,
                    facecolor=PANEL_BG, edgecolor=MUTED)
for t in leg.get_texts(): t.set_color(TEXT_DIM)

# ── BUBBLE: AI Score ──────────────────────────────────────────
max_score = dfs['ai_overall_score'].max()
ax_bub.set_xlim(-1.0, 1.0)
ax_bub.set_ylim(Y_MIN, Y_MAX)
ax_bub.set_aspect('auto')

for i, (_, row) in enumerate(dfs.iterrows()):
    y      = right_yc[i]
    c      = get_color(row['country'], row['region'])
    score  = float(row.get('ai_overall_score', 0) or 0)
    radius = (score / max_score) * 0.44 + 0.05
    ax_bub.add_patch(Circle((0, y), radius, color=c, alpha=0.85))
    ax_bub.text(0, y, f"{int(score)}",
                color='white', fontsize=6.5, fontweight='bold',
                ha='center', va='center')

ax_bub.text(0, Y_MAX - 0.05, 'AI SCORE',
            ha='center', va='top', fontsize=9,
            fontstyle='italic', color=TEXT_DIM, fontweight='bold')

# ══════════════════════════════════════════
# SECTION 3 — STACKED BAR: AI PILLARS
# ══════════════════════════════════════════
ax_s3 = fig.add_subplot(gs_main[2])
clean_ax(ax_s3)

SUBSET_NAMES = ['United States','China','Singapore','United Kingdom','Germany',
                'Finland','India','Brazil','Malaysia','Vietnam','Indonesia',
                'Colombia','Nigeria']
ds3 = df[df['country'].isin(SUBSET_NAMES)].copy()
ds3['_ord'] = ds3['country'].map({c:i for i,c in enumerate(SUBSET_NAMES)})
ds3 = ds3.sort_values('_ord').reset_index(drop=True)

n3  = len(ds3)
ys3 = np.arange(n3, 0, -1, dtype=float)

ax_s3.set_xlim(0, 118)
ax_s3.set_ylim(0, n3 + 2.2)

for i, (_, row) in enumerate(ds3.iterrows()):
    y    = ys3[i]
    left = 0.0
    for col, pc in zip(PILLARS, PIL_COLORS):
        val = float(row.get(col, 0) or 0)
        ax_s3.barh(y, val, height=0.62, left=left, color=pc, alpha=0.88)
        left += val

    fw = 'bold' if row['country'] == 'Indonesia' else 'normal'
    fc = '#E24B4A' if row['country'] == 'Indonesia' else TEXT_DIM
    ax_s3.text(-0.6, y, row['country'], ha='right', va='center',
               fontsize=8.5, fontweight=fw, color=fc)

    if row['country'] == 'Indonesia':
        ax_s3.barh(y, 110, height=0.78, left=0,
                   color='none', edgecolor='#E24B4A', lw=1.5, zorder=5)

# Pillar legend
for k, (lbl, pc) in enumerate(zip(PIL_LABELS, PIL_COLORS)):
    bw = 4.5
    ax_s3.barh(n3 + 1.5, bw, height=0.45, left=k * 8.5, color=pc, alpha=0.92)
    ax_s3.text(k * 8.5 + bw / 2, n3 + 1.5, lbl,
               ha='center', va='center', fontsize=7.5, color=TEXT)

ax_s3.text(55, n3 + 2.0, 'AI PILLAR DISTRIBUTION',
           ha='center', va='center', fontsize=12,
           fontweight='bold', color=TEXT_DIM, fontstyle='italic')

# ══════════════════════════════════════════
# SECTION 4 — RADAR × 3 + INSIGHT CARDS
# ══════════════════════════════════════════
gs4 = gridspec.GridSpecFromSubplotSpec(
    1, 4, subplot_spec=gs_main[3],
    width_ratios=[3, 3, 3, 2.6], wspace=0.12
)

def draw_radar(ax, values, color, fill_alpha=0.25, lw=2, ls='-'):
    N      = len(RADAR_LABELS)
    angles = np.linspace(0, 2*np.pi, N, endpoint=False).tolist()
    vals   = list(values) + [values[0]]
    a      = angles + [angles[0]]

    ax.set_facecolor(BG)
    ax.set_theta_offset(np.pi / 2)
    ax.set_theta_direction(-1)
    ax.set_ylim(0, 5)
    ax.set_xticks(angles)
    ax.set_xticklabels(RADAR_LABELS, fontsize=8.5, color=TEXT_DIM)
    ax.set_yticks([1, 2, 3, 4, 5])
    ax.set_yticklabels([])
    ax.grid(color=MUTED, lw=0.5, alpha=0.5)
    ax.spines['polar'].set_visible(False)
    ax.plot(a, vals, color=color, lw=lw, ls=ls)
    ax.fill(a, vals, color=color, alpha=fill_alpha)

radar_defs = [
    (idn_radar,  '#E24B4A', 'Indonesia',    '-'),
    (adv_radar,  '#378ADD', 'Negara Maju',  '-'),
    (ideal_radar,'#94A3B8', 'Kondisi Ideal','--'),
]

for ci, (vals, color, title, ls) in enumerate(radar_defs):
    ax_r = fig.add_subplot(gs4[ci], projection='polar')
    draw_radar(ax_r, vals, color, ls=ls)
    ax_r.set_title(title, fontsize=11, fontweight='bold', color=color, pad=16)

# Insight cards
ax_card = fig.add_subplot(gs4[3])
clean_ax(ax_card)
ax_card.set_xlim(0, 1)
ax_card.set_ylim(0, 1)

ax_card.text(0.5, 0.97, 'PROFIL MAHASISWA\nINDONESIA',
             ha='center', va='top', fontsize=9.5,
             fontweight='bold', color=TEXT_DIM)

insights = [
    ('AI Literacy',          f"{idn_radar[0]:.2f}/5", True,  '#34D399'),
    ('Tidak Takut AI',       f"{idn_radar[5]:.2f}/5", True,  '#34D399'),
    ('Kurang Percaya Diri',  f"{idn_radar[3]:.2f}/5", False, '#E24B4A'),
    ('Niat Pakai AI',        f"{idn_radar[4]:.2f}/5", True,  '#34D399'),
    ('Readiness',            f"{idn_radar[1]:.2f}/5", False, '#FBBF24'),
]

CH, CG = 0.13, 0.035
sy = 0.87
for k, (lbl, val, ok, col) in enumerate(insights):
    yb = sy - (k + 1) * (CH + CG)
    ax_card.add_patch(FancyBboxPatch((0.03, yb), 0.94, CH,
                                     boxstyle='round,pad=0.01',
                                     facecolor=PANEL_BG, edgecolor=col, lw=0.9))
    mark = 'v' if ok else 'x'
    ax_card.text(0.09, yb + CH/2, f"[{mark}] {lbl}",
                 va='center', fontsize=8.5, color=TEXT_DIM)
    ax_card.text(0.95, yb + CH/2, val,
                 va='center', ha='right', fontsize=9,
                 fontweight='bold', color=col)

# ══════════════════════════════════════════
# SECTION 5 — CTA + FOOTER
# ══════════════════════════════════════════
ax_cta = fig.add_subplot(gs_main[4])
clean_ax(ax_cta)

ax_cta.text(0.5, 0.88,
    '"Masalahnya bukan uang. Bukan talenta. Bukan internet."',
    transform=ax_cta.transAxes, ha='center', va='top',
    fontsize=16, fontweight='bold', color=TEXT, fontstyle='italic')

ax_cta.text(0.5, 0.60,
    'Gov. Strategy: 19 -> 39  =  proyeksi naik dari rank #39 ke #16 dunia   |   '
    'India (GDP < Indonesia) · Gov Strategy 55 = rank #12',
    transform=ax_cta.transAxes, ha='center', va='top',
    fontsize=9.5, color=ACCENT)

ax_cta.text(0.5, 0.22,
    'Tortoise Global AI Index 2024  ·  UNDP Human Development Report 2023  ·  '
    'World Bank Internet Penetration 2023  ·  FITPED Cross-National AI Education Survey 2024 (n=1,205)',
    transform=ax_cta.transAxes, ha='center', va='center',
    fontsize=7.5, color=MUTED)

# ══════════════════════════════════════════
# EXPORT
# ══════════════════════════════════════════
print("Rendering poster...")
plt.savefig('poster_ai_indonesia.png',
            dpi=150, bbox_inches='tight',
            facecolor=BG, edgecolor='none')
print("Saved: poster_ai_indonesia.png")

try:
    plt.savefig('poster_ai_indonesia_print.pdf',
                dpi=300, bbox_inches='tight',
                facecolor=BG, edgecolor='none', format='pdf')
    print("Saved: poster_ai_indonesia_print.pdf")
except Exception as e:
    print("PDF export skipped:", e)

print("Done!")
