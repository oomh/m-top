"""
M-Pesa Data Loading and Preprocessing Module

This module handles the loading, cleaning, and preprocessing of M-Pesa transaction data
from PDF statements. It includes functions for data extraction, transformation, and
standardization.

Functions:
    load_pdf_data: Extracts transaction data from PDF statements
    clean_data: Cleans and standardizes the extracted data
    split_details: Helper function to parse transaction details
    split_type: Helper function to parse transaction types

Dependencies:
    - pandas: For data manipulation
    - tabula: For PDF data extraction
    - streamlit: For progress indicators
"""

import pandas as pd
import numpy as np
import re
import warnings
import streamlit as st
import sys
from tabula.io import read_pdf

# Suppress warnings for cleaner output
warnings.filterwarnings("ignore")

# Configuration constants
EXPECTED_COLUMNS = [
    "Receipt No.",
    "Receipt No",
    "Completion Time",
    "Details",
    "Paid In",
    "Withdrawn",
]


# @st.cache_data(show_spinner="Extracting and cleaning your statement...")
# Step 1: Load and examine raw data
def load_pdf_data(pdf_path, password):
    """
    Load M-Pesa transaction data from PDF statement.

    Args:
        pdf_path (str): Path to the PDF statement file
        password (str): Password for protected PDF files

    Returns:
        pd.DataFrame: Combined DataFrame containing extracted transaction data
            or None if extraction fails
    """
    try:
        print(f"📄 Loading PDF: {pdf_path}")
        df_list = read_pdf(
            pdf_path, pages="all", guess=True, lattice=True, password=password
        )

        print(f"📊 Found {len(df_list)} tables in PDF")

        # Filter for transaction tables
        selected_dfs = [
            df
            for df in df_list
            if isinstance(df, pd.DataFrame) and df.columns.isin(EXPECTED_COLUMNS).any()
        ]

        # print(f"\n✅ Found {len(selected_dfs)} transaction tables")

        if selected_dfs:
            combined_df = pd.concat(selected_dfs, ignore_index=True)
            combined_df.columns = (
                combined_df.columns.str.strip()
                .str.lower()
                .str.replace(r"\s+", "", regex=True)
            )
            print(f"📈 Combined dataset shape: {combined_df.shape}")
            return combined_df
        else:
            print("❌ No valid transaction tables found!")
            return None

    except Exception as e:
        print(f"❌ Error loading PDF: {str(e)}")
        return None


def split_details(details_text):
    """
    Parse transaction details into type and entity components.

    Args:
        details_text (str): Raw transaction details text

    Returns:
        tuple: Contains (transaction_type, entity_name)
    """
    pattern = r"(.*?)(?<!\S)(?: *)-(?: *)\s(?=\S)(.*)"
    match = re.search(pattern, str(details_text), re.IGNORECASE)

    if match:
        return match.group(1).strip(), match.group(2).strip()
    else:
        return details_text, details_text


def split_type(transaction_type):
    """
    Parse transaction type into class and description components.

    Args:
        transaction_type (str): Raw transaction type text

    Returns:
        pd.Series: Contains [type_class, type_description]
    """
    if pd.isna(transaction_type):
        return pd.Series(["", ""])
    else:
        split_list = str(transaction_type).split(" ")
        right = " ".join(split_list[0:2])
        left = " ".join(split_list[2:])
        return pd.Series([right, left])


# @st.cache_data(show_spinner="Cleaning your M-Pesa data...")
def clean_data(df):
    """
    Clean and standardize M-Pesa transaction data.

    Args:
        df (pd.DataFrame): Raw transaction data DataFrame

    Returns:
        pd.DataFrame: Cleaned and standardized DataFrame with additional
            computed columns, or exits if cleaning fails

    Columns added:
        - month: Transaction month in format "Month_YY"
        - week: Transaction week in format "WeekNumber_YY"
        - type_class: Standardized transaction type category
        - type_desc: Detailed transaction type description
    """
    print("\n🧹 Cleaning data...")
    if df is None:
        print("❌ The DataFrame is empty after loading.")
        st.error(
            "The DataFrame is empty after loading. Please check the PDF file., reload the page to try again."
        )
        sys.exit(1)
    else:
        print(f"Original shape: {df.shape}")

        df_clean = df.copy()

        # Rename columns to a consistent format
        mapping = {}
        for c in df_clean.columns:
            if "receipt" in c or "ref" in c:
                mapping[c] = "receipt_no"
            elif "completion" in c or "time" in c:
                mapping[c] = "date_time"
            elif "detail" in c:
                mapping[c] = "details"
            elif "paid" in c and "in" in c:
                mapping[c] = "paid_in"
            elif "withdraw" in c:
                mapping[c] = "withdrawn"

        print(f"📝 Mapping found: {mapping}")
        df_clean = df_clean.rename(columns=mapping)
        df_clean = df_clean.drop(
            columns=[
                col
                for col in df_clean.columns
                if col
                not in ["receipt_no", "date_time", "details", "paid_in", "withdrawn"]
            ]
        )

        # Rest of your code unchanged...
        df_clean["receipt_no"] = df_clean["receipt_no"].astype("string")
        df_clean["date_time"] = pd.to_datetime(df_clean["date_time"], errors="coerce")

        df_clean["withdrawn"] = (
            pd.to_numeric(
                df_clean["withdrawn"]
                .astype(str)
                .str.replace(",", "")
                .replace(["", "-", "N/A", "nan"], "0"),
                errors="coerce",
            )
            .abs()
            .fillna(0)
        )

        df_clean["paid_in"] = pd.to_numeric(
            df_clean["paid_in"]
            .astype(str)
            .str.replace(",", "")
            .replace(["", "-", "N/A", "nan"], "0"),
            errors="coerce",
        ).fillna(0)

        df_clean["details"] = df_clean["details"].str.replace(r"\s+", " ", regex=True)

        # Split details into type and entity
        df_clean[["type", "entity"]] = df_clean["details"].apply(
            lambda x: pd.Series(split_details(x))
        )

        # Split type into type_class and type_desc
        df_clean[["type_class", "type_desc"]] = df_clean["type"].apply(
            lambda x: pd.Series(split_type(x))
        )
        # Create sortable date columns with first day of month/week
        df_clean["month_sort"] = df_clean["date_time"].dt.to_period('M').dt.to_timestamp()
        df_clean["week_sort"] = df_clean["date_time"].dt.to_period('W').dt.to_timestamp()
        
        # Create display columns with formatted strings
        df_clean["month"] = df_clean["date_time"].dt.strftime("%B_%y")
        df_clean["week"] = df_clean["date_time"].dt.strftime("%V_%y")

        print(f"Cleaned shape: {df_clean.shape}")
        print(f"Final columns: {list(df_clean.columns)}")  # ← Debug print
        print(
            f"Date range: {df_clean['date_time'].min().strftime('%B %d, %Y %H:%M')} to {df_clean['date_time'].max().strftime('%B %d, %Y %H:%M')}"
        )

        return df_clean


if __name__ == "__main__":
    pass
