"""
Airtime Purchase Analysis Module

This module provides functionality to analyze M-Pesa airtime purchase transactions.
It includes visualization and analysis of airtime spending patterns and volumes.

Functions:
    airtime_box: Creates visualizations and analytics for airtime purchases
"""

import plotly.express as px


def airtime_box(filtered_df, nlargest, color, template):
    """
    Analyze airtime purchase transactions and create visualization.

    Args:
        filtered_df (pd.DataFrame): DataFrame containing M-Pesa transaction data with columns:
            - type_class: Transaction type classification
            - entity: Provider/recipient name
            - withdrawn: Transaction amount
        nlargest (int): Number of top entries to display
        color (str): Color scale name for the visualization
        template (str): Plotly template name for consistent styling

    Returns:
        tuple: Contains:
            - plotly.Figure: Bar chart showing airtime purchases by provider
            - int: Total airtime purchase amount
    """

    # Filter and aggregate airtime transactions
    airtimeFrame = (
        filtered_df[filtered_df["type_class"].str.contains("Airtime", na=False)]
        .groupby("entity")
        .agg(
            count=("withdrawn", "count"),  # Number of purchases per provider
            sum=("withdrawn", "sum"),  # Total amount spent per provider
        )
        .sort_values(by="sum")
        .reset_index()
    )

    # Create bar chart visualization
    topAirtime_fig = px.pie(
        airtimeFrame.nlargest(nlargest, "sum").sort_values(by="sum", ascending=False),
        values="sum",
        names="entity",
        # color_discrete_sequence=px.colors.sequential[color],
        template=template,
        title="Airtime Purchases",
        hover_data=["count"],  # Show purchase count in hover tooltip
    ).update_layout(
        height=500  # Fixed height since pie chart doesn't need dynamic sizing
    )

    # Configure hover and text display formats
    topAirtime_fig.update_traces(
        texttemplate="Ksh. %{value:,}",  # Format amounts with currency and commas
        hovertemplate="%{customdata} transaction(s) | %{x:,} Ksh | %{y}",
        textposition="auto",
    )

    # Calculate total airtime spend
    totalairtime = airtimeFrame["sum"].sum().astype(int)
    totalairtimetransactions = airtimeFrame["count"].sum()

    return topAirtime_fig, totalairtime, totalairtimetransactions, airtimeFrame
