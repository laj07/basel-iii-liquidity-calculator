"""
Basel III Liquidity Risk Calculator: Streamlit App
Run with: streamlit run app.py
"""

import streamlit as st
import pandas as pd

st.set_page_config(page_title="Basel III Liquidity Risk Calculator", layout="wide")

st.title("Basel III Liquidity Risk Calculator")
st.caption("LCR and NSFR calculator with stress scenario testing, aligned to APRA APS 210 concepts.")

# SIDEBAR 

st.sidebar.header("Bank Balance Sheet Inputs ($m)")

st.sidebar.subheader("Assets")
cash = st.sidebar.number_input("Cash", value=500, step=50)
cb_reserves = st.sidebar.number_input("Central Bank Reserves", value=200, step=50)
gov_bonds = st.sidebar.number_input("Government Bonds", value=300, step=50)
aaa_bonds = st.sidebar.number_input("AAA Corporate Bonds", value=200, step=50)
bb_bonds = st.sidebar.number_input("BB Corporate Bonds", value=100, step=50)
home_loans = st.sidebar.number_input("Home Loans", value=2000, step=100)
corp_loans = st.sidebar.number_input("Corporate Loans", value=800, step=100)

st.sidebar.subheader("Liabilities & Capital")
retail_stable = st.sidebar.number_input("Retail Deposits (Stable)", value=1000, step=50)
retail_less_stable = st.sidebar.number_input("Retail Deposits (Less Stable)", value=500, step=50)
wholesale_30d = st.sidebar.number_input("Wholesale Funding (<30 days)", value=400, step=50)
interbank_30d = st.sidebar.number_input("Interbank Loans (<30 days)", value=200, step=50)
equity = st.sidebar.number_input("Equity / Tier 1 Capital", value=600, step=50)
wholesale_1yr = st.sidebar.number_input("Wholesale Funding (>1 year)", value=300, step=50)

balance_sheet = {
    "Cash": cash,
    "Central Bank Reserves": cb_reserves,
    "Government Bonds": gov_bonds,
    "AAA Corporate Bonds": aaa_bonds,
    "BB Corporate Bonds": bb_bonds,
    "Home Loans": home_loans,
    "Corporate Loans": corp_loans,
    "Retail Deposits (Stable)": retail_stable,
    "Retail Deposits (Less Stable)": retail_less_stable,
    "Wholesale Funding (<30 days)": wholesale_30d,
    "Interbank Loans (<30 days)": interbank_30d,
    "Equity / Tier 1 Capital": equity,
    "Wholesale Funding (>1 year)": wholesale_1yr,
}

# CALCULATION FUNCTIONS 

def calculate_lcr(bs, runoff_overrides=None):
    hqla = (
        bs["Cash"] * 1.00
        + bs["Central Bank Reserves"] * 1.00
        + bs["Government Bonds"] * 1.00
        + bs["AAA Corporate Bonds"] * 0.85
        + bs["BB Corporate Bonds"] * 0.50
    )

    runoff = {
        "retail_stable": 0.05,
        "retail_less_stable": 0.10,
        "wholesale_30d": 0.25,
        "interbank_30d": 1.00,
    }
    if runoff_overrides:
        runoff.update(runoff_overrides)

    outflows = (
        bs["Retail Deposits (Stable)"] * runoff["retail_stable"]
        + bs["Retail Deposits (Less Stable)"] * runoff["retail_less_stable"]
        + bs["Wholesale Funding (<30 days)"] * runoff["wholesale_30d"]
        + bs["Interbank Loans (<30 days)"] * runoff["interbank_30d"]
    )

    lcr = hqla / outflows if outflows > 0 else float("inf")
    return {"Total HQLA": hqla, "Total Outflows": outflows, "LCR": lcr, "Status": "PASS" if lcr >= 1.0 else "FAIL"}


def calculate_nsfr(bs):
    asf = (
        bs["Equity / Tier 1 Capital"] * 1.00
        + bs["Retail Deposits (Stable)"] * 0.95
        + bs["Retail Deposits (Less Stable)"] * 0.90
        + bs["Wholesale Funding (>1 year)"] * 0.50
        + bs["Interbank Loans (<30 days)"] * 0.00
    )
    rsf = (
        bs["Cash"] * 0.00
        + bs["Government Bonds"] * 0.05
        + bs["AAA Corporate Bonds"] * 0.15
        + bs["Home Loans"] * 0.65
        + bs["Corporate Loans"] * 0.85
    )
    nsfr = asf / rsf if rsf > 0 else float("inf")
    return {"Total ASF": asf, "Total RSF": rsf, "NSFR": nsfr, "Status": "PASS" if nsfr >= 1.0 else "FAIL"}


stress_scenarios = {
    "Base Case": {"retail_stable": 0.05, "retail_less_stable": 0.10, "wholesale_30d": 0.25, "interbank_30d": 1.00},
    "Mild Stress": {"retail_stable": 0.08, "retail_less_stable": 0.15, "wholesale_30d": 0.35, "interbank_30d": 1.00},
    "Moderate Stress": {"retail_stable": 0.12, "retail_less_stable": 0.20, "wholesale_30d": 0.50, "interbank_30d": 1.00},
    "Severe Stress": {"retail_stable": 0.20, "retail_less_stable": 0.30, "wholesale_30d": 0.75, "interbank_30d": 1.00},
}


def run_stress_test(bs, scenarios):
    rows = []
    for name, runoff in scenarios.items():
        result = calculate_lcr(bs, runoff_overrides=runoff)
        rows.append({
            "Scenario": name,
            "Total HQLA": result["Total HQLA"],
            "Total Outflows": result["Total Outflows"],
            "LCR": result["LCR"],
            "Status": result["Status"],
        })
    return pd.DataFrame(rows)

# MAIN PAGE 

lcr_result = calculate_lcr(balance_sheet)
nsfr_result = calculate_nsfr(balance_sheet)

col1, col2 = st.columns(2)

with col1:
    st.subheader("Liquidity Coverage Ratio (LCR)")
    st.metric("LCR", f"{lcr_result['LCR']:.1%}", delta=f"{(lcr_result['LCR']-1)*100:.1f} pts vs 100% minimum")
    if lcr_result["Status"] == "PASS":
        st.success(f"Status: {lcr_result['Status']}")
    else:
        st.error(f"Status: {lcr_result['Status']}")
    st.write(f"Total HQLA: **${lcr_result['Total HQLA']:,.0f}m**")
    st.write(f"Total 30-day Outflows: **${lcr_result['Total Outflows']:,.0f}m**")

with col2:
    st.subheader("Net Stable Funding Ratio (NSFR)")
    st.metric("NSFR", f"{nsfr_result['NSFR']:.1%}", delta=f"{(nsfr_result['NSFR']-1)*100:.1f} pts vs 100% minimum")
    if nsfr_result["Status"] == "PASS":
        st.success(f"Status: {nsfr_result['Status']}")
    else:
        st.error(f"Status: {nsfr_result['Status']}")
    st.write(f"Total ASF: **${nsfr_result['Total ASF']:,.0f}m**")
    st.write(f"Total RSF: **${nsfr_result['Total RSF']:,.0f}m**")

st.divider()

# STRESS TEST SECTION

st.subheader("LCR Under Stress Scenarios")
st.caption("Shows how the LCR deteriorates as deposit and funding run-off rates increase under stress.")

stress_df = run_stress_test(balance_sheet, stress_scenarios)

# Chart
chart_df = stress_df[["Scenario", "LCR"]].copy()
chart_df["LCR"] = chart_df["LCR"] * 100
st.bar_chart(chart_df.set_index("Scenario"))

# Table
display_df = stress_df.copy()
display_df["LCR"] = display_df["LCR"].apply(lambda x: f"{x:.1%}")
display_df["Total HQLA"] = display_df["Total HQLA"].apply(lambda x: f"${x:,.0f}m")
display_df["Total Outflows"] = display_df["Total Outflows"].apply(lambda x: f"${x:,.0f}m")
st.dataframe(display_df, use_container_width=True, hide_index=True)

st.divider()
st.caption("Built as a Basel III / APRA APS 210 style liquidity risk model. For portfolio demonstration purposes and not for actual regulatory compliance use.")
