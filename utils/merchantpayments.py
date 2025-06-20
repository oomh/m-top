"""
Merchant Payments Analysis Module

This module provides functionality to analyze M-Pesa merchant payment transactions (Buy Goods).
It includes visualization and statistical analysis of payment patterns, merchant distribution,
and transaction volumes.

Main function:
    merchant_box: Creates visualizations and analytics for merchant payment transactions

Dependencies:
    - plotly.express: For creating interactive visualizations
"""

import plotly.express as px


def merchant_box(
    filtered_df,
    nlargest,
    color,
    template,
):
    """
    Analyze merchant payment transactions and create visualization dashboard.

    This function processes M-Pesa merchant payment transactions to generate insights
    about spending patterns, top merchants, and transaction volumes.

    Args:
        filtered_df (pd.DataFrame): DataFrame containing M-Pesa transaction data with columns:
            - type_class: Transaction type classification
            - entity: Merchant name/identifier
            - withdrawn: Transaction amount
        nlargest (int): Number of top merchants to display in visualizations
        color (str): Color scale name for the visualization (plotly color scale)
        template (str): Plotly template name for consistent styling

    Returns:
        tuple: Contains:
            - plotly.Figure: Bar chart showing top merchant payments
            - float: Total spend amount across all merchants
            - float: Total transaction charges
            - int: Total number of merchant transactions
            - pd.DataFrame: Detailed merchant transaction data

    Example:
        >>> fig, total, charges, count, data = merchant_box(df, 10, 'viridis', 'plotly_white')
        >>> fig.show()
    """

    # Filter and aggregate merchant payment transactions
    merchantFrame = (
        filtered_df[filtered_df["type_class"].str.contains("Merchant Payment")]
        .groupby("entity")
        .agg(
            count=("withdrawn", "count"),  # Number of transactions per merchant
            sum=("withdrawn", "sum"),  # Total amount spent per merchant
        )
        .sort_values(by="sum", ascending=False)
        .reset_index()
    )

    # Create bar chart visualization for top merchants
    topMerchant_fig = px.bar(
        merchantFrame.head(nlargest).sort_values(by="sum", ascending=True),
        x="sum",
        y="entity",
        color_continuous_scale=color,
        template=template,
        title=f"These are the top {nlargest} merchants you paid with Buy Goods",
        hover_data="count",  # Show transaction count in hover tooltip
        text="sum",  # Display amount on bars
    ).update_layout(
        xaxis_title="",
        yaxis_title="",
        dragmode = False,
        xaxis=dict(showticklabels=False),
        height=((nlargest - 1) * 100),  # Dynamic height based on number of merchants
    )

    # Configure hover and text display formats
    topMerchant_fig.update_traces(
        texttemplate="Ksh. %{value:,}",  # Format amounts with currency and commas
        hovertemplate="%{customdata} transaction(s) | %{x:,} Ksh | %{y}",
        textposition="auto",
    )

    # Calculate summary statistics
    totalspend = merchantFrame["sum"].sum()  # Total amount spent across all merchants
    
    # Calculate total merchant payment charges
    totalcharges = round(
        float(filtered_df[filtered_df["type_class"]
                        .str.contains("Pay Merchant")]
                ["withdrawn"].sum()), 2,)

    # Get total number of merchant transactions
    merchantCount = merchantFrame["count"].sum()

    return topMerchant_fig, totalspend, totalcharges, merchantCount, merchantFrame
