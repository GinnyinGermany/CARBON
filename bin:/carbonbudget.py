import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


def calculate_adjusted_carbon_budgets(merged_global: pd.DataFrame,
                                      target_budget: float,
                                      hist_start: int = 1970,
                                      hist_end: int = 2023,
                                      future_start: int = 2024,
                                      future_end: int = 2050) -> pd.DataFrame:
    """
    Calculates the historical carbon debt, fair share of remaining budget,
    and the final adjusted carbon budget for each country.

    Args:
        merged_global (pd.DataFrame): The merged dataset containing emissions and population.
        target_budget (float): The remaining global carbon budget for the target year (e.g., 2024).
        hist_start (int): Start year for historical debt calculation. Default is 1970.
        hist_end (int): End year for historical debt calculation. Default is 2023.
        future_start (int): Start year for future fair share allocation. Default is 2024.
        future_end (int): End year for future fair share allocation. Default is 2050.

    Returns:
        pd.DataFrame: A dataframe sorted by adjusted budget containing the final calculations.
    """
    # Conversion factor: tonnes to Gigatonnes (Gt)
    TONNES_TO_GT = 1e9

    # =====================================================================
    # 1. Calculate Historical Carbon Debt
    # =====================================================================
    # Filter historical data
    hist_df = merged_global[merged_global['year'].between(hist_start, hist_end)]

    # Calculate global cumulative emissions (in Gt) and global cumulative population
    global_emi_hist = hist_df['emission'].sum() / TONNES_TO_GT
    global_pop_hist = hist_df['population'].sum()

    # Aggregate cumulative emissions (in Gt) and population by country
    country_hist = hist_df.groupby('country_code').agg(
        emi_hist_sum=('emission', lambda x: x.sum() / TONNES_TO_GT),
        pop_hist_sum=('population', 'sum')
    ).reset_index()

    # Calculate Carbon Debt per country
    country_hist['debt'] = country_hist['emi_hist_sum'] - (global_emi_hist * (country_hist['pop_hist_sum'] / global_pop_hist))

    # =====================================================================
    # 2. Allocate Fair Share of Remaining Budget
    # =====================================================================
    # Filter future projection data
    future_df = merged_global[merged_global['year'].between(future_start, future_end)]

    # Calculate global cumulative future population
    global_pop_future = future_df['population'].sum()

    # Aggregate cumulative future population by country
    country_future = future_df.groupby('country_code').agg(
        pop_future_sum=('population', 'sum')
    ).reset_index()

    # Calculate Fair Share per country using the target global budget
    country_future['fair_share'] = target_budget * (country_future['pop_future_sum'] / global_pop_future)

    # =====================================================================
    # 3. Calculate Final Adjusted Remaining Budget
    # =====================================================================
    # Merge the historical (Debt) and future (Fair Share) dataframes
    final_budget_df = pd.merge(
        country_hist[['country_code', 'debt']],
        country_future[['country_code', 'fair_share']],
        on='country_code',
        how='inner'
    )

    # Adjusted Budget = Fair Share - Debt
    final_budget_df['adjusted_budget'] = final_budget_df['fair_share'] - final_budget_df['debt']

    # Extract unique country codes and names from the original merged_global dataframe
    country_mapping = merged_global[['country_code', 'country_name_em']].drop_duplicates(subset=['country_code'], keep='first')

    # Merge the country names into the final budget dataframe
    final_budget_df = pd.merge(final_budget_df, country_mapping, on='country_code', how='left')

    # Reorder columns to put the country name first for better readability
    final_budget_df = final_budget_df[['country_name_em', 'country_code', 'debt', 'fair_share', 'adjusted_budget']]

    # Sort by adjusted budget to see which countries have the largest deficits or surpluses
    final_budget_df = final_budget_df.sort_values(by='adjusted_budget', ascending=True)

    # Return the final dataframe instead of printing
    return final_budget_df


def plot_germany_carbon_analysis(final_budget_df: pd.DataFrame,
                                 merged_global: pd.DataFrame,
                                 total_em: pd.DataFrame,
                                 temp: str) -> None:
    """
    Visualizes Germany's carbon budget status with a publication-ready single plot.
    Historical data is sourced directly from total_em.
    """
    # 1. Data Extraction & Preparation
    deu_budget = final_budget_df[final_budget_df['country_code'] == 'DEU'].iloc[0]
    fair_share_gt = deu_budget['fair_share']

    emission_2023_row = total_em[total_em['year'] == 2023].iloc[0]
    annual_emission_2023_gt = emission_2023_row['emission'] / 1e9

    deu_pop_2024 = merged_global[(merged_global['country_code'] == 'DEU') & (merged_global['year'] == 2024)]['population'].values[0]

    avg_annual_fair_national_gt = fair_share_gt / 27
    individual_fair_allowance_total = (fair_share_gt * 1e9) / deu_pop_2024

    years_left = fair_share_gt / annual_emission_2023_gt
    depletion_date = 2023 + years_left

    hist_years = total_em['year'].values
    hist_emissions = total_em['emission'].values / 1e9

    proj_years = np.arange(2024, 2041)
    bau_emissions = np.full(len(proj_years), annual_emission_2023_gt)
    fair_line = np.full(len(proj_years), avg_annual_fair_national_gt)

    # 2. Plotting (Publication Quality)
    FS = 12  # Base Font Size
    fig, ax = plt.subplots(figsize=(8, 5))

    # Professional Hex Color Palette (Muted tones)
    c_hist = '#2c3e50'  # Dark Slate Gray
    c_bau = '#c0392b'   # Muted Dark Red
    c_fair = '#27ae60'  # Muted Green

    # Plot Lines with adjusted thickness
    ax.plot(hist_years, hist_emissions, color=c_hist, linewidth=2.5, label='Historical Emissions (2000-2023)')
    ax.plot(proj_years, bau_emissions, color=c_bau, linewidth=2.5, linestyle='--', label='BAU Projection (Keep 2023 Level)')
    ax.plot(proj_years, fair_line, color=c_fair, linewidth=2.5, label='Fair Annual Budget (Average)')

    # Shading the Gap (Subtle alpha)
    ax.fill_between(proj_years, fair_line, bau_emissions, color=c_bau, alpha=0.08)

    # Draw a vertical line at the depletion date
    ax.axvline(x=depletion_date, color='purple', linestyle=':', linewidth=1.5, zorder=0)

    # Add text next to the vertical line
    ax.text(depletion_date + 0.5, annual_emission_2023_gt + 0.2,
            f'Budget Depleted\n{depletion_date:.1f}',
            color='purple', fontsize=FS, fontweight='bold')

    # Formatting & Labels
    ax.set_title(f'Germany: Carbon Budget Analysis ({temp}°C Scenario)', fontsize=FS+4, fontweight='bold', pad=15)
    ax.set_xlabel('Year', fontsize=FS+1)

    # Using Matplotlib's math text for CO2 subscript
    ax.set_ylabel('Annual Emissions (GtCO$_2$)', fontsize=FS+1)

    ax.set_xticks(np.arange(2000, 2041, 5))
    ax.set_xlim(1999, 2040)
    ax.set_ylim(0, max(hist_emissions) * 1.15)

    ax.tick_params(axis='both', labelsize=FS)
    # Add labels directly above the lines instead of a legend
    # Adjust the +0.02 (Y offset) and X coordinates to fit perfectly
    ax.text(2008, hist_emissions[10] + 0.05, 'Historical Emissions', color=c_hist, fontsize=FS, fontweight='bold')
    ax.text(2025, bau_emissions[1] + 0.05, 'BAU Projection', color=c_bau, fontsize=FS, fontweight='bold')
    ax.text(2025, fair_line[1] + 0.05, 'Fair Annual Budget', color=c_fair, fontsize=FS, fontweight='bold')

    ax.spines['bottom'].set_linewidth(2.0)
    ax.spines['bottom'].set_color('black')
    ax.spines['left'].set_linewidth(2.0)
    ax.spines['left'].set_color('black')

    plt.show()

    # 3. Summary Results
    print("\n" + "="*60)
    print(f"  ANALYSIS SUMMARY FOR GERMANY (DEU) | {temp}°C SCENARIO")
    print("="*60)
    print(f"  ● Allocated Fair Share (2024-2050)      : {fair_share_gt:.2f} GtCO2")
    print(f"  ● Current Annual Emission (2023)        : {annual_emission_2023_gt:.2f} GtCO2")
    print(f"  ● Time left under BAU                   : {years_left:.2f} years")
    print(f"  ● Actual Time (Depletion Date)          : {depletion_date:.1f}")
    print(f"  ● Individual fair allowance             : {individual_fair_allowance_total:.2f} tCO2 per person (Total until 2050)")
    print("="*60 + "\n")
