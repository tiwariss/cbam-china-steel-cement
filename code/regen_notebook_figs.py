"""
Regenerate fig2, fig4, fig9 (previously notebook-only) without figure-number titles.
"""
import os as _os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import warnings
warnings.filterwarnings('ignore')

plt.rcParams.update({
    'figure.dpi': 150,
    'font.family': 'serif',
    'axes.spines.top': False,
    'axes.spines.right': False,
    'axes.grid': True,
    'grid.alpha': 0.3,
    'axes.titlesize': 12,
    'axes.labelsize': 10,
    'legend.fontsize': 9,
})
BLUE  = '#2166AC'
RED   = '#D6604D'
GREEN = '#4DAC26'
GREY  = '#636363'

_ROOT    = _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))
DATA_DIR = _os.path.join(_ROOT, 'resources', 'data')
OUT_DIR  = _os.path.join(_ROOT, 'output', 'figures')

# ── Load data ──────────────────────────────────────────────────────────────────
plant_df = pd.read_excel(
    f'{DATA_DIR}/Plant-level-data-Global-Iron-and-Steel-Tracker-March-2026-V1.xlsx',
    sheet_name='Plant data')
china_plants = plant_df[plant_df['Country/area'] == 'China'].copy()
china_ids = set(china_plants['GEM plant ID'])

bof_df = pd.read_excel(
    f'{DATA_DIR}/Steel-unit-data-Global-Iron-and-Steel-Tracker-March-2026-V1.xlsx',
    sheet_name='Basic oxygen furnaces')
china_bof = bof_df[bof_df['GEM plant ID'].isin(china_ids) &
                   (bof_df['Unit status'] == 'operating')].copy()
china_bof['cap'] = pd.to_numeric(china_bof['Current capacity (ttpa)'], errors='coerce').fillna(0)
china_bof = china_bof.merge(china_plants[['GEM plant ID', 'Subnational unit']],
                            on='GEM plant ID', how='left')

eaf_df = pd.read_excel(
    f'{DATA_DIR}/Steel-unit-data-Global-Iron-and-Steel-Tracker-March-2026-V1.xlsx',
    sheet_name='Electric arc furnaces')
china_eaf = eaf_df[eaf_df['GEM plant ID'].isin(china_ids) &
                   (eaf_df['Unit status'] == 'operating')].copy()
china_eaf['cap'] = pd.to_numeric(china_eaf['Current capacity (ttpa)'], errors='coerce').fillna(0)
china_eaf = china_eaf.merge(china_plants[['GEM plant ID', 'Subnational unit']],
                            on='GEM plant ID', how='left')

pw_df = pd.read_excel(
    f'{DATA_DIR}/Global-Integrated-Power-March-2026-II.xlsx',
    sheet_name='Power facilities')
china_pw = pw_df[(pw_df['Country/area'] == 'China') &
                 (pw_df['Status'] == 'operating')].copy()
china_pw['cap_mw'] = pd.to_numeric(china_pw['Capacity (MW)'], errors='coerce').fillna(0)

total_bof = china_bof['cap'].sum() / 1000
total_eaf = china_eaf['cap'].sum() / 1000

print(f'BOF: {total_bof:.1f} Mtpa  EAF: {total_eaf:.1f} Mtpa')


# ══════════════════════════════════════════════════════════════════════════════
# fig2 · Top 15 Provinces by Steel Capacity
# ══════════════════════════════════════════════════════════════════════════════
bof_prov = china_bof.groupby('Subnational unit')['cap'].sum().rename('BOF') / 1000
eaf_prov = china_eaf.groupby('Subnational unit')['cap'].sum().rename('EAF') / 1000
prov_df  = pd.concat([bof_prov, eaf_prov], axis=1).fillna(0)
prov_df['Total'] = prov_df.sum(axis=1)
prov_df = prov_df.sort_values('Total', ascending=True).tail(15)

fig, ax = plt.subplots(figsize=(10, 7))
y = np.arange(len(prov_df))
h = 0.5
ax.barh(y, prov_df['BOF'], height=h, color=RED,  label='BF-BOF', alpha=0.9)
ax.barh(y, prov_df['EAF'], height=h, color=BLUE, label='EAF',
        left=prov_df['BOF'], alpha=0.9)
for i, (_, row) in enumerate(prov_df.iterrows()):
    ax.text(row['Total'] + 2, i, f"{row['Total']:.0f}", va='center', fontsize=8.5, color=GREY)
ax.set_yticks(y)
ax.set_yticklabels(prov_df.index, fontsize=9)
ax.set_xlabel('Operating Capacity (Mtpa)')
ax.set_title('Top 15 Provinces by Steel Capacity — BF-BOF vs EAF\n(China, GEM March 2026)',
             fontsize=12, fontweight='bold', pad=10)
ax.legend(loc='lower right')
ax.set_xlim(0, prov_df['Total'].max() * 1.12)
if 'Hebei' in prov_df.index:
    hebei_idx = list(prov_df.index).index('Hebei')
    ax.annotate('Hebei = 23.9%\nof national BOF',
                xy=(prov_df.loc['Hebei', 'BOF'] / 2, hebei_idx),
                xytext=(120, hebei_idx - 2),
                arrowprops=dict(arrowstyle='->', color='black', lw=1),
                fontsize=8.5, color='black',
                bbox=dict(boxstyle='round,pad=0.3', fc='#FFF3CD', ec='#FFC107', alpha=0.9))
plt.tight_layout()
plt.savefig(f'{OUT_DIR}/fig2_steel_provinces.png', bbox_inches='tight', dpi=150)
plt.close()
print('Saved fig2')


# ══════════════════════════════════════════════════════════════════════════════
# fig4 · CBAM Liability Heatmap  (EAF = 0.10 Scope 1 CBAM-applicable)
# ══════════════════════════════════════════════════════════════════════════════
EF = {'BF-BOF Steel': 2.10, 'EAF Steel': 0.10, 'Cement': 0.627}

cn_price = np.linspace(0, 80, 100)
eu_price = np.linspace(40, 95, 100)
X, Y = np.meshgrid(cn_price, eu_price)

Z_bf     = np.maximum(0, EF['BF-BOF Steel'] * (Y - X))
Z_cement = np.maximum(0, EF['Cement']       * (Y - X))
Z_eaf    = np.maximum(0, EF['EAF Steel']    * (Y - X))

fig, axs = plt.subplots(2, 2, figsize=(14, 12))
plt.subplots_adjust(wspace=0.25, hspace=0.3)

cf1 = axs[0, 0].contourf(X, Y, Z_bf, levels=50, cmap='RdYlGn_r')
fig.colorbar(cf1, ax=axs[0, 0], label='CBAM Liability (EUR/t)')
axs[0, 0].contour(X, Y, Z_bf, levels=[0], colors='black', linewidths=2)
axs[0, 0].set_title('BF-BOF Steel\n(EF = 2.10 tCO$_2$/t)', fontweight='bold')

cf2 = axs[0, 1].contourf(X, Y, Z_cement, levels=50, cmap='RdYlGn_r')
fig.colorbar(cf2, ax=axs[0, 1], label='CBAM Liability (EUR/t)')
axs[0, 1].contour(X, Y, Z_cement, levels=[0], colors='black', linewidths=2)
axs[0, 1].set_title('Cement\n(EF = 0.627 tCO$_2$/t)', fontweight='bold')

cf3 = axs[1, 0].contourf(X, Y, Z_eaf, levels=50, cmap='RdYlGn_r')
fig.colorbar(cf3, ax=axs[1, 0], label='CBAM Liability (EUR/t)')
axs[1, 0].contour(X, Y, Z_eaf, levels=[0], colors='black', linewidths=2)
axs[1, 0].set_title('EAF Steel\n(EF = 0.10 tCO$_2$/t, Scope 1 only)', fontweight='bold')

axs[1, 1].axis('off')
axs[1, 1].text(0.5, 0.5,
               'Note: Color scales are independent\nto show gradients.\n\n'
               'Maximum per-tonne liability:\n'
               'BF-BOF ≈ 178 EUR/t\n'
               'Cement ≈ 53 EUR/t\n'
               'EAF ≈ 8.5 EUR/t (Scope 1 only)',
               ha='center', va='center', fontsize=13, style='italic',
               bbox=dict(facecolor='#f8f9fa', alpha=0.9,
                         edgecolor='#dee2e6', boxstyle='round,pad=1'))

for ax in [axs[0, 0], axs[0, 1], axs[1, 0]]:
    ax.set_xlabel('CN-ETS Price (EUR/tCO$_2$)')
    ax.set_ylabel('EU ETS Price (EUR/tCO$_2$)')
    ax.grid(alpha=0.3)
    ax.annotate('Current\n(CN=13, EU=65)', xy=(13, 65), xytext=(35, 58),
                arrowprops=dict(facecolor='red', width=1.5, headwidth=8),
                color='red', fontweight='bold', ha='center')
    ax.annotate('High EU\n(CN=13, EU=80)', xy=(13, 80), xytext=(45, 88),
                arrowprops=dict(facecolor='darkred', width=1.5, headwidth=8),
                color='darkred', fontweight='bold', ha='center')
    ax.plot(13, 65, 'ro', markersize=10)
    ax.plot(13, 80, 'r^', markersize=10)

plt.savefig(f'{OUT_DIR}/fig4_cbam_heatmap.png', dpi=300, bbox_inches='tight')
plt.close()
print('Saved fig4')


# ══════════════════════════════════════════════════════════════════════════════
# fig9 · China Power Mix
# ══════════════════════════════════════════════════════════════════════════════
type_cap = china_pw.groupby('Type')['cap_mw'].sum().sort_values(ascending=False)
total_pw = type_cap.sum()
clean_labels = {
    'coal': 'Coal', 'utility-scale solar': 'Solar (utility)', 'wind': 'Wind',
    'hydropower': 'Hydropower', 'oil/gas': 'Oil & Gas', 'nuclear': 'Nuclear',
    'bioenergy': 'Bioenergy', 'geothermal': 'Geothermal',
    'distributed solar': 'Solar (distributed)', 'offshore wind': 'Offshore Wind',
}
type_cap.index = [clean_labels.get(i, i) for i in type_cap.index]
type_cap_gw = type_cap / 1000

fig, axes = plt.subplots(1, 2, figsize=(13, 5))

ax = axes[0]
top8 = type_cap_gw.head(8)
other = type_cap_gw[8:].sum()
plot_vals   = list(top8.values) + [other]
plot_labels = list(top8.index) + ['Other']
palette = ['#636363', '#FDCC8A', '#7FCDBB', '#225EA8', '#C7E9B4',
           '#F03B20', '#74C476', '#FD8D3C', '#BDBDBD']
total_vals = sum(plot_vals)
# Only bake labels into slices >= 5% — small slices (Bioenergy, Geothermal, etc.) go to legend
pie_labels = [l if (v / total_vals * 100 >= 5) else '' for l, v in zip(plot_labels, plot_vals)]
wedges, texts, autotexts = ax.pie(
    plot_vals, labels=pie_labels, colors=palette[:len(plot_vals)],
    autopct=lambda p: f'{p:.1f}%' if p >= 5 else '',
    startangle=90, wedgeprops=dict(width=0.6),
    textprops={'fontsize': 8.5}, pctdistance=0.78)
# Legend for small slices
small_idx = [j for j, v in enumerate(plot_vals) if v / total_vals * 100 < 5]
if small_idx:
    ax.legend([wedges[j] for j in small_idx],
              [f'{plot_labels[j]} ({plot_vals[j]/total_vals*100:.1f}%)' for j in small_idx],
              loc='lower left', fontsize=7.5, framealpha=0.8)
ax.text(0, 0, f'{total_pw/1e6:.2f}\nTW\ntotal', ha='center', va='center',
        fontsize=9, fontweight='bold', color=GREY)
ax.set_title(f'China Operating Power Mix\n(GEM March 2026, {total_pw/1000:.0f} GW)',
             fontsize=11, fontweight='bold')

ax2 = axes[1]
y = np.arange(len(type_cap_gw.head(8)))
bar_colors = ['#636363' if 'Coal' in l else
              ('#4575B4' if l in ('Hydropower', 'Wind', 'Solar (utility)', 'Nuclear', 'Geothermal') else '#FDAE61')
              for l in type_cap_gw.head(8).index]
bars = ax2.barh(y, type_cap_gw.head(8).values, color=bar_colors, edgecolor='white')
for b, v in zip(bars, type_cap_gw.head(8).values):
    ax2.text(v + 5, b.get_y() + b.get_height() / 2,
             f'{v:.0f} GW ({100*v*1000/total_pw:.1f}%)', va='center', fontsize=8.5)
ax2.set_yticks(y)
ax2.set_yticklabels(type_cap_gw.head(8).index, fontsize=9.5)
ax2.set_xlabel('Operating Capacity (GW)')
ax2.set_title('Power Capacity by Type\n(GEM March 2026)',
              fontsize=11, fontweight='bold')
ax2.text(0.98, 0.02,
         'National grid EF: 0.581 kgCO₂/kWh (MEE 2023)\n'
         'EAF total intensity ref. only — Scope 2 excluded from CBAM',
         transform=ax2.transAxes, ha='right', va='bottom',
         fontsize=7.5, color=GREY,
         bbox=dict(boxstyle='round', fc='white', ec=GREY, alpha=0.7))

plt.suptitle('China Power Mix — Grid Emission Factor Basis',
             fontsize=12, fontweight='bold')
plt.tight_layout()
plt.savefig(f'{OUT_DIR}/fig9_power_mix.png', bbox_inches='tight', dpi=150)
plt.close()
print('Saved fig9')

print('\nDone — fig2, fig4, fig9 regenerated in output/figures/')
