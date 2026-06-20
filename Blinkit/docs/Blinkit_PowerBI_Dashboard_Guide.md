# Blinkit Grocery — Power BI Dashboard Build Guide

**Dataset:** Blinkit Grocery.xlsx — Sheet: Tableau BlinkIT Grocery Project
**Rows:** 8,523 | **Columns:** 12 | **Total Sales:** $18,591,125

---

## Step 1 — Load & Clean Data in Power Query

Open Power BI Desktop → Get Data → Excel → select `Blinkit Grocery.xlsx` → select sheet `Tableau BlinkIT Grocery Project`.

### Cleaning Steps (in order)

**1. Standardize Fat Content**
Add Column → Custom Column → name it `Fat_Content_Clean`
```
= if [Item_Fat_Content] = "LF" or [Item_Fat_Content] = "low fat" or [Item_Fat_Content] = "Low Fat"
  then "Low Fat"
  else "Regular"
```

**2. Create MRP Price Bucket**
Add Column → Custom Column → name it `MRP_Bucket`
```
= if [Item_MRP] < 50 then "1. Under 50"
  else if [Item_MRP] < 100 then "2. 50-100"
  else if [Item_MRP] < 150 then "3. 100-150"
  else if [Item_MRP] < 200 then "4. 150-200"
  else "5. 200+"
```
*(Prefix with numbers so Power BI sorts them correctly)*

**3. Calculate Outlet Age**
Add Column → Custom Column → name it `Outlet_Age`
```
= 2024 - [Outlet_Establishment_Year]
```

**4. Fix Outlet Size nulls**
Select `Outlet_Size` column → Replace Values → replace `null` with `Unknown`

**5. Fix Item Weight nulls**
Select `Item_Weight` column → Replace Values → replace `null` with `12.86`
*(12.86 is the dataset mean — use this as a neutral fill)*

**6. Set correct data types**
| Column | Type |
|---|---|
| Item_MRP | Decimal Number |
| Item_Outlet_Sales | Decimal Number |
| Item_Visibility | Decimal Number |
| Item_Weight | Decimal Number |
| Outlet_Establishment_Year | Whole Number |
| Outlet_Age | Whole Number |
| All text columns | Text |

Click **Close & Apply**.

---

## Step 2 — Create DAX Measures

In the Report view, create a dedicated **Measures** table (Enter Data → blank table named `_Measures`).

### Core Measures

```dax
Total Sales = SUM('BlinkIT'[Item_Outlet_Sales])

Avg Sales per Item = AVERAGE('BlinkIT'[Item_Outlet_Sales])

Total Items = COUNT('BlinkIT'[Item_Identifier])

Total Outlets = DISTINCTCOUNT('BlinkIT'[Outlet_Identifier])

Sales % of Total =
DIVIDE(
    [Total Sales],
    CALCULATE([Total Sales], ALL('BlinkIT'))
)

Avg Sales vs Overall =
VAR OverallAvg = CALCULATE(AVERAGE('BlinkIT'[Item_Outlet_Sales]), ALL('BlinkIT'))
RETURN
AVERAGE('BlinkIT'[Item_Outlet_Sales]) - OverallAvg

Sales per Outlet =
DIVIDE([Total Sales], [Total Outlets])
```

---

## Step 3 — Dashboard Pages

Build **3 pages**. One decision per page.

---

### Page 1: Sales Overview
**Decision this page answers:** *Where is the money coming from?*

**Canvas size:** 1280 × 720

#### Layout

```
+------------------+------------------+------------------+------------------+
|  KPI: Total      |  KPI: Avg Sales  |  KPI: Total      |  KPI: Active     |
|  Sales           |  per Item        |  Items           |  Outlets         |
+------------------+------------------+------------------+------------------+
|                                     |                                      |
|   Bar: Sales by Outlet Type         |   Horizontal Bar: Sales by Item Type |
|   (with avg line)                   |   (top 10, sorted desc)              |
|                                     |                                      |
+-------------------------------------+--------------------------------------+
|                                     |                                      |
|   Donut: Sales by Location Tier     |   Stacked Bar: Fat Content by        |
|                                     |   Outlet Type                        |
+-------------------------------------+--------------------------------------+
|  SLICERS: Outlet Type | Location Tier | Item Type | Fat_Content_Clean      |
+-------------------------------------------------------------------------------------+
```

#### Visual Specs

| Visual | Type | X-Axis / Legend | Y-Axis / Values | Notes |
|---|---|---|---|---|
| Total Sales | Card | — | `[Total Sales]` | Format: currency, 0 decimals |
| Avg Sales/Item | Card | — | `[Avg Sales per Item]` | Format: currency |
| Total Items | Card | — | `[Total Items]` | Format: whole number |
| Active Outlets | Card | — | `[Total Outlets]` | Format: whole number |
| Sales by Outlet Type | Clustered Bar | `Outlet_Type` | `[Total Sales]` | Sort desc by sales; add avg line using `[Avg Sales per Item]` as line on secondary axis |
| Sales by Item Type | Horizontal Bar | `Item_Type` | `[Total Sales]` | Sort desc; show top 10 using TopN filter |
| Sales by Location Tier | Donut | `Outlet_Location_Type` | `[Total Sales]` | Show % labels |
| Fat Content by Outlet Type | 100% Stacked Bar | `Outlet_Type` | `[Total Sales]` | Legend: `Fat_Content_Clean` |

#### Slicers
- `Outlet_Type` — Dropdown
- `Outlet_Location_Type` — Dropdown
- `Item_Type` — Dropdown
- `Fat_Content_Clean` — Tile (only 2 values)

---

### Page 2: Outlet Performance
**Decision this page answers:** *Which outlets to invest in and which to fix?*

#### Layout

```
+------------------------------------------+-----------------------------+
|   Bar: Sales by Outlet (ranked)           |   Matrix: Outlet Type       |
|   Color by Outlet_Type                    |   vs Location Tier          |
|                                           |   Values: Total Sales       |
+------------------------------------------+-----------------------------+
|   Line: Avg Sales by Est. Year            |   Bar: Avg Sales by         |
|   (X: Establishment Year, Y: Avg Sales)   |   Outlet Size               |
+------------------------------------------+-----------------------------+
|   Donut: Outlet Size distribution         |   Table: Outlet detail      |
|   (count of items)                        |   (see specs below)         |
+------------------------------------------+-----------------------------+
|  SLICERS: Outlet Type | Location Tier | Outlet Size | Est. Year (range) |
+-------------------------------------------------------------------------------+
```

#### Visual Specs

| Visual | Type | X-Axis / Rows | Y-Axis / Values | Notes |
|---|---|---|---|---|
| Sales by Outlet | Clustered Bar | `Outlet_Identifier` | `[Total Sales]` | Color by `Outlet_Type`; sort desc; this will immediately show OUT027 dominant and OUT010/OUT019 at bottom |
| Outlet Type × Location Tier | Matrix | Rows: `Outlet_Type` | Cols: `Outlet_Location_Type` | Values: `[Total Sales]`; conditional formatting (data bars) on values |
| Avg Sales by Est. Year | Line Chart | `Outlet_Establishment_Year` | `[Avg Sales per Item]` | Also add `[Total Sales]` as second line on secondary axis |
| Avg Sales by Outlet Size | Clustered Bar | `Outlet_Size` | `[Avg Sales per Item]` | Sort: High, Medium, Small, Unknown |
| Outlet Size distribution | Donut | `Outlet_Size` | `[Total Items]` | Highlights the 28% Unknown gap |
| Outlet detail table | Table | `Outlet_Identifier`, `Outlet_Type`, `Outlet_Location_Type`, `Outlet_Size`, `Outlet_Establishment_Year` | `[Total Sales]`, `[Avg Sales per Item]`, `[Total Items]` | Sort by Total Sales desc; conditional formatting on Avg Sales |

#### Slicers
- `Outlet_Type` — Tile
- `Outlet_Location_Type` — Dropdown
- `Outlet_Size` — Tile
- `Outlet_Establishment_Year` — Between slicer (range slider)

---

### Page 3: Product Intelligence
**Decision this page answers:** *What to stock, price, and promote?*

#### Layout

```
+----------------------------------+-------------------------------------+
|   Bar: Avg Sales by MRP Bucket   |   Scatter: Item_MRP vs Sales        |
|   (shows 6x price-sales gap)     |   (each dot = 1 item)               |
+----------------------------------+-------------------------------------+
|   Bar+Line Combo: Item Type      |   Stacked Bar: Fat Content          |
|   Total Sales (bar) +            |   split by Item Type                |
|   Avg Sales (line)               |                                     |
+----------------------------------+-------------------------------------+
|   Table: Zero-Visibility items   |   Bar: Item Type avg MRP ranking    |
|   (Item_Visibility = 0)          |                                     |
+----------------------------------+-------------------------------------+
|  SLICERS: Item Type | Fat_Content_Clean | MRP_Bucket | Outlet Type     |
+-----------------------------------------------------------------------------+
```

#### Visual Specs

| Visual | Type | X-Axis | Y-Axis / Values | Notes |
|---|---|---|---|---|
| Avg Sales by MRP Bucket | Clustered Bar | `MRP_Bucket` | `[Avg Sales per Item]` | Sort by bucket order (prefix numbers handle this); color gradient low→high |
| MRP vs Sales scatter | Scatter | X: `Item_MRP` | Y: `Item_Outlet_Sales` | Details: `Item_Identifier`; add trend line via Analytics pane |
| Item Type combo | Line and Clustered Column | X: `Item_Type` | Column: `[Total Sales]`, Line: `[Avg Sales per Item]` | Sort by Total Sales desc; reveals Fruits/Veg volume vs Household efficiency |
| Fat Content by Item Type | 100% Stacked Bar | `Item_Type` | `[Total Sales]` | Legend: `Fat_Content_Clean`; sort by total sales |
| Zero-Visibility table | Table | `Item_Identifier`, `Item_Type`, `Item_Visibility` | `[Total Sales]` | Add filter: `Item_Visibility = 0`; 526 rows |
| Avg MRP by Item Type | Horizontal Bar | `Item_Type` | `AVERAGE(Item_MRP)` | Sort desc; shows which categories carry high-value SKUs |

#### Slicers
- `Item_Type` — Dropdown
- `Fat_Content_Clean` — Tile
- `MRP_Bucket` — Tile
- `Outlet_Type` — Dropdown

---

## Step 4 — Formatting Standards

### Colors
| Meaning | Color |
|---|---|
| Primary metric / good | #1AB394 (teal green) |
| Warning / underperformer | #E74C3C (red) |
| Neutral / secondary | #2C3E50 (dark navy) |
| Background | #F7F9FC (off-white) |
| Card background | #FFFFFF |

### Typography
- Title: Segoe UI Bold, 14pt
- Axis labels: Segoe UI, 9pt
- Card values: Segoe UI Bold, 28pt
- Card labels: Segoe UI, 10pt, grey

### Global settings
- Turn off chart borders — use padding only
- Enable data labels on all bar charts
- Set all monetary values to format: `$#,##0`
- Set percentage values to format: `0.0%`
- Page background: #F7F9FC

---

## Step 5 — Cross-Page Filters & Interactions

1. Go to **View → Sync Slicers** for `Outlet_Type` and `Item_Type` — sync these across all 3 pages so selections persist when navigating.

2. On each page, select each slicer → **Format → Edit Interactions** → set all visuals to **Filter** (not Highlight) for cleaner behaviour.

3. Add **Page Navigation buttons** (Insert → Buttons → Navigation) in a consistent top bar across all pages labelled: `Sales Overview` | `Outlet Performance` | `Product Intelligence`

---

## Step 6 — Key Filters to Always Keep Accessible

These filters unlock the most critical comparisons in the dataset:

| Filter | Why it matters |
|---|---|
| `Outlet_Type` | Instantly separates Grocery Stores (underperformers) from Supermarkets |
| `Outlet_Location_Type` | Exposes the Tier 1 underperformance story |
| `MRP_Bucket` | Reveals price-tier revenue concentration |
| `Item_Type` | Drills from category-level to SKU performance |
| `Fat_Content_Clean` | Quick health-mix check across any segment |
| `Outlet_Establishment_Year` | Age vs performance analysis for expansion decisions |

---

## Quick Reference — Column Guide

| Column | Type | Use in |
|---|---|---|
| `Item_Identifier` | Text ID | Count distinct SKUs; table drills |
| `Item_Weight` | Numeric | Lower priority; 17% nulls |
| `Item_Fat_Content` | Text (dirty) | Use `Fat_Content_Clean` instead |
| `Fat_Content_Clean` | Calculated | Page 1 & 3 slicers and visuals |
| `Item_Visibility` | Numeric (0–0.33) | Page 3 zero-visibility table only |
| `Item_Type` | Category | Page 1 & 3 — primary category axis |
| `Item_MRP` | Numeric | Page 3 scatter + `MRP_Bucket` |
| `MRP_Bucket` | Calculated | Page 3 bar chart + slicer |
| `Outlet_Identifier` | Text ID | Page 2 ranked bar chart |
| `Outlet_Establishment_Year` | Numeric | Page 2 line chart + range slicer |
| `Outlet_Age` | Calculated | Optional tooltip on outlet visuals |
| `Outlet_Size` | Category (+ Unknown) | Page 2 bar + donut |
| `Outlet_Location_Type` | Category (Tier 1/2/3) | Page 1 donut + Page 2 matrix |
| `Outlet_Type` | Category | Primary segment across all 3 pages |
| `Item_Outlet_Sales` | Numeric — **the target metric** | Every sales visual |
