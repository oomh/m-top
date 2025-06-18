# M-Top: M-Pesa Statement Analyzer

A  Streamlit web application for analyzing M-Pesa transaction data from PDF statements.

## 📁 Project Structure

```
m-top/
├── m_top_enhanced.py          # Enhanced main application
├── load_wrangle.py            # PDF loading and data cleaning utilities (your existing file)
├── utils/                    # Transaction analysis utilities
│   ├── __init__.py           # Package initialization
│   ├── merchantpayments.py   # Merchant payment analysis
│   ├── paybill.py            # PayBill analysis
│   ├── cashwithdrawal.py     # Cash withdrawal analysis
│   ├── airtime.py            # Airtime purchase analysis
│   ├── sendmoney.py          # Send money transaction analysis
│   ├── receivemoney.py       # Receive money transaction analysis
├── requirements.txt          # Dependencies
└── README.md                 # This documentation
```

## 🚀 Quick Start
It's a Streamlit web app so use it at this URL: https://m-pesalytics.streamlit.app/

## 🔧 Features

### Transaction Type Analysis

- **Merchant Payments (Buy Goods)**: Spending at various merchants (Buy Goods)
- **Pay-bill payments**: PayBill transactions breakdown
- **Send Money**: Person-to-person money transfers analysis
- **Receive Money**: Incoming money transfers from individuals and businesses, like banks.
- **Cash Withdrawals**: Agent withdrawal patterns
- **Airtime Purchases**: Mobile airtime spending trends and patterns

### Visualizations

- Interactive bar charts for top entities by transaction volume
- Counts and cumulative amounts for transaction types.

## 📊 Usage

1. Upload your M-Pesa PDF statement
2. Enter the PDF password provided by Safaricom
3. Explore comprehensive transaction analysis with:
   - Individual analysis for each transaction type
   - Interactive filtering by date range or month


## 📋 Requirements

- Official M-Pesa PDF statements from Safaricom
- PDF password from Safaricom

## 🔒 Privacy & Security

- All processing happens locally
- No data transmitted to external servers
- Files and passwords are not stored, they are cleared when browser is closed, or when the page is reloaded

## 📄 License

Open source - ensure compliance with local data protection regulations.

## ⚠️ Disclaimer

For personal financial analysis only. Users responsible for data protection and accuracy verification. I am still working on this project, leave any comments or feedback.
