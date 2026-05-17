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
    global_carbon_budget = pd.merge(
        country_hist[['country_code', 'debt']],
        country_future[['country_code', 'fair_share']],
        on='country_code',
        how='inner'
    )

    # Adjusted Budget = Fair Share - Debt
    global_carbon_budget['adjusted_budget'] = global_carbon_budget['fair_share'] - global_carbon_budget['debt']

    # Extract unique country codes and names from the original merged_global dataframe
    country_mapping = merged_global[['country_code', 'country_name_em']].drop_duplicates(subset=['country_code'], keep='first')

    # Merge the country names into the final budget dataframe
    global_carbon_budget = pd.merge(global_carbon_budget, country_mapping, on='country_code', how='left')

    # Reorder columns to put the country name first for better readability
    global_carbon_budget = global_carbon_budget[['country_name_em', 'country_code', 'debt', 'fair_share', 'adjusted_budget']]

    # Sort by adjusted budget to see which countries have the largest deficits or surpluses
    global_carbon_budget = global_carbon_budget.sort_values(by='adjusted_budget', ascending=True)

    # Return the final dataframe instead of printing
    return global_carbon_budget

