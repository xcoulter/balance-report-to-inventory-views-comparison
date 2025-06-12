import streamlit as st
import pandas as pd

st.title("Balance Report Comparison Tool")

# Upload files
balance_file = st.file_uploader("Upload Balance Report (Required)", type="csv")
dashboard_file = st.file_uploader("Upload Dashboard Report (Optional)", type="csv")
rollforward_file = st.file_uploader("Upload Rollforward Report (Optional)", type="csv")

def load_data(file):
    return pd.read_csv(file) if file else None

def normalize_ticker(ticker):
    return str(ticker).strip().upper()

def safe_numeric(series):
    return pd.to_numeric(series, errors='coerce').fillna(0)

def compare_reports(balance_df, compare_df, mode="dashboard"):
    results = []

    balance_df['ticker'] = balance_df['ticker'].apply(normalize_ticker)
    balance_df['value'] = safe_numeric(balance_df['value'])
    balance_df['fiatValue'] = safe_numeric(balance_df['fiatValue'])

    if mode == "dashboard":
        compare_df['Asset'] = compare_df['Asset'].apply(normalize_ticker)
        compare_df['Qty'] = safe_numeric(compare_df['Qty'])
        compare_df['Fair Market Value'] = safe_numeric(compare_df['Fair Market Value'])

        merged = balance_df.merge(compare_df, how='outer', left_on='ticker', right_on='Asset', indicator=True)
        for _, row in merged.iterrows():
            ticker = row['ticker'] if pd.notnull(row['ticker']) else row['Asset']
            balance_qty = row.get('value', 0)
            dashboard_qty = row.get('Qty', 0)
            balance_fmv = row.get('fiatValue', 0)
            dashboard_fmv = row.get('Fair Market Value', 0)

            qty_diff = abs(balance_qty - dashboard_qty)
            fmv_diff = abs(balance_fmv - dashboard_fmv)

            results.append({
                "Ticker": ticker,
                "Balance Qty": balance_qty,
                "Dashboard Qty": dashboard_qty,
                "Qty Diff": qty_diff,
                "Balance FMV": balance_fmv,
                "Dashboard FMV": dashboard_fmv,
                "FMV Diff": fmv_diff
            })
    else:  # rollforward
        compare_df['asset'] = compare_df['asset'].apply(normalize_ticker)
        compare_df['ending_qty_value'] = safe_numeric(compare_df['ending_qty_value'])
        compare_df['ending_fiat_value'] = safe_numeric(compare_df['ending_fiat_value'])

        merged = balance_df.merge(compare_df, how='outer', left_on='ticker', right_on='asset', indicator=True)
        for _, row in merged.iterrows():
            ticker = row['ticker'] if pd.notnull(row['ticker']) else row['asset']
            balance_qty = row.get('value', 0)
            rollforward_qty = row.get('ending_qty_value', 0)
            balance_fmv = row.get('fiatValue', 0)
            rollforward_fmv = row.get('ending_fiat_value', 0)

            qty_diff = abs(balance_qty - rollforward_qty)
            fmv_diff = abs(balance_fmv - rollforward_fmv)

            results.append({
                "Ticker": ticker,
                "Balance Qty": balance_qty,
                "Rollforward Qty": rollforward_qty,
                "Qty Diff": qty_diff,
                "Balance FMV": balance_fmv,
                "Rollforward FMV": rollforward_fmv,
                "FMV Diff": fmv_diff
            })

    return pd.DataFrame(results)

if balance_file:
    balance_df = load_data(balance_file)
    if dashboard_file:
        dashboard_df = load_data(dashboard_file)
        result_df = compare_reports(balance_df, dashboard_df, mode="dashboard")
        st.subheader("Comparison with Dashboard Report")
        st.dataframe(result_df)
    elif rollforward_file:
        rollforward_df = load_data(rollforward_file)
        result_df = compare_reports(balance_df, rollforward_df, mode="rollforward")
        st.subheader("Comparison with Rollforward Report")
        st.dataframe(result_df)
    else:
        st.warning("Please upload either a Dashboard or Rollforward report to compare.")
else:
    st.info("Please upload the required Balance Report.")
