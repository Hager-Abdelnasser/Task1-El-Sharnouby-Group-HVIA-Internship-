from pathlib import Path
import numpy as np, pandas as pd, streamlit as st
from sklearn.linear_model import Ridge

D = Path(__file__).parent / "data"

def _csv(name, **kw):
    return pd.read_csv(D / name, encoding="utf-8-sig", **kw)

@st.cache_data(show_spinner="Loading sales…")
def sales():
    s = pd.read_parquet(D / "sales.parquet")
    s["Month"] = s["Order_Date"].dt.to_period("M").dt.to_timestamp()
    return s

@st.cache_data
def table(name, dates=()):
    return _csv(name, parse_dates=list(dates))

@st.cache_data
def customers():
    return _csv("Customers.csv", parse_dates=["Join_Date"])

# ---------- RFM ----------
@st.cache_data(show_spinner="Scoring customers (RFM)…")
def rfm():
    s = sales()
    ref = s.Order_Date.max()
    g = s.groupby("Customer_ID").agg(Last=("Order_Date", "max"), Orders=("Invoice_ID", "nunique"),
                                      Revenue=("Net_Sales_EGP", "sum"), Profit=("Gross_Profit_EGP", "sum"),
                                      Type=("Channel", lambda x: "Wholesale" if (x == "Wholesale").any() else "Retail/Online"))
    g["Recency"] = (ref - g.Last).dt.days
    q = lambda x, asc: pd.qcut(x.rank(method="first", ascending=asc), 5, labels=[1, 2, 3, 4, 5]).astype(int)
    g["R"], g["F"], g["M"] = q(g.Recency, False), q(g.Orders, True), q(g.Revenue, True)
    def seg(r):
        if r.R >= 4 and r.F >= 4: return "Champions"
        if r.R >= 3 and r.F >= 4: return "Loyal"
        if r.R == 5 and r.F == 1: return "New"
        if r.R >= 4: return "Potential loyalists"
        if r.R <= 2 and r.F >= 3: return "At risk"
        if r.R == 3: return "Need attention"
        return "Hibernating"
    g["Segment"] = g.apply(seg, axis=1)
    return g.reset_index()

@st.cache_data
def cohorts():
    s = sales()
    f = s.groupby("Customer_ID").Order_Date.min().dt.to_period("Q").rename("Cohort")
    t = s[["Customer_ID", "Order_Date"]].drop_duplicates().join(f, on="Customer_ID")
    t["Q"] = t.Order_Date.dt.to_period("Q")
    t["k"] = (t.Q - t.Cohort).apply(lambda x: x.n)
    m = t.groupby(["Cohort", "k"]).Customer_ID.nunique().unstack()
    r = m.div(m[0], axis=0)
    r.index = r.index.astype(str)
    # drop first cohort (company start, not a real "new" cohort) and incomplete tail
    return r, m[0]

# ---------- Forecast ----------
def _design(idx, t0):
    t = (np.arange(len(idx)) + t0).reshape(-1, 1)
    mo = np.eye(12)[idx.month.values - 1]
    return np.hstack([t / 12.0, mo])

def fit_forecast(y: pd.Series, h=3):
    """log-linear trend + month-of-year effect (ridge). Returns forecast df with 80% band + residual sigma."""
    y = y.sort_index()
    X = _design(y.index, 0)
    m = Ridge(alpha=0.05).fit(X, np.log(y.values))
    res = np.log(y.values) - m.predict(X)
    sig = float(np.std(res, ddof=1))
    fut = pd.date_range(y.index[-1] + pd.offsets.MonthBegin(1), periods=h, freq="MS")
    Xf = _design(fut, len(y))
    mu = m.predict(Xf)
    out = pd.DataFrame({"Forecast": np.exp(mu), "Low": np.exp(mu - 1.28 * sig * 1.3), "High": np.exp(mu + 1.28 * sig * 1.3)}, index=fut)
    return out, sig

def backtest(y: pd.Series, h=3, n_cut=6):
    errs = []
    for k in range(n_cut):
        cut = len(y) - h - k
        if cut < 24: break
        fc, _ = fit_forecast(y.iloc[:cut], h)
        act = y.iloc[cut:cut + h]
        errs += list(np.abs(fc.Forecast.values - act.values) / act.values)
    return float(np.mean(errs)) if errs else np.nan

@st.cache_data(show_spinner="Training forecast…")
def forecasts():
    s = sales()
    m = s.groupby(["Month", "Channel"]).agg(Net=("Net_Sales_EGP", "sum"), Units=("Quantity", "sum")).reset_index()
    res = {}
    for ch in ["Wholesale", "Retail", "Online"]:
        y = m[m.Channel == ch].set_index("Month").Net
        fc, sig = fit_forecast(y)
        res[ch] = dict(hist=y, fc=fc, mape=backtest(y))
    tot = m.groupby("Month").Net.sum()
    fc, sig = fit_forecast(tot)
    res["Total"] = dict(hist=tot, fc=fc, mape=backtest(tot))
    return res

def season_factor(month_ts):
    """How much the forecast month's demand differs from the trailing-3-month average (used for replenishment)."""
    f = forecasts()["Total"]
    base = f["hist"].iloc[-3:].mean()
    return float(f["fc"].Forecast.iloc[0] / base)
