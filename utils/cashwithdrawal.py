"""
Cash Withdrawal Analysis Module

This module provides functionality to analyze M-Pesa cash withdrawal transactions.
It includes visualization and analysis of withdrawal patterns, locations, and charges.

Functions:
    cash_withdrawal_box: Creates visualizations and analytics for cash withdrawals
"""

import plotly.express as px


def cash_withdrawal_box(filtered_df, nlargest, color, template):
    """
    Analyze cash withdrawal transactions and create visualization.

    Args:
        filtered_df (pd.DataFrame): DataFrame containing M-Pesa transaction data with columns:
            - type_class: Transaction type classification
            - entity: Agent/ATM location
            - withdrawn: Transaction amount
        nlargest (int): Number of top locations to display
        color (str): Color scale name for the visualization
        template (str): Plotly template name for consistent styling

    Returns:
        tuple: Contains:
            - plotly.Figure: Bar chart showing top withdrawal locations
            - int: Total withdrawal amount
            - float: Total withdrawal charges
            - int: Total number of withdrawals
            - pd.DataFrame: Detailed withdrawal location data
    """

    # Filter and aggregate withdrawal transactions
    withdrawalFrame = (
        filtered_df[filtered_df["type_class"].str.contains("Customer Withdrawal", na=False)]
        .groupby("entity")
        .agg(
            count=("withdrawn", "count"),  # Number of withdrawals per location
            sum=("withdrawn", "sum"),  # Total amount withdrawn per location
        )
        .sort_values(by="sum", ascending=False)
        .reset_index()
    )

    # Create bar chart visualization
    topWithdrawal_fig = px.bar(
        withdrawalFrame.head(nlargest).sort_values(by="sum", ascending=True),
        x="sum",
        y="entity",
        color_continuous_scale=color,
        template=template,
        title="Cash Withdrawals by Location",
        hover_data="count",  # Show withdrawal count in hover tooltip
        text="sum",  # Display amount on bars
    ).update_layout(
        xaxis_title="",
        yaxis_title="",
        xaxis=dict(showticklabels=False),
        height=((nlargest - 1) * 100),  # Dynamic height based on number of merchants
    )

    # Configure hover and text display formats
    topWithdrawal_fig.update_traces(
        texttemplate="Ksh. %{value:,}",  # Format amounts with currency and commas
        hovertemplate="%{customdata} transaction(s) | %{x:,} Ksh | %{y}",
        textposition="auto",
    )

    # Calculate summary statistics
    totalwithdrawal = withdrawalFrame["sum"].sum().astype(int)
    
    # Calculate total withdrawal charges
    totalcharges = round(
        float(
            filtered_df[filtered_df["type_class"].str.contains("Cash Withdrawal", na=False)][
                "withdrawn"
            ].sum()
        ),
        1,
    )

    # Get total number of withdrawals
    totalWithdrawals = withdrawalFrame["count"].sum()

    return (
        topWithdrawal_fig,
        totalwithdrawal,
        totalcharges,
        totalWithdrawals,
        withdrawalFrame,
    )
