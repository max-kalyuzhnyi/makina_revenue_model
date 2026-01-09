# Makina Revenue Model Dashboard

An interactive dashboard for analyzing Makina's revenue projections for 2025-2027.

## Features

### Dashboard Tab
- **End of 2027 Summary**: Key metrics including Total TVL, Revenue, DAO Revenue, DAO Take Rate, FDV, and FDV/TVL ratio
- **TVL by Asset Chart**: Stacked bar chart showing TVL breakdown by USDC, ETH, and BTC across 2025-2027
- **FDV and FDV/TVL Chart**: Combined bar and line chart showing valuation metrics
- **DAO Fees Chart**: Stacked bar chart showing Management and Performance fees
- **DAO Take Rate Chart**: Line chart showing DAO take rate trends

### Configuration Tab
- **Year Selector**: Choose which year (2025, 2026, 2027) to configure
- **Asset Parameters**: Adjust TVL amounts, prices, management fees, performance fees, and performance growth for each asset (USDC, ETH, BTC)
- **Fee Split**: Configure DAO/Operator split for management and performance fees
- **Valuation Parameters**: Adjust Price/Revenue ratio
- **DAO Revenue Split**: Configure allocation between DAO Operations, Buyback, and Revenue Share
- **Save/Reset**: Save changes or reset to original Excel values

## Running the Dashboard

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Run the dashboard:
```bash
streamlit run makina_app.py
```

3. Open your browser to the URL shown in the terminal (usually http://localhost:8501)

## Data Source

The dashboard loads initial data from `Makina Revenue Generation Estimates.xlsx`, which contains:
- 3 sheets: MAK Revenue 2025, 2026, 2027
- Input parameters: TVL (in native units), asset prices, fee rates, performance growth
- Fee split configurations between DAO and Operator

## How It Works

### Revenue Calculation
1. **TVL in USD** = Native Units × Asset Price
2. **Management Fee Revenue** = TVL (native) × Management Fee %
3. **Performance Fee Revenue** = TVL (native) × Performance Growth % × Performance Fee %
4. **DAO Revenue** = (Management Fees × DAO Mgmt Split %) + (Performance Fees × DAO Perf Split %)
5. **DAO Take Rate** = DAO Revenue / Total TVL × 100

### Valuation Metrics
- **FDV (Fully Diluted Valuation)** = DAO Revenue × Price/Revenue Ratio
- **FDV/TVL Ratio** = FDV / Total TVL

## Modifying Inputs

Use the Configuration tab to adjust:
- TVL amounts for each asset (in native units: USDC, ETH count, BTC count)
- Asset prices (USDC=$1, ETH price, BTC price)
- Fee percentages (Management and Performance)
- Performance growth rates (expected return for each asset)
- DAO/Operator split (how fees are divided)
- Price/Revenue multiple (for valuation)
- DAO revenue allocation (Operations/Buyback/Revenue Share)

Changes are applied in real-time to all charts and metrics.
