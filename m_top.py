"""
M-Top: M-Pesa Statement Analysis Web Application

This is the main module for the M-Top web application, which provides comprehensive
analysis of M-Pesa statements through interactive visualizations and statistics.

Features:
    - PDF statement upload and processing
    - Transaction filtering by date range or month
    - Analysis of multiple transaction types:
        * Merchant payments
        * Customer transfers
        * Cash withdrawals
        * Airtime purchases
        * PayBill payments
        * Received money
    - Interactive visualizations
    - Detailed transaction statistics

Dependencies:
    - streamlit: Web application framework
    - plotly.express: Interactive visualizations
    - pandas: Data manipulation
    - millify: Number formatting
"""

import streamlit as st
import pandas as pd
from load_wrangle import load_pdf_data, clean_data
import plotly.express as px

# Import utility modules
from utils.merchantpayments import merchant_box
from utils.customertransfer import customer_transfer_box
from utils.cashwithdrawal import cash_withdrawal_box
from utils.airtime import airtime_box
from utils.paybill import paybill_box
from utils.receivemoney import receive_money_box

# Configuration constants
PX_TEMPLATE = "ggplot2"
COLOR_SCALE = "Blue"
N_LARGEST = 9

# App configuration
st.set_page_config(
    layout="wide",
    page_title="M-Top: M-Pesa Statement Analyzer",
    page_icon="💸"
)

# Initialize session state variables
if "pdf_path" not in st.session_state:
    st.session_state.pdf_path = None
if "pdf_password" not in st.session_state:
    st.session_state.pdf_password = ""
if "process_clicked" not in st.session_state:
    st.session_state.process_clicked = False
if "load_error" not in st.session_state:
    st.session_state.load_error = None

# --- App Header ---
st.markdown(
    """
# M-Top

This web app will take your M-Pesa statement for a given period, extract the transactions and give you an over view of where you have spent your moneies. You will have an option to filter by month(s) or a specific period. 


Upload your M-Pesa statement PDF and see your money pits.
"""
)

# --- File Upload and Password Input ---
with st.form("pdf_upload_form"):
    pdf = st.file_uploader("Upload your M-Pesa statement (PDF)", type=["pdf"])
    password = st.text_input(
        "Enter PDF password (leave blank if not protected)",
        type="password",
        key="pdf_password_input",
    )
    process = st.form_submit_button("Process")

if process:
    st.session_state.pdf_path = pdf
    st.session_state.pdf_password = password
    st.session_state.process_clicked = True
    st.session_state.load_error = None  # Reset error

# Only proceed if the user has clicked "Process" and a file is uploaded
if st.session_state.get("process_clicked") and st.session_state.pdf_path is not None:

    @st.cache_data(show_spinner="Extracting and cleaning your statement...")
    def load_and_clean(pdf_file, password):
        df = load_pdf_data(pdf_file, password)
        df_cleaned = clean_data(df)
        return df_cleaned

    try:
        df_cleaned = load_and_clean(
            st.session_state.pdf_path, st.session_state.pdf_password
        )
        st.session_state.load_error = None
    except Exception as e:
        st.session_state.load_error = str(e)
        df_cleaned = None

    if st.session_state.load_error:
        st.error(f"Failed to load or clean PDF: {st.session_state.load_error}")
        st.session_state.process_clicked = False
        st.stop()
else:
    st.info("Please upload your PDF and click 'Process' to continue.")
    st.stop()


# --- Sidebar Filters ---
st.sidebar.markdown("---")
st.sidebar.subheader("Filter Options")
st.sidebar.text(
    f"Analyzing transactions from "
    f"{df_cleaned['date_time'].min().strftime('%H:%M - %B %d, %Y')} to "  # type: ignore
    f"{df_cleaned['date_time'].max().strftime('%H:%M - %B %d, %Y')}"  # type: ignore
)
st.sidebar.markdown("---")
N_LARGEST = st.sidebar.number_input(
    "Number of Top Entities to Display",
    min_value=5,
    max_value=15,
    value=N_LARGEST,
    key="n_largest",
    help="Adjust the number of top entities to display in the visualizations. Default is 9, Minimum is 5, Maximum is 15.",
)
st.sidebar.markdown("---")

# Initialize toggle state if not present
if "disable" not in st.session_state:
    st.session_state.disable = {"date": False, "month": False}


def update_toggles():
    st.session_state.disable["month"] = st.session_state.date_filter
    st.session_state.disable["date"] = st.session_state.month_filter


date_toggle = st.sidebar.toggle(
    "Use Date Range Filter",
    key="date_filter",
    on_change=update_toggles,
    disabled=st.session_state.disable["date"],
)
month_toggle = st.sidebar.toggle(
    "Use Month Filter",
    key="month_filter",
    on_change=update_toggles,
    disabled=st.session_state.disable["month"],
)

filtered_df = df_cleaned  # Default to the full DataFrame

if st.session_state.get("date_filter"):
    st.sidebar.subheader("Date Range Filter")
    date_range = st.sidebar.date_input(
        "Select Date Range",
        value=[
            df_cleaned["date_time"].min().date(),  # type: ignore
            df_cleaned["date_time"].max().date(),  # type: ignore
        ],  # type: ignore
        min_value=df_cleaned["date_time"].min().date(),  # type: ignore
        max_value=df_cleaned["date_time"].max().date(),  # type: ignore
    )

    if len(date_range) == 2:
        start_date, end_date = date_range
        mask = (df_cleaned["date_time"] >= pd.to_datetime(start_date)) & (  # type: ignore
            df_cleaned["date_time"] <= pd.to_datetime(end_date)  # type: ignore
        )
        filtered_df = df_cleaned.loc[mask]  # type: ignore
    else:
        st.sidebar.warning("Please select both start and end dates")


elif st.session_state.get("month_filter"):
    st.sidebar.subheader("Month Filter")
    month_list = list(
        df_cleaned["date_time"].dt.month_name()  # type: ignore
        + "_"
        + df_cleaned["date_time"].dt.year.astype(str)  # type: ignore
    )
    month_list = sorted(
        set(month_list),
        key=lambda x: pd.to_datetime(x.split("_")[0] + " 1, " + x.split("_")[1]),
    )
    month = st.sidebar.segmented_control(
        "Select Month",
        options=month_list,
        selection_mode="multi",
        default=month_list[0:3] if len(month_list) >= 3 else month_list,
    )
    filtered_df = df_cleaned[df_cleaned["date_time"].dt.strftime("%B_%Y").isin(month)]  # type: ignore
st.divider()

# --- Merchant Payments Section ---

topMerchant_fig, totalspend, totalcharges, merchantCount, merchantFrame = merchant_box(
    filtered_df, N_LARGEST, COLOR_SCALE, PX_TEMPLATE
)

if merchantCount > 0:
    st.header("🛒 Buy Goods")
    merchant1, merchant2 = st.columns([2, 1])

    with merchant1:
        st.plotly_chart(
            topMerchant_fig, use_container_width=True, use_container_height=True
        )

    with merchant2:
        st.metric("Number of payments", f"{merchantCount} transactions")
        st.metric("Amount paid to merchants", f"Ksh. {totalspend:,.2f}")
        st.metric("Charges incurred", f"Ksh. {totalcharges:.2f}")
        st.markdown("---")
        st.dataframe(
            merchantFrame[["entity", "count"]]
            .sort_values(by="count", ascending=False)
            .head(N_LARGEST),
            use_container_width=True,
            hide_index=True,
            column_config={
                "entity": st.column_config.TextColumn("Most frequented Merchant"),
                "count": st.column_config.NumberColumn("Transactions"),
            },
        )

    st.divider()

    # --- Pay Bill Payments Section ---
    st.header("🤑 PayBill Section")

    paybill1, paybill2 = st.columns([2, 1])

    toppaybill_fig, totalsent, totalpbcharges, paybillFrame, pbtranactions = (
        paybill_box(filtered_df, N_LARGEST, COLOR_SCALE, PX_TEMPLATE)
    )

    with paybill1:
        st.plotly_chart(
            toppaybill_fig, use_container_width=True, use_container_height=True
        )

    with paybill2:
        st.metric("Number of payments", f"{pbtranactions} transactions")
        st.metric("Amount paid to merchants", f"Ksh. {totalsent:,.2f}")
        st.metric("Charges incurred", f"Ksh. {totalpbcharges:,.2f}")
        st.markdown("---")
        st.dataframe(
            paybillFrame[["entity2", "count"]]
            .sort_values(by="count", ascending=False)
            .head(N_LARGEST),
            use_container_width=True,
            hide_index=True,
            column_config={
                "entity2": st.column_config.TextColumn("Most frequented Paybills"),
                "count": st.column_config.NumberColumn("Transactions"),
            },
        )

    st.divider()
else:
    st.warning("No merchant payments found in the provided statement.")


# --- Customer Transfer Section ---

topTransfer_fig, totalspend, totalcharges, totaltransferTransactions, transferFrame = (
    customer_transfer_box(filtered_df, N_LARGEST, COLOR_SCALE, PX_TEMPLATE)
)
if totaltransferTransactions > 0:
    st.header("💸💸 Cash Transfers (Send Money)")

    transfer1, transfer2 = st.columns([2, 1])

    with transfer1:
        st.plotly_chart(topTransfer_fig, use_container_width=True)
    with transfer2:
        st.metric("Number of transfers", f"{totaltransferTransactions} Transactions")
        st.metric("Amount sent", f"Ksh. {totalspend:,.2f}")
        st.metric("Charges incurred", f"Ksh. {totalcharges:,.2f}")
        st.markdown("---")
        st.dataframe(
            transferFrame[["entity", "count"]]
            .sort_values(by="count", ascending=False)
            .head(N_LARGEST),
            use_container_width=True,
            hide_index=True,
            column_config={
                "entity": st.column_config.TextColumn("Most frequented recipients"),
                "count": st.column_config.NumberColumn("Transactions"),
            },
        )

    st.divider()
else:
    st.warning("No customer transfers found in the provided statement.")

# --- Receive Money Section ---
(
    topReceive_fig,
    totalreceived,
    totalreceivedTransactions,
    receiveFrame,
) = receive_money_box(filtered_df, N_LARGEST, COLOR_SCALE, PX_TEMPLATE)

if totalreceivedTransactions > 0:
    st.header("📥 Received Money (From Individuals and Business)")

    receive1, receive2 = st.columns([2, 1])

    with receive1:
        st.plotly_chart(topReceive_fig, use_container_width=True)
    with receive2:
        st.metric("Total transactions", f"{totalreceivedTransactions} Transactions")
        st.metric("Total Received", f"{totalreceived:,.2f} KES")
        st.markdown("---")
        st.dataframe(
            receiveFrame[["entity", "count"]]
            .sort_values(by="count", ascending=False)
            .head(N_LARGEST),
            use_container_width=True,
            hide_index=True,
            column_config={
                "entity": st.column_config.TextColumn("Most frequent senders"),
                "count": st.column_config.NumberColumn("Transactions"),
            },
        )
else:
    st.warning("No received money transactions found in the provided statement.")

# --- Cash Withdrawal Section ---
(
    topWithdrawal_fig,
    totalwithdrawal,
    withdrawalcharges,
    totalWithdrawals,
    withdrawalFrame,
) = cash_withdrawal_box(filtered_df, N_LARGEST, COLOR_SCALE, PX_TEMPLATE)



if totalWithdrawals > 0:
    st.header("🏧 Cash Withdrawals")

    withdrawal1, withdrawal2 = st.columns([2, 1])

    with withdrawal1:
        st.plotly_chart(topWithdrawal_fig, use_container_width=True)

    with withdrawal2:
        st.metric("Total Transactions", f"{totalWithdrawals} Withdrawals")
        st.metric("Total Withdrawal", f"{totalwithdrawal:,.2f} KES")
        st.metric("Total Charges", f"{withdrawalcharges} KES")
        st.markdown("---")
        st.dataframe(
            withdrawalFrame[["entity", "count"]]
            .sort_values(by="count", ascending=False)
            .head(N_LARGEST),
            use_container_width=True,
            hide_index=True,
            column_config={
                "entity": st.column_config.TextColumn("Most frequented Agents"),
                "count": st.column_config.NumberColumn("Transactions"),
            },
        )
else:
    st.warning("No cash withdrawal transactions found in the provided statement.")
    st.divider()


# --- Airtime Section ---
topAirtime_fig, totalairtime, totalairtimetransactions, airtimeFrame = airtime_box(
    filtered_df, N_LARGEST, COLOR_SCALE, PX_TEMPLATE
)

if totalairtime > 0:
    st.header("📱 Airtime Purchases")

    airtime1, airtime2 = st.columns([2, 1])

    with airtime1:
        st.plotly_chart(topAirtime_fig, use_container_width=True)

    with airtime2:
        st.metric("Total Transactions", f"{totalairtimetransactions} Airtime Purchases")
        st.metric("Total Airtime", f"{totalairtime:,.2f} KES")
    
    st.dataframe(airtimeFrame)    

    st.divider()
else:
    st.warning("No airtime purchases found in the provided statement.")

# --- Reset Option ---
if st.button("Upload a new statement"):
    for key in ["pdf_uploaded", "pdf_path", "pdf_password"]:
        if key in st.session_state:
            del st.session_state[key]

# Main application logic
def main():
    """
    Main application function that handles:
        1. File upload and processing
        2. Data filtering
        3. Visualization generation
        4. Displaying results in the Streamlit app"""
    # --- Session State Initialization ---
    if "pdf_path" not in st.session_state:
        st.session_state.pdf_path = None
    if "pdf_password" not in st.session_state:
        st.session_state.pdf_password = ""
    if "process_clicked" not in st.session_state:
        st.session_state.process_clicked = False
    if "load_error" not in st.session_state:
        st.session_state.load_error = None

# Run the main application
if __name__ == "__main__":
    main()