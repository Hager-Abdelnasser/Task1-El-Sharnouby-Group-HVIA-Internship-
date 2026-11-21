# El-Sharnouby Group · Intelligence Hub

Streamlit dashboard for the HVIA Task 01 case (El-Sharnouby Group / Leo Moda).
Eleven tabs: Executive, Sales & Profit, Customers, Channels & Regions, Inventory & Demand, Marketing & Web,
Factory & Print, Quality & Returns, Supply Chain, AI Lab, Action Plan.

## Run
```bash
pip install -r requirements.txt
streamlit run app.py
```
Opens at http://localhost:8501. The data folder already holds the cleaned inputs (`sales.parquet` is the slim sales table),
so nothing else is needed. To rebuild from the original CSVs: `python prep.py path/to/Sharnouby_Enterprise`.

## Files
- `app.py` – tabs and charts
- `data.py` – loading, RFM, cohorts, forecast model, backtest
- `theme.py` – colors (navy / electric blue / cyan, from the HVIA and Leo Moda identity), fonts, KPI cards
- `prep.py` – builds `data/sales.parquet`

## AI Lab tools
1. Wholesale Deal Desk – discount ceiling simulator and approval ladder
2. Demand forecast (30/60/90 days, backtested) and replenishment list
3. Customer win-back list (opted-in customers only)
4. Marketing budget optimizer (same budget, diminishing returns)

Data is modeled training data. Purchase-order values do not reconcile with sales, so use them for relative comparison only.
