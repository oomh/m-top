"""
Customer Transfer Analysis Module

This module provides functionality to analyze M-Pesa customer-to-customer transfer transactions.
It includes visualization and analysis of transfer patterns, recipient distribution, and charges.

Features:
    - Analysis of both personal and business transfers
    - Handling of masked phone numbers in transfer data
    - Aggregation of transfer amounts by recipient
    - Visualization of top transfer recipients
    - Calculation of transfer charges and statistics

Dependencies:
    - pandas: For data manipulation
    - plotly.express: For interactive visualizations
    - millify: For number formatting
"""

import plotly.express as px
import pandas as pd

def customer_transfer_box(filtered_df, nlargest, color, template):
    """
    Analyze customer transfer transactions and create visualization dashboard.

    This function processes both personal and business transfers, handling masked 
    phone numbers and creating visualizations of transfer patterns.

    Args:
        filtered_df (pd.DataFrame): DataFrame containing M-Pesa transaction data with columns:
            - type_class: Transaction type classification
            - entity: Recipient name/identifier 
            - withdrawn: Transaction amount
            - type_desc: Transaction description
        nlargest (int): Number of top recipients to display in visualizations
        color (str): Color scale name for the visualization
        template (str): Plotly template name for consistent styling

    Returns:
        tuple: Contains:
            - plotly.Figure: Bar chart showing top transfer recipients
            - int: Total transfer amount
            - float: Total transfer charges
            - int: Total number of transfers
            - pd.DataFrame: Detailed transfer data by recipient

    Example:
        >>> fig, total, charges, count, data = customer_transfer_box(df, 10, 'viridis', 'plotly_white')
        >>> fig.show()
    """

    # Filter for transfer transactions and separate charges
    transferFrame = filtered_df[
        filtered_df["type_class"].str.contains("Customer Transfer", na=False)
    ]
    transferChargesFrame = transferFrame[transferFrame["type_desc"] == "of Funds Charge"]
    transferFrame = transferFrame[transferFrame["type_desc"] != "of Funds Charge"]

    # Clean up recipient names and handle masked phone numbers
    mask = transferFrame["entity"].str.contains(r"\*+", regex=True)
    try:
        # Extract actual name from masked format (e.g., "254*****123 John Doe" -> "John Doe")
        transferFrame.loc[mask, "entity"] = (
            transferFrame.loc[mask, "entity"].str.partition(" ")[2].str.title()
        )
    except Exception as e:
        # Fallback formatting for non-masked names
        transferFrame.loc[~mask, "entity"] = transferFrame.loc[~mask, "entity"].str.title()

    # Aggregate transfer data by recipient
    transferFrame = (
        transferFrame.groupby("entity")
        .agg(
            count=("withdrawn", "count"),  # Number of transfers per recipient
            sum=("withdrawn", "sum"),      # Total amount sent per recipient
        )
        .sort_values(by="sum", ascending=False)
        .reset_index()
    )

    # Get total number of transfers
    totalTransactions = transferFrame["count"].sum()

    # Calculate total transfer charges
    transferChargesFrame = (
        transferChargesFrame.groupby("type_class")
        .agg(sum=("withdrawn", "sum"))
        .sort_values(by="sum", ascending=False)
        .reset_index()
    ).iloc[0, 1]

    # Create bar chart visualization for top recipients
    topTransfer_fig = px.bar(
        transferFrame.head(nlargest).sort_values(by="sum", key=abs, ascending=True),
        x="sum",
        y="entity",
        color_continuous_scale=color,
        template=template,
        title=f"These are the top {nlargest} Individuals you sent money",
        hover_data="count",  # Show transfer count in hover tooltip
        text="sum",         # Display amount on bars
    ).update_layout(
        xaxis_title="",
        yaxis_title="",
        xaxis=dict(showticklabels=False),
        height=((nlargest - 1) * 100),  # Dynamic height based on number of merchants
        )

    # Configure hover and text display formats
    topTransfer_fig.update_traces(
        texttemplate="Ksh. %{value:,}",  # Format amounts with currency and commas
        hovertemplate="%{customdata} transfer(s) | %{x:,} Ksh | %{y}",
        textposition="auto",
    )

    # Calculate summary statistics
    totalspend = transferFrame["sum"].sum().astype(int)  # Total amount transferred
    totalcharges = transferChargesFrame  # Total transfer charges

    return (topTransfer_fig, totalspend, totalcharges, totalTransactions, transferFrame)