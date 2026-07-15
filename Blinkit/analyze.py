"""BlinkIT Grocery — full EDA + insight extraction. Emits data.json for the dashboard."""
import pandas as pd
import numpy as np
import json

df = pd.read_excel("Blinkit Grocery.xlsx")

# ---------- CLEANING ----------
# Item_Fat_Content has inconsistent labels: LF / low fat / Low Fat, reg / Regular
df["Item_Fat_Content"] = df["Item_Fat_Content"].replace({
    "LF": "Low Fat", "low fat": "Low Fat", "reg": "Regular"
})
# Missing Item_Weight -> impute by item mean, then global mean
df["Item_Weight"] = df["Item_Weight"].fillna(
    df.groupby("Item_Identifier")["Item_Weight"].transform("mean")
)
df["Item_Weight"] = df["Item_Weight"].fillna(df["Item_Weight"].mean())
# Missing Outlet_Size -> mode per outlet type
mode_size = df.groupby("Outlet_Type")["Outlet_Size"].agg(
    lambda x: x.mode().iat[0] if not x.mode().empty else "Medium"
)
df["Outlet_Size"] = df.apply(
    lambda r: mode_size[r["Outlet_Type"]] if pd.isna(r["Outlet_Size"]) else r["Outlet_Size"],
    axis=1,
)
# Item_Visibility 0 is impossible -> treat as missing, impute item mean
df["Item_Visibility"] = df["Item_Visibility"].replace(0, np.nan)
df["Item_Visibility"] = df["Item_Visibility"].fillna(
    df.groupby("Item_Identifier")["Item_Visibility"].transform("mean")
)
df["Item_Visibility"] = df["Item_Visibility"].fillna(df["Item_Visibility"].mean())

CUR = 2024
df["Outlet_Age"] = CUR - df["Outlet_Establishment_Year"]

def r(x, n=2):
    return round(float(x), n)

out = {}

# ---------- KPIs ----------
total_sales = df["Item_Outlet_Sales"].sum()
out["kpi"] = {
    "total_sales": r(total_sales),
    "total_sales_m": r(total_sales / 1e6, 2),
    "avg_sales": r(df["Item_Outlet_Sales"].mean()),
    "n_items": int(df["Item_Identifier"].nunique()),
    "n_records": int(len(df)),
    "n_outlets": int(df["Outlet_Identifier"].nunique()),
    "avg_rating_proxy": r(df["Item_Outlet_Sales"].median()),
    "avg_mrp": r(df["Item_MRP"].mean()),
    "avg_visibility": r(df["Item_Visibility"].mean() * 100, 2),
    "item_types": int(df["Item_Type"].nunique()),
}

# ---------- Sales by Item Type ----------
it = df.groupby("Item_Type")["Item_Outlet_Sales"].agg(["sum", "mean", "count"]).sort_values("sum", ascending=False)
out["item_type"] = [
    {"type": k, "sales": r(v["sum"]), "avg": r(v["mean"]), "count": int(v["count"])}
    for k, v in it.iterrows()
]

# ---------- Fat content ----------
fc = df.groupby("Item_Fat_Content")["Item_Outlet_Sales"].agg(["sum", "count"])
out["fat_content"] = [
    {"label": k, "sales": r(v["sum"]), "count": int(v["count"])} for k, v in fc.iterrows()
]

# ---------- Outlet Type ----------
ot = df.groupby("Outlet_Type")["Item_Outlet_Sales"].agg(["sum", "mean", "count"]).sort_values("sum", ascending=False)
out["outlet_type"] = [
    {"type": k, "sales": r(v["sum"]), "avg": r(v["mean"]), "count": int(v["count"])}
    for k, v in ot.iterrows()
]

# ---------- Outlet Size ----------
os_ = df.groupby("Outlet_Size")["Item_Outlet_Sales"].agg(["sum", "mean", "count"])
order = ["Small", "Medium", "High"]
out["outlet_size"] = [
    {"size": s, "sales": r(os_.loc[s, "sum"]), "avg": r(os_.loc[s, "mean"]), "count": int(os_.loc[s, "count"])}
    for s in order if s in os_.index
]

# ---------- Location Tier ----------
lt = df.groupby("Outlet_Location_Type")["Item_Outlet_Sales"].agg(["sum", "mean", "count"]).sort_index()
out["location"] = [
    {"tier": k, "sales": r(v["sum"]), "avg": r(v["mean"]), "count": int(v["count"])}
    for k, v in lt.iterrows()
]

# ---------- Sales by Establishment Year ----------
yr = df.groupby("Outlet_Establishment_Year")["Item_Outlet_Sales"].agg(["sum", "count"]).sort_index()
out["by_year"] = [
    {"year": int(k), "sales": r(v["sum"]), "count": int(v["count"])} for k, v in yr.iterrows()
]

# ---------- Per-outlet performance ----------
op = df.groupby(["Outlet_Identifier", "Outlet_Type", "Outlet_Size", "Outlet_Location_Type", "Outlet_Establishment_Year"])["Item_Outlet_Sales"].agg(["sum", "mean", "count"]).reset_index().sort_values("sum", ascending=False)
out["outlets"] = [
    {
        "id": row["Outlet_Identifier"], "type": row["Outlet_Type"], "size": row["Outlet_Size"],
        "tier": row["Outlet_Location_Type"], "year": int(row["Outlet_Establishment_Year"]),
        "sales": r(row["sum"]), "avg": r(row["mean"]), "count": int(row["count"]),
    }
    for _, row in op.iterrows()
]

# ---------- MRP bands ----------
df["MRP_Band"] = pd.cut(df["Item_MRP"], bins=[0, 69, 137, 203, 300],
                        labels=["Low (<₹69)", "Medium (₹69–137)", "High (₹137–203)", "Premium (>₹203)"])
mb = df.groupby("MRP_Band", observed=True)["Item_Outlet_Sales"].agg(["sum", "mean", "count"])
out["mrp_band"] = [
    {"band": str(k), "sales": r(v["sum"]), "avg": r(v["mean"]), "count": int(v["count"])}
    for k, v in mb.iterrows()
]

# ---------- Correlations ----------
corr = df[["Item_Weight", "Item_Visibility", "Item_MRP", "Item_Outlet_Sales", "Outlet_Age"]].corr()
out["corr"] = {
    "mrp_sales": r(corr.loc["Item_MRP", "Item_Outlet_Sales"], 3),
    "vis_sales": r(corr.loc["Item_Visibility", "Item_Outlet_Sales"], 3),
    "weight_sales": r(corr.loc["Item_Weight", "Item_Outlet_Sales"], 3),
    "age_sales": r(corr.loc["Outlet_Age", "Item_Outlet_Sales"], 3),
}

# ---------- MRP vs Sales scatter (sampled) ----------
samp = df.sample(min(600, len(df)), random_state=42)
out["scatter"] = [
    {"mrp": r(row["Item_MRP"]), "sales": r(row["Item_Outlet_Sales"]), "type": row["Outlet_Type"]}
    for _, row in samp.iterrows()
]

# ---------- Type x OutletType matrix (heatmap) ----------
piv = df.pivot_table(index="Item_Type", columns="Outlet_Type", values="Item_Outlet_Sales", aggfunc="sum", fill_value=0)
out["heatmap"] = {
    "rows": list(piv.index),
    "cols": list(piv.columns),
    "values": [[r(piv.loc[i, c]) for c in piv.columns] for i in piv.index],
}

# ---------- Data quality summary ----------
raw = pd.read_excel("Blinkit Grocery.xlsx")
out["quality"] = {
    "missing_weight": int(raw["Item_Weight"].isna().sum()),
    "missing_size": int(raw["Outlet_Size"].isna().sum()),
    "zero_visibility": int((raw["Item_Visibility"] == 0).sum()),
    "fat_labels_raw": int(raw["Item_Fat_Content"].nunique()),
    "fat_labels_clean": int(df["Item_Fat_Content"].nunique()),
}

with open("data.json", "w") as f:
    json.dump(out, f, indent=2)

# ---------- Console narrative ----------
print("TOTAL SALES     : ${:,.0f}".format(total_sales))
print("RECORDS/OUTLETS : {:,} / {}".format(len(df), df['Outlet_Identifier'].nunique()))
print("\nTOP 5 ITEM TYPES BY SALES:")
for x in out["item_type"][:5]:
    print("  {:24s} ${:>12,.0f}  (avg ${:,.0f})".format(x['type'], x['sales'], x['avg']))
print("\nOUTLET TYPE:")
for x in out["outlet_type"]:
    print("  {:20s} ${:>12,.0f}  {:>6} items  avg ${:,.0f}".format(x['type'], x['sales'], x['count'], x['avg']))
print("\nLOCATION TIER:")
for x in out["location"]:
    print("  {:10s} ${:>12,.0f}  avg ${:,.0f}".format(x['tier'], x['sales'], x['avg']))
print("\nCORRELATIONS vs SALES:")
for k, v in out["corr"].items():
    print("  {:14s} {:+.3f}".format(k, v))
print("\nTOP OUTLET: {} (${:,.0f})  |  WORST: {} (${:,.0f})".format(
    out['outlets'][0]['id'], out['outlets'][0]['sales'],
    out['outlets'][-1]['id'], out['outlets'][-1]['sales']))
print("\nData quality:", out["quality"])
print("\n>> data.json written")
