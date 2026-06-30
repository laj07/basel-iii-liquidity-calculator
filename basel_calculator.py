"""
Basel III Liquidity Risk Calculator
Calculates LCR (Liquidity Coverage Ratio) and NSFR (Net Stable Funding Ratio)
under APRA APS 210 style assumptions, with stress scenario testing.
"""

import pandas as pd

# ============================================================
# 1. INPUTS
# ============================================================

balance_sheet = {
    "Cash": 500,
    "Central Bank Reserves": 200,
    "Government Bonds": 300,
    "AAA Corporate Bonds": 200,
    "BB Corporate Bonds": 100,
    "Home Loans": 2000,
    "Corporate Loans": 800,
    "Retail Deposits (Stable)": 1000,
    "Retail Deposits (Less Stable)": 500,
    "Wholesale Funding (<30 days)": 400,
    "Interbank Loans (<30 days)": 200,
    "Equity / Tier 1 Capital": 600,
    "Wholesale Funding (>1 year)": 300,
}


# ============================================================
# 2. LCR CALCULATION
# ============================================================

def calculate_lcr(bs: dict, runoff_overrides: dict = None) -> dict:
    """
    Calculates the Liquidity Coverage Ratio.
    runoff_overrides lets us pass in stressed run-off rates for scenario testing.
    """
    # HQLA haircuts (how much of each asset counts as liquid)
    hqla = (
        bs["Cash"] * (1 - 0.00)
        + bs["Central Bank Reserves"] * (1 - 0.00)
        + bs["Government Bonds"] * (1 - 0.00)
        + bs["AAA Corporate Bonds"] * (1 - 0.15)
        + bs["BB Corporate Bonds"] * (1 - 0.50)
    )

    # Default run-off rates (base case), overridden under stress
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

    lcr = hqla / outflows

    return {
        "Total HQLA": hqla,
        "Total Outflows": outflows,
        "LCR": lcr,
        "Status": "PASS" if lcr >= 1.0 else "FAIL",
    }


# ============================================================
# 3. NSFR CALCULATION
# ============================================================

def calculate_nsfr(bs: dict) -> dict:
    """
    Calculates the Net Stable Funding Ratio.
    """
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

    nsfr = asf / rsf

    return {
        "Total ASF": asf,
        "Total RSF": rsf,
        "NSFR": nsfr,
        "Status": "PASS" if nsfr >= 1.0 else "FAIL",
    }


# ============================================================
# 4. STRESS SCENARIOS
# ============================================================

stress_scenarios = {
    "Base Case": {"retail_stable": 0.05, "retail_less_stable": 0.10, "wholesale_30d": 0.25, "interbank_30d": 1.00},
    "Mild Stress": {"retail_stable": 0.08, "retail_less_stable": 0.15, "wholesale_30d": 0.35, "interbank_30d": 1.00},
    "Moderate Stress": {"retail_stable": 0.12, "retail_less_stable": 0.20, "wholesale_30d": 0.50, "interbank_30d": 1.00},
    "Severe Stress": {"retail_stable": 0.20, "retail_less_stable": 0.30, "wholesale_30d": 0.75, "interbank_30d": 1.00},
}


def run_stress_test(bs: dict, scenarios: dict) -> pd.DataFrame:
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


# ============================================================
# 5. SUMMARY
# ============================================================

if __name__ == "__main__":
    print("=" * 60)
    print("BASEL III LIQUIDITY RISK CALCULATOR")
    print("=" * 60)

    lcr_result = calculate_lcr(balance_sheet)
    print("\n--- LCR (Base Case) ---")
    for k, v in lcr_result.items():
        if isinstance(v, float):
            print(f"{k}: {v:,.2f}  ({v:.1%})" if k == "LCR" else f"{k}: {v:,.2f}")
        else:
            print(f"{k}: {v}")

    nsfr_result = calculate_nsfr(balance_sheet)
    print("\n--- NSFR ---")
    for k, v in nsfr_result.items():
        if isinstance(v, float):
            print(f"{k}: {v:,.2f}  ({v:.1%})" if k == "NSFR" else f"{k}: {v:,.2f}")
        else:
            print(f"{k}: {v}")

    print("\n--- Stress Test Results (LCR under increasing stress) ---")
    stress_df = run_stress_test(balance_sheet, stress_scenarios)
    stress_df["LCR"] = stress_df["LCR"].apply(lambda x: f"{x:.1%}")
    print(stress_df.to_string(index=False))

    print("\n" + "=" * 60)
