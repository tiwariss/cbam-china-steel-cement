# The EU Carbon Border Adjustment Mechanism and China's Strategic Response: Carbon Pricing Realignment and Industrial Decarbonization

**Tang Qian · Sirawit Tangchitwatthanakon · Liu Xianghui**  
The Hong Kong University of Science and Technology (Guangzhou)  
IPEN6100G Final Project

---

## Abstract

This paper analyses the CBAM liability exposure of China's steel and cement sectors under the EU's Carbon Border Adjustment Mechanism, and examines China's strategic decarbonization response through the lens of CN-ETS price convergence. Using plant-level data from the Global Energy Monitor (GEM) Iron & Steel Tracker (March 2026), Cement & Concrete Tracker (July 2025), and Global Integrated Power Tracker (March 2026), we quantify CBAM net liability as a function of the EU–CN carbon price gap, assess CCS deployment readiness, and model three CN-ETS convergence scenarios through 2030.

**Key findings:**
- At EU ETS = EUR 65 and CN-ETS = EUR 13, BF-BOF steel faces **EUR 136.5/t** CBAM liability vs EUR 6.5/t for EAF (Scope 1 only) and EUR 40.8/t for cement
- China's 83.1% BF-BOF share (835.7 Mtpa) creates structural CBAM exposure far exceeding peer economies
- Only 4 of 1,016 operating cement plants (0.4%) have CCS; cement CCS becomes economically viable above EUR 60–80/tCO₂ EU ETS price
- Under the moderate scenario (CN-ETS → EUR 60 by 2030), the offset rate reaches ~83%, sharply reducing net liability but requiring sustained ETS reform
- Monte Carlo robustness checks (N = 10,000) confirm central estimates are stable under emission factor uncertainty

---

## Repository Structure

```
├── resources/
│   └── data/                                             # Raw source files (GEM trackers)
│       ├── gem_steel_units_2026.xlsx
│       ├── gem_iron_units_2026.xlsx
│       ├── gem_steel_plants_2026.xlsx
│       ├── gem_cement_2025.xlsx
│       ├── gem_power_2026.xlsx
│       ├── gem_hydro_2026.xlsx
│       └── *.html                                        # Web-archived reference pages
├── output/
│   └── figures/                                          # All output plots (PNG)
├── code/
│   ├── cbam_analysis.ipynb                              # Main analysis notebook
│   ├── build_figures.py                                 # Standalone figure generation
│   ├── regen_notebook_figs.py                           # Regenerate fig2, fig4, fig9
│   └── build_notebook.py                                # Regenerate the notebook from source
└── paper.pdf                                             # Full paper
```

---

## Data Sources

| Dataset | Source | Coverage |
|---------|--------|----------|
| Iron & Steel Tracker (unit-level) | [Global Energy Monitor](https://globalenergymonitor.org/projects/global-steel-plant-tracker/) | March 2026 |
| Iron & Steel Tracker (plant-level) | Global Energy Monitor | March 2026 |
| Cement & Concrete Tracker | [Global Energy Monitor](https://globalenergymonitor.org/projects/global-cement-and-concrete-tracker/) | July 2025 |
| Integrated Power Tracker | [Global Energy Monitor](https://globalenergymonitor.org/projects/global-integrated-power-tracker/) | March 2026 |
| CN-ETS prices | MEE / Shanghai Environment & Energy Exchange | 2024 |
| EU ETS prices | EU ETS market | 2024–2025 |
| Emission factors | IEA ETP 2023; IPCC 2006 Vol. 3; MEE 2023 | — |

---

## Methods

**CBAM liability model** (Equation 1):

```
CBAM Liability_i = max(0, EF_i × (P^EU - P^CN))
```

| Sector | Emission Factor | Scope |
|--------|----------------|-------|
| BF-BOF steel | 2.10 tCO₂/t | Scope 1 |
| EAF steel | 0.10 tCO₂/t | Scope 1 only (CBAM-applicable; Reg. EU 2023/956) |
| Cement | 0.627 tCO₂/t | Scope 1 (GEM clinker ratio × IPCC 2006) |

**Uncertainty:** Monte Carlo analysis (N = 10,000) with triangular distributions on emission factors calibrated to IEA/IPCC source ranges. Results confirm central estimates are stable (CV < 5%).

---

## How to Run

**Requirements:**
```
pandas numpy matplotlib seaborn openpyxl scipy jupyter
```

**1. Set up environment:**
```bash
conda env create -f environment.yml
conda activate cbam-analysis
```
or:
```bash
pip install -r requirements.txt
```

**2. Main analysis notebook:**
```bash
jupyter notebook code/cbam_analysis.ipynb
```

**3. Regenerate standalone figures:**
```bash
python code/build_figures.py
python code/regen_notebook_figs.py
```

**4. Rebuild notebook from source:**
```bash
python code/build_notebook.py
```

---

## Keywords

CBAM · carbon border adjustment mechanism · China · steel · cement · CN-ETS · EU ETS · carbon pricing · decarbonization · GEM · emission factor · CCS
