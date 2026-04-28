### Radar Chart — FITPED Raw Data (Per-Country)
# Ganti SELURUH section "Radar Chart" yang lama dengan cell-cell ini.
# df_fp lama (agregat) tidak dipakai lagi di section ini.

# ── CELL 1: Load raw FITPED ──────────────────────────────────────────────────

df_raw = pd.read_csv(
    "https://drive.google.com/uc?id=1KKdZTPQgepgI5YcL7AN3Pf-BANEHVU0Y"
)

print(f"Raw FITPED: {df_raw.shape[0]} responden × {df_raw.shape[1]} kolom")
print(f"Distribusi negara:\n{df_raw['Country'].value_counts().to_string()}")

# ── CELL 2: Compute per-country construct means ───────────────────────────────

CONSTRUCTS = {
    'AI Literacy'         : ['L1','L2','L3','L4','L5'],
    'AI Readiness'        : ['RE1','RE2','RE3','RE4','RE5','RE6'],
    'Relevance of AI'     : ['R1','R2','R3','R4','R5','R6'],
    'Career Motivation'   : ['CM1','CM2','CM3','CM4'],
    'Confidence'          : ['C1','C2','C3','C4','C5'],
    'Social Goods'        : ['SG1','SG2','SG3','SG4','SG5'],
    'Intrinsic Motivation': ['IM1','IM2','IM3','IM4'],
    'Satisfaction'        : ['S1','S2','S3','S4','S5'],
    'AI Anxiety'          : ['A1','A2','A3','A4','A5'],
    'Behavioural Intention': ['BI1','BI2','BI3','BI4','BI5'],
}

COUNTRY_NAMES = {
    'SK': 'Slovakia', 'PL': 'Poland', 'CZ': 'Czech Republic',
    'ID': 'Indonesia', 'LT': 'Lithuania',
    'TR': 'Turkey',    'FR': 'France',  'UA': 'Ukraine',
}

rows = []
for code, grp in df_raw.groupby('Country'):
    row = {'code': code, 'country': COUNTRY_NAMES.get(code, code), 'n': len(grp)}
    for construct, cols in CONSTRUCTS.items():
        valid = [c for c in cols if c in grp.columns]
        vals  = grp[valid].replace(0, pd.NA)           # 0 = N/A di dataset ini
        row[construct] = vals.mean(skipna=True).mean()
    rows.append(row)

df_country = pd.DataFrame(rows).set_index('country')

# Pakai hanya negara dengan n >= 30 (representatif)
df_country = df_country[df_country['n'] >= 30].copy()

# Invert AI Anxiety: rendah di data = bagus → di radar, tinggi = lebih baik
df_country['Low Anxiety'] = 6 - df_country['AI Anxiety']   # invert: 5 - val + 1

print("\nNegara eligible (n ≥ 30):")
print(df_country[['n']].sort_values('n', ascending=False))
print("\nMean konstruk utama:")
SHOW_COLS = ['AI Literacy','AI Readiness','Confidence',
             'Career Motivation','Behavioural Intention','Low Anxiety']
print(df_country[SHOW_COLS].round(2).to_string())

# ── CELL 3: Figur 1 — highlight 3 angka kunci Indonesia ─────────────────────
# (Menggantikan panel kiri lama yang pakai df_fp agregat)

AMBER_C = '#E8A838'

idn_row = df_country.loc['Indonesia']
highlight_vals = [
    ('AI Literacy',          idn_row['AI Literacy'],           SING),
    ('AI Anxiety\n(skor raw)', idn_row['AI Anxiety'],          IDN),   # tampilkan raw, beri ket
    ('Confidence',           idn_row['Confidence'],            AMBER_C),
]

fig, axes = plt.subplots(1, 2, figsize=(15, 6))

ax = axes[0]
ax.axis('off')
ax.set_xlim(0, 3)
ax.set_ylim(0, 1)
ax.set_facecolor('#FAFAF8')

for i, (label, val, color) in enumerate(highlight_vals):
    xc = i * 1.02 + 0.5
    ax.text(xc, 0.72, f'{val:.2f}', ha='center', va='center',
            fontsize=44, fontweight='bold', color=color)
    ax.text(xc, 0.48, label, ha='center', va='center',
            fontsize=12, fontweight='bold', color=DARK, linespacing=1.4)
    bar_len = (val / 5) * 0.7
    ax.barh(0.12, bar_len, left=xc - 0.35, height=0.06, color=color, alpha=0.85)
    ax.barh(0.12, 0.70,    left=xc - 0.35, height=0.06, color=color, alpha=0.12)

ax.annotate('', xy=(1.12, 0.48), xytext=(0.98, 0.48),
            arrowprops=dict(arrowstyle='->', color='#aaa', lw=1.0))
ax.annotate('', xy=(2.14, 0.48), xytext=(2.00, 0.48),
            arrowprops=dict(arrowstyle='->', color='#aaa', lw=1.0))

ax.text(1.5, 0.04,
        f'Indonesia n = {int(idn_row["n"])} | FITPED raw data 2022–2024',
        ha='center', fontsize=8.5, color='#888', style='italic')

# ── CELL 3 lanjutan: Construct bar (panel kanan) — per construct Indonesia ──

def fp_clr(c):
    if c == 'AI Literacy':                                return SING
    if c == 'AI Anxiety':                                 return IDN
    if c in ('Confidence','Intrinsic Motivation','Satisfaction'): return AMBER_C
    if c == 'Behavioural Intention':                      return DARK
    return MUTED

ORDER = ['AI Literacy','AI Readiness','Relevance of AI','Social Goods',
         'Behavioural Intention','Career Motivation','Confidence',
         'Intrinsic Motivation','Satisfaction','AI Anxiety']

idn_means = pd.Series({c: idn_row[c] for c in ORDER})
bar_colors_fp = [fp_clr(c) for c in idn_means.index]

bars_fp = axes[1].barh(idn_means.index, idn_means.values,
                       color=bar_colors_fp, height=0.65, zorder=3)
for bar, val in zip(bars_fp, idn_means.values):
    axes[1].text(bar.get_width() + 0.01, bar.get_y() + bar.get_height()/2,
                 f'{val:.2f}', va='center', ha='left', fontsize=10)

axes[1].axvline(idn_means['Behavioural Intention'], color=DARK, lw=1.2, ls='--', alpha=0.5,
                label=f'Behavioural Intention ({idn_means["Behavioural Intention"]:.2f})')
axes[1].axvline(idn_means['AI Literacy'], color=SING, lw=1.0, ls=':', alpha=0.4,
                label=f'AI Literacy ({idn_means["AI Literacy"]:.2f})')
axes[1].set_xlim(2.2, 4.65)
axes[1].set_xlabel('Mean Score (1–5)')
axes[1].set_title(f'FITPED Constructs — Indonesia (n={int(idn_row["n"])})', fontsize=11)

leg_fp = [
    mpatches.Patch(color=SING,    label='Awareness tinggi (AI Literacy)'),
    mpatches.Patch(color=AMBER_C, label='Gap: confidence & motivation'),
    mpatches.Patch(color=DARK,    label='Target: Behavioural Intention'),
    mpatches.Patch(color=IDN,     label='AI Anxiety (rendah = tidak takut)'),
    mpatches.Patch(color=MUTED,   label='Konstruk lain'),
]
axes[1].legend(handles=leg_fp, fontsize=8.5, bbox_to_anchor=(1, 0))
axes[1].grid(axis='y', alpha=0)

plt.tight_layout()
plt.savefig('beat4_fitped.png', dpi=150, bbox_inches='tight')
plt.show()

# ── CELL 4: Radar helper & per-country data prep ────────────────────────────

RADAR_AXES   = ['AI Literacy','AI Readiness','Confidence',
                'Career Motivation','Behavioural Intention','Low Anxiety']
RADAR_LABELS = ['AI\nLiteracy','AI\nReadiness','Confidence',
                'Career\nMotiv.','Intent','Low\nAnxiety']

# Pilih negara untuk perbandingan (n ≥ 30)
EUR_COUNTRIES = [c for c in ['Slovakia','Poland','Czech Republic','Lithuania']
                 if c in df_country.index]

# Rata-rata Eropa (semua negara Eropa eligible)
eur_vals_dict = df_country.loc[EUR_COUNTRIES, RADAR_AXES].mean()
idn_vals_list = [idn_row[ax] for ax in RADAR_AXES]
eur_vals_list = [eur_vals_dict[ax] for ax in RADAR_AXES]
ideal_vals    = [4.3, 4.2, 4.2, 4.1, 4.2, 4.0]   # target kondisi ideal

def draw_radar(ax, values, color, fill_alpha=0.22, lw=2.0, ls='-', label=None):
    N      = len(values)
    angles = np.linspace(0, 2*np.pi, N, endpoint=False).tolist()
    v      = values + [values[0]]
    a      = angles + [angles[0]]
    ax.set_theta_offset(np.pi / 2)
    ax.set_theta_direction(-1)
    ax.set_ylim(1, 5)
    ax.set_yticks([2, 3, 4, 5])
    ax.set_yticklabels(['2','3','4','5'], color='#aaa', fontsize=7)
    ax.grid(color='#ddd', linewidth=0.5, alpha=0.6)
    ax.plot(a, v, color=color, lw=lw, ls=ls, zorder=3, label=label)
    ax.fill(a, v, color=color, alpha=fill_alpha, zorder=2)
    return angles

print("Radar data siap:")
print(f"  Indonesia          : {[f'{v:.2f}' for v in idn_vals_list]}")
print(f"  European avg       : {[f'{v:.2f}' for v in eur_vals_list]}")
print(f"  Ideal              : {ideal_vals}")
print(f"  Axes               : {RADAR_AXES}")

# ── CELL 5: Figur 2 — Overlay radar (semua negara) ──────────────────────────

COUNTRY_COLORS = {
    'Indonesia'     : IDN,
    'Slovakia'      : SING,
    'Poland'        : BRAZ,
    'Czech Republic': AMBER,
    'Lithuania'     : '#A78BFA',
}

fig, axes = plt.subplots(1, 2, subplot_kw=dict(polar=True),
                         figsize=(15, 6))
fig.patch.set_facecolor('#FAFAF8')

# Panel kiri: overlay semua negara
for country in ['Indonesia'] + EUR_COUNTRIES:
    if country not in df_country.index:
        continue
    vals  = [df_country.loc[country, ax] for ax in RADAR_AXES]
    col   = COUNTRY_COLORS.get(country, MUTED)
    lw    = 2.5 if country == 'Indonesia' else 1.5
    alpha = 0.30 if country == 'Indonesia' else 0.12
    angles = draw_radar(axes[0], vals, col, fill_alpha=alpha, lw=lw,
                        label=f"{country} (n={int(df_country.loc[country,'n'])})")

axes[0].set_xticks(angles)
axes[0].set_xticklabels(RADAR_LABELS, fontsize=9, linespacing=1.3)
axes[0].set_title('Semua Negara — Overlay', fontsize=11, fontweight='bold', pad=18, y=1.12)
axes[0].legend(loc='lower left', bbox_to_anchor=(-0.15, -0.18),
               fontsize=8.5, framealpha=0.9)

# Panel kanan: Indonesia vs European Average
angles = draw_radar(axes[1], eur_vals_list, SING, fill_alpha=0.15, lw=1.8, ls='--',
                    label=f"European Avg ({', '.join(EUR_COUNTRIES[:2])}...)")
draw_radar(axes[1], idn_vals_list, IDN, fill_alpha=0.30, lw=2.5,
           label=f"Indonesia (n={int(idn_row['n'])})")

axes[1].set_xticks(angles)
axes[1].set_xticklabels(RADAR_LABELS, fontsize=9, linespacing=1.3)
axes[1].set_title('Indonesia vs European Average', fontsize=11, fontweight='bold', pad=18, y=1.12)
axes[1].legend(loc='lower left', bbox_to_anchor=(-0.15, -0.18),
               fontsize=8.5, framealpha=0.9)

fig.suptitle('AI Literacy & Readiness — Student Comparison by Country\n'
             'FITPED Raw Data 2022–2024 (total n=1,205)',
             fontsize=13, fontweight='bold', y=1.02)

plt.tight_layout()
plt.savefig('beat4b_radar_overlay.png', dpi=150, bbox_inches='tight')
plt.show()

# ── CELL 6: Figur 3 — 3 panel radar untuk poster ────────────────────────────
# Indonesia | European Average | Kondisi Ideal

fig2, axes2 = plt.subplots(1, 3, subplot_kw=dict(polar=True),
                            figsize=(18, 6))
fig2.patch.set_facecolor('#FAFAF8')

radar_panels = [
    (f'Indonesia\n(n={int(idn_row["n"])})', idn_vals_list, IDN,    0.28),
    (f"European Avg\n({', '.join(EUR_COUNTRIES[:2])}...)", eur_vals_list, SING, 0.18),
    ('Kondisi Ideal\n(target)',              ideal_vals,    MUTED,  0.12),
]

for ax2, (title, vals, color, alpha) in zip(axes2, radar_panels):
    angles = draw_radar(ax2, vals, color, fill_alpha=alpha, lw=2.2)
    ax2.set_xticks(angles)
    ax2.set_xticklabels(RADAR_LABELS, fontsize=9, linespacing=1.3)
    ax2.set_title(title, color=color, fontsize=11, fontweight='bold', pad=18, y=1.12)
    # Annotate nilai di vertex
    for angle, val in zip(angles, vals):
        ax2.annotate(f'{val:.2f}', xy=(angle, val),
                     xytext=(angle, val + 0.22),
                     color=color, fontsize=7.5, fontweight='bold',
                     ha='center', va='center')

fig2.suptitle('Kesiapan Mahasiswa Menghadapi AI — Perbandingan Internasional\n'
              'FITPED Cross-National Survey 2022–2024',
              fontsize=13, fontweight='bold', y=1.03)

plt.tight_layout()
plt.savefig('beat4c_radar_3panel.png', dpi=150, bbox_inches='tight')
plt.show()
print("Saved: beat4c_radar_3panel.png  ← siap masuk poster")

# ── CELL 7: Gap summary ──────────────────────────────────────────────────────

print("\n" + "="*58)
print("GAP SUMMARY — Indonesia vs European Average")
print("="*58)
for ax_name in RADAR_AXES:
    idn_v = idn_row[ax_name]
    eur_v = eur_vals_dict[ax_name]
    gap   = idn_v - eur_v
    flag  = "  ← GAP" if gap < -0.2 else ("  ← UNGGUL" if gap > 0.2 else "")
    print(f"  {ax_name:<25} ID={idn_v:.2f}  EU={eur_v:.2f}  "
          f"{'▲' if gap>=0 else '▼'}{abs(gap):.2f}{flag}")

print(f"\nAngka poster (Indonesia):")
print(f"  AI Literacy       : {idn_row['AI Literacy']:.2f}/5  → TAHU soal AI")
print(f"  AI Anxiety (raw)  : {idn_row['AI Anxiety']:.2f}/5  → TIDAK TAKUT (skor rendah = bagus)")
print(f"  Confidence        : {idn_row['Confidence']:.2f}/5  → TIDAK PERCAYA DIRI")
print(f"  Behavioural Intent: {idn_row['Behavioural Intention']:.2f}/5  → NIAT TINGGI")