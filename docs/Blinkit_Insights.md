# Blinkit Grocery — Data Insights Report

**Dataset:** Blinkit Grocery.xlsx | 8,523 rows | 12 columns
**Total Sales:** $18,591,125 | **Avg Sales/Item:** $2,181

---

## Data Quality Summary

| Column | Issue | Status |
|---|---|---|
| Item_Weight | 17.2% nulls (1,463 rows) | Impute with median per Item_Type |
| Outlet_Size | 28.3% nulls (2,410 rows) | Map by Outlet_Identifier |
| Item_Fat_Content | Dirty values (LF, low fat, reg) | Standardize to Low Fat / Regular |
| Item_Visibility | 526 rows = 0 | Flag — sales are normal, keep rows |

**Verdict: Usable with caveats.** No time dimension exists — trend analysis is not possible.

---

## Insight 1 — Supermarket Type3 is the most efficient channel, yet under-expanded

**Finding:** Supermarket Type3 generates 18.6% of total sales ($3.45M) with the highest avg sales per item at $3,694 — 60% above the overall mean of $2,181, and 10x above Grocery Stores ($340).

**Impact:** If Type3's per-item avg were applied across all 8,523 items, total sales would reach ~$31.5M vs the current $18.6M — a theoretical $13M gap from format underutilization.

**Likely Cause:** Type3 has only 1 outlet (OUT027, Tier 3, est. 1985). It's not a scaled format — the number reflects a single high-performing store, likely large-format with optimized assortment.

**Action:** Study OUT027's assortment, location, and format for replication. If the format is scalable, it's the #1 expansion candidate in the network.

---

## Insight 2 — Tier 1 (premium cities) are the weakest performers per item

**Finding:** Tier 1 outlets average $1,877/item — 18% below Tier 3 ($2,280) and 19% below Tier 2 ($2,324). Tier 1 also holds the smallest volume share at 24.1%.

**Impact:** Tier 1 underperforms on both volume and efficiency, despite likely higher operating costs (real estate, logistics). It contributes only $4.48M vs Tier 3's $7.64M from fewer items.

**Likely Cause:** Tier 1 contains OUT019, a Grocery Store (est. 1985) averaging $340/item, which drags the tier average down significantly. The Grocery Store format is structurally incompatible with Tier 1 economics.

**Action:** Audit Tier 1 Grocery Stores specifically. Convert or close them. Redirect Tier 1 investment to Supermarket Type1 or Type3 formats.

---

## Insight 3 — MRP has a near-linear relationship with sales

**Finding:** Items priced below $50 MRP average $616 in sales. Items priced $200+ average $3,679 — a 6x difference. This holds cleanly across all 5 MRP buckets with no reversals.

| MRP Range | Items | Avg Sales | Total Sales |
|---|---|---|---|
| <$50 | 757 | $616 | $466K |
| $50–100 | 1,682 | $1,202 | $2.0M |
| $100–150 | 2,210 | $1,891 | $4.2M |
| $150–200 | 2,434 | $2,722 | $6.6M |
| $200+ | 1,440 | $3,679 | $5.3M |

**Impact:** The top two MRP buckets ($150–200 and $200+) represent 45% of items but generate 64% of total revenue ($11.9M).

**Likely Cause:** Higher MRP items are premium SKUs, larger pack sizes, or household/non-food categories with higher basket value. The $150–200 bucket alone has the most items (2,434) and generates the most total revenue ($6.6M).

**Action:** Prioritize shelf space and item visibility for $150+ MRP items. Design promotions to lift the $100–150 bucket into the $150–200 range. Avoid over-indexing on low-MRP items for volume — they contribute minimally to revenue.

---

## Insight 4 — Grocery Stores are value destroyers

**Finding:** OUT010 and OUT019 (both Grocery Stores) average $339–340/item vs the $2,181 overall mean. They represent 12.7% of all items in the dataset but generate only 2% of total revenue.

| Outlet | Type | Tier | Est. | Total Sales | Avg/Item |
|---|---|---|---|---|---|
| OUT010 | Grocery Store | Tier 3 | 1998 | $188,340 | $339 |
| OUT019 | Grocery Store | Tier 1 | 1985 | $179,694 | $340 |

**Impact:** A single average Supermarket Type1 outlet generates ~$2.1M. The two Grocery Stores combined generate $368K — from a similar item count. That's a $1.7M+ revenue gap per equivalent slot in the network.

**Likely Cause:** Grocery Stores carry a structurally different SKU mix — primarily low-MRP, high-frequency FMCG with no room for premium or household items. The format ceiling is low by design.

**Action:** Do not expand the Grocery Store format. Evaluate conversion to Supermarket Type1 or use these locations only for hyper-local, high-frequency commodity fulfilment where the economics are justified.

---

## Insight 5 — Outlet age does not hurt performance; the oldest store leads

**Finding:** Outlets established in 1985 average $2,484/item — the second highest of any establishment year cohort. The 2009 cohort averages $1,995. The 1998 cohort averages only $339, but that is entirely explained by OUT010 being a Grocery Store.

**Impact:** OUT027 (est. 1985) is the single highest-revenue outlet in the network at $3,453,926 total. Older outlets are not liabilities — they are often the network's anchors.

**Likely Cause:** Mature outlets have established catchment loyalty, optimized product mix, and stable operations. The 1985 establishment advantage is primarily OUT027's Type3 format, not age alone.

**Action:** Retention investment in mature outlets is justified — they are not candidates for closure based on age. Build expansion business cases with realistic 3–5 year ramp-up timelines rather than assuming new outlets will match mature performance immediately.

---

## Executive Summary

| # | Finding | Number |
|---|---|---|
| 1 | Supermarket Type3 is 60% more efficient per item than any other format | $3,694 avg vs $2,181 overall |
| 2 | Tier 1 cities underperform — counter to expectation | $1,877 avg vs $2,280 for Tier 3 |
| 3 | Higher MRP items sell 6x more than low-price items | $3,679 (MRP $200+) vs $616 (MRP <$50) |
| 4 | Grocery Stores contribute only 2% of revenue from 13% of items | $339 avg vs $2,181 overall |
| 5 | Fat content is not a meaningful sales driver | $2,158 (Low Fat) vs $2,225 (Regular) — negligible difference |

### Top 3 Recommended Actions

1. **Expand Supermarket Type3 format** — study OUT027 and build a replication plan. Highest priority.
2. **Audit Grocery Store strategy** — two stores generating $368K combined on an $18.6M network are structural underperformers.
3. **Prioritize $150+ MRP SKUs for shelf space and promotion** — they generate 64% of revenue from 45% of items.

### Key Data Caveats
- No date/time column — trend and seasonality analysis is impossible
- Outlet_Size is unknown for 28% of rows — size-based analysis is partially unreliable
- Item_Weight is missing for 17% of rows — weight-based analyses should be treated as indicative only
