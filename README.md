# El-Sharnouby Group — Enterprise Intelligence Hub

An end-to-end interactive **Business Intelligence & Operations Analytics Web Application** built with **Python** and **Streamlit** for **El-Sharnouby Group**, a vertically integrated apparel manufacturing and multi-channel retail enterprise. The platform unifies commercial, customer, supply chain, factory floor, quality control, marketing, and decision-simulation analytics into a single executive hub covering **3 years of operational data (Oct 2023 – Sep 2026)**.

---

## Application Preview

![El-Sharnouby Group Intelligence Hub Demo](assets/demo.gif)

> *Note: Replace `assets/demo.gif` above with the relative path to your uploaded GIF file (e.g., `./demo.gif` if placed in the root folder) or drag-and-drop the GIF directly into the GitHub README editor.*

---

## Business Problem & Objectives

Rapid top-line revenue growth often masks underlying margin erosion, inventory misallocation, and production bottlenecks. This Intelligence Hub was engineered to answer critical cross-functional questions:
- **Commercial & Margin Protection:** How severely is wholesale discounting eroding gross profit, and where should discount approval ceilings be set?
- **Customer Retention & Value:** Which RFM segments and acquisition cohorts drive sustainable repeat revenue versus one-time volume?
- **Inventory & Regional Optimization:** Where is stock trapped across warehouses and retail stores, and how do regional demand and margins compare across Egyptian governorates?
- **Marketing & Funnel Efficiency:** Which paid and organic channels deliver the highest ROAS, and how do promotional discounts impact campaign profitability?
- **Factory Floor & Quality Control:** Which production lines, manufacturing stages, and defect categories account for late orders and financial scrap/return losses?
- **Prescriptive Action Planning:** What quantified, ranked operational interventions will recover the highest annual gross profit?

---

## Key Features & Application Architecture

### 1. Executive Header & Global Operational Pulse
- **Cross-Entity Operational Efficiency Scorecards:** Real-time operational efficiency metrics and open issue counters across all five group entities:
  - **L&D Design** (Design & Sampling)
  - **L&D Tex** (Fabric & Knitting)
  - **L&D Production Hub** (Cutting, Sewing & Finishing)
  - **L&D Print** (Printing)
  - **L&D Moda** (Retail & Online)
- **Interactive Global Sidebar Filters:** Dynamic filtering by **Date Range** (`2023-10-01` to `2026-09-30`), **Sales Channel** (`Retail`, `Wholesale`, `Online`), and **Product Family** (`Kids Sets`, `Pajamas/Homewear`, `Sweatshirts`, `T-Shirts`), with clear scope notes indicating which views respond to commercial filters versus full-history operational baselines.

### 2. Multi-Tab Analytical Modules (11 Specialized Views)
1. **Executive Overview:**
   - Top-level KPIs: Net Sales (`EGP 421.3M`), Gross Margin (`EGP 64.9M` / `15.4%`), Units Sold (`1.66M`), Active Customers (`25.6K`), and Return Rate (`4.7%`).
   - Monthly Net Sales vs. Gross Margin trendlines, multi-year seasonality comparison (`2024` vs. `2025`), YoY net sales progression, and Channel Share of Sales vs. Share of Profit comparison.
2. **Sales & Profit:**
   - Discount-band profitability analysis (`No discount`, `Up to 10%`, `10% to 20%`, `20% to 30%`, `Over 30%`) illustrating margin compression on deep wholesale discounts.
   - Product portfolio bubble matrix (Net Sales vs. Gross Margin % sized by Gross Profit), margin by product family, Top 10 SKUs by Gross Profit, and Top-Quartile Volume SKUs operating under 10% margin.
3. **Customers:**
   - **RFM Segmentation:** Customer distribution and revenue share across *Champions, Loyal, Need Attention, Potential Loyalists, Hibernating, At Risk,* and *New* segments.
   - **Cohort Retention Heatmap:** Quarter-over-quarter cohort retention tracking from `2023Q4` through `2026Q3`.
   - Revenue per retail customer by acquisition channel and revenue breakdown by age band and gender.
4. **Channels & Regions:**
   - Channel unit economics comparing Online, Retail, and Wholesale margins alongside AOV (`with discount` vs. `no discount`).
   - Quarterly net sales trajectory, payment method distribution (`Bank Transfer`, `Card`, `Cash`, `Wallet`), and demand/margin breakdown across **13 Egyptian governorates** (led by Alexandria, Cairo, and Giza).
5. **Inventory & Demand:**
   - Stock health KPIs: Units in Stock (`77.9K`), Total Stocked Days (`1,197`), SKUs over 180 days of cover (`40`), and SKUs under 15 days of cover (`38`).
   - Stocked days and median days of cover across locations (`El-Sharnouby Wholesale Dock`, `L&D MODA - Mall Misr Store`, `L&D MODA Online Store`), an **ABC (Value) × XYZ (Demand Stability)** SKU matrix, and Top 10 slow-moving SKUs.
6. **Marketing & Web:**
   - Campaign KPIs: Marketing Spend (`EGP 14.6M`), Attributed Revenue (`EGP 179.7M`), Blended ROAS (`12.3x`), and High-ROAS Campaigns (`22 of 420`).
   - Platform performance comparison (`WhatsApp / CRM`, `Google`, `TikTok`, `Meta`, `Influencer`), Spend vs. Attributed Revenue bubble plot, ROAS by discount tier, web sessions vs. conversion rate trend, and full e-commerce funnel (`Sessions → Add to cart → Checkout → Order`).
7. **Factory & Print:**
   - Production KPIs: On-Time Delivery (`82.2%`), Late Orders (`16.3%`), First-Pass Yield (`90.9%`), Print Yield (`97.3%`), and Downtime (`4,949 h`).
   - Line-by-line efficiency (`LINE-01` to `LINE-05`), bottleneck stage breakdown (`Sewing`, `Finishing`, `Packing`, `Cutting`, `Printing`), print machine yield (`PR-M01` to `PR-M05`), and stacked downtime hours by machine and root cause.
8. **Quality & Returns:**
   - Quality KPIs: QC Reject Rate (`2.4%`), Reject Cost (`EGP 16.3M`), Customer Return Rate (`4.7%`), Return Cost (`EGP 2.5M`), and Total Quality Loss (`EGP 19.6M`).
   - **Defect Pareto Chart** (losses in EGP + cumulative % curve across defect types) and root-cause loss ranking (`Curing temperature`, `Process variation`, `Handling / packing`, `Operator method`, etc.).
9. **Supply Chain:**
   - Supplier KPIs: On-Time Delivery (`65.4%`), Average Delay (`1.0 day`), Material Reject Rate (`1.8%`), and High-Risk Suppliers (`2 of 12`).
   - Supplier reliability bubble chart (OTD % vs. Reject Rate % sized by order value), on-time delivery by material category, and a detailed supplier scorecard table.
10. **AI Lab (Decision Simulators):**
    - Interactive simulation tools designed to test operational changes before execution:
      - **Wholesale Deal Desk:** Simulates annual gross profit vs. volume lost across discount ceilings (`15%` to `40%`), plus an interactive **Deal Check Calculator** (select SKU, order quantity, and proposed discount to evaluate resulting order margin, gross profit, and required approval level).
      - **Forecast & Replenishment**, **Customer Win-Back List**, and **Marketing Budget Optimizer** modules.
11. **Action Plan:**
    - Prioritized, quantified executive roadmap ranking the top 8 cross-functional initiatives by indicative annual EGP impact, backed by data-driven evidence and implementation complexity ratings (`High`, `Medium`, `Low`).

---

## Project Structure

```text
.
├── .streamlit/          # Streamlit theme & server configuration
├── assets/              # Demo GIF and visual media assets
├── data/                # Structured commercial, customer, inventory, marketing & factory datasets
├── app.py               # Main Streamlit UI, multi-tab architecture, KPI cards & interactive charts
├── data.py              # Data ingestion, caching, and relational dataset loading utilities
├── prep.py              # Analytical aggregations, RFM/cohort calculations & metric formatting
├── theme.py             # Custom dark-mode executive styling, color palette & chart templates
└── requirements.txt     # Python package dependencies
```

---

## Installation & Local Setup

1. **Clone the repository:**
   ```bash
   git clone <your-repository-url>
   cd <your-repository-folder>
   ```

2. **Create and activate a virtual environment (recommended):**
   ```bash
   python -m venv venv
   # On Windows:
   venv\Scripts\activate
   # On macOS/Linux:
   source venv/bin/activate
   ```

3. **Install required dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Launch the Streamlit application:**
   ```bash
   streamlit run app.py
   ```

---

## Tech Stack

- **Language:** Python
- **Web Framework:** Streamlit
- **Data Manipulation & Analytics:** Pandas, NumPy
- **Interactive Data Visualization:** Plotly
- **Architecture:** Modular separation of data ingestion (`data.py`), analytical transformations (`prep.py`), custom UI/chart theming (`theme.py`), and interactive multi-tab presentation (`app.py`)
