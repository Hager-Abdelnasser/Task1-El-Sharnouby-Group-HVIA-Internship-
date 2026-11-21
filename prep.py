"""Build the slim sales table (and copy small CSVs) so the dashboard starts fast.
Usage: python prep.py path/to/Sharnouby_Enterprise_folder
"""
import sys, shutil, pandas as pd
from pathlib import Path
src = Path(sys.argv[1] if len(sys.argv) > 1 else "raw")
out = Path(__file__).parent / "data"; out.mkdir(exist_ok=True)
cols = ["Invoice_ID","Order_Date","Channel","Location_Name","Customer_ID","Customer_Governorate","Product_ID",
        "Product_Name","Product_Family","Quantity","Discount_Pct","Gross_Sales_EGP","Net_Sales_EGP",
        "Estimated_COGS_EGP","Gross_Profit_EGP","Payment_Method","Returned","Return_Reason",
        "Refund_Value_EGP","Quality_Related_Return"]
s = pd.read_csv(src/"Sales_Transactions.csv", encoding="utf-8-sig", usecols=cols, parse_dates=["Order_Date"])
s.to_parquet(out/"sales.parquet", index=False)
for f in src.glob("*.csv"):
    if f.name != "Sales_Transactions.csv":
        shutil.copy(f, out/f.name)
print("done", len(s), "sales rows")
