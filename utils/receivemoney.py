import plotly.express as px
import pandas as pd


def receive_money_box(
    filtered_df,
    nlargest,
    color,
    template,
):
    """Analyze receive money transactions and create visualization.

    Args:
        filtered_df (pd.DataFrame): DataFrame containing transaction data
        nlargest (int): Number of top senders to display
        color (str): Color scale for the visualization
        template (str): Plotly template name

    Returns:
        tuple: Contains:
            - plotly.Figure: Bar chart of top money senders
            - plotly.Figure: Time series of money received
            - str: Total received amount (formatted)
            - int: Average amount per transaction
            - dict: Top 3 senders by transaction count
    """

    # Filter and process the DataFrame for receive money transactions
    # Because of my split_entity function, transactions from individuals end with 'from' in the type_desc column and those from businesses end with 'from Business
    receiveFrame = filtered_df[
        filtered_df["type_class"].str.contains("Funds received")
        & ~filtered_df["type_desc"].str.contains("Business", na=False)
    ]

    # M-Pesa returns "2547******09 Firstname Lastname" for transactions from individuals, I'm only interested in the names part.
    mask = receiveFrame["entity"].str.contains(r"\*+", regex=True)
    try:
        receiveFrame.loc[mask, "entity"] = (
            receiveFrame.loc[mask, "entity"].str.partition(" ")[2].str.title()
        )
    except Exception as e:
        print(
            f"Error processing entity names with strategy 1: {e}, trying alternative method."
        )
        receiveFrame.loc[~mask, "entity"] = receiveFrame.loc[
            ~mask, "entity"
        ].str.title()

    receiveFrame_business = filtered_df[
        filtered_df["type_class"].str.contains("Funds received")
        & filtered_df["type_desc"].str.contains("Business", na=False)
    ]

    receiveFrame = pd.concat([receiveFrame, receiveFrame_business], ignore_index=True)

    receiveFrame["type_desc"] = receiveFrame["type_desc"].apply(
        lambda x: "Individual" if str(x).endswith("from") else "Business"
    )

    receiveFrame = (
        receiveFrame.groupby(["entity", "type_desc"])
        .agg(sum=("paid_in", "sum"), count=("paid_in", "count"))
        .reset_index()
    )

    # Bar chart for top senders
    topReceive_fig = px.bar(
        receiveFrame.nlargest(nlargest, "sum").sort_values(by="sum", ascending=True),
        x="sum",
        y="entity",
        color_continuous_scale=color,
        template=template,
        title=f"These are the top {nlargest} individuals & businesses you received money from",
        hover_data="count",
        text="sum",
    ).update_layout(
        xaxis_title="",
        yaxis_title="",
        xaxis=dict(showticklabels=False),
        height=((nlargest - 1) * 100),  # Dynamic height based on number of individuals/businesses
    )

    topReceive_fig.update_traces(
        texttemplate="Ksh. %{value:,}",
        hovertemplate="%{customdata} transaction(s) | %{x:,} Ksh | %{y}",
        textposition="auto",
    )
    

    totalreceived = receiveFrame["sum"].sum().astype(int)
    totalreceivedTransactions = receiveFrame["count"].sum()

    return (
        topReceive_fig,
        totalreceived,
        totalreceivedTransactions,
        receiveFrame,
    )
