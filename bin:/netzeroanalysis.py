import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

# ---------------------------------------------------------
# Set Modern Academic/Consulting Style
# ---------------------------------------------------------
plt.rcParams.update({
    'font.family': 'sans-serif',
    'font.sans-serif': ['Arial', 'Helvetica', 'DejaVu Sans'],
    'axes.spines.top': False,
    'axes.spines.right': False,
    'axes.grid': False,
    'figure.dpi': 300
})

def analyze_policy_pathway(result_15, result_20, total_em, e_1990_gt):
    # 1. Extract Historical Data
    e_2023 = total_em[total_em['year'] == 2023]['emission'].iloc[0] / 1e9
    
    hist_df = total_em[total_em['year'].between(2000, 2023)]
    hist_years = hist_df['year'].values
    hist_emissions = hist_df['emission'].values / 1e9

    # 2. Calculate Policy Target Points
    e_2030 = e_1990_gt * (1 - 0.65)
    e_2040 = e_1990_gt * (1 - 0.88)
    e_2045 = 0.0

    proj_years = np.arange(2024, 2051)
    xp = [2023, 2030, 2040, 2045, 2050]
    fp = [e_2023, e_2030, e_2040, e_2045, 0.0]
    policy_emissions = np.interp(proj_years, xp, fp)

    # 3. Calculate CAGR (Steepness) & Cumulative
    cagr_24_30 = ((e_2030 / e_2023) ** (1 / (2030 - 2023)) - 1) * 100
    cagr_30_40 = ((e_2040 / e_2030) ** (1 / (2040 - 2030)) - 1) * 100
    cumulative_policy = policy_emissions.sum()

    # 4. Extract Budgets and Calculate Overshoots
    # --- 1.5°C Scenario ---
    deu_15 = result_15[result_15['country_code'] == 'DEU'].iloc[0]
    fs_15 = deu_15['fair_share']
    debt_15 = deu_15['debt']
    # Fair Share Overshoot: Cumulative Policy - Future Fair Share
    over_fs_15 = cumulative_policy - fs_15 
    true_over_15 = cumulative_policy - (fs_15 - debt_15)
    years_eq_15 = true_over_15 / e_2023

    # --- 2.0°C Scenario ---
    deu_20 = result_20[result_20['country_code'] == 'DEU'].iloc[0]
    fs_20 = deu_20['fair_share']
    debt_20 = deu_20['debt']
    # Fair Share Overshoot: Cumulative Policy - Future Fair Share
    over_fs_20 = cumulative_policy - fs_20 
    true_over_20 = cumulative_policy - (fs_20 - debt_20)
    years_eq_20 = true_over_20 / e_2023

    # 5. Plotting (Single Policy Pathway)
    FS = 12
    fig, ax = plt.subplots(figsize=(10, 6))

    c_hist = '#7F8C8D'
    c_pol = '#2980B9'

    ax.plot(hist_years, hist_emissions, color=c_hist, linewidth=2.5)
    ax.plot(proj_years, policy_emissions, color=c_pol, linewidth=3.0)
    ax.fill_between(proj_years, 0, policy_emissions, color=c_pol, alpha=0.1)

    ax.scatter(xp[1:4], fp[1:4], color='#2C3E50', s=80, zorder=5)
    
    ax.text(2010, hist_emissions[10] + 0.05, 'Historical Emissions', color=c_hist, fontsize=FS, fontweight='bold')
    ax.text(2028, policy_emissions[5] + 0.1, 'Committed Policy Pathway', color=c_pol, fontsize=FS, fontweight='bold')

    ax.text(2030, e_2030 + 0.05, '2030\n(-65%)', ha='center', fontsize=FS-1, fontweight='bold')
    ax.text(2040, e_2040 + 0.05, '2040\n(-88%)', ha='center', fontsize=FS-1, fontweight='bold')
    ax.text(2045, 0.05, '2045\n(Net-Zero)', ha='center', fontsize=FS-1, fontweight='bold')

    ax.spines['bottom'].set_linewidth(2.0)
    ax.spines['bottom'].set_color('black')
    ax.spines['left'].set_linewidth(2.0)
    ax.spines['left'].set_color('black')

    ax.set_title('Germany: Committed Policy Pathway & Cumulative Emissions', fontsize=FS+4, fontweight='bold', pad=15)
    ax.set_xlabel('Year', fontsize=FS+1)
    ax.set_ylabel('Annual Emissions (GtCO$_2$)', fontsize=FS+1) 
    
    ax.set_xticks(np.arange(2000, 2051, 5))
    ax.set_xlim(1999, 2050)
    ax.set_ylim(0, max(hist_emissions) * 1.15)
    ax.tick_params(axis='both', labelsize=FS, width=2.0)

    plt.tight_layout()
    plt.show()

    # 6. Comparative Print Output (The Reality Check)
    print("=" * 80)
    print(f"  ANALYSIS: GERMANY'S COMMITED PATHWAY VS GLOBAL FAIR SHARE (1.5°C vs 2.0°C)")
    print("=" * 80)
    print("  [1] Required Steepness of Policy Pathway")
    print(f"      ● 2024 - 2030 : {cagr_24_30:+.1f}% per year")
    print(f"      ● 2030 - 2040 : {cagr_30_40:+.1f}% per year")
    print(f"      ● 2040 - 2045 : 100% phase-out to Net-Zero")
    print(f"      ▶ Total Cumulative Emissions (2024-2050) : {cumulative_policy:.2f} GtCO2")
    print("-" * 80)
    print("  [2] The Reality Check: True Overshoot & Debt Comparison")
    print(f"      Metric                        | 1.5°C Target       | 2.0°C Target")
    print(f"      ------------------------------------------------------------------")
    print(f"      Future Fair Share (2024-2050) | {fs_15:>6.2f} GtCO2      | {fs_20:>6.2f} GtCO2")
    print(f"      Fair Share OVERSHOOT (Future) | {over_fs_15:>6.2f} GtCO2      | {over_fs_20:>6.2f} GtCO2")
    print(f"      Historical Debt (1970-2023)   | {debt_15:>6.2f} GtCO2      | {debt_20:>6.2f} GtCO2")
    print(f"      TRUE OVERSHOOT (Total CDR)    | {true_over_15:>6.2f} GtCO2      | {true_over_20:>6.2f} GtCO2")
    print(f"      ------------------------------------------------------------------")
    print(f"      ▶ Equivalent to (2023 basis)  | {years_eq_15:>5.1f} Years       | {years_eq_20:>5.1f} Years")
    print("=" * 80 + "\n")