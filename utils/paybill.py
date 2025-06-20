import plotly.express as px


def paybill_box(
    filtered_df,
    nlargest,
    color,
    template,
):
    """Analyze paybill transactions and create visualization.

    Args:
        filtered_df (pd.DataFrame): DataFrame containing transaction data
        nlargest (int): Number of top recipients to display
        color (str): Color scale for the visualization
        template (str): Plotly template name

    Returns:
        tuple: Contains:
            - plotly.Figure: Bar chart of top recipients
            - plotly.Figure: Histogram of transaction amounts
            - str: Total sent amount (formatted)
            - int: Total charges
            - dict: Top 3 recipients by transaction count
    """

    paybillFrame = filtered_df[
        filtered_df["type_class"].str.contains("Pay Bill", na=False)
        & ~filtered_df["type_desc"].str.contains("Charge", na=False)
    ]

    paybillCharges_df = (
        filtered_df[
            filtered_df["type_class"].str.contains("Pay Bill", na=False)
            & filtered_df["type_desc"].str.contains("Charge", na=False)
        ]
        .groupby("entity")
        .agg(count=("entity", "count"), total=("withdrawn", "sum"))
    )
    paybillCharges = paybillCharges_df.iloc[0, 1] if not paybillCharges_df.empty else 0

    def agg_concat(x):
        return ", ".join(map(str, x))

    paybillFrame[["entity2", "accounts"]] = paybillFrame["entity"].str.extract(
        r"(.*?)(?:\s+Acc\.\s+(.*)|$)"
    )

    paybillFrame = (
        paybillFrame.groupby("entity2")
        .agg(
            count=("entity", "count"),
            sum=("withdrawn", "sum"),
            accounts=("accounts", agg_concat),
        )
        .sort_values(by="sum", ascending=False)
        .reset_index()
    )

    # Bar chart for top recipients
    toppaybill_fig = px.bar(
        paybillFrame.head(nlargest).sort_values(by="sum", ascending=True),
        x="sum",
        y="entity2",
        template=template,
        title=f"These are the top {nlargest} merchants you paid with Pay Bill",
        hover_data=["count", "accounts"],  # Show transaction count and accounts in hover tooltip
        text="sum",
    ).update_layout(
        xaxis_title="",
        yaxis_title="",
        xaxis=dict(showticklabels=False),
        dragmode = False,
        height=((nlargest - 1) * 100),  # Dynamic height based on number of merchants
    )
    toppaybill_fig.update_traces(
        texttemplate="Ksh. %{value:,}",
        hovertemplate="%{customdata[0]} transaction(s) | %{x:,} Ksh | %{y}<br>To these accounts <br> %{customdata[1]}",
        textposition="auto",
    )

    totalsent = paybillFrame["sum"].sum().astype(int)
    totalcharges = round(paybillCharges, 2)
    totaltransactions = paybillFrame["count"].sum()

    return (
        toppaybill_fig,
        totalsent,
        totalcharges,
        paybillFrame,
        totaltransactions,
    )
