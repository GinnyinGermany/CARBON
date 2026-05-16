import pandas as pd
import plotly.express as px


def plot_global_carbon_debt_map(global_carbon_budget: pd.DataFrame,
                                country_code_column: str,
                                carbon_debt_column: str,
                                country_name_column: str = 'country_name_em',
                                title: str = "Global Carbon Debt: Geographic Distribution (1.5°C Target)"):
    """
    Plots a interactive global choropleth map of carbon debt.
    Uses a color scale centered at zero (Debt in Red, Surplus in Blue).
    Hovering over a country displays its Name, Carbon Debt, and Global Ranking.

    Args:
        global_carbon_budget (pd.DataFrame): Dataframe containing global carbon budget analysis.
        country_code_column (str): Column name containing country codes (e.g., 'DEU').
        carbon_debt_column (str): Column name containing the carbon debt values to plot.
        country_name_column (str): Column name containing the full country names for the tooltip.
        title (str): Title of the map.

    Returns:
        plotly.graph_objs._figure.Figure: The Plotly figure object containing the interactive map.
    """

    # Basic parameter validation
    assert country_code_column in global_carbon_budget.columns, f"Column '{country_code_column}' not found in input DataFrame."
    assert carbon_debt_column in global_carbon_budget.columns, f"Column '{carbon_debt_column}' not found in input DataFrame."
    assert country_name_column in global_carbon_budget.columns, f"Column '{country_name_column}' not found in input DataFrame."

    # 0. Data Validation & Sanity Check Pipeline
    total_input_countries = len(global_carbon_budget)

    # Check for missing ISO codes
    valid_country_codes = global_carbon_budget.dropna(subset=[country_code_column]).copy()
    dropped_iso_count = total_input_countries - len(valid_country_codes)
    if dropped_iso_count > 0:
        print(f"Sanity Check Warning: {dropped_iso_count} rows dropped due to missing ISO codes.")

    # Check for missing debt values and explicitly list the dropped countries
    plot_df = valid_country_codes.dropna(subset=[carbon_debt_column]).copy()
    dropped_country_count = len(valid_country_codes) - len(plot_df)
    if dropped_country_count > 0:
        missing_countries = valid_country_codes[valid_country_codes[carbon_debt_column].isna()][country_name_column].tolist()
        print(f"Sanity Check Warning: {dropped_country_count} countries dropped due to missing '{carbon_debt_column}' values:")
        print(f" -> {missing_countries}")

    print(f"Sanity Check Passed: {len(plot_df)} out of {total_input_countries} records are ready for mapping.\n")

    # 1. Prepare Data: Calculate global ranking based on carbon debt
    plot_df = global_carbon_budget.copy()
    plot_df['Global_Rank'] = plot_df[carbon_debt_column].rank(ascending=False, method='min')

    # Clip extreme outliers to maintain a balanced color scale
    vmax_val = plot_df[carbon_debt_column].quantile(0.95) if plot_df[carbon_debt_column].quantile(0.95) > 0 else plot_df[carbon_debt_column].max()
    vmin_val = plot_df[carbon_debt_column].quantile(0.05) if plot_df[carbon_debt_column].quantile(0.05) < 0 else plot_df[carbon_debt_column].min()

    # 2. Plot the interactive choropleth map using Plotly Express
    fig = px.choropleth(
        plot_df,
        locations=country_code_column,
        color=carbon_debt_column,
        hover_name=country_name_column,
        hover_data={
            country_code_column: False,
            carbon_debt_column: ':.2f',
            'Global_Rank': True
        },
        color_continuous_scale='RdBu_r',
        range_color=[vmin_val, vmax_val],
        title=title
    )

    # 3. Layout Configuration
    fig.update_layout(
        title={'x': 0.5, 'xanchor': 'center', 'font': {'size': 20}},
        geo=dict(
            projection_type='equirectangular',
            showframe=False,
            showcoastlines=True,
            coastlinecolor="rgba(0,0,0,0.2)",
            showland=True,
            landcolor="#e0e0e0",
        ),
        coloraxis_colorbar=dict(
            title="Carbon Debt (Gt CO2)",
            title_side="top",
            orientation="h",
            y=-0.1,
            x=0.5,
            xanchor="center",
            yanchor="top",
            len=0.5,
            thickness=15
        ),
        margin={"r": 0, "t": 50, "l": 0, "b": 0}
    )

    return fig
