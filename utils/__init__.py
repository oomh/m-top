"""
M-Pesa Transaction Analysis Utilities

This package contains utility functions for analyzing different types of M-Pesa transactions.
Each module focuses on a specific transaction type and provides visualization and analysis functions.

Modules:
- merchantpayments: Analyze merchant payment transactions (Buy Goods)
- customertransfer: Analyze customer transfer transactions (PayBill/Till)
- cashwithdrawal: Analyze cash withdrawal transactions
- airtime: Analyze airtime purchase transactions
- sendmoney: Analyze send money transactions
- receivemoney: Analyze receive money transactions
- general_analysis: General analysis functions and transaction overview

Usage:
    from utils.merchantpayments import merchant_box
    from utils.customertransfer import customer_transfer_box
    from utils.general_analysis import transaction_overview
"""

__version__ = "1.0.0"
__author__ = "M-Top Team"

# Import all main functions for easy access
from .merchantpayments import merchant_box
from .customertransfer import customer_transfer_box
from .cashwithdrawal import cash_withdrawal_box
from .airtime import airtime_box
from .paybill import paybill_box
from .receivemoney import receive_money_box

__all__ = [
    "merchant_box",
    "customer_transfer_box",
    "cash_withdrawal_box",
    "airtime_box",
    "paybill_box",
    "receive_money_box",
]
