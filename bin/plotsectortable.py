import pandas as pd


def generate_sparkline(series: pd.Series) -> str:
    """
    Converts a time-series of numeric values into a line chart
    and creates sparklines for trend visualization.
    """
    data = series.dropna().tolist()
    if not data:
        return ""

    min_val, max_val = min(data), max(data)
    # Prevent division by zero if all values are identical
    if min_val == max_val:
        min_val, max_val = 0, max_val + 1

    # Define SVG canvas size
    width, height = 120, 25

    # Calculate spacing between points on the x-axis
    dx = width / (len(data) - 1) if len(data) > 1 else width

    # Generate SVG points
    points = []
    for i, val in enumerate(data):
        x = i * dx
        # Y-axis is inverted in SVG (0 is top)
        y = height - ((val - min_val) / (max_val - min_val) * height)
        points.append(f"{x},{y}")

    pts_str = " ".join(points)

    # Return HTML SVG string (Grey line with 2px thickness)
    return f'<svg width="{width}" height="{height}"><polyline points="{pts_str}" fill="none" stroke="#555555" stroke-width="2" stroke-linejoin="round"/></svg>'


def generate_sectoral_emissions_table(sector_emission: pd.DataFrame,
                                      start_year: int = 2000,
                                      end_year: int = 2023,
                                      top_n: int = 9) -> str:
    """
    Analyzes sectoral emission profiles across a specific timeframe to identify top polluters,
    calculate cumulative shares and growth rates, and generate an aggregated HTML summary table.

    Args:
        sector_emission (pd.DataFrame): Sectoral dataset containing 'year', 'sector_code', 'sector_name', and 'emission'.
        start_year (int): Start year for filtering the emission timeframe. Default is 2000.
        end_year (int): End year for filtering the emission timeframe. Default is 2023.
        top_n (int): Number of top individual sectors to distinctively display. Default is 9.

    Returns:
        str: A styled HTML table containing cumulative shares, embedded sparkline trends, and growth indicators.
    """
    # 1. Filter timeframe
    df_filtered = sector_emission[(sector_emission['year'] >= start_year) & (sector_emission['year'] <= end_year)].copy()

    # 2. Pivot data incorporating BOTH Sector Code and Sector Name
    pivot_df = df_filtered.pivot_table(
        index=['sector_code', 'sector_name'],
        columns='year',
        values='emission',
        aggfunc='sum'
    )

    # 3. Sort by the end_year
    pivot_df = pivot_df.sort_values(by=end_year, ascending=False)

    # 4. Slice into Top N and Others
    top_sectors = pivot_df.head(top_n).copy()

    # Calculate 'Others' and assign a MultiIndex so it matches the format
    remaining_count = len(pivot_df) - top_n
    others = pivot_df.iloc[top_n:].sum().to_frame().T

    # Indicate number of other sectors
    others_name = f'Other Sectors ({remaining_count} combined)'
    others.index = pd.MultiIndex.from_tuples([('N/A', others_name)], names=['sector_code', 'sector_name'])

    # 5. Combine Top N and Others
    final_df = pd.concat([top_sectors, others])

    # 6. Calculate Metrics
    cumulative_per_sector = final_df.loc[:, start_year:end_year].sum(axis=1)
    total_cumulative = cumulative_per_sector.sum()
    final_df['Cumulative Share (%)'] = ((cumulative_per_sector / total_cumulative) * 100).round(2)
    final_df['Growth Rate (%)'] = (((final_df[end_year] - final_df[start_year]) / final_df[start_year]) * 100).round(2)

    # 7. Apply HTML Arrows (Red for Increasing, Blue for Decreasing trend)
    final_df['Direction'] = final_df['Growth Rate (%)'].apply(
        lambda x: '<span style="color: red; font-weight: bold;">▲</span>' if x > 0 else '<span style="color: blue; font-weight: bold;">▼</span>'
    )

    # 8. Apply Sparklines
    title = f'Trend ({start_year}-{end_year})'
    final_df[title] = final_df.loc[:, start_year:end_year].apply(generate_sparkline, axis=1)

    # 9. Clean up layout
    result_columns = ['Cumulative Share (%)', title, 'Direction', 'Growth Rate (%)']
    result_table = final_df[result_columns].copy()
    result_table.columns.name = None

    # 10. Convert to HTML, allowing SVG and standard HTML tags to render safely
    html_output = result_table.to_html(escape=False, classes='table table-striped table-hover', border=0)

    return html_output
