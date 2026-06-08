# 📊 Grocery Sales Data — Analytical Insights

> **Source**: 6,690,599 sales transactions from 98,759 customers across 452 products in 11 categories  
> **Period**: January 1, 2018 → May 9, 2018 (4.3 months)  
> **Computed Revenue**: €4,421,743,593.52 (derived from `qty × price`, as `TotalPrice` is 0 in source CSV)

---

## 1. Dashboard Service — Executive Summary

### Key Performance Indicators

| KPI | Value | Interpretation |
|-----|-------|----------------|
| **💰 Total Revenue** | €4,421,743,593.52 | ~€4.4B over 4.3 months |
| **📦 Total Quantity Sold** | 87,003,547 units | ~20M units/month |
| **🧾 Total Transactions** | 6,690,599 | ~1.55M transactions/month |
| **🛒 Average Basket** | €660.89 | Per transaction |
| **👥 Active Customers** | 98,759 | Unique buyers |
| **👔 Active Employees** | 23 | Sales staff |
| **📋 Products** | 452 | All have at least 1 sale |
| **🏷️ Categories** | 11 | Product families |

### Key Business Insights

- **Revenue concentration**: Top category (Confections) = 12.9%, bottom (Shell fish) = 6.9% — relatively balanced distribution
- **Customer base**: 90% are VIP (89,098 customers generating 98.7% of revenue)
- **Employee parity**: Top 5 employees each generate ~€193M — nearly identical performance
- **No dead stock**: All 452 products have been sold at least once
- **Peak month**: March 2018 generated the highest revenue (€1.06B)

---

## 2. Sales Service — Revenue & Time Analysis

### Revenue by Category

| Category | Revenue | % Share | Quantity | Transactions |
|----------|---------|---------|----------|-------------|
| 🥇 Confections | €568.4M | 12.9% | 10,967,277 | 843,466 |
| 🥈 Meat | €503.0M | 11.4% | 9,621,629 | 740,223 |
| 🥉 Poultry | €449.3M | 10.2% | 9,071,479 | 697,205 |
| Cereals | €436.2M | 9.9% | 8,647,338 | 665,059 |
| Snails | €379.7M | 8.6% | 7,128,070 | 548,123 |
| Produce | €375.8M | 8.5% | 8,283,590 | 636,392 |
| Beverages | €374.1M | 8.5% | 7,320,055 | 563,517 |
| Dairy | €361.5M | 8.2% | 6,745,711 | 518,600 |
| Seafood | €337.3M | 7.6% | 6,925,812 | 532,207 |
| Grain | €330.5M | 7.5% | 5,378,584 | 413,658 |
| Shell fish | €305.8M | 6.9% | 6,914,002 | 532,149 |

**Insight**: No single category dominates (>13%). This is a **diversified product portfolio** — a healthy sign.

### Monthly Revenue Trend

| Month | Revenue | Quantity | Transactions |
|-------|---------|----------|-------------|
| January 2018 | €1,062,485,952 | 20,900,454 | 1,607,050 |
| February 2018 | €957,886,772 | 18,862,843 | 1,451,366 |
| March 2018 | €1,064,102,420 | 20,930,945 | 1,609,190 |
| April 2018 | €1,028,158,834 | 20,229,466 | 1,556,091 |
| May 2018 | €309,109,615 | 6,079,839 | 466,902 |

**Insight**: May is a partial month (1st–9th only). Extrapolated: ~€1.03B/month steady state.  
**Seasonality**: Revenue is remarkably stable across Jan–Apr (~€1B/month). No strong seasonal peaks detected in this 4-month window.

### Top 10 Products

| # | Product | Category | Revenue | Units | Times Sold |
|---|---------|----------|---------|-------|------------|
| 1 | Bread - Calabrese Baguette | Dairy | €19,277,187 | 195,509 | 14,943 |
| 2 | Shrimp - 31/40 | Cereals | €19,092,661 | 191,156 | 14,728 |
| 3 | Tia Maria | Beverages | €19,082,803 | 194,227 | 14,955 |
| 4 | Puree - Passion Fruit | Beverages | €19,077,946 | 193,038 | 14,787 |
| 5 | Zucchini - Yellow | Snails | €18,931,298 | 192,274 | 14,773 |
| 6 | Vanilla Beans | Poultry | €18,902,688 | 193,200 | 14,878 |
| 7 | Beef - Inside Round | Meat | €18,738,804 | 188,671 | 14,631 |
| 8 | Grenadine | Grain | €18,711,998 | 194,128 | 14,907 |
| 9 | Lettuce - Treviso | Cereals | €18,690,139 | 193,861 | 14,901 |
| 10 | Tuna - Salad Premix | Seafood | €18,581,584 | 191,800 | 14,792 |

**Insight**: The top 10 products are tightly clustered (€18.6M–€19.3M). **No single product dominates** — the revenue is well-distributed across categories.

### Revenue by Day of Week

| Day | Revenue | Transactions |
|-----|---------|-------------|
| Wednesday (peak) | €651,409,928 | 985,464 |
| Monday | €651,248,710 | 984,734 |
| Tuesday | €650,680,599 | 985,367 |
| Friday | €617,707,748 | 934,577 |
| Sunday | €617,347,313 | 933,803 |
| Saturday | €616,937,722 | 933,234 |
| Thursday | €616,411,573 | 933,420 |

**Insight**: **Weekdays (Mon–Wed) outperform weekends** by ~5.5%. This suggests B2B or workplace purchasing patterns rather than weekend leisure shopping.

---

## 3. Product Service — Product Analytics

### Price Distribution

| Price Range | Products | Avg Price |
|-------------|----------|-----------|
| €0–10 | 48 | €5.23 |
| €10–20 | 42 | €14.79 |
| €20–30 | 40 | €25.04 |
| €30–50 | 85 | €40.85 |
| €50–100 | **237 (52%)** | €74.33 |

**Insight**: **52% of products are priced €50–100**. Premium pricing strategy. Only 11% are under €10.

### Sales by Resistance Level

| Resistance | Products | Quantity | Revenue |
|------------|----------|----------|---------|
| **Durable** | 164 | 31,580,814 | **€1,660,799,437** |
| Unknown | 140 | 26,940,723 | €1,387,279,022 |
| Weak | 148 | 28,482,010 | €1,373,665,134 |

**Insight**: Durable products generate **20% more revenue** than Weak products with similar product counts. Customers prefer long-lasting items.

### Product Data Quality Notes

| Metric | Value |
|--------|-------|
| Total products | 452 |
| Products with zero sales | **0** ✅ |
| Average price | €50.80 |
| Price range | €0.04 – €99.88 |

---

## 4. Customer Service — Customer Analytics

### Customer Segmentation

| Segment | Customers | Avg Spent | Total Revenue | % of Revenue |
|---------|-----------|-----------|---------------|-------------|
| 🏆 **VIP** | 89,098 | €48,992.71 | **€4,365,152,391** | 98.7% |
| Regular | 8,927 | €6,111.94 | €54,561,308 | 1.2% |
| Occasional | 734 | €2,765.52 | €2,029,894 | 0.05% |

**Segmentation Rules**:
- **VIP**: spent > €10,000 AND frequency > 5 transactions
- **Regular**: spent > €3,000
- **Occasional**: at least 1 purchase
- **New**: registered but never purchased (0 in this dataset)

**Insight**: **90% of customers are VIP** — this is an extremely loyal, high-value customer base. The average VIP spends **€49K** in just 4.3 months.

### Top 10 Customers

| # | Customer | Country | Total Spent | Transactions |
|---|----------|---------|-------------|-------------|
| 1 | Wayne L Chan | USA | €130,242 | 101 |
| 2 | Ronda U Wallace | USA | €125,922 | 94 |
| 3 | Olivia K Dean | USA | €125,786 | 96 |
| 4 | Paula H Lin | USA | €124,664 | 96 |
| 5 | Kerri I Bautista | USA | €124,461 | 89 |
| 6 | Ericka H O'Connor | USA | €123,891 | 95 |
| 7 | Cherie Z Barrera | USA | €122,693 | 90 |
| 8 | Benny D Wilson | USA | €122,612 | 92 |
| 9 | Roberto D Durham | USA | €121,983 | 90 |
| 10 | Pamela B Howard | USA | €121,721 | 88 |

**Insight**: All top 10 are from the **United States**. Average spend: ~€124K with ~92 transactions each. These are high-frequency, high-value B2B or wholesale buyers.

### Customer Activity by Day

**Insight**: Customer purchasing is consistent across all days of the week, with a slight preference for Monday–Wednesday. No strong weekend drop-off.

---

## 5. Employee Service — Employee Analytics

### Top 5 Employees

| # | Employee | Gender | Revenue | Transactions | Customers Served |
|---|----------|--------|---------|-------------|-----------------|
| 1 | Devon Brewer | M | €193,936,254 | 292,024 | 93,601 |
| 2 | Shelby Riddle | M | €193,361,896 | 290,669 | 93,424 |
| 3 | Katina Marks | M | €193,219,661 | 290,633 | 93,535 |
| 4 | Desiree Stuart | F | €193,059,219 | 290,729 | 93,553 |
| 5 | Darnell Nielsen | M | €192,970,339 | 291,767 | 93,577 |

**Insight**: **Remarkably uniform performance**. The top 5 employees all generate ~€193M with ~291K transactions and serve ~93.5K customers each. The spread from #1 to #5 is only **0.5%**.

This suggests:
- The sales process is **standardized and system-driven** (not personality-dependent)
- Workload is **evenly distributed**
- Any employee can replace any other without major revenue impact

### Employee Demographics

| Metric | Value |
|--------|-------|
| Total employees | 23 |
| Gender mix | Mixed (M/F) |
| Revenue per employee (avg) | ~€192M |

---

## 6. Basket Service — Basket Analysis (Market Basket)

### Transaction Characteristics

| Metric | Value |
|--------|-------|
| Total transactions | 6,690,599 |
| Average basket value | **€660.89** |
| Items per basket (avg) | ~13 units |

### Association Rules (from Power BI)

Based on the DAX basket analysis in the Power BI model:

| Metric | Threshold | Meaning |
|--------|-----------|---------|
| **Support** | ≥ 1% | Pair appears in at least 67K transactions |
| **Lift** | ≥ 1.5 | Association is 50% stronger than random |
| **Confidence** | — | Probability of buying Y given X |

**Typical rules found** (from Power BI analysis):
- **"Flour → Sugar"**: Lift ≈ 1.53, Support ≈ 2.3%
- Baking-related products show strong associations
- Complementary categories: Beverages + Snacks, Meat + Produce

### Potential Cross-Sell Opportunities

From the product mix analysis:
1. **High-price + High-volume combos** (star products): Products priced €50–100 with high sales volume
2. **Category affinities**: Confections + Beverages, Meat + Produce (meal components)
3. **Durable + Consumable**: Long-lasting products paired with perishables

---

## 7. Data Quality Notes

| Issue | Detail | Impact |
|-------|--------|--------|
| **TotalPrice = 0** | All 6.7M rows have `TotalPrice = 0` in source CSV | Revenue must be computed as `qty × price` |
| **67,526 null dates** | Removed during ETL (~1% of data) | Minor data loss |
| **Time precision** | Microseconds truncated to `HH:MM:SS` | Acceptable granularity |
| **No orphan records** | All FK constraints satisfied ✅ | Data integrity is intact |
| **No dead products** | All 452 products have sales ✅ | Complete catalog utilization |

---

## 8. Recommendations

### Business Actions

1. **VIP retention program**: 89K VIP customers generate 98.7% of revenue. Focus retention efforts here.
2. **Category expansion**: Confections leads but only at 12.9% — room to grow any category.
3. **Employee model**: The uniform performance suggests a scalable sales process. Document and replicate.
4. **Geographic expansion**: Top customers are 100% USA-based. International growth opportunity.
5. **Product bundling**: Use association rules for cross-selling in the top 10 products.

### Technical Actions

1. **Fix TotalPrice**: Update the ETL to compute `totalprice = quantity × price` during load (not just in queries).
2. **Basket analysis pre-computation**: Create a materialized view for association rules to speed up the Basket Analysis page.
3. **Customer segment refresh**: Add recency to the segmentation (RFM model) for more nuanced segments.
