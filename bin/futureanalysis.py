import pandas as pd
import matplotlib.pyplot as plt
import numpy as np


def analyze_german_bau_pathway(global_carbon_budget: pd.DataFrame,
                               global_emission_population: pd.DataFrame,
                               country_emission: pd.DataFrame,
                               temperature: str) -> None:
    """
    Evaluates Germany's Business-As-Usual (BAU) emission pathway against its allocated
    carbon budget for a specified temperature scenario.
    Displays a comparative projection plot and prints a detailed budget depletion analysis summary.

    Args:
        global_carbon_budget (pd.DataFrame): Allocated carbon budget data containing fair share values.
        global_emission_population (pd.DataFrame): Global demographic data used to calculate individual fair allowances.
        country_emission (pd.DataFrame): Historical annual emissions containing 'year' and 'emission'.
        temperature (str): The specific temperature scenario being analyzed (e.g., '1.5' or '2.0').
    """
    # 1. Data Extraction & Preparation
    deu_budget = global_carbon_budget[global_carbon_budget['country_code'] == 'DEU'].iloc[0]
    fair_share_gt = deu_budget['fair_share']

    emission_2023_row = country_emission[country_emission['year'] == 2023].iloc[0]
    annual_emission_2023_gt = emission_2023_row['emission'] / 1e9

    deu_pop_2024 = global_emission_population[(global_emission_population['country_code'] == 'DEU') & (global_emission_population['year'] == 2024)]['population'].values[0]

    avg_annual_fair_national_gt = fair_share_gt / 27
    individual_fair_allowance_total = (fair_share_gt * 1e9) / deu_pop_2024

    years_left = fair_share_gt / annual_emission_2023_gt
    depletion_date = 2023 + years_left

    # Format years_left into years and months
    left_y = int(years_left)
    left_m = int(round((years_left - left_y) * 12))
    if left_m == 12:
        left_y += 1
        left_m = 0

    # Format depletion_date into Month of Year string
    month_names = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]
    depletion_y = int(depletion_date)
    depletion_m_idx = min(int((depletion_date - depletion_y) * 12), 11)
    depletion_month_str = f"{month_names[depletion_m_idx]} of {depletion_y}"

    hist_years = country_emission['year'].values
    hist_emissions = country_emission['emission'].values / 1e9

    proj_years = np.arange(2024, 2041)
    bau_emissions = np.full(len(proj_years), annual_emission_2023_gt)
    fair_line = np.full(len(proj_years), avg_annual_fair_national_gt)

    # 2. Plotting
    FS = 12  # Base Font Size
    fig, ax = plt.subplots(figsize=(10, 6))

    # Professional Hex Color Palette
    color_historical = '#2c3e50'  # Dark Slate Gray
    color_bau = '#c0392b'         # Muted Dark Red
    color_fairshare = '#27ae60'   # Muted Green

    # Plot Lines with adjusted thickness
    ax.plot(hist_years, hist_emissions, color=color_historical, linewidth=2.5, label='Historical Emissions (2000-2023)')
    ax.plot(proj_years, bau_emissions, color=color_bau, linewidth=2.5, linestyle='--', label='BAU Projection (Keep 2023 Level)')
    ax.plot(proj_years, fair_line, color=color_fairshare, linewidth=2.5, label='Fair Annual Budget (Average)')

    # Shading the Gap
    ax.fill_between(proj_years, fair_line, bau_emissions, color=color_bau, alpha=0.08)

    # Draw a vertical line at the depletion date
    ax.axvline(x=depletion_date, color='purple', linestyle=':', linewidth=1.5, zorder=0)

    # Add text next to the vertical line
    ax.text(depletion_date + 0.5, annual_emission_2023_gt + 0.2,
            f'Budget Depleted\n{depletion_month_str}',
            color='purple', fontsize=FS, fontweight='bold')

    # Formatting & Labels
    ax.set_title(f'Germany: Carbon Budget Analysis ({temperature}°C Scenario)', fontsize=FS+4, fontweight='bold', pad=15)
    ax.set_xlabel('Year', fontsize=FS+1)

    # Using Matplotlib's math text for CO2 subscript
    ax.set_ylabel('Annual Emissions (GtCO$_2$)', fontsize=FS+1)

    ax.set_xticks(np.arange(2000, 2041, 5))
    ax.set_xlim(1999, 2040)
    ax.set_ylim(0, max(hist_emissions) * 1.15)

    ax.tick_params(axis='both', labelsize=FS)

    # Add labels directly above the lines instead of a legend
    # Adjust the +0.02 (Y offset) and X coordinates to fit perfectly
    ax.text(2008, hist_emissions[10] + 0.05, 'Historical Emissions', color=color_historical, fontsize=FS, fontweight='bold')
    ax.text(2025, bau_emissions[1] + 0.05, 'BAU Projection', color=color_bau, fontsize=FS, fontweight='bold')
    ax.text(2025, fair_line[1] + 0.05, 'Fair Annual Budget', color=color_fairshare, fontsize=FS, fontweight='bold')

    ax.spines['bottom'].set_linewidth(2.0)
    ax.spines['bottom'].set_color('black')
    ax.spines['left'].set_linewidth(2.0)
    ax.spines['left'].set_color('black')

    plt.show()

    # 3. Summary Results
    print("\n" + "="*60)
    print(f"  ANALYSIS SUMMARY FOR GERMANY (DEU) | {temperature}°C SCENARIO")
    print("="*60)
    print(f"  ● Allocated Fair Share (2024-2050)      : {fair_share_gt:.2f} GtCO2")
    print(f"  ● Current Annual Emission (2023)        : {annual_emission_2023_gt:.2f} GtCO2")
    print(f"  ● Time left under BAU                   : {left_y} years {left_m} months")
    print(f"  ● Actual Time (Depletion Date)          : {depletion_month_str}")
    print(f"  ● Individual fair allowance             : {individual_fair_allowance_total:.2f} tCO2 per person (Total until 2050)")
    print("="*60 + "\n")


def analyze_german_netzero_pathway(global_carbon_budget_1_5C: pd.DataFrame,
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

    ax.set_title('Germany: Committed Policy Emission Reduction Pathway', fontsize=FS+4, fontweight='bold', pad=15)
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
