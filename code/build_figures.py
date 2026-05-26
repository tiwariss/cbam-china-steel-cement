"""
Generate replacement figures for IPEN6100G paper draft.
Figures saved to output/figures/
"""
import os as _os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyArrowPatch
import warnings
warnings.filterwarnings('ignore')

_ROOT    = _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))
DATA_DIR = _os.path.join(_ROOT, 'resources', 'data')
OUT_DIR  = _os.path.join(_ROOT, 'output', 'figures')

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

BLUE   = '#2166AC'
RED    = '#D6604D'
GREEN  = '#4DAC26'
GREY   = '#636363'
ORANGE = '#F4A582'

# ── Load GEM steel unit data ───────────────────────────────────────────────────
eaf = pd.read_excel(f'{DATA_DIR}/gem_steel_units_2026.xlsx',
                    sheet_name='Electric arc furnaces')
bof = pd.read_excel(f'{DATA_DIR}/gem_steel_units_2026.xlsx',
                    sheet_name='Basic oxygen furnaces')

eaf_op = eaf[eaf['Unit status'] == 'operating'].copy()
bof_op = bof[bof['Unit status'] == 'operating'].copy()
eaf_op['cap'] = pd.to_numeric(eaf_op['Current capacity (ttpa)'], errors='coerce').fillna(0)
bof_op['cap'] = pd.to_numeric(bof_op['Current capacity (ttpa)'], errors='coerce').fillna(0)

eaf_by_country = eaf_op.groupby('Country/area')['cap'].sum()
bof_by_country = bof_op.groupby('Country/area')['cap'].sum()

countries = pd.DataFrame({'EAF': eaf_by_country, 'BOF': bof_by_country}).fillna(0)
countries['total']     = countries['EAF'] + countries['BOF']
countries['eaf_share'] = countries['EAF'] / countries['total'] * 100

# ── Load GEM cement data ───────────────────────────────────────────────────────
cem = pd.read_excel(f'{DATA_DIR}/gem_cement_2025.xlsx',
                    sheet_name='Plant Data')
china_cem = cem[(cem['Country/Area'] == 'China') & (cem['Operating status'] == 'operating')].copy()
china_cem['cem_cap']  = pd.to_numeric(
    china_cem['Cement Capacity (millions metric tonnes per annum)'], errors='coerce').fillna(0)
china_cem['clin_cap'] = pd.to_numeric(
    china_cem['Clinker Capacity (millions metric tonnes per annum)'], errors='coerce').fillna(0)

total_cem  = china_cem['cem_cap'].sum()
total_clin = china_cem['clin_cap'].sum()
clinker_ratio = total_clin / total_cem

print(f'Loaded {len(countries)} countries, {len(china_cem)} China cement plants')
print(f'Clinker/cement ratio: {clinker_ratio:.3f}')


# ══════════════════════════════════════════════════════════════════════════════
# FIGURE A · EAF Share by Country (replaces §IV-E prose)
# ══════════════════════════════════════════════════════════════════════════════
# Select key countries relevant to CBAM/CN-ETS paper
key_countries = [
    'China', 'India', 'United States', 'Japan', 'Russia',
    'South Korea', 'Türkiye', 'Germany', 'Brazil', 'Italy',
    'Spain', 'France', 'Vietnam', 'Iran', 'Indonesia',
]
plot_df = countries.loc[countries.index.isin(key_countries)].copy()
plot_df = plot_df.sort_values('eaf_share', ascending=True)

# WorldSteel2024 production-weighted global EAF share (~29%); GEM capacity-weighted
# gives ~35% due to capacity/production divergence — use production figure to match paper.
global_eaf_share = 29.0

fig, ax = plt.subplots(figsize=(9, 6))

bar_colors = [
    RED if c == 'China' else
    '#4393C3' if c in ('United States', 'Germany', 'Italy', 'Spain', 'France') else
    GREY
    for c in plot_df.index
]

bars = ax.barh(plot_df.index, plot_df['eaf_share'], color=bar_colors,
               edgecolor='white', height=0.7)

# Value labels
for bar, val in zip(bars, plot_df['eaf_share']):
    ax.text(val + 0.8, bar.get_y() + bar.get_height() / 2,
            f'{val:.0f}%', va='center', fontsize=8.5, color=GREY)

# Reference lines — WorldSteel2024
eu_eaf_share = 44.0   # WorldSteel2024
ax.axvline(global_eaf_share, color='black', linestyle='--', linewidth=1.4)
ax.axvline(eu_eaf_share, color='#4393C3', linestyle='--', linewidth=1.4)

ax.set_xlabel('EAF Share of Operating Crude Steel Capacity (%)')
ax.set_title('EAF Share by Country\n(GEM Iron & Steel Tracker, March 2026)',
             fontsize=12, fontweight='bold', pad=10)
ax.set_xlim(0, 115)

# Legend patches
china_patch = mpatches.Patch(color=RED, label='China')
eu_patch    = mpatches.Patch(color='#4393C3', label='EU members')
other_patch = mpatches.Patch(color=GREY, label='Other')
ax.legend(handles=[china_patch, eu_patch, other_patch,
                   plt.Line2D([0], [0], color='black', linestyle='--', linewidth=1.4,
                              label=f'World avg = {global_eaf_share:.0f}% (WorldSteel2024)'),
                   plt.Line2D([0], [0], color='#4393C3', linestyle='--', linewidth=1.4,
                              label=f'EU avg = {eu_eaf_share:.0f}% (WorldSteel2024)')],
          loc='lower right', fontsize=8.5)

plt.tight_layout()
plt.savefig(f'{OUT_DIR}/figA_eaf_share_by_country.png', bbox_inches='tight', dpi=150)
plt.close()
print('Saved figA')


# ══════════════════════════════════════════════════════════════════════════════
# FIGURE B · Steel Technology Mix — China (clean version, replaces broken Fig1)
# ══════════════════════════════════════════════════════════════════════════════
china = countries.loc['China']
total_steel = china['total'] / 1000   # Mtpa
bof_mt = china['BOF'] / 1000
eaf_mt = china['EAF'] / 1000

# Compare China EAF share vs World vs EU
eu_countries = ['Germany', 'Italy', 'Spain', 'France', 'Belgium',
                'Netherlands', 'Austria', 'Sweden', 'Finland']
eu = countries.loc[countries.index.isin(eu_countries)]
eu_eaf = eu['EAF'].sum() / eu['total'].sum() * 100

us_eaf = countries.loc['United States', 'eaf_share']
world_eaf = countries['EAF'].sum() / countries['total'].sum() * 100
china_eaf = china['eaf_share']

fig, axes = plt.subplots(1, 2, figsize=(12, 5))

# Left: donut
ax = axes[0]
sizes  = [bof_mt, eaf_mt]
labels = [f'BF-BOF\n{bof_mt:.0f} Mtpa\n({100*bof_mt/total_steel:.1f}%)',
          f'EAF\n{eaf_mt:.0f} Mtpa\n({100*eaf_mt/total_steel:.1f}%)']
ax.pie(sizes, labels=labels, colors=[RED, BLUE],
       startangle=90, wedgeprops=dict(width=0.55),
       textprops={'fontsize': 10})
ax.text(0, 0, f'{total_steel:.0f}\nMtpa', ha='center', va='center',
        fontsize=11, fontweight='bold', color=GREY)
ax.set_title('China Operating Crude Steel Capacity\nby Route (GEM March 2026)',
             fontsize=11, fontweight='bold', pad=10)

# Right: EAF share comparison China vs peers
ax2 = axes[1]
comp_labels = ['China', 'India', 'World avg', 'EU avg', 'United States']
comp_vals   = [china_eaf,
               countries.loc['India', 'eaf_share'],
               world_eaf, eu_eaf, us_eaf]
comp_colors = [RED, GREY, 'black', '#4393C3', '#4393C3']
bars2 = ax2.bar(comp_labels, comp_vals,
                color=[RED, GREY, '#636363', '#4393C3', '#2166AC'],
                edgecolor='white', width=0.6)
for b, v in zip(bars2, comp_vals):
    ax2.text(b.get_x() + b.get_width() / 2, v + 1.5,
             f'{v:.0f}%', ha='center', va='bottom', fontsize=10, fontweight='bold')
ax2.set_ylabel('EAF Share of Crude Steel Capacity (%)')
ax2.set_title('EAF Share Comparison\n(China vs Global Peers)',
              fontsize=11, fontweight='bold', pad=10)
ax2.set_ylim(0, 100)
ax2.axhline(world_eaf, color='black', linestyle=':', linewidth=1.2, alpha=0.6)

plt.suptitle('China Steel Sector — Technology Mix & Global Context',
             fontsize=13, fontweight='bold')
plt.tight_layout()
plt.savefig(f'{OUT_DIR}/figB_steel_tech_mix.png', bbox_inches='tight', dpi=150)
plt.close()
print('Saved figB')


# ══════════════════════════════════════════════════════════════════════════════
# FIGURE C · CN-ETS Price Convergence (replaces §IV-C three-paragraph block)
# ══════════════════════════════════════════════════════════════════════════════
years = np.array([2024, 2025, 2026, 2027, 2028, 2029, 2030])

# CN-ETS scenarios (paper §IV-C: conservative/moderate/full)
scenarios = {
    'Conservative (→ EUR 40, 2030)': np.interp(years, [2024, 2030], [13, 40]),
    'Moderate (→ EUR 60, 2030)':     np.interp(years, [2024, 2030], [13, 60]),
    'Full convergence (→ EUR 65+)':  np.interp(years, [2024, 2030], [13, 72]),
}

# EU ETS: illustrative flat-to-rising path (labelled as projected)
eu_central = np.array([65, 65, 63, 65, 67, 69, 72])
eu_lo      = eu_central - 10
eu_hi      = eu_central + 10

fig, axes = plt.subplots(1, 2, figsize=(14, 6))

# Left: price paths
ax = axes[0]
ax.fill_between(years, eu_lo, eu_hi, alpha=0.12, color='darkred')
ax.plot(years, eu_central, color='darkred', linewidth=2.2,
        label='EU ETS (projected, ±10 EUR band)')

sc_colors = ['#92C5DE', '#2166AC', '#053061']
sc_styles = ['--', '--', '--']
for (label, vals), col, ls in zip(scenarios.items(), sc_colors, sc_styles):
    ax.plot(years, vals, linewidth=2, linestyle=ls, color=col, label=f'CN-ETS: {label}')

ax.scatter([2024], [13], color='black', s=60, zorder=5)
ax.annotate('CN-ETS 2024\n(~EUR 13)', xy=(2024, 13), xytext=(2025, 22),
            arrowprops=dict(arrowstyle='->', lw=1), fontsize=8.5)
ax.set_xlabel('Year')
ax.set_ylabel('Carbon Price (EUR/tCO₂)')
ax.set_title('CN-ETS Price Scenarios vs EU ETS\n(EUR-denominated, stylised EU path)',
             fontsize=11, fontweight='bold')
ax.legend(fontsize=9, loc='upper left')
ax.set_xlim(2024, 2030)
ax.set_ylim(0, 95)
ax.tick_params(labelsize=9)

# Right: implied CBAM offset rate (for BF-BOF)
ax2 = axes[1]
for (label, vals), col in zip(scenarios.items(), sc_colors):
    offset = np.clip(vals / eu_central * 100, 0, 100)
    ax2.plot(years, offset, linewidth=2, linestyle='--', color=col, label=label)

ax2.scatter([2024], [13/65*100], color='black', s=60, zorder=5)
ax2.annotate(f'Current ~{13/65*100:.0f}%\n(CN-ETS EUR 13,\nEU ETS EUR 65)',
             xy=(2024, 13/65*100),
             xytext=(2025.2, 27), arrowprops=dict(arrowstyle='->', lw=1), fontsize=9)
ax2.set_xlabel('Year')
ax2.set_ylabel('CN-ETS / EU ETS Price Ratio (%)\n(= CBAM offset rate)')
ax2.set_title('Implied CBAM Offset Rate by Scenario\n(Authors\' scenarios)',
              fontsize=11, fontweight='bold')
ax2.legend(fontsize=9, loc='upper left')
ax2.set_xlim(2024, 2031)
ax2.set_ylim(0, 110)
ax2.tick_params(labelsize=9)

plt.suptitle('CN-ETS Convergence Scenarios and CBAM Offset Rate (2024–2030)',
             fontsize=12, fontweight='bold')
plt.tight_layout()
plt.savefig(f'{OUT_DIR}/figC_price_convergence.png', bbox_inches='tight', dpi=150)
plt.close()
print('Saved figC')


# ══════════════════════════════════════════════════════════════════════════════
# FIGURE D · Cement CCS Deployment + CBAM Breakeven (replaces §IV-F prose)
# ══════════════════════════════════════════════════════════════════════════════
# CCS status from GEM
ccs_raw   = china_cem['CCS/CCUS'].str.lower().str.strip()
yes_ccs   = (ccs_raw == 'yes').sum()
no_ccs    = (ccs_raw == 'no').sum()
other_ccs = len(china_cem) - yes_ccs - no_ccs

ef_cement = clinker_ratio * 0.825   # tCO2/t cement

# CCS cost assumption: 60–80 EUR/tCO2 captured (IEA range for cement CCS)
ccs_cost_lo, ccs_cost_hi = 60, 80

fig, axes = plt.subplots(1, 2, figsize=(12, 5))

# Left: deployment bar
ax = axes[0]
labels_ccs = ['CCS deployed\n(yes)', 'No CCS\n(no)', 'Unknown /\nN/A']
vals_ccs   = [yes_ccs, no_ccs, other_ccs]
colors_ccs = [GREEN, RED, GREY]
bars_ccs = ax.bar(labels_ccs, vals_ccs, color=colors_ccs, edgecolor='white', width=0.55)
for b, v in zip(bars_ccs, vals_ccs):
    ax.text(b.get_x() + b.get_width() / 2, v + 8,
            f'{v}\n({100*v/len(china_cem):.1f}%)',
            ha='center', va='bottom', fontsize=9.5, fontweight='bold')
ax.set_ylabel('Number of Operating Plants')
ax.set_title(f'CCS/CCUS Deployment Status\n(China cement, {len(china_cem)} operating plants, GEM Jul 2025)',
             fontsize=11, fontweight='bold')
ax.set_ylim(0, max(vals_ccs) * 1.25)
ax.text(0.5, 0.02,
        f'Only {yes_ccs} of {len(china_cem)} plants ({100*yes_ccs/len(china_cem):.1f}%) have CCS',
        transform=ax.transAxes, ha='center', va='bottom', fontsize=9, color='#D73027', style='italic',
        bbox=dict(boxstyle='round,pad=0.2', fc='white', ec='#D73027', alpha=0.85))

# Right: breakeven analysis
ax2 = axes[1]
eu_range   = np.linspace(40, 100, 200)
capture_rates = [0.70, 0.85, 0.90]
cr_colors     = ['#FC8D59', '#D73027', '#67001F']
cr_labels     = ['70% capture', '85% capture', '90% capture']

for rate, col, lab in zip(capture_rates, cr_colors, cr_labels):
    cbam_saving  = ef_cement * rate * eu_range          # EUR/t cement saved
    ax2.plot(eu_range, cbam_saving, color=col, linewidth=2, label=f'{lab}')

# CCS cost band (shaded region = cost range, anything above = net benefit)
ax2.axhspan(ccs_cost_lo * ef_cement * 0.85,
            ccs_cost_hi * ef_cement * 0.85,
            alpha=0.15, color='purple',
            label=f'Cement CCS cost range\n(~EUR {ccs_cost_lo}–{ccs_cost_hi}/tCO₂ captured)')

# Breakeven markers
for rate, col in zip([0.70, 0.85, 0.90], cr_colors):
    # breakeven: saving = cost_mid * ef * rate → EU_ETS = cost_mid
    be_lo = ccs_cost_lo
    be_hi = ccs_cost_hi
    ax2.axvspan(be_lo, be_hi, alpha=0.05, color=col)

ax2.axvline(65, color='black', linestyle='--', linewidth=1, alpha=0.6)
ax2.axvline(80, color=GREY,   linestyle='--', linewidth=1, alpha=0.6)
ax2.text(65.5, 2, 'EU ETS\n~65', fontsize=8, color='black')
ax2.text(80.5, 2, 'EU ETS\n~80', fontsize=8, color=GREY)

ax2.set_xlabel('EU ETS Price (EUR/tCO₂)')
ax2.set_ylabel('CBAM Liability Avoided by CCS (EUR/t cement)')
ax2.set_title(f'CBAM Savings from CCS by Capture Rate\n(clinker ratio = {clinker_ratio:.3f}, EF = {ef_cement:.3f} tCO₂/t)',
              fontsize=11, fontweight='bold')
ax2.legend(fontsize=8, loc='upper left')
ax2.set_xlim(40, 100)

plt.suptitle('Cement CCS — Current Deployment & CBAM Breakeven Incentive',
             fontsize=12, fontweight='bold')
plt.tight_layout()
plt.savefig(f'{OUT_DIR}/figD_cement_ccs.png', bbox_inches='tight', dpi=150)
plt.close()
print('Saved figD')

print('\nAll figures saved to output/figures/')
