import pandas as pd
import plotly.express as px


def plot_global_carbon_debt_map(analysis_df: pd.DataFrame,
                                iso_col: str,
                                debt_col: str,
                                name_col: str = 'country_name_em',
                                title: str = "Global Carbon Debt: Geographic Distribution (1.5°C Target)",
                                output_path: str = None):
    """
    Plots a interactive global choropleth map of carbon debt.
    Uses a color scale centered at zero (Debt in Red, Surplus in Blue).
    Hovering over a country displays its Name, Carbon Debt, and Global Ranking.

    Args:
        analysis_df (pd.DataFrame): Dataframe containing the analysis results.
        iso_col (str): Column name containing ISO Alpha-3 country codes (e.g., 'DEU').
        debt_col (str): Column name containing the carbon debt values to plot.
        name_col (str): Column name containing the full country names for the tooltip.
        title (str): Title of the map.
        output_path (str, optional): Path to save the map as an interactive HTML file (e.g., '../results/map.html').

    Returns:
        plotly.graph_objs._figure.Figure: The Plotly figure object containing the interactive map.
    """

    # Basic parameter validation
    assert iso_col in analysis_df.columns, f"Column '{iso_col}' not found in input DataFrame."
    assert debt_col in analysis_df.columns, f"Column '{debt_col}' not found in input DataFrame."
    assert name_col in analysis_df.columns, f"Column '{name_col}' not found in input DataFrame."

    # 0. Data Validation & Sanity Check Pipeline
    total_input_countries = len(analysis_df)

    # Check for missing ISO codes
    valid_iso_df = analysis_df.dropna(subset=[iso_col]).copy()
    dropped_iso_count = total_input_countries - len(valid_iso_df)
    if dropped_iso_count > 0:
        print(f"Sanity Check Warning: {dropped_iso_count} rows dropped due to missing ISO codes.")

    # Check for missing debt values and explicitly list the dropped countries
    plot_df = valid_iso_df.dropna(subset=[debt_col]).copy()
    dropped_debt_count = len(valid_iso_df) - len(plot_df)
    if dropped_debt_count > 0:
        missing_countries = valid_iso_df[valid_iso_df[debt_col].isna()][name_col].tolist()
        print(f"Sanity Check Warning: {dropped_debt_count} countries dropped due to missing '{debt_col}' values:")
        print(f" -> {missing_countries}")

    print(f"Sanity Check Passed: {len(plot_df)} out of {total_input_countries} records are ready for mapping.\n")

    # 1. Prepare Data: Calculate global ranking based on carbon debt
    plot_df = analysis_df.copy()
    plot_df['Global_Rank'] = plot_df[debt_col].rank(ascending=False, method='min')

    # Clip extreme outliers to maintain a balanced color scale
    vmax_val = plot_df[debt_col].quantile(0.95) if plot_df[debt_col].quantile(0.95) > 0 else plot_df[debt_col].max()
    vmin_val = plot_df[debt_col].quantile(0.05) if plot_df[debt_col].quantile(0.05) < 0 else plot_df[debt_col].min()

    # 2. Plot the interactive choropleth map using Plotly Express
    fig = px.choropleth(
        plot_df,
        locations=iso_col,
        color=debt_col,
        hover_name=name_col,
        hover_data={
            iso_col: False,
            debt_col: ':.2f',
            'Global_Rank': True
        },
        color_continuous_scale='RdBu_r',
        range_color=[vmin_val, vmax_val],
        title=title
    )

    # 3. Aesthetics & Layout Configuration
    fig.update_layout(
        title={'x': 0.5, 'xanchor': 'center', 'font': {'size': 20}},
        geo=dict(
            projection_type='equirectangular',  # Use equirectangular projection for a full rectangular map
            showframe=False,                    # Remove the outer circular frame
            showcoastlines=True,
            coastlinecolor="rgba(0,0,0,0.2)",
            showland=True,
            landcolor="#e0e0e0",
        ),
        coloraxis_colorbar=dict(
            title="Carbon Debt (Gt CO2)",
            title_side="top",                   # Place the title neatly above the colorbar
            orientation="h",
            y=-0.1,                             # Maintain appropriate spacing below the map
            x=0.5,                              # Align the colorbar to the horizontal center
            xanchor="center",
            yanchor="top",
            len=0.5,                            # Shorten the colorbar length for a refined look
            thickness=15                        # Reduce the thickness of the colorbar
        ),
        margin={"r": 0, "t": 50, "l": 0, "b": 0}  # Completely remove unnecessary margins to maximize map size
    )

    # 4. Save or return figure
    if output_path:
        fig.write_html(output_path)
        print(f"Interactive map successfully saved to: {output_path}")

    return fig
