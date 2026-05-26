import json, os
_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def md(source):
    return {"cell_type": "markdown", "metadata": {}, "source": source, "id": ""}

def code(source):
    return {"cell_type": "code", "execution_count": None, "metadata": {},
            "outputs": [], "source": source, "id": ""}

cells = []

# ── TITLE ──────────────────────────────────────────────────────────────────────
cells.append(md("""# EU CBAM and China's Strategic Response — Data Analysis
## IPEN 6100 / CNGF 5100 · HKUST(GZ) Spring 2026
### Tang Qian · Sirawit Tangchitwatthanakon · Liu Xianghui

This notebook operationalises the paper's analytical framework using plant-level data from the
**Global Energy Monitor (GEM)** Iron & Steel Tracker (March 2026) and Cement & Concrete Tracker
(July 2025), supplemented by the GEM Global Integrated Power Tracker (March 2026).

All figures are original analyses produced for Sections 3.2, 4.4, 4.5, and 4.6 of the paper.

---
"""))

# ── SETUP ─────────────────────────────────────────────────────────────────────
cells.append(md("## 0 · Setup & Imports"))

cells.append(code("""\
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import matplotlib.ticker as mticker
from matplotlib.gridspec import GridSpec
import seaborn as sns
import warnings
warnings.filterwarnings('ignore')

# ── Style ──────────────────────────────────────────────────────────────────────
plt.rcParams.update({
    'figure.dpi': 130,
    'font.family': 'serif',
    'axes.spines.top': False,
    'axes.spines.right': False,
    'axes.grid': True,
    'grid.alpha': 0.3,
    'axes.titlesize': 12,
    'axes.labelsize': 10,
    'legend.fontsize': 9,
})
BLUE   = '#2166AC'
RED    = '#D6604D'
GREEN  = '#4DAC26'
ORANGE = '#F4A582'
GREY   = '#636363'
LIGHT  = '#F7F7F7'

DATA_DIR = '../resources/data'
FIG_DIR  = '../output/figures'
print('Setup complete ✓')
"""))

# ── LOAD DATA ─────────────────────────────────────────────────────────────────
cells.append(md("## 1 · Load GEM Data"))

cells.append(code("""\
# ── Steel: plant-level ─────────────────────────────────────────────────────────
plant_df = pd.read_excel(
    f'{DATA_DIR}/Plant-level-data-Global-Iron-and-Steel-Tracker-March-2026-V1.xlsx',
    sheet_name='Plant data')
china_plants = plant_df[plant_df['Country/area'] == 'China'].copy()
china_ids    = set(china_plants['GEM plant ID'])
print(f'China steel plants: {len(china_plants)}')

# ── Steel: BOF units ──────────────────────────────────────────────────────────
bof_df = pd.read_excel(
    f'{DATA_DIR}/Steel-unit-data-Global-Iron-and-Steel-Tracker-March-2026-V1.xlsx',
    sheet_name='Basic oxygen furnaces')
china_bof = bof_df[bof_df['GEM plant ID'].isin(china_ids) &
                   (bof_df['Unit status'] == 'operating')].copy()
china_bof['cap'] = pd.to_numeric(china_bof['Current capacity (ttpa)'], errors='coerce').fillna(0)
china_bof = china_bof.merge(china_plants[['GEM plant ID','Subnational unit','SOE status']],
                            on='GEM plant ID', how='left')

# ── Steel: EAF units ──────────────────────────────────────────────────────────
eaf_df = pd.read_excel(
    f'{DATA_DIR}/Steel-unit-data-Global-Iron-and-Steel-Tracker-March-2026-V1.xlsx',
    sheet_name='Electric arc furnaces')
china_eaf = eaf_df[eaf_df['GEM plant ID'].isin(china_ids) &
                   (eaf_df['Unit status'] == 'operating')].copy()
china_eaf['cap'] = pd.to_numeric(china_eaf['Current capacity (ttpa)'], errors='coerce').fillna(0)
china_eaf = china_eaf.merge(china_plants[['GEM plant ID','Subnational unit','SOE status']],
                            on='GEM plant ID', how='left')

# ── Steel: BF units ───────────────────────────────────────────────────────────
bf_df = pd.read_excel(
    f'{DATA_DIR}/Iron-unit-data-Global-Iron-and-Steel-Tracker-March-2026-V1.xlsx',
    sheet_name='Blast furnaces')
china_bf = bf_df[bf_df['GEM plant ID'].isin(china_ids) &
                 (bf_df['Unit status'] == 'operating')].copy()
china_bf['cap'] = pd.to_numeric(china_bf['Current capacity (ttpa)'], errors='coerce').fillna(0)

# ── Cement ────────────────────────────────────────────────────────────────────
cem_df = pd.read_excel(
    f'{DATA_DIR}/Global-Cement-and-Concrete-Tracker_July-2025.xlsx',
    sheet_name='Plant Data')
china_cem = cem_df[(cem_df['Country/Area'] == 'China') &
                   (cem_df['Operating status'] == 'operating')].copy()
china_cem['cem_cap']  = pd.to_numeric(
    china_cem['Cement Capacity (millions metric tonnes per annum)'], errors='coerce').fillna(0)
china_cem['clin_cap'] = pd.to_numeric(
    china_cem['Clinker Capacity (millions metric tonnes per annum)'], errors='coerce').fillna(0)

# ── Power ─────────────────────────────────────────────────────────────────────
pw_df = pd.read_excel(
    f'{DATA_DIR}/Global-Integrated-Power-March-2026-II.xlsx',
    sheet_name='Power facilities')
china_pw = pw_df[(pw_df['Country/area'] == 'China') &
                 (pw_df['Status'] == 'operating')].copy()
china_pw['cap_mw'] = pd.to_numeric(china_pw['Capacity (MW)'], errors='coerce').fillna(0)

# ── Summary ───────────────────────────────────────────────────────────────────
total_bof = china_bof['cap'].sum() / 1000   # Mtpa
total_eaf = china_eaf['cap'].sum() / 1000
total_bf  = china_bf['cap'].sum()  / 1000
total_cem = china_cem['cem_cap'].sum()
total_clin= china_cem['clin_cap'].sum()
clinker_ratio = total_clin / total_cem

print(f'BOF capacity : {total_bof:.1f} Mtpa  ({100*total_bof/(total_bof+total_eaf):.1f}%)')
print(f'EAF capacity : {total_eaf:.1f} Mtpa  ({100*total_eaf/(total_bof+total_eaf):.1f}%)')
print(f'BF  capacity : {total_bf:.1f} Mtpa  ({len(china_bf)} units)')
print(f'Cement cap   : {total_cem:.0f} Mt/yr')
print(f'Clinker cap  : {total_clin:.1f} Mt/yr')
print(f'Clinker ratio: {clinker_ratio:.3f}')
"""))

# ── SECTION 2: STEEL ──────────────────────────────────────────────────────────
cells.append(md("""---
## 2 · China Steel Sector Analysis
"""))

cells.append(md("### 2.1 Technology mix — BOF vs EAF capacity"))

cells.append(code("""\
fig, axes = plt.subplots(1, 2, figsize=(12, 5))

# ── Donut chart ───────────────────────────────────────────────────────────────
ax = axes[0]
total_steel = total_bof + total_eaf
sizes  = [total_bof, total_eaf]
labels = [f'BF-BOF\\n{total_bof:.1f} Mtpa\\n({100*total_bof/total_steel:.1f}%)',
          f'EAF\\n{total_eaf:.1f} Mtpa\\n({100*total_eaf/total_steel:.1f}%)']
colors = [RED, BLUE]
wedges, texts = ax.pie(sizes, labels=labels, colors=colors,
                       startangle=90, wedgeprops=dict(width=0.55),
                       textprops={'fontsize': 10})
ax.text(0, 0, f'{total_steel:.0f}\\nMtpa\\ntotal', ha='center', va='center',
        fontsize=10, fontweight='bold', color=GREY)
ax.set_title('China Operating Crude Steel Capacity\\nby Production Route (GEM March 2026)', pad=12)

# ── BF unit count bar ─────────────────────────────────────────────────────────
ax2 = axes[1]
categories = ['BF-BOF\\nunits\\n(583)', 'EAF\\nunits\\n(270)', 'BF\\nunits\\n(599)']
unit_caps   = [china_bof['cap'].sum()/1e3, china_eaf['cap'].sum()/1e3, china_bf['cap'].sum()/1e3]
bar_colors  = [RED, BLUE, '#762A83']
bars = ax2.bar(categories, unit_caps, color=bar_colors, width=0.55, edgecolor='white', linewidth=1.2)
for b, v in zip(bars, unit_caps):
    ax2.text(b.get_x() + b.get_width()/2, b.get_height() + 8,
             f'{v:.0f} Mtpa', ha='center', va='bottom', fontsize=9, fontweight='bold')
ax2.set_ylabel('Operating Capacity (Mtpa)')
ax2.set_title('Operating Unit Count & Aggregate Capacity\\n(China, GEM March 2026)', pad=12)
ax2.set_ylim(0, max(unit_caps)*1.15)

plt.suptitle('China Steel Sector — Technology Structure', fontsize=13, fontweight='bold', y=1.01)
plt.tight_layout()
plt.savefig(f'{FIG_DIR}/fig1_steel_technology_mix.png', bbox_inches='tight', dpi=150)
plt.show()
"""))

cells.append(md("### 2.2 Provincial distribution — BOF vs EAF"))

cells.append(code("""\
# ── Provincial aggregation ────────────────────────────────────────────────────
bof_prov = china_bof.groupby('Subnational unit')['cap'].sum().rename('BOF') / 1000
eaf_prov = china_eaf.groupby('Subnational unit')['cap'].sum().rename('EAF') / 1000
prov_df  = pd.concat([bof_prov, eaf_prov], axis=1).fillna(0)
prov_df['Total'] = prov_df.sum(axis=1)
prov_df = prov_df.sort_values('Total', ascending=True).tail(15)

fig, ax = plt.subplots(figsize=(10, 7))
y   = np.arange(len(prov_df))
h   = 0.5
ax.barh(y, prov_df['BOF'], height=h, color=RED,  label='BF-BOF', alpha=0.9)
ax.barh(y, prov_df['EAF'], height=h, color=BLUE, label='EAF',
        left=prov_df['BOF'], alpha=0.9)

for i, (_, row) in enumerate(prov_df.iterrows()):
    ax.text(row['Total'] + 2, i, f"{row['Total']:.0f}", va='center', fontsize=8.5, color=GREY)

ax.set_yticks(y)
ax.set_yticklabels(prov_df.index, fontsize=9)
ax.set_xlabel('Operating Capacity (Mtpa)')
ax.set_title('Top 15 Provinces by Steel Capacity — BF-BOF vs EAF\\n(China, GEM March 2026)',
             fontsize=12, fontweight='bold', pad=10)
ax.legend(loc='lower right')
ax.set_xlim(0, prov_df['Total'].max() * 1.12)

# Hebei annotation
hebei_idx = list(prov_df.index).index('Hebei')
ax.annotate('Hebei = 23.9%\\nof national BOF',
            xy=(prov_df.loc['Hebei','BOF']/2, hebei_idx),
            xytext=(120, hebei_idx - 2),
            arrowprops=dict(arrowstyle='->', color='black', lw=1),
            fontsize=8.5, color='black',
            bbox=dict(boxstyle='round,pad=0.3', fc='#FFF3CD', ec='#FFC107', alpha=0.9))
plt.tight_layout()
plt.savefig(f'{FIG_DIR}/fig2_steel_provinces.png', bbox_inches='tight', dpi=150)
plt.show()
"""))

cells.append(md("### 2.3 BF province distribution"))

cells.append(code("""\
china_bf_m = china_bf.merge(china_plants[['GEM plant ID','Subnational unit']],
                             on='GEM plant ID', how='left')
bf_prov = china_bf_m.groupby('Subnational unit')['cap'].sum() / 1000
bf_prov = bf_prov.sort_values(ascending=True).tail(12)

fig, ax = plt.subplots(figsize=(9, 5))
colors_bf = [plt.cm.YlOrRd(0.4 + 0.6*i/len(bf_prov)) for i in range(len(bf_prov))]
bars = ax.barh(bf_prov.index, bf_prov.values, color=colors_bf, edgecolor='white')
for b, v in zip(bars, bf_prov.values):
    ax.text(v + 1, b.get_y() + b.get_height()/2,
            f'{v:.0f}', va='center', fontsize=8.5, color=GREY)
ax.set_xlabel('Hot Metal Capacity (Mtpa)')
ax.set_title('Top 12 Provinces — Blast Furnace Hot Metal Capacity\\n'
             f'(China, {len(china_bf)} operating BFs, {total_bf:.0f} Mtpa total, GEM March 2026)',
             fontsize=12, fontweight='bold', pad=10)
plt.tight_layout()
plt.savefig(f'{FIG_DIR}/fig3_bf_provinces.png', bbox_inches='tight', dpi=150)
plt.show()
"""))

# ── SECTION 3: CBAM COST ──────────────────────────────────────────────────────
cells.append(md("""---
## 3 · CBAM Cost Quantification

**Methodology** (Equation 1 from paper):

$$\\text{CBAM Liability}_i = \\max(0,\\; EF_i \\times (P^{\\text{EU}} - P^{\\text{CN}}))$$

| Sector | Emission Factor | Source |
|---|---|---|
| BF-BOF steel | 2.10 tCO₂/t | IEA ETP 2023 |
| EAF steel | **0.10 tCO₂/t** (Scope 1, CBAM-applicable; Scope 2 excluded per Reg. EU 2023/956) | IEA ETP 2023 + MEE 2023 |
| Cement | 0.627 tCO₂/t | GEM clinker ratio × IPCC 2006 |

"""))

cells.append(code("""\
# ── Emission factors ──────────────────────────────────────────────────────────
EF = {'BF-BOF Steel': 2.10, 'EAF Steel': 0.10, 'Cement': 0.627}  # EAF = Scope 1 only (CBAM-applicable)

# Clinker ratio from GEM data
clinker_ratio_gem = total_clin / total_cem
ef_cement_gem     = clinker_ratio_gem * 0.825   # IPCC factor
print(f'Clinker/cement ratio (GEM): {clinker_ratio_gem:.3f}')
print(f'Cement EF (derived):        {ef_cement_gem:.3f} tCO2/t')
print()

# ── Sensitivity table ─────────────────────────────────────────────────────────
eu_ets_prices  = [65, 80]
cn_ets_labels  = ['Not covered\\n(current)', 'EUR 13', 'EUR 40', 'EUR 60', 'Full parity']
cn_ets_prices  = [0, 13, 40, 60, 65]   # last row uses EU ETS = 65 as parity

rows = []
for eu in eu_ets_prices:
    for cn_label, cn in zip(cn_ets_labels, cn_ets_prices):
        cn_actual = cn if cn < eu else eu
        row = {'EU ETS (EUR/tCO2)': eu, 'CN-ETS Scenario': cn_label}
        for sec, ef in EF.items():
            row[sec] = max(0, ef * (eu - cn_actual))
        row['Offset rate (%)'] = round(100 * cn_actual / eu, 1)
        rows.append(row)

sens_df = pd.DataFrame(rows)
display_cols = ['EU ETS (EUR/tCO2)', 'CN-ETS Scenario', 'BF-BOF Steel', 'EAF Steel', 'Cement', 'Offset rate (%)']
print(sens_df[display_cols].to_string(index=False, float_format='{:.1f}'.format))
"""))

cells.append(md("### 3.1 CBAM liability heatmap"))

cells.append(code("""\
# ── 2D heatmap: EU ETS price (y) × CN-ETS price (x) for BF-BOF ───────────────
eu_range = np.arange(40, 100, 5)
cn_range = np.arange(0, 85, 5)
EU_grid, CN_grid = np.meshgrid(eu_range, cn_range)
liability_bfbof  = np.maximum(0, EF['BF-BOF Steel'] * (EU_grid - CN_grid))

fig, axes = plt.subplots(1, 3, figsize=(15, 5))
sectors   = ['BF-BOF Steel', 'EAF Steel', 'Cement']
ef_vals   = [2.10, 0.10, 0.627]  # EAF Scope 1 only (CBAM-applicable)
titles    = ['BF-BOF Steel', 'EAF Steel', 'Cement']

for i, (sec, ef) in enumerate(zip(sectors, ef_vals)):
    Z = np.maximum(0, ef * (EU_grid - CN_grid))
    im = axes[i].contourf(cn_range, eu_range, Z.T, levels=20, cmap='RdYlGn_r')
    axes[i].contour(cn_range, eu_range, Z.T, levels=[0], colors='black', linewidths=2)
    cb = plt.colorbar(im, ax=axes[i], shrink=0.9)
    cb.set_label('CBAM Liability (EUR/t)', fontsize=8)

    # Mark current state
    axes[i].scatter([13], [65], color='red', s=80, zorder=5, label='Current (CN=13, EU=65)')
    axes[i].scatter([13], [80], color='darkred', s=80, marker='^', zorder=5, label='Peak (CN=13, EU=80)')
    axes[i].set_xlabel('CN-ETS Price (EUR/tCO₂)')
    axes[i].set_ylabel('EU ETS Price (EUR/tCO₂)')
    axes[i].set_title(f'{titles[i]}\\n(EF = {ef} tCO₂/t)', fontsize=10, fontweight='bold')
    if i == 0:
        axes[i].legend(fontsize=7, loc='upper left')

plt.suptitle('CBAM Net Liability Heatmap by Price Scenario\\n'
             '(Black contour = zero liability / full offset line)', fontsize=12, fontweight='bold')
plt.tight_layout()
plt.savefig(f'{FIG_DIR}/fig4_cbam_heatmap.png', bbox_inches='tight', dpi=150)
plt.show()
"""))

cells.append(md("### 3.2 CBAM liability by sector — bar chart"))

cells.append(code("""\
eu_vals    = [65, 80]
cn_prices  = [0, 13, 40, 60]
cn_labels  = ['Not covered\\n(EU=65)', 'EUR 13\\n(EU=65)', 'EUR 40\\n(EU=65)', 'EUR 60\\n(EU=65)',
              'Not covered\\n(EU=80)', 'EUR 13\\n(EU=80)', 'EUR 40\\n(EU=80)', 'EUR 60\\n(EU=80)']

bfbof_vals, eaf_vals, cem_vals = [], [], []
for eu in [65, 80]:
    for cn in cn_prices:
        bfbof_vals.append(max(0, EF['BF-BOF Steel'] * (eu - cn)))
        eaf_vals.append(max(0,   EF['EAF Steel']    * (eu - cn)))
        cem_vals.append(max(0,   EF['Cement']        * (eu - cn)))

x     = np.arange(len(cn_labels))
width = 0.26
fig, ax = plt.subplots(figsize=(14, 6))
b1 = ax.bar(x - width, bfbof_vals, width, label='BF-BOF Steel', color=RED,   alpha=0.85, edgecolor='white')
b2 = ax.bar(x,          eaf_vals,  width, label='EAF Steel',    color=BLUE,  alpha=0.85, edgecolor='white')
b3 = ax.bar(x + width,  cem_vals,  width, label='Cement',       color=GREEN, alpha=0.85, edgecolor='white')

for b_group in [b1, b2, b3]:
    for bar in b_group:
        h = bar.get_height()
        if h > 5:
            ax.text(bar.get_x() + bar.get_width()/2, h + 1.5,
                    f'{h:.0f}', ha='center', va='bottom', fontsize=7.5, color=GREY)

ax.axvline(3.5, color='black', linestyle='--', linewidth=1.2, alpha=0.5)
ax.text(1.5, ax.get_ylim()[1]*0.95 if ax.get_ylim()[1] > 0 else 150,
        'EU ETS = EUR 65', ha='center', fontsize=9, color=GREY, style='italic')
ax.text(5.5, 160, 'EU ETS = EUR 80', ha='center', fontsize=9, color=GREY, style='italic')

ax.set_xticks(x)
ax.set_xticklabels(cn_labels, fontsize=8.5)
ax.set_ylabel('CBAM Net Liability (EUR per tonne of product)')
ax.set_title('CBAM Liability per Tonne by Sector and CN-ETS Price Scenario',
             fontsize=12, fontweight='bold', pad=10)
ax.legend()

# Re-fix annotation y position now that ylim is set
ymax = ax.get_ylim()[1]
ax.texts[-2].set_y(ymax * 0.95)
ax.texts[-1].set_y(ymax * 0.95)

plt.tight_layout()
plt.savefig(f'{FIG_DIR}/fig5_cbam_by_sector.png', bbox_inches='tight', dpi=150)
plt.show()
"""))

cells.append(md("### 3.3 Carbon price convergence pathways"))

cells.append(code("""\
years = np.array([2024, 2025, 2026, 2027, 2028, 2029, 2030])

# Scenarios for CN-ETS price trajectory
scenarios = {
    'Conservative (→ EUR 40 by 2030)': np.interp(years, [2024, 2030], [13, 40]),
    'Moderate (→ EUR 60 by 2030)':     np.interp(years, [2024, 2030], [13, 60]),
    'Ambitious (→ EUR 80 by 2030)':    np.interp(years, [2024, 2030], [13, 80]),
}
eu_ets_baseline = np.array([65, 65, 62, 63, 67, 70, 72])   # stylised EU ETS path

fig, axes = plt.subplots(1, 2, figsize=(14, 5))

# ── Left: Price trajectories ──────────────────────────────────────────────────
ax = axes[0]
ax.fill_between(years, eu_ets_baseline - 8, eu_ets_baseline + 8,
                alpha=0.15, color='darkred', label='EU ETS (±8 EUR band)')
ax.plot(years, eu_ets_baseline, color='darkred', linewidth=2.2, label='EU ETS (central)')
colors_sc = ['#4393C3', '#2166AC', '#053061']
for (label, vals), col in zip(scenarios.items(), colors_sc):
    ax.plot(years, vals, linewidth=2, linestyle='--', color=col, label=f'CN-ETS: {label}')
ax.scatter([2024], [13], color='black', s=70, zorder=5)
ax.annotate('Current CN-ETS\\n(EUR 13)', xy=(2024, 13), xytext=(2025.2, 22),
            arrowprops=dict(arrowstyle='->', lw=1), fontsize=8)
ax.set_xlabel('Year')
ax.set_ylabel('Carbon Price (EUR/tCO₂)')
ax.set_title('CN-ETS Price Convergence Scenarios\\nvs EU ETS Baseline', fontsize=11, fontweight='bold')
ax.legend(fontsize=7.5, loc='upper left')
ax.set_xlim(2024, 2030)
ax.set_ylim(0, 100)

# ── Right: Offset rate trajectories ──────────────────────────────────────────
ax2 = axes[1]
for (label, vals), col in zip(scenarios.items(), colors_sc):
    offset = np.clip(vals / eu_ets_baseline * 100, 0, 100)
    ax2.plot(years, offset, linewidth=2, linestyle='--', color=col, label=label)

ax2.axhline(60, color=GREY, linestyle=':', linewidth=1.2, alpha=0.8)
ax2.axhline(30, color=GREY, linestyle=':', linewidth=1.2, alpha=0.8)
ax2.text(2030.05, 61, 'Wang et al. 60%\\nupper bound', fontsize=7.5, color=GREY, va='bottom')
ax2.text(2030.05, 31, 'Wang et al. 30%\\nlower bound', fontsize=7.5, color=GREY, va='bottom')
ax2.set_xlabel('Year')
ax2.set_ylabel('CBAM Offset Rate (%)')
ax2.set_title('CN-ETS Offset Rate Against CBAM Liability\\n(= CN-ETS price / EU ETS price)',
              fontsize=11, fontweight='bold')
ax2.legend(fontsize=7.5, loc='upper left')
ax2.set_xlim(2024, 2030)
ax2.set_ylim(0, 110)

plt.suptitle('Carbon Price Convergence and CBAM Offset Rate (2024–2030)',
             fontsize=12, fontweight='bold')
plt.tight_layout()
plt.savefig(f'{FIG_DIR}/fig6_price_convergence.png', bbox_inches='tight', dpi=150)
plt.show()
"""))

# ── SECTION 4: CEMENT ─────────────────────────────────────────────────────────
cells.append(md("""---
## 4 · China Cement Sector Analysis
"""))

cells.append(code("""\
# ── Province aggregation ──────────────────────────────────────────────────────
cem_prov = china_cem.groupby('Subnational unit').agg(
    cem_cap  = ('cem_cap', 'sum'),
    clin_cap = ('clin_cap', 'sum'),
    n_plants = ('GEM Plant ID', 'count')
).sort_values('cem_cap', ascending=False)
cem_prov['clinker_ratio'] = cem_prov['clin_cap'] / cem_prov['cem_cap'].replace(0, np.nan)
cem_prov['cbam_ef']       = cem_prov['clinker_ratio'] * 0.825   # tCO2/t cement

# ── CCS status ────────────────────────────────────────────────────────────────
ccs_counts = china_cem['CCS/CCUS'].value_counts()
print('CCS/CCUS breakdown:')
print(ccs_counts.to_string())
print(f'\\nTotal operating plants: {len(china_cem)}')
print(f'Plants with CCS: {ccs_counts.get(\"yes\", 0)} ({100*ccs_counts.get(\"yes\", 0)/len(china_cem):.1f}%)')
print(f'\\nNational clinker/cement ratio: {total_clin/total_cem:.3f}')
print(f'National cement EF:             {total_clin/total_cem*0.825:.3f} tCO2/t')
"""))

cells.append(md("### 4.1 Cement capacity — top provinces & clinker ratio"))

cells.append(code("""\
top15_cem = cem_prov.head(15).sort_values('cem_cap', ascending=True)

fig, axes = plt.subplots(1, 2, figsize=(14, 6))

# ── Capacity bar ──────────────────────────────────────────────────────────────
ax = axes[0]
y   = np.arange(len(top15_cem))
ax.barh(y, top15_cem['cem_cap'], color='#74C476', edgecolor='white', label='Cement cap.')
ax.barh(y, top15_cem['clin_cap'], color='#238B45', edgecolor='white', alpha=0.85, label='Clinker cap.')
ax.set_yticks(y)
ax.set_yticklabels(top15_cem.index, fontsize=9)
ax.set_xlabel('Capacity (Mt/yr)')
ax.set_title('Top 15 Provinces — Cement & Clinker Capacity\\n(GEM July 2025)', fontsize=11, fontweight='bold')
ax.legend()
for i, (_, row) in enumerate(top15_cem.iterrows()):
    ax.text(row['cem_cap'] + 1, i, f'{row[\"cem_cap\"]:.0f}', va='center', fontsize=8, color=GREY)

# ── Clinker ratio scatter ─────────────────────────────────────────────────────
ax2 = axes[1]
valid = cem_prov.dropna(subset=['clinker_ratio']).head(20).sort_values('clinker_ratio')
colors_cr = ['#D73027' if r > total_clin/total_cem else '#4575B4' for r in valid['clinker_ratio']]
bars = ax2.barh(valid.index, valid['clinker_ratio'], color=colors_cr, edgecolor='white')
ax2.axvline(total_clin/total_cem, color='black', linestyle='--', linewidth=1.5,
            label=f'National avg = {total_clin/total_cem:.3f}')
ax2.axvline(0.73, color=GREY, linestyle=':', linewidth=1.2, label='Global avg ≈ 0.730')
ax2.set_xlabel('Clinker-to-Cement Ratio')
ax2.set_title('Clinker-to-Cement Ratio by Province\\n(higher = higher CBAM emissions intensity)',
              fontsize=11, fontweight='bold')
ax2.legend(fontsize=8)
ax2.set_xlim(0, 1.05)

plt.suptitle('China Cement Sector — Capacity and Clinker Ratio by Province',
             fontsize=12, fontweight='bold')
plt.tight_layout()
plt.savefig(f'{FIG_DIR}/fig7_cement_provinces.png', bbox_inches='tight', dpi=150)
plt.show()
"""))

cells.append(md("### 4.2 CCS status and CBAM decarbonization potential"))

cells.append(code("""\
fig, axes = plt.subplots(1, 2, figsize=(12, 5))

# ── CCS pie ───────────────────────────────────────────────────────────────────
ax = axes[0]
ccs_clean = china_cem['CCS/CCUS'].replace({'n/a': 'Unknown/N/A', 'unknown': 'Unknown/N/A'})
ccs_agg   = ccs_clean.value_counts()
ccs_colors = {'yes': GREEN, 'no': RED, 'Unknown/N/A': GREY}
c_list = [ccs_colors.get(k, GREY) for k in ccs_agg.index]
wedges, texts, autotexts = ax.pie(
    ccs_agg.values, labels=ccs_agg.index, colors=c_list,
    autopct='%1.1f%%', startangle=90,
    textprops={'fontsize': 9})
ax.set_title(f'CCS/CCUS Deployment Status\\n(China, {len(china_cem)} operating plants, GEM 2025)',
             fontsize=11, fontweight='bold')
ax.text(0, -1.4, f'Only {ccs_agg.get(\"yes\", 0)} plants (0.4%) have CCS',
        ha='center', fontsize=9, color='#D73027', style='italic')

# ── CBAM savings from CCS ─────────────────────────────────────────────────────
ax2 = axes[1]
eu_prices = np.linspace(40, 100, 100)
ef_base = total_clin / total_cem * 0.825
ccs_rates = [0.70, 0.85, 0.90]
colors_ccs = ['#FC8D59', '#D73027', '#67001F']
labels_ccs = ['70% capture', '85% capture', '90% capture']
for rate, col, lab in zip(ccs_rates, colors_ccs, labels_ccs):
    ef_reduced = ef_base * (1 - rate)
    cbam_savings = (ef_base - ef_reduced) * eu_prices
    ax2.plot(eu_prices, cbam_savings, color=col, linewidth=2, label=lab)

ax2.fill_between(eu_prices,
                 ef_base * (1 - 0.70) * eu_prices,
                 ef_base * (1 - 0.90) * eu_prices,
                 alpha=0.1, color=RED)
ax2.axvline(65, color='black', linestyle='--', linewidth=1, alpha=0.6)
ax2.axvline(80, color=GREY,  linestyle='--', linewidth=1, alpha=0.6)
ax2.text(65.5, 5, 'EU ETS\\n= 65', fontsize=8, color='black')
ax2.text(80.5, 5, 'EU ETS\\n= 80', fontsize=8, color=GREY)
ax2.set_xlabel('EU ETS Price (EUR/tCO₂)')
ax2.set_ylabel('CBAM Savings from CCS (EUR/t cement)')
ax2.set_title('CCS-Enabled CBAM Liability Reduction\\n(China cement, clinker ratio = 0.760)',
              fontsize=11, fontweight='bold')
ax2.legend()

plt.suptitle('Cement CCS — Current Deployment & CBAM Incentive for Investment',
             fontsize=12, fontweight='bold')
plt.tight_layout()
plt.savefig(f'{FIG_DIR}/fig8_cement_ccs.png', bbox_inches='tight', dpi=150)
plt.show()
"""))

# ── SECTION 5: POWER ─────────────────────────────────────────────────────────
cells.append(md("""---
## 5 · China Power Mix — Grid Emission Factor Basis
"""))

cells.append(code("""\
# ── Power type aggregation ────────────────────────────────────────────────────
type_cap = china_pw.groupby('Type')['cap_mw'].sum().sort_values(ascending=False)
total_pw  = type_cap.sum()

# Clean labels
clean_labels = {
    'coal': 'Coal',
    'utility-scale solar': 'Solar (utility)',
    'wind': 'Wind',
    'hydropower': 'Hydropower',
    'oil/gas': 'Oil & Gas',
    'nuclear': 'Nuclear',
    'bioenergy': 'Bioenergy',
    'geothermal': 'Geothermal',
    'distributed solar': 'Solar (distributed)',
    'offshore wind': 'Offshore Wind',
}
type_cap.index = [clean_labels.get(i, i) for i in type_cap.index]
type_cap_gw = type_cap / 1000

fig, axes = plt.subplots(1, 2, figsize=(13, 5))

# ── Donut ─────────────────────────────────────────────────────────────────────
ax = axes[0]
top8 = type_cap_gw.head(8)
other = type_cap_gw[8:].sum()
plot_vals   = list(top8.values) + [other]
plot_labels = list(top8.index)  + ['Other']
palette = ['#636363','#FDCC8A','#7FCDBB','#225EA8','#C7E9B4','#F03B20','#74C476','#FD8D3C','#BDBDBD']
wedges, texts, autotexts = ax.pie(
    plot_vals, labels=plot_labels, colors=palette[:len(plot_vals)],
    autopct=lambda p: f'{p:.1f}%' if p > 2 else '',
    startangle=90, wedgeprops=dict(width=0.6),
    textprops={'fontsize': 8.5})
ax.text(0, 0, f'{total_pw/1e6:.2f}\\nTW\\ntotal', ha='center', va='center',
        fontsize=9, fontweight='bold', color=GREY)
ax.set_title(f'China Operating Power Mix\\n(GEM March 2026, {total_pw/1000:.0f} GW)',
             fontsize=11, fontweight='bold')

# ── Bar with CO2 annotation ────────────────────────────────────────────────────
ax2 = axes[1]
y  = np.arange(len(type_cap_gw.head(8)))
bar_colors = ['#636363' if 'Coal' in l else
              ('#4575B4' if l in ('Hydropower','Wind','Solar (utility)','Nuclear','Geothermal') else '#FDAE61')
              for l in type_cap_gw.head(8).index]
bars = ax2.barh(y, type_cap_gw.head(8).values, color=bar_colors, edgecolor='white')
for b, v in zip(bars, type_cap_gw.head(8).values):
    ax2.text(v + 5, b.get_y() + b.get_height()/2,
             f'{v:.0f} GW ({100*v*1000/total_pw:.1f}%)', va='center', fontsize=8.5)
ax2.set_yticks(y)
ax2.set_yticklabels(type_cap_gw.head(8).index, fontsize=9.5)
ax2.set_xlabel('Operating Capacity (GW)')
ax2.set_title('Power Capacity by Type\\n(relevant to EAF Scope 2 emissions)',
              fontsize=11, fontweight='bold')
ax2.axvline(0, color='black', linewidth=0.5)

# Annotation: grid EF
ax2.text(0.98, 0.02,
         'National grid EF: 0.581 kgCO₂/kWh (MEE 2023)\\n'
         'EAF total intensity ref. only — Scope 2 excluded from CBAM',
         transform=ax2.transAxes, ha='right', va='bottom',
         fontsize=7.5, color=GREY,
         bbox=dict(boxstyle='round', fc='white', ec=GREY, alpha=0.7))

plt.suptitle('China Power Mix — Grid Emission Factor Basis',
             fontsize=12, fontweight='bold')
plt.tight_layout()
plt.savefig(f'{FIG_DIR}/fig9_power_mix.png', bbox_inches='tight', dpi=150)
plt.show()
"""))

# ── SECTION 6: SUMMARY DASHBOARD ─────────────────────────────────────────────
cells.append(md("""---
## 6 · Summary Dashboard
"""))

cells.append(code("""\
fig = plt.figure(figsize=(16, 10))
gs  = GridSpec(2, 3, figure=fig, hspace=0.45, wspace=0.38)

# ── Panel A: Technology donut ─────────────────────────────────────────────────
ax_a = fig.add_subplot(gs[0, 0])
total_steel = total_bof + total_eaf
sizes = [total_bof, total_eaf]
ax_a.pie(sizes, labels=[f'BF-BOF\\n{total_bof:.0f} Mt\\n(83.1%)',
                         f'EAF\\n{total_eaf:.0f} Mt\\n(16.9%)'],
         colors=[RED, BLUE], startangle=90, wedgeprops=dict(width=0.5),
         textprops={'fontsize': 8})
ax_a.text(0, 0, f'{total_steel:.0f}\\nMtpa', ha='center', va='center',
          fontsize=9, fontweight='bold')
ax_a.set_title('A · Steel Technology Mix', fontweight='bold', fontsize=10)

# ── Panel B: Top provinces (BOF) ──────────────────────────────────────────────
ax_b = fig.add_subplot(gs[0, 1])
bof_top8 = china_bof.groupby('Subnational unit')['cap'].sum().sort_values(ascending=True).tail(8) / 1000
eaf_top8_aligned = china_eaf.groupby('Subnational unit')['cap'].sum().reindex(
    bof_top8.index, fill_value=0) / 1000
y = np.arange(len(bof_top8))
ax_b.barh(y, bof_top8.values, height=0.6, color=RED, alpha=0.85, label='BOF')
ax_b.barh(y, eaf_top8_aligned.values, height=0.6, color=BLUE, alpha=0.85,
          left=bof_top8.values, label='EAF')
ax_b.set_yticks(y)
ax_b.set_yticklabels(bof_top8.index, fontsize=8)
ax_b.set_xlabel('Mtpa', fontsize=8)
ax_b.set_title('B · Top 8 Provinces\\n(Steel Capacity)', fontweight='bold', fontsize=10)
ax_b.legend(fontsize=7)

# ── Panel C: CBAM liability bars ──────────────────────────────────────────────
ax_c = fig.add_subplot(gs[0, 2])
cn_pts     = [0, 13, 40, 60, 65]
cn_lbs     = ['Not\ncovered', 'EUR\n13', 'EUR\n40', 'EUR\n60', 'Parity\nEUR65']
bfbof_c    = [max(0, 2.10*(65-p)) for p in cn_pts]
eaf_c      = [max(0, 0.10*(65-p)) for p in cn_pts]
cem_c      = [max(0, 0.627*(65-p)) for p in cn_pts]
x_c = np.arange(len(cn_pts))
w   = 0.25
ax_c.bar(x_c - w, bfbof_c, w, color=RED,   label='BF-BOF', alpha=0.85)
ax_c.bar(x_c,     eaf_c,   w, color=BLUE,  label='EAF',    alpha=0.85)
ax_c.bar(x_c + w, cem_c,   w, color=GREEN, label='Cement', alpha=0.85)
ax_c.set_xticks(x_c)
ax_c.set_xticklabels(cn_lbs, fontsize=7.5)
ax_c.set_ylabel('EUR/t', fontsize=8)
ax_c.set_title('C · CBAM Liability by Sector\\n(EU ETS = EUR 65)', fontweight='bold', fontsize=10)
ax_c.legend(fontsize=7)

# ── Panel D: Convergence paths ────────────────────────────────────────────────
ax_d = fig.add_subplot(gs[1, 0:2])
yrs = np.linspace(2024, 2030, 100)
paths = {
    'Conservative (EUR 40)': np.interp(yrs, [2024, 2030], [13, 40]),
    'Moderate (EUR 60)':      np.interp(yrs, [2024, 2030], [13, 60]),
    'Ambitious (EUR 80)':     np.interp(yrs, [2024, 2030], [13, 80]),
}
eu_base = np.interp(yrs, [2024, 2030], [65, 72])
ax_d.fill_between(yrs, eu_base - 8, eu_base + 8, alpha=0.12, color='darkred')
ax_d.plot(yrs, eu_base, color='darkred', linewidth=2, label='EU ETS (central)')
cols_d = ['#4393C3', '#2166AC', '#08306B']
for (label, vals), col in zip(paths.items(), cols_d):
    ax_d.plot(yrs, vals, '--', linewidth=2, color=col, label=f'CN-ETS: {label}')
ax_d.set_xlabel('Year', fontsize=9)
ax_d.set_ylabel('EUR/tCO₂', fontsize=9)
ax_d.set_title('D · CN-ETS Price Convergence Scenarios (2024–2030)', fontweight='bold', fontsize=10)
ax_d.legend(fontsize=7.5, ncol=2)
ax_d.set_ylim(0, 100)

# ── Panel E: Cement CCS status ────────────────────────────────────────────────
ax_e = fig.add_subplot(gs[1, 2])
no_ccs  = len(china_cem[china_cem['CCS/CCUS'] == 'no'])
yes_ccs = len(china_cem[china_cem['CCS/CCUS'] == 'yes'])
na_ccs  = len(china_cem) - no_ccs - yes_ccs
wedges, _, auts = ax_e.pie([yes_ccs, no_ccs, na_ccs],
                           labels=[f'CCS: yes ({yes_ccs})', f'No CCS ({no_ccs})', f'Unknown ({na_ccs})'],
                           colors=[GREEN, RED, GREY],
                           autopct='%1.1f%%', startangle=90,
                           textprops={'fontsize': 7.5})
ax_e.set_title(f'E · Cement CCS Status\\n({len(china_cem)} operating plants)', fontweight='bold', fontsize=10)

fig.suptitle('Summary Dashboard — EU CBAM and China Industrial Decarbonization\n'
             'Data: GEM Iron & Steel Tracker (Mar 2026), GEM Cement Tracker (Jul 2025)',
             fontsize=13, fontweight='bold', y=1.01)
plt.savefig(f'{FIG_DIR}/fig10_summary_dashboard.png', bbox_inches='tight', dpi=150)
plt.show()
print('All figures saved.')
"""))

# ── SECTION 7: KEY STATS TABLE ────────────────────────────────────────────────
cells.append(md("""---
## 7 · Key Statistics Summary Table
"""))

cells.append(code("""\
from IPython.display import display, HTML

summary_data = {
    'Indicator': [
        'China steel plants (GEM tracked)',
        'BF-BOF operating capacity',
        'EAF operating capacity',
        'BOF share of total steel capacity',
        'Blast furnaces (operating)',
        'BF hot metal capacity',
        'Hebei BOF capacity (largest province)',
        'Cement plants (operating)',
        'Cement capacity',
        'Clinker capacity',
        'Clinker-to-cement ratio (GEM)',
        'Cement plants with CCS',
        'Emission factor: BF-BOF steel',
        'Emission factor: EAF steel (CBAM, Scope 1 only)',
        'Emission factor: EAF steel (total, incl. Scope 2)',
        'Emission factor: Cement',
        'BF-BOF / EAF CBAM intensity ratio',
        'CBAM liability: BF-BOF (current, EU ETS 65)',
        'CBAM liability: EAF (current, EU ETS 65)',
        'CBAM liability: Cement (current, EU ETS 65)',
        'CN-ETS price (2024)',
        'EU ETS price (2024-25 avg)',
        'Price gap',
        'Wang et al. current offset rate',
    ],
    'Value': [
        '458',
        '835.7 Mtpa',
        '169.5 Mtpa',
        '83.1%',
        '599 units',
        '854.5 Mtpa',
        '199.7 Mtpa (23.9% of national)',
        '1,016',
        '1,772 Mt/yr',
        '1,346 Mt/yr',
        '0.760',
        '4 / 1,016 (0.4%)',
        '2.10 tCO₂/t',
        '0.10 tCO₂/t (Scope 1, CBAM-applicable)',
        '0.44 tCO₂/t (Scope 1+2, non-CBAM reference)',
        '0.627 tCO₂/t',
        '21.0 : 1',
        'EUR 136.5 / t steel',
        'EUR 6.5 / t steel',
        'EUR 40.8 / t cement',
        '~EUR 13/tCO₂',
        '~EUR 65/tCO₂',
        '~EUR 52/tCO₂',
        '30–60% (Wang et al. 2025)',
    ],
    'Source': [
        'GEM Mar 2026', 'GEM Mar 2026', 'GEM Mar 2026', 'GEM Mar 2026',
        'GEM Mar 2026', 'GEM Mar 2026', 'GEM Mar 2026',
        'GEM Jul 2025', 'GEM Jul 2025', 'GEM Jul 2025', 'GEM Jul 2025', 'GEM Jul 2025',
        'IEA ETP 2023', 'IEA ETP 2023 (Scope 1)', 'GEM + MEE 2023 (Scope 1+2)', 'GEM + IPCC 2006', 'Derived',
        'Eq. 1 (paper)', 'Eq. 1 (paper)', 'Eq. 1 (paper)',
        'MEE 2024', 'EU ETS market', 'Derived', 'Wang et al. 2025',
    ]
}
summary_df = pd.DataFrame(summary_data)

# Pretty print
styled = summary_df.style.set_properties(**{'text-align': 'left'}).hide(axis='index')
display(styled)
"""))

# ── ASSEMBLE NOTEBOOK ─────────────────────────────────────────────────────────
nb = {
    "nbformat": 4,
    "nbformat_minor": 5,
    "metadata": {
        "kernelspec": {
            "display_name": "Python 3",
            "language": "python",
            "name": "python3"
        },
        "language_info": {
            "name": "python",
            "version": "3.10.0"
        }
    },
    "cells": cells
}

out_path = os.path.join(_ROOT, 'code', 'cbam_analysis.ipynb')
with open(out_path, 'w', encoding='utf-8') as f:
    json.dump(nb, f, indent=1, ensure_ascii=False)

print(f'Notebook written: {out_path}')

