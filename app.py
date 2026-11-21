import numpy as np, pandas as pd, streamlit as st
import plotly.express as px, plotly.graph_objects as go
import data as dm
from theme import *

st.set_page_config(page_title="El-Sharnouby Group · Intelligence Hub", page_icon="🧵", layout="wide")
st.markdown(CSS, unsafe_allow_html=True)

S = dm.sales()
DMIN, DMAX = S.Order_Date.min().date(), S.Order_Date.max().date()

# ---------------- Sidebar filters ----------------
with st.sidebar:
    st.markdown("### Filters")
    dr = st.date_input("Date range", (DMIN, DMAX), min_value=DMIN, max_value=DMAX)
    if len(dr) != 2: dr = (DMIN, DMAX)
    chans = st.multiselect("Channel", ["Wholesale", "Retail", "Online"], default=["Wholesale", "Retail", "Online"])
    fams = st.multiselect("Product family", sorted(S.Product_Family.unique()), default=sorted(S.Product_Family.unique()))
    st.caption("Filters drive the Sales, Customers, Channels and Executive tabs. Factory, Quality and Supply tabs use the date range only.")
    st.divider()
    st.caption("Data: 3 years (Oct 2023 – Sep 2026). Modeled training data anchored to public Leo Moda products and prices. "
               "Q4 2023 is the first quarter on record, so 2023 is a partial year.")

d0, d1 = pd.Timestamp(dr[0]), pd.Timestamp(dr[1])
mask = S.Order_Date.between(d0, d1) & S.Channel.isin(chans) & S.Product_Family.isin(fams)
F = S[mask]
span = (d1 - d0).days + 1
P = S[S.Order_Date.between(d0 - pd.Timedelta(days=span), d0 - pd.Timedelta(days=1)) & S.Channel.isin(chans) & S.Product_Family.isin(fams)]
if F.empty:
    st.warning("No sales match these filters. Widen the date range or channels."); st.stop()

def dl(cur, prev):
    return None if prev in (0, None) or pd.isna(prev) or P.empty else cur / prev - 1

def inrange(df, col):
    return df[df[col].between(d0, d1)]

# ---------------- Header + value chain ----------------
GO = dm.table("Group_Operations.csv", ["Month"])
last_m = GO.Month.max()
order = ["LEO DESIGN", "LEO TEX", "LEO PRODUCTION HUB", "LEO PRINT", "LEO MODA"]
fn = {"LEO DESIGN": "Design & patterns", "LEO TEX": "Woven fabric", "LEO PRODUCTION HUB": "Garments, up to 5,000 pcs/day",
      "LEO PRINT": "Printing", "LEO MODA": "Retail & online"}
nodes = ""
for u in order:
    g = GO[GO.Business_Unit == u]
    cur = g[g.Month == last_m].iloc[0]
    avg = g.Operational_Efficiency_Pct.tail(12).mean()
    nodes += (f'<div class="node"><b>{u.title().replace("Leo","LEO")}</b><span>{fn[u]}</span>'
              f'<em>{cur.Operational_Efficiency_Pct:.1f}%</em><i>{int(cur.Open_Issues_Count)} open issues</i></div>')
st.markdown(f'<div class="hero"><div><h1>El-Sharnouby Group · Intelligence Hub</h1>'
            f'<small>From raw fabric to the customer who wears it. Showing {dr[0]:%d %b %Y} to {dr[1]:%d %b %Y}</small></div>'
            f'<small>Operational efficiency, {last_m:%b %Y}</small></div><div class="chain">{nodes}</div>', unsafe_allow_html=True)

tabs = st.tabs(["Executive", "Sales & Profit", "Customers", "Channels & Regions", "Inventory & Demand",
                "Marketing & Web", "Factory & Print", "Quality & Returns", "Supply Chain", "AI Lab", "Action Plan"])

net, gp, units = F.Net_Sales_EGP.sum(), F.Gross_Profit_EGP.sum(), F.Quantity.sum()
marg = gp / net
ret_rate = (F.Returned == "Yes").mean()
by_ch = F.groupby("Channel").agg(Net=("Net_Sales_EGP", "sum"), GP=("Gross_Profit_EGP", "sum"), Units=("Quantity", "sum"),
                                  Inv=("Invoice_ID", "nunique"), Disc=("Discount_Pct", "mean"),
                                  Ret=("Returned", lambda x: (x == "Yes").mean()), Refund=("Refund_Value_EGP", "sum"))
by_ch["Margin"] = by_ch.GP / by_ch.Net

# ===================== 1. EXECUTIVE =====================
with tabs[0]:
    c = st.columns(6)
    c[0].markdown(kpi("Net sales", fmt(net), dl(net, P.Net_Sales_EGP.sum())), unsafe_allow_html=True)
    c[1].markdown(kpi("Gross profit", fmt(gp), dl(gp, P.Gross_Profit_EGP.sum())), unsafe_allow_html=True)
    pm = P.Gross_Profit_EGP.sum() / P.Net_Sales_EGP.sum() if len(P) else None
    c[2].markdown(kpi("Gross margin", fmt(marg, "pct"), None if pm is None else marg - pm, suffix=" pts vs prior"), unsafe_allow_html=True)
    c[3].markdown(kpi("Units sold", fmt(units, "num"), dl(units, P.Quantity.sum())), unsafe_allow_html=True)
    c[4].markdown(kpi("Active customers", fmt(F.Customer_ID.nunique(), "num"), dl(F.Customer_ID.nunique(), P.Customer_ID.nunique())), unsafe_allow_html=True)
    c[5].markdown(kpi("Return rate", fmt(ret_rate, "pct"), None), unsafe_allow_html=True)

    wsh = by_ch.loc["Wholesale"] if "Wholesale" in by_ch.index else None
    if wsh is not None and len(by_ch) > 1:
        st.markdown(insight(f"<b>Wholesale brings {wsh.Net/net:.0%} of sales but only {wsh.GP/gp:.0%} of profit.</b> "
                            f"Its margin is {wsh.Margin:.1%}, against {(gp-wsh.GP)/(net-wsh.Net):.1%} for retail and online together. "
                            f"Growth is not the problem. Discounting is."), unsafe_allow_html=True)

    a, b = st.columns([1.7, 1])
    m = F.groupby("Month").agg(Net=("Net_Sales_EGP", "sum"), GP=("Gross_Profit_EGP", "sum")).reset_index()
    m["Margin"] = m.GP / m.Net
    fig = go.Figure()
    fig.add_bar(x=m.Month, y=m.Net, name="Net sales", marker_color=BLUE)
    fig.add_scatter(x=m.Month, y=m.Margin, name="Gross margin", yaxis="y2", line=dict(color=CYAN, width=2.5))
    fig.update_layout(title="Monthly net sales and gross margin", yaxis2=dict(overlaying="y", side="right", tickformat=".0%", showgrid=False, range=[0, .3]),
                      yaxis=dict(tickformat=".2s"))
    a.plotly_chart(style(fig, 360), width="stretch")

    mix = by_ch.reset_index()
    fig = go.Figure()
    fig.add_bar(x=mix.Channel, y=mix.Net / net, name="Share of sales", marker_color=BLUE, text=(mix.Net / net).map("{:.0%}".format))
    fig.add_bar(x=mix.Channel, y=mix.GP / gp, name="Share of profit", marker_color=CYAN, text=(mix.GP / gp).map("{:.0%}".format))
    fig.update_layout(title="Share of sales vs share of profit", barmode="group", yaxis=dict(tickformat=".0%"))
    b.plotly_chart(style(fig, 360), width="stretch")

    a, b = st.columns(2)
    seas = S[S.Order_Date.dt.year.isin([2024, 2025])].groupby(["Month"]).Net_Sales_EGP.sum().reset_index()
    seas["m"] = seas.Month.dt.month; seas["y"] = seas.Month.dt.year.astype(str)
    fig = px.line(seas, x="m", y="Net_Sales_EGP", color="y", markers=True, title="Seasonality: 2024 vs 2025 (full years)",
                  labels={"m": "Month", "Net_Sales_EGP": "Net sales"})
    fig.update_xaxes(dtick=1); fig.update_yaxes(tickformat=".2s")
    a.plotly_chart(style(fig, 320), width="stretch")
    yr = S.assign(Y=S.Order_Date.dt.year.astype(str)).groupby("Y").agg(Net=("Net_Sales_EGP", "sum"), GP=("Gross_Profit_EGP", "sum")).reset_index()
    yr["Margin"] = yr.GP / yr.Net
    ytd = S[S.Order_Date.dt.month <= 9].assign(Y=lambda d: d.Order_Date.dt.year).groupby("Y").Net_Sales_EGP.sum()
    g = ytd.get(2026, 0) / ytd.get(2025, 1) - 1
    fig = px.bar(yr, x="Y", y="Net", text=yr.Margin.map("{:.1%} margin".format), title="Net sales by year (2023 = Q4 only, 2026 = Jan to Sep)")
    fig.update_traces(marker_color=BLUE, textposition="outside"); fig.update_yaxes(tickformat=".2s")
    b.plotly_chart(style(fig, 320), width="stretch")
    st.markdown(insight(f"December is the peak month and January to February the low point. Jan to Sep 2026 is <b>{g:+.1%}</b> vs Jan to Sep 2025, "
                        f"and the margin has stayed flat near 15% for three years. Growth has not improved the quality of profit."), unsafe_allow_html=True)

# ===================== 2. SALES & PROFIT =====================
with tabs[1]:
    st.markdown('<div class="sec">Does the discount pay for itself?</div>', unsafe_allow_html=True)
    F2 = F.assign(Band=pd.cut(F.Discount_Pct, [-.01, 0, .10, .20, .30, .60], labels=["No discount", "Up to 10%", "10 to 20%", "20 to 30%", "Over 30%"]))
    bd = F2.groupby("Band", observed=True).agg(Net=("Net_Sales_EGP", "sum"), GP=("Gross_Profit_EGP", "sum"), Lines=("Row_ID" if "Row_ID" in F2 else "Invoice_ID", "count")).reset_index()
    bd["Margin"] = bd.GP / bd.Net
    a, b = st.columns(2)
    fig = px.bar(bd, x="Band", y="Margin", text=bd.Margin.map("{:.1%}".format), title="Gross margin by discount level")
    fig.update_traces(marker_color=[MINT, MINT, GOLD, CORAL, CORAL][:len(bd)], textposition="outside"); fig.update_yaxes(tickformat=".0%")
    a.plotly_chart(style(fig, 340), width="stretch")
    fig = px.pie(bd, names="Band", values="Net", hole=.6, title="Where the sales volume sits", color_discrete_sequence=[MINT, "#6FD8B0", GOLD, CORAL, "#FF9A9A"])
    b.plotly_chart(style(fig, 340), width="stretch")
    hi = F2[F2.Discount_Pct > .30]
    if len(hi):
        st.markdown(insight(f"<b>{hi.Net_Sales_EGP.sum()/net:.0%} of sales are sold at more than 30% off, and they earn a {hi.Gross_Profit_EGP.sum()/hi.Net_Sales_EGP.sum():.1%} margin.</b> "
                            f"Full-price sales earn about 40%. Every deep discount in the data is a wholesale order. See the Deal Desk in the AI Lab.", warn=True), unsafe_allow_html=True)

    st.markdown('<div class="sec">Product portfolio</div>', unsafe_allow_html=True)
    pr = F.groupby(["Product_Name", "Product_Family"]).agg(Net=("Net_Sales_EGP", "sum"), GP=("Gross_Profit_EGP", "sum"), Units=("Quantity", "sum"), Disc=("Discount_Pct", "mean")).reset_index()
    pr["Margin"] = pr.GP / pr.Net
    pr["Size"] = pr.GP.clip(lower=0) + 1
    a, b = st.columns([1.5, 1])
    fig = px.scatter(pr, x="Net", y="Margin", size="Size", color="Product_Family", hover_name="Product_Name", title="Sales vs margin (bubble = gross profit)")
    fig.add_hline(y=marg, line_dash="dot", line_color=GOLD, annotation_text="group margin"); fig.update_xaxes(tickformat=".2s"); fig.update_yaxes(tickformat=".0%")
    a.plotly_chart(style(fig, 400), width="stretch")
    fam = F.groupby("Product_Family").agg(Net=("Net_Sales_EGP", "sum"), GP=("Gross_Profit_EGP", "sum")).reset_index(); fam["Margin"] = fam.GP / fam.Net
    fig = px.bar(fam.sort_values("Margin"), x="Margin", y="Product_Family", orientation="h", text=fam.sort_values("Margin").Margin.map("{:.1%}".format), title="Margin by family")
    fig.update_traces(marker_color=CYAN); fig.update_xaxes(tickformat=".0%")
    b.plotly_chart(style(fig, 400), width="stretch")
    thin = pr[(pr.Net > pr.Net.quantile(.75)) & (pr.Margin < .10)].sort_values("Net", ascending=False)
    top = pr.sort_values("GP", ascending=False).head(10)
    a, b = st.columns(2)
    a.markdown("**Top 10 by gross profit**"); a.dataframe(top[["Product_Name", "Net", "GP", "Margin"]].style.format({"Net": "{:,.0f}", "GP": "{:,.0f}", "Margin": "{:.1%}"}), hide_index=True, width="stretch")
    b.markdown("**Big sellers with thin margin (top quartile sales, under 10% margin)**")
    b.dataframe(thin[["Product_Name", "Net", "GP", "Margin", "Disc"]].style.format({"Net": "{:,.0f}", "GP": "{:,.0f}", "Margin": "{:.1%}", "Disc": "{:.0%}"}), hide_index=True, width="stretch")
    if len(thin):
        t0 = thin.iloc[0]
        st.markdown(insight(f"<b>{len(thin)} best-selling products earn under 10% margin.</b> The worst is <i>{t0.Product_Name}</i>: {fmt(t0.Net)} of sales and only {fmt(t0.GP)} of profit ({t0.Margin:.1%}). Reprice or cap discounts here first."), unsafe_allow_html=True)

# ===================== 3. CUSTOMERS =====================
with tabs[2]:
    R = dm.rfm()
    ret = R[R.Type == "Retail/Online"]
    c = st.columns(5)
    c[0].markdown(kpi("Customers with purchases", fmt(len(R), "num")), unsafe_allow_html=True)
    c[1].markdown(kpi("Repeat rate (retail/online)", fmt((ret.Orders > 1).mean(), "pct")), unsafe_allow_html=True)
    c[2].markdown(kpi("Avg orders per customer", f"{ret.Orders.mean():.1f}"), unsafe_allow_html=True)
    c[3].markdown(kpi("Inactive over 180 days", fmt((R.Recency > 180).mean(), "pct")), unsafe_allow_html=True)
    top10 = R.Revenue.sort_values(ascending=False).head(int(len(R) * .1)).sum() / R.Revenue.sum()
    c[4].markdown(kpi("Top 10% of customers", fmt(top10, "pct") + " of sales"), unsafe_allow_html=True)
    st.caption("RFM scores use the full purchase history up to 30 Sep 2026 and ignore the sidebar filters.")
    sg = R.groupby("Segment").agg(Customers=("Customer_ID", "count"), Revenue=("Revenue", "sum"), Recency=("Recency", "median"), Orders=("Orders", "mean")).reset_index()
    sg["Share"] = sg.Revenue / sg.Revenue.sum()
    a, b = st.columns(2)
    cmap = {"Champions": BLUE, "Loyal": CYAN, "Potential loyalists": MINT, "New": "#7CE0C1", "Need attention": GOLD, "At risk": CORAL, "Hibernating": "#7B8BB0"}
    fig = px.bar(sg.sort_values("Customers"), x="Customers", y="Segment", orientation="h", color="Segment", color_discrete_map=cmap, title="Customers per RFM segment", text="Customers")
    fig.update_layout(showlegend=False); a.plotly_chart(style(fig, 340), width="stretch")
    fig = px.pie(sg, names="Segment", values="Revenue", hole=.6, color="Segment", color_discrete_map=cmap, title="Share of revenue by segment")
    b.plotly_chart(style(fig, 340), width="stretch")
    ch = sg[sg.Segment == "Champions"].iloc[0]; ar = sg[sg.Segment == "At risk"].iloc[0]
    st.markdown(insight(f"<b>{ch.Customers:,.0f} Champions ({ch.Customers/len(R):.0%} of customers) produce {ch.Share:.0%} of revenue</b> (wholesale accounts are a big part of this). "
                        f"<b>{ar.Customers:,.0f} customers are At Risk</b>: they bought several times but have gone quiet, worth {fmt(ar.Revenue)} so far. This is the first win-back target."), unsafe_allow_html=True)
    coh, size = dm.cohorts()
    fig = px.imshow(coh.iloc[:, :9].round(2), text_auto=".0%", color_continuous_scale=[[0, NAVY], [1, CYAN]], aspect="auto",
                    labels=dict(x="Quarters since first purchase", y="First-purchase quarter", color="Still buying"), title="Cohort retention: share of each cohort that is still buying")
    st.plotly_chart(style(fig, 400), width="stretch")
    st.markdown(insight("About <b>4 in 10 new customers are still buying one year later</b>, and a newer cohort loses roughly half of its customers in the first quarter. "
                        "The 2023 Q4 cohort looks stronger because it includes customers who were already buying before our data starts."), unsafe_allow_html=True)
    C = dm.customers()
    a, b = st.columns(2)
    acq = C.merge(R[["Customer_ID", "Revenue", "Orders"]], on="Customer_ID", how="inner").groupby("Acquisition_Channel").agg(Customers=("Customer_ID", "count"), Revenue=("Revenue", "sum"), Orders=("Orders", "mean")).reset_index()
    acq = acq[acq.Acquisition_Channel != "Wholesale Sales"]; acq["Per customer"] = acq.Revenue / acq.Customers
    fig = px.bar(acq.sort_values("Per customer"), x="Per customer", y="Acquisition_Channel", orientation="h", text=acq.sort_values("Per customer")["Per customer"].map("{:,.0f}".format), title="Revenue per retail customer by acquisition channel (EGP)")
    fig.update_traces(marker_color=BLUE); a.plotly_chart(style(fig, 320), width="stretch")
    dem = C[C.Customer_Type == "Retail"].merge(R[["Customer_ID", "Revenue"]], on="Customer_ID")
    dg = dem.groupby(["Age_Band", "Gender"]).Revenue.sum().reset_index()
    fig = px.bar(dg, x="Age_Band", y="Revenue", color="Gender", barmode="group", title="Retail revenue by age band and gender", color_discrete_sequence=[BLUE, CYAN, VIOLET])
    fig.update_yaxes(tickformat=".2s"); b.plotly_chart(style(fig, 320), width="stretch")
    w = R[R.Type == "Wholesale"].sort_values("Revenue", ascending=False)
    st.markdown(insight(f"<b>Wholesale is a long tail, not a few giants:</b> {len(w):,} accounts, the top 50 hold only {w.Revenue.head(50).sum()/w.Revenue.sum():.0%} of wholesale revenue. "
                        f"A tiering programme (volume bands with matching discount ceilings) is more realistic than a handful of key-account deals."), unsafe_allow_html=True)

# ===================== 4. CHANNELS & REGIONS =====================
with tabs[3]:
    t = by_ch.reset_index()
    t["AOV"] = t.Net / t.Inv; t["Profit per invoice"] = t.GP / t.Inv
    cols = st.columns(len(t))
    for col, (_, r) in zip(cols, t.iterrows()):
        col.markdown(kpi(f"{r.Channel}: margin", fmt(r.Margin, "pct")) + f'<div class="kpi" style="margin-top:6px"><div class="l">AOV · returns · avg discount</div><div class="d flat">{fmt(r.AOV)} · {r.Ret:.1%} · {r.Disc:.0%}</div></div>', unsafe_allow_html=True)
    q = F.assign(Q=F.Order_Date.dt.to_period("Q").astype(str)).groupby(["Q", "Channel"]).Net_Sales_EGP.sum().reset_index()
    a, b = st.columns(2)
    fig = px.bar(q, x="Q", y="Net_Sales_EGP", color="Channel", title="Quarterly net sales by channel", color_discrete_sequence=[BLUE, CYAN, VIOLET]); fig.update_yaxes(tickformat=".2s")
    a.plotly_chart(style(fig, 340), width="stretch")
    pay = F.groupby(["Channel", "Payment_Method"]).Net_Sales_EGP.sum().reset_index()
    fig = px.bar(pay, x="Channel", y="Net_Sales_EGP", color="Payment_Method", barmode="relative", title="Payment mix by channel", color_discrete_sequence=[BLUE, CYAN, VIOLET, MINT]); fig.update_yaxes(tickformat=".2s")
    b.plotly_chart(style(fig, 340), width="stretch")
    gv = F.groupby("Customer_Governorate").agg(Net=("Net_Sales_EGP", "sum"), GP=("Gross_Profit_EGP", "sum")).reset_index(); gv["Margin"] = gv.GP / gv.Net
    gv = gv.sort_values("Net", ascending=False)
    fig = go.Figure(); fig.add_bar(x=gv.Customer_Governorate, y=gv.Net, name="Net sales", marker_color=BLUE)
    fig.add_scatter(x=gv.Customer_Governorate, y=gv.Margin, name="Margin", yaxis="y2", mode="lines+markers", line=dict(color=CYAN))
    fig.update_layout(title="Demand by governorate: sales and margin", yaxis2=dict(overlaying="y", side="right", tickformat=".0%", showgrid=False, range=[0, .4]), yaxis=dict(tickformat=".2s"))
    st.plotly_chart(style(fig, 360), width="stretch")
    alx = gv[gv.Customer_Governorate == "Alexandria"].Net.sum() / gv.Net.sum()
    st.markdown(insight(f"<b>Alexandria alone is {alx:.0%} of sales</b>, followed by Cairo and Giza. Retail has one store (Sidi Bishr) and online reaches the whole country. "
                        f"Cairo and Giza demand is large enough to test a second Leo Moda location or a Cairo pick-up point. Online margin ({by_ch.Margin.get('Online', float('nan')):.0%}) is close to the store, so online can grow without losing profit."), unsafe_allow_html=True)

# ===================== 5. INVENTORY & DEMAND =====================
INV = dm.table("Inventory_History.csv", ["Snapshot_Month"])
with tabs[4]:
    snap = INV[INV.Snapshot_Month == INV.Snapshot_Month.max()].copy()
    snap["Cover"] = snap.Days_of_Cover.clip(upper=365)
    byloc = INV.groupby("Location_Name").agg(Stockout=("Stockout_Days_In_Month", "sum")).join(
        snap.groupby("Location_Name").agg(Stock=("Closing_Stock", "sum"), Cover=("Cover", "median")))
    c = st.columns(4)
    c[0].markdown(kpi("Units in stock (Sep 2026)", fmt(snap.Closing_Stock.sum(), "num")), unsafe_allow_html=True)
    c[1].markdown(kpi("Total stockout days (3 yrs)", fmt(INV.Stockout_Days_In_Month.sum(), "num")), unsafe_allow_html=True)
    c[2].markdown(kpi("SKUs over 180 days of cover", f"{(snap.Days_of_Cover > 180).sum()}"), unsafe_allow_html=True)
    c[3].markdown(kpi("SKUs under 15 days of cover", f"{(snap.Days_of_Cover < 15).sum()}"), unsafe_allow_html=True)
    a, b = st.columns(2)
    fig = px.bar(byloc.reset_index(), x="Location_Name", y="Stockout", text="Stockout", title="Stockout days by location", color_discrete_sequence=[CORAL])
    a.plotly_chart(style(fig, 330), width="stretch")
    fig = px.bar(byloc.reset_index(), x="Location_Name", y="Cover", text=byloc.Cover.round(0).values, title="Median days of cover by location (Sep 2026)", color_discrete_sequence=[CYAN])
    b.plotly_chart(style(fig, 330), width="stretch")
    w_so = byloc.loc["El-Sharnouby Wholesale Desk", "Stockout"] / byloc.Stockout.sum()
    st.markdown(insight(f"<b>The stock is in the wrong place.</b> The wholesale desk has {w_so:.0%} of all stockout days and only ~20 days of cover, while the store and online hold 140 to 170 days of cover. "
                        f"Cash is tied up in retail shelves while the biggest-volume channel runs dry. Rebalancing is the cheapest win in the business.", warn=True), unsafe_allow_html=True)
    # ABC / XYZ
    s12 = S[S.Order_Date > S.Order_Date.max() - pd.Timedelta(days=365)]
    pm_ = s12.groupby(["Product_Name", "Month"]).Quantity.sum().unstack(fill_value=0)
    abc = s12.groupby("Product_Name").Net_Sales_EGP.sum().sort_values(ascending=False)
    cum = abc.cumsum() / abc.sum()
    abc_c = pd.Series(np.where(cum <= .8, "A", np.where(cum <= .95, "B", "C")), index=abc.index)
    cv = (pm_.std(axis=1) / pm_.mean(axis=1)).reindex(abc.index)
    xyz = pd.Series(np.where(cv <= cv.quantile(.33), "X", np.where(cv <= cv.quantile(.66), "Y", "Z")), index=abc.index)
    mat = pd.crosstab(abc_c, xyz).reindex(index=["A", "B", "C"], columns=["X", "Y", "Z"]).fillna(0)
    a, b = st.columns([1, 1.4])
    fig = px.imshow(mat, text_auto=True, color_continuous_scale=[[0, CARD], [1, BLUE]], title="ABC (value) × XYZ (demand stability), SKU count", labels=dict(x="XYZ: X steady, Z erratic", y="ABC: A = top 80% of sales"))
    a.plotly_chart(style(fig, 340), width="stretch")
    sk = INV.groupby("Product_Name").Stockout_Days_In_Month.sum().sort_values(ascending=False).head(10).reset_index()
    fig = px.bar(sk.sort_values("Stockout_Days_In_Month"), x="Stockout_Days_In_Month", y="Product_Name", orientation="h", title="Top 10 SKUs by stockout days", color_discrete_sequence=[CORAL])
    b.plotly_chart(style(fig, 340), width="stretch")
    st.markdown(insight(f"{(abc_c=='A').sum()} products (class A) make 80% of sales. Keep service levels highest on the steady A/X items and use make-to-order logic for erratic C/Z items. "
                        f"The 30/60/90-day forecast and the replenishment list are in the <b>AI Lab</b>."), unsafe_allow_html=True)

# ===================== 6. MARKETING & WEB =====================
MK = dm.table("Marketing.csv", ["Start_Date", "End_Date"])
WT = dm.table("Web_Traffic_Daily.csv", ["Date"])
with tabs[5]:
    mk = inrange(MK, "Start_Date")
    pl = mk.groupby("Platform").agg(Spend=("Spend_EGP", "sum"), Rev=("Attributed_Revenue_EGP", "sum"), Orders=("Orders_Attributed", "sum"), Clicks=("Clicks", "sum"), Imp=("Impressions", "sum"), Sess=("Landing_Page_Sessions", "sum")).reset_index()
    pl["ROAS"] = pl.Rev / pl.Spend; pl["CAC"] = pl.Spend / pl.Orders; pl["CTR"] = pl.Clicks / pl.Imp; pl["Conv"] = pl.Orders / pl.Clicks
    c = st.columns(5)
    c[0].markdown(kpi("Marketing spend", fmt(mk.Spend_EGP.sum())), unsafe_allow_html=True)
    c[1].markdown(kpi("Attributed revenue", fmt(mk.Attributed_Revenue_EGP.sum())), unsafe_allow_html=True)
    c[2].markdown(kpi("Blended ROAS", f"{mk.Attributed_Revenue_EGP.sum()/mk.Spend_EGP.sum():.1f}x"), unsafe_allow_html=True)
    c[3].markdown(kpi("Cost per order (CAC)", fmt(mk.Spend_EGP.sum() / mk.Orders_Attributed.sum())), unsafe_allow_html=True)
    c[4].markdown(kpi("Campaigns under 1x ROAS", f"{((mk.Attributed_Revenue_EGP/mk.Spend_EGP)<1).sum()} of {len(mk)}"), unsafe_allow_html=True)
    a, b = st.columns(2)
    fig = px.bar(pl.sort_values("ROAS"), x="ROAS", y="Platform", orientation="h", text=pl.sort_values("ROAS").ROAS.map("{:.1f}x".format), title="Return on ad spend by platform", color_discrete_sequence=[BLUE])
    fig.update_xaxes(type="log"); a.plotly_chart(style(fig, 320), width="stretch")
    fig = px.scatter(pl, x="Spend", y="Rev", size="Orders", color="Platform", text="Platform", title="Spend vs attributed revenue (bubble = orders)", color_discrete_sequence=COLORWAY)
    fig.update_traces(textposition="top center"); fig.update_xaxes(tickformat=".2s"); fig.update_yaxes(tickformat=".2s")
    b.plotly_chart(style(fig, 320), width="stretch")
    st.dataframe(pl[["Platform", "Spend", "Rev", "ROAS", "CAC", "CTR", "Conv"]].style.format({"Spend": "{:,.0f}", "Rev": "{:,.0f}", "ROAS": "{:.1f}x", "CAC": "{:,.0f}", "CTR": "{:.2%}", "Conv": "{:.1%}"}), hide_index=True, width="stretch")
    inf = pl[pl.Platform == "Influencer"]
    if len(inf):
        i = inf.iloc[0]
        st.markdown(insight(f"<b>Influencer spend of {fmt(i.Spend)} returns {i.ROAS:.2f}x</b>, so each order costs {fmt(i.CAC)}. After product cost it loses money. "
                            f"WhatsApp/CRM and Google cost a fraction per order. <b>Caution:</b> WhatsApp/CRM mostly reaches people who already know the brand, so its huge ROAS will not scale linearly. Test moves in steps (see the Budget Optimizer in the AI Lab).", warn=True), unsafe_allow_html=True)
    a, b = st.columns(2)
    mm = mk.assign(M=mk.Start_Date.dt.to_period("Q").astype(str)).groupby(["M", "Platform"]).Spend_EGP.sum().reset_index()
    fig = px.bar(mm, x="M", y="Spend_EGP", color="Platform", title="Quarterly spend by platform", color_discrete_sequence=COLORWAY); fig.update_yaxes(tickformat=".2s")
    a.plotly_chart(style(fig, 320), width="stretch")
    mk["Disc"] = pd.cut(mk.Discount_Pct, [-.01, 0, .1, .2, .5], labels=["0%", "up to 10%", "10 to 20%", "over 20%"])
    dd = mk.groupby("Disc", observed=True).apply(lambda d: d.Attributed_Revenue_EGP.sum() / d.Spend_EGP.sum(), include_groups=False).reset_index(name="ROAS")
    fig = px.bar(dd, x="Disc", y="ROAS", text=dd.ROAS.map("{:.1f}x".format), title="ROAS by campaign discount", color_discrete_sequence=[CYAN])
    b.plotly_chart(style(fig, 320), width="stretch")
    w = inrange(WT, "Date")
    mw = w.assign(M=w.Date.dt.to_period("M").dt.to_timestamp()).groupby("M").agg(Sessions=("Sessions", "sum"), Orders=("Orders", "sum"), Load=("Avg_Page_Load_Sec", "mean")).reset_index()
    mw["Conv"] = mw.Orders / mw.Sessions
    a, b = st.columns(2)
    fig = go.Figure(); fig.add_scatter(x=mw.M, y=mw.Sessions, name="Sessions", line=dict(color=BLUE)); fig.add_scatter(x=mw.M, y=mw.Conv, name="Conversion", yaxis="y2", line=dict(color=CYAN))
    fig.update_layout(title="Web sessions and conversion rate", yaxis2=dict(overlaying="y", side="right", tickformat=".1%", showgrid=False, range=[0, .05]))
    a.plotly_chart(style(fig, 320), width="stretch")
    fun = pd.DataFrame({"Step": ["Sessions", "Add to cart", "Checkout", "Order"], "Value": [w.Sessions.sum(), (w.Sessions * w.Add_To_Cart_Rate).sum(), (w.Sessions * w.Checkout_Rate).sum(), w.Orders.sum()]})
    fig = px.funnel(fun, x="Value", y="Step", title="Online funnel", color_discrete_sequence=[BLUE])
    b.plotly_chart(style(fig, 320), width="stretch")
    st.markdown(insight(f"Conversion sits near {w.Orders.sum()/w.Sessions.sum():.1%} and {w.Mobile_Pct.mean():.0%} of visits are on mobile. Only about {(w.Add_To_Cart_Rate.mean()):.0%} of visits add to cart, and about half of those carts never reach checkout ({(w.Checkout_Rate.mean()):.1%} of visits), "
                        f"so a simpler mobile checkout and cart reminders matter more than extra traffic."), unsafe_allow_html=True)

# ===================== 7. FACTORY & PRINT =====================
PO = dm.table("Production_Orders.csv", ["Start_Date", "Due_Date", "Completion_Date"])
PB = dm.table("Printing_Batches.csv", ["Print_Date"])
DT = dm.table("Machine_Downtime.csv", ["Date"])
with tabs[6]:
    po = inrange(PO, "Start_Date"); pb = inrange(PB, "Print_Date"); dt_ = inrange(DT, "Date")
    c = st.columns(5)
    c[0].markdown(kpi("Avg line efficiency", f"{po.Efficiency_Pct.mean():.1f}%"), unsafe_allow_html=True)
    c[1].markdown(kpi("Orders finished late", fmt((po.Delay_Days > 0).mean(), "pct")), unsafe_allow_html=True)
    c[2].markdown(kpi("Plan attainment", fmt(po.Produced_Qty.sum() / po.Planned_Qty.sum(), "pct")), unsafe_allow_html=True)
    c[3].markdown(kpi("Print yield", fmt(pb.Good_Qty.sum() / pb.Printed_Qty.sum(), "pct")), unsafe_allow_html=True)
    c[4].markdown(kpi("Unplanned downtime", f"{dt_[dt_.Planned=='No'].Downtime_Hours.sum():,.0f} h"), unsafe_allow_html=True)
    a, b = st.columns(2)
    ln = po.groupby("Line_ID").agg(Eff=("Efficiency_Pct", "mean"), Late=("Delay_Days", lambda x: (x > 0).mean()), Delay=("Delay_Days", "mean"), OT=("Overtime_Hours", "sum")).reset_index()
    fig = go.Figure(); fig.add_bar(x=ln.Line_ID, y=ln.Late, name="Share of orders late", marker_color=CORAL)
    fig.add_scatter(x=ln.Line_ID, y=ln.Eff / 100, name="Efficiency", yaxis="y2", mode="lines+markers", line=dict(color=CYAN))
    fig.update_layout(title="Production lines: lateness and efficiency", yaxis=dict(tickformat=".0%"), yaxis2=dict(overlaying="y", side="right", tickformat=".0%", showgrid=False, range=[.7, .9]))
    a.plotly_chart(style(fig, 330), width="stretch")
    bn = po.Primary_Bottleneck.value_counts().reset_index(); bn.columns = ["Stage", "Delayed orders"]
    fig = px.bar(bn.sort_values("Delayed orders"), x="Delayed orders", y="Stage", orientation="h", title="Where late orders get stuck (primary bottleneck)", color_discrete_sequence=[BLUE])
    b.plotly_chart(style(fig, 330), width="stretch")
    top2 = bn.head(2)
    st.markdown(insight(f"<b>{(po.Delay_Days>0).mean():.0%} of production orders finish late</b>, and <b>{top2.iloc[0]['Stage']} and {top2.iloc[1]['Stage']}</b> cause {top2['Delayed orders'].sum()/bn['Delayed orders'].sum():.0%} of the delays. "
                        f"Efficiency is flat across lines (~82%), so the gap is not one bad line. It is the flow between stages. Add buffer capacity at {top2.iloc[0]['Stage'].lower()} before adding machines."), unsafe_allow_html=True)
    a, b = st.columns(2)
    mc = pb.groupby("Machine_ID").agg(P=("Printed_Qty", "sum"), G=("Good_Qty", "sum"), Rework=("Rework_Cost_EGP", "sum"), Reprint=("Reprint_Qty", "sum")).reset_index(); mc["Yield"] = mc.G / mc.P
    fig = px.bar(mc, x="Machine_ID", y="Yield", text=mc.Yield.map("{:.2%}".format), title="Print yield by machine"); fig.update_traces(marker_color=[CORAL if v == mc.Yield.min() else BLUE for v in mc.Yield]); fig.update_yaxes(range=[.96, .98], tickformat=".1%")
    a.plotly_chart(style(fig, 320), width="stretch")
    dr_ = dt_.groupby(["Machine_ID", "Reason"]).Downtime_Hours.sum().reset_index()
    order_m = dt_.groupby("Machine_ID").Downtime_Hours.sum().sort_values().index
    fig = px.bar(dr_, y="Machine_ID", x="Downtime_Hours", color="Reason", orientation="h", title="Downtime hours by machine and reason", category_orders={"Machine_ID": list(order_m)}, color_discrete_sequence=COLORWAY)
    b.plotly_chart(style(fig, 320), width="stretch")
    rs = dt_.groupby("Reason").Downtime_Hours.sum().sort_values(ascending=False)
    worst = mc.sort_values("Yield").iloc[0]
    st.markdown(insight(f"<b>{rs.index[0]} and {rs.index[1].lower()} are the two biggest downtime causes</b> ({rs.iloc[:2].sum():,.0f} hours). Planned maintenance is only {rs.get('Planned maintenance',0)/rs.sum():.0%} of downtime, so most stops are unplanned. "
                        f"{worst.Machine_ID} has the lowest print yield ({worst.Yield:.2%}) and the highest rework cost. Start preventive maintenance there, and cut changeover time with quick-changeover (SMED) routines."), unsafe_allow_html=True)

# ===================== 8. QUALITY & RETURNS =====================
QC = dm.table("Quality.csv", ["Inspection_Date"])
with tabs[7]:
    qc = inrange(QC, "Inspection_Date")
    ret_rows = F[F.Returned == "Yes"]
    cpq = qc.Estimated_Loss_EGP.sum() + pb.Rework_Cost_EGP.sum() + ret_rows[ret_rows.Quality_Related_Return == "Yes"].Refund_Value_EGP.sum()
    c = st.columns(5)
    c[0].markdown(kpi("QC reject rate", fmt(qc.Rejected_Qty.sum() / qc.Inspected_Qty.sum(), "pct")), unsafe_allow_html=True)
    c[1].markdown(kpi("QC loss", fmt(qc.Estimated_Loss_EGP.sum())), unsafe_allow_html=True)
    c[2].markdown(kpi("Customer return rate", fmt(ret_rate, "pct")), unsafe_allow_html=True)
    c[3].markdown(kpi("Quality-related refunds", fmt(ret_rows[ret_rows.Quality_Related_Return == "Yes"].Refund_Value_EGP.sum())), unsafe_allow_html=True)
    c[4].markdown(kpi("Cost of poor quality", fmt(cpq)), unsafe_allow_html=True)
    dfp = qc.groupby("Defect_Type").Estimated_Loss_EGP.sum().sort_values(ascending=False).reset_index(); dfp["Cum"] = dfp.Estimated_Loss_EGP.cumsum() / dfp.Estimated_Loss_EGP.sum()
    a, b = st.columns(2)
    fig = go.Figure(); fig.add_bar(x=dfp.Defect_Type, y=dfp.Estimated_Loss_EGP, name="Loss", marker_color=BLUE)
    fig.add_scatter(x=dfp.Defect_Type, y=dfp.Cum, name="Cumulative %", yaxis="y2", line=dict(color=GOLD)); fig.update_layout(title="Defect Pareto by loss (EGP)", yaxis=dict(tickformat=".2s"), yaxis2=dict(overlaying="y", side="right", tickformat=".0%", showgrid=False, range=[0, 1.05]))
    a.plotly_chart(style(fig, 340), width="stretch")
    rc = qc[qc.Root_Cause != "No significant issue"].groupby("Root_Cause").Estimated_Loss_EGP.sum().sort_values().reset_index()
    fig = px.bar(rc, x="Estimated_Loss_EGP", y="Root_Cause", orientation="h", title="Loss by root cause (excluding 'no significant issue')", color_discrete_sequence=[CYAN]); fig.update_xaxes(tickformat=".2s")
    b.plotly_chart(style(fig, 340), width="stretch")
    st.markdown(insight(f"<b>Quality loss is spread evenly</b>: the top 3 defect types make only about {dfp.Cum.iloc[2]:.0%} of the loss, so there is no single fix. The top root causes are {rc.iloc[-1].Root_Cause.lower()} and {rc.iloc[-2].Root_Cause.lower()}, "
                        f"which are process-control problems. Standard work instructions and calibration schedules will help across every stage."), unsafe_allow_html=True)
    a, b = st.columns(2)
    rr = ret_rows.groupby("Return_Reason").size().sort_values().reset_index(name="Returns")
    fig = px.bar(rr, x="Returns", y="Return_Reason", orientation="h", title="Why customers return items", color_discrete_sequence=[BLUE]); a.plotly_chart(style(fig, 320), width="stretch")
    sr = qc.groupby("Stage").agg(I=("Inspected_Qty", "sum"), R_=("Rejected_Qty", "sum")).reset_index(); sr["Rate"] = sr.R_ / sr.I
    fig = px.bar(sr, x="Stage", y="Rate", text=sr.Rate.map("{:.2%}".format), title="Reject rate by production stage", color_discrete_sequence=[CYAN]); fig.update_yaxes(tickformat=".1%", range=[0, .03])
    b.plotly_chart(style(fig, 320), width="stretch")
    top_r = rr.sort_values("Returns", ascending=False).iloc[0]
    st.markdown(insight(f"<b>{top_r.Return_Reason} is the first reason for returns ({top_r.Returns/rr.Returns.sum():.0%}).</b> It is a product-information problem more than a factory one: size charts, fit notes and the 'size guidance' tickets in customer service point the same way. "
                        f"Customer service is healthy (about 95% resolved, CSAT near 4.0 out of 5), so the fix belongs on the product page."), unsafe_allow_html=True)

# ===================== 9. SUPPLY CHAIN =====================
PU = dm.table("Purchase_Orders.csv", ["Order_Date", "Promised_Date", "Actual_Receipt_Date"])
SU = dm.table("Suppliers.csv")
with tabs[8]:
    pu = inrange(PU, "Order_Date").copy()
    pu["Late"] = (pu.Actual_Receipt_Date - pu.Promised_Date).dt.days; pu["OTD"] = pu.Late <= 0; pu["Reject"] = pu.Rejected_Qty / pu.Ordered_Qty
    pu["Lead"] = (pu.Actual_Receipt_Date - pu.Order_Date).dt.days; pu["Spend"] = pu.Ordered_Qty * pu.Unit_Cost_EGP
    sc = pu.groupby("Supplier_ID").agg(OTD=("OTD", "mean"), DaysLate=("Late", "mean"), Reject=("Reject", "mean"), Lead=("Lead", "mean"), Spend=("Spend", "sum")).join(SU.set_index("Supplier_ID")[["Primary_Category", "Contracted", "Payment_Terms_Days"]]).reset_index()
    sc["Risk"] = np.where(sc.OTD < .55, "High", np.where(sc.OTD < .68, "Medium", "Low"))
    c = st.columns(4)
    c[0].markdown(kpi("On-time delivery", fmt(pu.OTD.mean(), "pct")), unsafe_allow_html=True)
    c[1].markdown(kpi("Avg days late", f"{pu.Late.clip(lower=0).mean():.1f}"), unsafe_allow_html=True)
    c[2].markdown(kpi("Material reject rate", fmt(pu.Reject.mean(), "pct")), unsafe_allow_html=True)
    c[3].markdown(kpi("High-risk suppliers", f"{(sc.Risk=='High').sum()} of {len(sc)}"), unsafe_allow_html=True)
    a, b = st.columns(2)
    fig = px.scatter(sc, x="OTD", y="DaysLate", size="Spend", color="Risk", text="Supplier_ID", title="Supplier reliability (bubble = order value)", color_discrete_map={"High": CORAL, "Medium": GOLD, "Low": MINT})
    fig.update_traces(textposition="top center"); fig.update_xaxes(tickformat=".0%"); a.plotly_chart(style(fig, 360), width="stretch")
    mt = pu.groupby("Material_Name").agg(OTD=("OTD", "mean"), Lead=("Lead", "mean")).reset_index().sort_values("OTD")
    fig = px.bar(mt, x="OTD", y="Material_Name", orientation="h", title="On-time delivery by material", color_discrete_sequence=[BLUE]); fig.update_xaxes(tickformat=".0%", range=[.4, .8])
    b.plotly_chart(style(fig, 360), width="stretch")
    bad = sc[sc.Risk == "High"]
    st.markdown(insight(f"<b>Two suppliers drag delivery performance: {', '.join(bad.Supplier_ID)}</b> deliver on time only {bad.OTD.min():.0%} to {bad.OTD.max():.0%} of the time and arrive {bad.DaysLate.mean():.1f} days late on average, "
                        f"against under 0.6 days for the rest. They supply {', '.join(sorted(set(bad.Primary_Category)))}, the items that feed printing. Material rejects are almost identical across suppliers (~1.8%), so the problem is delivery, not quality.", warn=True), unsafe_allow_html=True)
    st.dataframe(sc[["Supplier_ID", "Primary_Category", "Contracted", "Payment_Terms_Days", "OTD", "DaysLate", "Reject", "Lead", "Risk"]].sort_values("OTD").style.format({"OTD": "{:.0%}", "DaysLate": "{:.1f}", "Reject": "{:.2%}", "Lead": "{:.1f}"}), hide_index=True, width="stretch")
    st.markdown(insight("<b>Data note:</b> the modeled purchase-order values add up to more than total sales, so use them to compare suppliers and materials, not as the real cost base.", warn=True), unsafe_allow_html=True)

# ===================== 10. AI LAB =====================
FC = dm.forecasts()
RF = dm.rfm()
CU = dm.customers()
YEARS = 3.0  # Oct 2023 to Sep 2026

def budget_opt(pl_, beta, cap, floor, total=None):
    """Greedy allocation with diminishing returns: revenue_p = Rev_p * (spend/Spend_p)^beta."""
    cur = pl_.set_index("Platform")
    total = total or cur.Spend.sum()
    x = cur.Spend * floor
    step = total / 400
    left = total - x.sum()
    while left > 1e-6:
        mr = {}
        for p in cur.index:
            if x[p] + step <= cur.Spend[p] * cap:
                a = cur.Rev[p] / cur.Spend[p] ** beta
                mr[p] = a * ((x[p] + step) ** beta - max(x[p], 1e-9) ** beta)
        if not mr: break
        p = max(mr, key=mr.get); x[p] += step; left -= step
    rev = cur.Rev * (x / cur.Spend) ** beta
    return pd.DataFrame({"Current spend": cur.Spend, "Recommended spend": x, "Current revenue": cur.Rev, "Expected revenue": rev})

with tabs[9]:
    st.markdown(insight("<b>The business question behind these tools:</b> growth is strong but profit quality is weak. The first tool, the <b>Wholesale Deal Desk</b>, is the application nobody asked for and the one with the largest value. "
                        "Every tool below uses the real data, shows its assumptions, and can be changed with the sliders."), unsafe_allow_html=True)
    t1, t2, t3, t4 = st.tabs(["Wholesale Deal Desk", "Demand forecast & replenishment", "Customer win-back list", "Marketing budget optimizer"])

    # ---- Deal desk ----
    with t1:
        W = S[S.Channel == "Wholesale"]
        c1, c2 = st.columns(2)
        cap = c1.slider("Discount ceiling for wholesale", 15, 50, 30, 1, format="%d%%") / 100
        loss = c2.slider("Expected volume lost on deals that were above the ceiling", 0, 50, 15, 1, format="%d%%") / 100
        hi = W[W.Discount_Pct > cap]
        gp0 = hi.Gross_Profit_EGP.sum()
        new_gp = (hi.Gross_Sales_EGP * (1 - cap) - hi.Estimated_COGS_EGP) * (1 - loss)
        gp1 = new_gp.sum()
        den = (hi.Gross_Sales_EGP * (1 - cap) - hi.Estimated_COGS_EGP).sum()
        be = 1 - gp0 / den if den > 0 else np.nan
        c = st.columns(4)
        c[0].markdown(kpi("Wholesale lines above ceiling", f"{len(hi)/len(W):.0%}"), unsafe_allow_html=True)
        c[1].markdown(kpi("Gross profit today (per year)", fmt(gp0 / YEARS)), unsafe_allow_html=True)
        c[2].markdown(kpi("Gross profit with ceiling (per year)", fmt(gp1 / YEARS), (gp1 / gp0 - 1) if gp0 else None, suffix=" change"), unsafe_allow_html=True)
        c[3].markdown(kpi("Break-even volume loss", fmt(be, "pct")), unsafe_allow_html=True)
        sw = []
        for cp in [0.25, 0.30, 0.35, 0.40]:
            hh = W[W.Discount_Pct > cp]; base = hh.Gross_Profit_EGP.sum()
            for l in np.arange(0, 0.51, 0.05):
                sw.append((f"Ceiling {cp:.0%}", l, ((hh.Gross_Sales_EGP * (1 - cp) - hh.Estimated_COGS_EGP).sum() * (1 - l) - base) / YEARS))
        sw = pd.DataFrame(sw, columns=["Ceiling", "Volume lost", "Extra gross profit per year"])
        fig = px.line(sw, x="Volume lost", y="Extra gross profit per year", color="Ceiling", title="Extra yearly gross profit vs volume lost, by discount ceiling", color_discrete_sequence=COLORWAY)
        fig.add_hline(y=0, line_dash="dot", line_color=GOLD); fig.update_xaxes(tickformat=".0%"); fig.update_yaxes(tickformat=".2s")
        st.plotly_chart(style(fig, 360), width="stretch")
        st.markdown(insight(f"With a {cap:.0%} ceiling, wholesale can lose up to <b>{be:.0%} of the volume on those deals</b> and still make the same profit. "
                            f"At {loss:.0%} volume lost, gross profit changes by <b>{fmt((gp1-gp0)/YEARS)} per year</b>. The ceiling pays off because those deals earn almost nothing today."), unsafe_allow_html=True)
        st.markdown('<div class="sec">Deal check: what should the approval level be?</div>', unsafe_allow_html=True)
        pu_ = S.groupby("Product_Name").agg(P=("Gross_Sales_EGP", "sum"), C=("Estimated_COGS_EGP", "sum"), Q=("Quantity", "sum"))
        pu_["List"] = pu_.P / pu_.Q; pu_["Cost"] = pu_.C / pu_.Q
        d1_, d2_, d3_ = st.columns(3)
        prod = d1_.selectbox("Product", pu_.index)
        qty = d2_.number_input("Quantity", 1, 100000, 500, 50)
        dsc = d3_.slider("Proposed discount", 0, 60, 30, 1, format="%d%%") / 100
        L, Cst = pu_.loc[prod, "List"], pu_.loc[prod, "Cost"]
        mg = 1 - Cst / (L * (1 - dsc))
        lvl, cls = ("Auto-approve", "up") if dsc <= .20 else (("Sales manager", "flat") if dsc <= .30 else ("Director sign-off", "down"))
        e1, e2, e3 = st.columns(3)
        e1.markdown(kpi("Order margin", fmt(mg, "pct")), unsafe_allow_html=True)
        e2.markdown(kpi("Order gross profit", fmt(qty * (L * (1 - dsc) - Cst))), unsafe_allow_html=True)
        e3.markdown(f'<div class="kpi"><div class="l">Approval level</div><div class="v {cls}">{lvl}</div></div>', unsafe_allow_html=True)

    # ---- Forecast ----
    with t2:
        T = FC["Total"]
        hist, fc = T["hist"], T["fc"]
        fig = go.Figure()
        fig.add_scatter(x=hist.index, y=hist.values, name="Actual", line=dict(color=BLUE, width=2.5))
        fig.add_scatter(x=fc.index, y=fc.High, line=dict(width=0), showlegend=False, hoverinfo="skip")
        fig.add_scatter(x=fc.index, y=fc.Low, fill="tonexty", fillcolor="rgba(61,214,245,.18)", line=dict(width=0), name="80% range")
        fig.add_scatter(x=fc.index, y=fc.Forecast, name="Forecast", line=dict(color=CYAN, width=3, dash="dash"), mode="lines+markers")
        fig.update_layout(title="Net sales forecast, next 90 days", yaxis=dict(tickformat=".2s"))
        st.plotly_chart(style(fig, 360), width="stretch")
        rows = []
        for i, lab in enumerate(["30 days", "60 days", "90 days"]):
            r = {"Horizon": f"{lab} ({fc.index[i]:%b %Y})"}
            for ch in ["Wholesale", "Retail", "Online", "Total"]:
                r[ch] = FC[ch]["fc"].Forecast.iloc[i]
            rows.append(r)
        st.dataframe(pd.DataFrame(rows).style.format({k: "{:,.0f}" for k in ["Wholesale", "Retail", "Online", "Total"]}), hide_index=True, width="stretch")
        st.markdown(insight(f"Expected sales for Q4 2026: <b>{fmt(fc.Forecast.sum())}</b>, with December alone near {fmt(fc.Forecast.iloc[2])}. "
                            f"Method: a trend plus month-of-year pattern fitted on the monthly history. Tested on past months it was off by about <b>{T['mape']:.1%}</b> on average. "
                            f"It assumes the pattern of the last three years continues, so campaigns or price changes need a manual adjustment."), unsafe_allow_html=True)
        H = st.select_slider("Replenishment horizon", options=[30, 60, 90], value=30, format_func=lambda x: f"{x} days")
        base = hist.iloc[-3:].mean(); factor = fc.Forecast.iloc[:H // 30].mean() / base
        sn = INV[INV.Snapshot_Month == INV.Snapshot_Month.max()].copy()
        sn["Daily"] = sn.Avg_Daily_Sales_90D * factor
        sn["Target"] = sn.Daily * (H + sn.Supplier_Lead_Time_Days) + sn.Safety_Stock_Units
        sn["Order"] = (sn.Target - sn.Closing_Stock).clip(lower=0).round()
        sn["Excess"] = (sn.Closing_Stock - sn.Daily * (H + sn.Supplier_Lead_Time_Days + 90) - sn.Safety_Stock_Units).clip(lower=0).round()
        a, b = st.columns(2)
        a.markdown(f"**Needs stock in the next {H} days** (demand factor {factor:.2f}x vs last 3 months)")
        need = sn[sn.Order > 0].sort_values("Order", ascending=False).head(15)
        a.dataframe(need[["Location_Name", "Product_Name", "Closing_Stock", "Days_of_Cover", "Order"]].rename(columns={"Order": "Suggested order/transfer in"}).style.format({"Days_of_Cover": "{:.0f}", "Closing_Stock": "{:,.0f}", "Suggested order/transfer in": "{:,.0f}"}), hide_index=True, width="stretch")
        b.markdown("**Holding more than needed: candidates to move or stop reordering**")
        exc = sn[sn.Excess > 0].sort_values("Excess", ascending=False).head(15)
        b.dataframe(exc[["Location_Name", "Product_Name", "Closing_Stock", "Days_of_Cover", "Excess"]].rename(columns={"Excess": "Excess units"}).style.format({"Days_of_Cover": "{:.0f}", "Closing_Stock": "{:,.0f}", "Excess units": "{:,.0f}"}), hide_index=True, width="stretch")
        st.caption("Rule: target stock = daily demand (last 90 days, scaled by the forecast factor) × (horizon + supplier lead time) + safety stock. Excess = stock above that target plus 90 days of demand.")
        st.download_button("Download replenishment plan (CSV)", sn[sn.Order > 0].sort_values("Order", ascending=False)[["Location_Name", "SKU", "Product_Name", "Closing_Stock", "Days_of_Cover", "Supplier_Lead_Time_Days", "Order"]].to_csv(index=False).encode("utf-8-sig"), "replenishment_plan.csv", "text/csv")

    # ---- Win-back ----
    with t3:
        rec_min = st.slider("Counts as 'gone quiet' after (days without a purchase)", 90, 365, 180, 15)
        min_orders = st.slider("Minimum past orders", 1, 10, 3)
        pct = st.slider("Share we expect to win back", 2, 30, 10, 1, format="%d%%") / 100
        g = RF[(RF.Type == "Retail/Online") & (RF.Recency >= rec_min) & (RF.Orders >= min_orders)].merge(CU[["Customer_ID", "Governorate", "Age_Band", "Gender", "Acquisition_Channel", "Consent_Status"]], on="Customer_ID")
        ok = g[g.Consent_Status == "Opted-in"].sort_values("Revenue", ascending=False)
        yr_rev = ok.Revenue.mean() / YEARS if len(ok) else 0
        c = st.columns(4)
        c[0].markdown(kpi("Customers who went quiet", fmt(len(g), "num")), unsafe_allow_html=True)
        c[1].markdown(kpi("Can be contacted (opted in)", fmt(len(ok), "num")), unsafe_allow_html=True)
        c[2].markdown(kpi("Their past revenue", fmt(ok.Revenue.sum())), unsafe_allow_html=True)
        c[3].markdown(kpi("Win-back potential (per year)", fmt(len(ok) * pct * yr_rev)), unsafe_allow_html=True)
        st.markdown(insight(f"Only customers who <b>opted in</b> are on the list, so the campaign respects consent. Start with the top 500 by past spend through WhatsApp/CRM, the cheapest channel in the data (about EGP 7 per order). "
                            f"The estimate = list size × {pct:.0%} win-back × average past yearly revenue per customer."), unsafe_allow_html=True)
        st.dataframe(ok[["Customer_ID", "Governorate", "Age_Band", "Gender", "Acquisition_Channel", "Orders", "Revenue", "Recency", "Segment"]].head(200).style.format({"Revenue": "{:,.0f}"}), hide_index=True, width="stretch")
        st.download_button("Download full list (CSV)", ok[["Customer_ID", "Governorate", "Age_Band", "Gender", "Acquisition_Channel", "Orders", "Revenue", "Recency", "Segment"]].to_csv(index=False).encode("utf-8-sig"), "winback_list.csv", "text/csv")

    # ---- Budget ----
    with t4:
        plf = MK.groupby("Platform").agg(Spend=("Spend_EGP", "sum"), Rev=("Attributed_Revenue_EGP", "sum")).reset_index()
        c1, c2, c3 = st.columns(3)
        beta = c1.slider("Diminishing returns (lower = saturates faster)", 0.3, 1.0, 0.7, 0.05)
        capx = c2.slider("Max spend per platform vs today", 1.0, 3.0, 1.5, 0.1)
        floor = c3.slider("Keep at least this share of today's spend", 0, 100, 40, 5, format="%d%%") / 100
        res = budget_opt(plf, beta, capx, floor).reset_index()
        tot0, tot1 = res["Current revenue"].sum(), res["Expected revenue"].sum()
        fig = go.Figure()
        fig.add_bar(x=res.Platform, y=res["Current spend"], name="Current spend", marker_color=BLUE)
        fig.add_bar(x=res.Platform, y=res["Recommended spend"], name="Recommended spend", marker_color=CYAN)
        fig.update_layout(barmode="group", title="Same total budget, different split", yaxis=dict(tickformat=".2s"))
        st.plotly_chart(style(fig, 340), width="stretch")
        st.markdown(insight(f"Moving the same budget to where each extra EGP earns most lifts attributed revenue from {fmt(tot0)} to <b>{fmt(tot1)} ({tot1/tot0-1:+.1%})</b>. "
                            f"Influencer is cut to its floor and the money goes first to the platforms with the best marginal return. <b>Treat this as a test plan:</b> shift in two or three steps and measure each step, because the data is attributed revenue and returns shrink as spend grows."), unsafe_allow_html=True)
        st.dataframe(res.style.format({c: "{:,.0f}" for c in res.columns if c != "Platform"}), hide_index=True, width="stretch")

# ===================== 11. ACTION PLAN =====================
with tabs[10]:
    st.markdown('<div class="sec">Quantified actions, ranked by value</div>', unsafe_allow_html=True)
    W = S[S.Channel == "Wholesale"]; hi = W[W.Discount_Pct > .30]
    a1 = ((hi.Gross_Sales_EGP * .70 - hi.Estimated_COGS_EGP) * .85 - hi.Gross_Profit_EGP).sum() / YEARS
    plf = MK.groupby("Platform").agg(Spend=("Spend_EGP", "sum"), Rev=("Attributed_Revenue_EGP", "sum")).reset_index()
    r_ = budget_opt(plf, .7, 1.5, .4); a2 = (r_["Expected revenue"].sum() - r_["Current revenue"].sum()) / YEARS
    w_inv = INV[INV.Location_Name == "El-Sharnouby Wholesale Desk"]
    wu = W.Net_Sales_EGP.sum() / W.Quantity.sum(); wm = W.Gross_Profit_EGP.sum() / W.Net_Sales_EGP.sum()
    a3 = (w_inv.Stockout_Days_In_Month * w_inv.Avg_Daily_Sales_90D).sum() * wu * 0.5 / YEARS
    okw = RF[(RF.Type == "Retail/Online") & (RF.Recency >= 180) & (RF.Orders >= 3)].merge(CU[["Customer_ID", "Consent_Status"]], on="Customer_ID")
    okw = okw[okw.Consent_Status == "Opted-in"]; a4 = len(okw) * .10 * okw.Revenue.mean() / YEARS
    sf = S[S.Return_Reason == "Size / fit"].Refund_Value_EGP.sum() * .30 / YEARS
    qcl = QC.Estimated_Loss_EGP.sum(); a6 = qcl * (1 - 2.0 / (QC.Rejected_Qty.sum() / QC.Inspected_Qty.sum() * 100)) / YEARS
    dh = DT.groupby("Reason").Downtime_Hours.sum()
    pu2 = PU.copy(); pu2["Late"] = (pu2.Actual_Receipt_Date - pu2.Promised_Date).dt.days
    plan = pd.DataFrame([
        ("1", "Cap wholesale discounts at 30% and add an approval ladder", "Deals above 30% off earn an 8.6% margin and are 50% of sales", f"{fmt(a1)} gross profit / yr", "Medium: depends on volume loss", "Sales director", "1 month"),
        ("2", "Rebalance stock to the wholesale desk and stop reordering overstocked retail/online SKUs", f"{w_inv.Stockout_Days_In_Month.sum():,.0f} wholesale stockout days vs 140-170 days of cover elsewhere", f"{fmt(a3 * wm)} gross profit / yr (halving stockouts)", "Medium", "Supply planning", "2 months"),
        ("3", "Shift influencer budget to Google and WhatsApp/CRM in steps", "Influencer ROAS 1.06x vs 10x (Google) and 67x (CRM)", f"{fmt(a2)} attributed revenue / yr", "Medium: test in steps", "Marketing", "1 quarter"),
        ("4", "Win-back campaign for opted-in customers who went quiet", f"{len(okw):,} contactable customers inactive 180+ days", f"{fmt(a4)} revenue / yr (10% win-back)", "Medium", "CRM", "1 month"),
        ("5", "Fix delivery with the two late suppliers (SUP04, SUP09)", "On time only 35-40% vs ~70% for the rest; 'Material wait' stops cost 846 h", f"Up to {dh.get('Material wait', 0) / YEARS / 2:,.0f} machine hours / yr (halving material waits)", "High", "Procurement", "1 quarter"),
        ("6", "Quick-changeover (SMED) and preventive maintenance on PR-M02, CUT-02, PR-M03", "Setup + mechanical faults = 45% of downtime", f"{(dh.get('Setup / changeover', 0) * .25 + dh.get('Mechanical fault', 0) * .20) / YEARS:,.0f} machine hours / yr (25% / 20% cut)", "Medium", "Plant manager", "1 quarter"),
        ("7", "Process-control programme (curing temperature, calibration, work instructions)", "QC reject rate 2.4%; loss spread evenly across defects", f"{fmt(a6)} / yr (reject rate 2.4% to 2.0%)", "Medium", "Quality", "2 quarters"),
        ("8", "Fix size guidance on product pages (size chart, fit notes)", "Size / fit is 36% of all returns", f"{fmt(sf)} refunds / yr (30% fewer)", "High", "E-commerce", "1 month"),
    ], columns=["#", "Action", "Why (evidence)", "Indicative yearly impact", "Confidence", "Owner", "Time to value"])
    st.dataframe(plan, hide_index=True, width="stretch", height=360)
    st.caption("Impacts are indicative estimates from the modeled data and the assumptions shown in the AI Lab. They are not additive and should be validated with a pilot.")
    st.markdown(insight("<b>The story in one line:</b> demand is growing, but the group sells its volume at a thin margin, keeps stock in the wrong place, spends part of its marketing where it does not pay back, and loses factory hours to unplanned stops. "
                        "Each action above attacks one link of that chain."), unsafe_allow_html=True)
