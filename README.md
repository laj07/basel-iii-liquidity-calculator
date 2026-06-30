# Basel III Liquidity Risk Calculator

An interactive tool that calculates the **Liquidity Coverage Ratio (LCR)** and **Net Stable Funding Ratio (NSFR)** for a hypothetical bank balance sheet, aligned to 
**APRA APS 210** (the Australian prudential standard for liquidity), with stress scenario testing.

<img width="2880" height="1334" alt="image" src="https://github.com/user-attachments/assets/813ab670-0138-403b-ad9a-66b586d388d6" />

---

## What it does

Banks are required under Basel III to hold enough liquid assets to survive a 30-day funding crisis (LCR) and to fund their long-term assets with stable, long-term funding (NSFR). 
This tool lets you:

- Input a custom bank balance sheet (assets, liabilities, capital)
- Instantly calculate LCR and NSFR against the 100% regulatory minimum
- Run three stress scenarios (Mild, Moderate, Severe) to see how the LCR deteriorates as deposit and funding run-off rates increase
- Visualise the results with live metrics and a stress test chart

## Why this matters

LCR and NSFR are core liquidity risk metrics used by treasury and risk teams at banks, and by regulators (APRA in Australia) to assess prudential soundness. 
Understanding how these ratios behave under stress is fundamental to bank liquidity risk management and is directly relevant to regulatory risk advisory work.

## How it works

**HQLA (High Quality Liquid Assets)** are categorised by liquidity tier and discounted with regulatory haircuts:
- Level 1 (cash, government bonds): 0% haircut
- Level 2A (AAA corporate bonds): 15% haircut
- Level 2B (lower-rated bonds): 50% haircut

**Net Cash Outflows** are estimated by applying run-off rates to each liability category (e.g. 5% for stable retail deposits, 100% for interbank funding),
reflecting how much of each funding source is assumed to leave the bank in a 30-day stress period.

```
LCR = Total HQLA / Total Net Cash Outflows
```

**ASF (Available Stable Funding)** and **RSF (Required Stable Funding)** are calculated similarly using NSFR factors that reflect funding stability and asset 
liquidity over a 1-year horizon.

```
NSFR = Total ASF / Total RSF
```

A ratio ≥ 100% means the bank passes the regulatory minimum.

## Stress testing

Three scenarios apply increasingly severe run-off assumptions to liabilities:

| Scenario | Retail (Stable) | Retail (Less Stable) | Wholesale | Interbank |
|---|---|---|---|---|
| Base Case | 5% | 10% | 25% | 100% |
| Mild Stress | 8% | 15% | 35% | 100% |
| Moderate Stress | 12% | 20% | 50% | 100% |
| Severe Stress | 20% | 30% | 75% | 100% |

This shows how a bank's liquidity position would deteriorate in a deposit run or funding market freeze, and at what point (if any) it would breach the regulatory minimum.

## Example output (default inputs)

| Metric | Result | Status |
|---|---|---|
| LCR (Base Case) | 305.0% | PASS |
| NSFR | 106.2% | PASS |
| LCR (Severe Stress) | 143.5% | PASS |

In this example, the bank maintains a strong liquidity buffer even under severe stress, though NSFR is the tighter of the two constraints, 
sitting only slightly above the regulatory minimum.

## Tech stack

- **Python** (core calculation logic)
- **pandas** (data structuring for stress test results)
- **Streamlit** (interactive web app interface)

## Project structure

```
├── app.py                                      # Streamlit web app
├── basel_calculator.py                         # Standalone Python script (terminal version)
├── Basel_III_Liquidity_Risk_Calculator.xlsx    # Original Excel model
├── requirements.txt
├── .gitignore
└── README.md
```

## How to run

**Streamlit app (recommended):**
```bash
pip install -r requirements.txt
streamlit run app.py
```

**Terminal script:**
```bash
python3 basel_calculator.py
```

## Limitations

This is a simplified educational model built for portfolio demonstration purposes. It is not intended for actual regulatory compliance use. 
Real-world LCR/NSFR calculations involve more granular asset/liability categorisation, intraday liquidity considerations, and currency-specific treatment that are out of scope here.
