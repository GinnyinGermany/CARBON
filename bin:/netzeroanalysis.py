import pandas as pd
import matplotlib.pyplot as plt
import numpy as np


def analyze_german_policy_pathway(global_carbon_budget_1_5C: pd.DataFrame,
                                  global_carbon_budget_2_0C: pd.DataFrame,
                                  country_emission: pd.DataFrame,
                                  emission_1990: float) -> None:
    """
    Evaluates Germany's committed climate policy pathway against its carbon debts
    and carbon budgets for both 1.5°C and 2.0°C scenarios.
    Displays a comparative projection plot and prints a detailed overshoot analysis table.

    Args:
        global_carbon_budget_1_5C (pd.DataFrame): Allocated carbon budget for the 1.5°C scenario.
        global_carbon_budget_2_0C (pd.DataFrame): Allocated carbon budget for the 2.0°C scenario.
        country_emission (pd.DataFrame): Historical annual emissions containing 'year' and 'emission'.
        emission_1990 (float): Germany's baseline emission level in 1990 (GtCO2) used for target reductions.
    """
    # 1. Extract Historical Data
    # e_: represent emission
    e_2023 = country_emission[country_emission['year'] == 2023]['emission'].iloc[0] / 1e9

    hist_data = country_emission[country_emission['year'].between(2000, 2023)]
    hist_years = hist_data['year'].values
    hist_emissions = hist_data['emission'].values / 1e9

    # 2. Calculate Policy Target Points
    e_2030 = emission_1990 * (1 - 0.65)
    e_2040 = emission_1990 * (1 - 0.88)
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
    german_carbon_budget_1_5C = global_carbon_budget_1_5C[global_carbon_budget_1_5C['country_code'] == 'DEU'].iloc[0]
    fair_share_1_5C = german_carbon_budget_1_5C['fair_share']
    carbon_debt_1_5C = german_carbon_budget_1_5C['debt']
    # Fair Share Overshoot: Cumulative Policy - Future Fair Share
    over_fair_share_1_5C = cumulative_policy - fair_share_1_5C
    over_true_1_5C = cumulative_policy - (fair_share_1_5C - carbon_debt_1_5C)
    years_equal_1_5C = over_true_1_5C / e_2023

    # --- 2.0°C Scenario ---
    german_carbon_budget_2_0C = global_carbon_budget_2_0C[global_carbon_budget_2_0C['country_code'] == 'DEU'].iloc[0]
    fair_share_2_0C = german_carbon_budget_2_0C['fair_share']
    carbon_debt_2_0C = german_carbon_budget_2_0C['debt']
    # Fair Share Overshoot: Cumulative Policy - Future Fair Share
    over_fair_share_2_0C = cumulative_policy - fair_share_2_0C
    over_true_2_0C = cumulative_policy - (fair_share_2_0C - carbon_debt_2_0C)
    years_equal_2_0C = over_true_2_0C / e_2023

    # 5. Plotting (Single Policy Pathway)
    FS = 12
    fig, ax = plt.subplots(figsize=(10, 6))

    color_historical = '#7F8C8D'
    color_policy = '#2980B9'

    ax.plot(hist_years, hist_emissions, color=color_historical, linewidth=2.5)
    ax.plot(proj_years, policy_emissions, color=color_policy, linewidth=3.0)
    ax.fill_between(proj_years, 0, policy_emissions, color=color_policy, alpha=0.1)

    ax.scatter(xp[1:4], fp[1:4], color='#2C3E50', s=80, zorder=5)

    ax.text(2010, hist_emissions[10] + 0.05, 'Historical Emissions', color=color_historical, fontsize=FS, fontweight='bold')
    ax.text(2028, policy_emissions[5] + 0.1, 'Committed Policy Pathway', color=color_policy, fontsize=FS, fontweight='bold')

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
    print("  ANALYSIS: GERMANY'S COMMITED PATHWAY VS GLOBAL FAIR SHARE (1.5°C vs 2.0°C)")
    print("=" * 80)
    print("  [1] Required Steepness of Policy Pathway")
    print(f"      ● 2024 - 2030 : {cagr_24_30:+.1f}% per year")
    print(f"      ● 2030 - 2040 : {cagr_30_40:+.1f}% per year")
    print("      ● 2040 - 2045 : 100% phase-out to Net-Zero")
    print(f"      ▶ Total Cumulative Emissions (2024-2050) : {cumulative_policy:.2f} GtCO2")
    print("-" * 80)
    print("  [2] The Reality Check: True Overshoot & Debt Comparison")
    print("      Metric                        | 1.5°C Target       | 2.0°C Target")
    print("      ------------------------------------------------------------------")
    print(f"      Future Fair Share (2024-2050) | {fair_share_1_5C:>6.2f} GtCO2      | {fair_share_2_0C:>6.2f} GtCO2")
    print(f"      Fair Share OVERSHOOT (Future) | {over_fair_share_1_5C:>6.2f} GtCO2      | {over_fair_share_2_0C:>6.2f} GtCO2")
    print(f"      Historical Debt (1970-2023)   | {carbon_debt_1_5C:>6.2f} GtCO2      | {carbon_debt_2_0C:>6.2f} GtCO2")
    print(f"      TRUE OVERSHOOT (Total CDR)    | {over_true_1_5C:>6.2f} GtCO2      | {over_true_2_0C:>6.2f} GtCO2")
    print("      ------------------------------------------------------------------")
    print(f"      ▶ Equivalent to (2023 basis)  | {years_equal_1_5C:>5.1f} Years       | {years_equal_2_0C:>5.1f} Years")
    print("=" * 80 + "\n")
