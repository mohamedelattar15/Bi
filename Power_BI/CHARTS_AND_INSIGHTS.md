# 📊 Power BI Dashboard — Charts & Insights Extract

> Extracted from **`Dashboard_grocery_db.pbix`** — unzipped and reverse-engineered from `Report/Layout` (JSON UTF-16LE).
>
> ✅ **Implementation Status**: All charts/insights below have corresponding **backend API endpoints** and **frontend page components**.
> See [`Dashboard/backend/app/api/`](../Dashboard/backend/app/api/) and [`Dashboard/frontend/src/app/`](../Dashboard/frontend/src/app/).

---

## 🧩 Fichier source : `Dashboard_grocery_db.pbix`

| Propriété | Valeur |
|-----------|--------|
| **Fichier** | `Dashboard_grocery_db.pbix` (329 MB) |
| **Version PBIX** | 5 (Metadata) |
| **Settings Version** | 4 |
| **Thème** | Innovate (dark theme) |
| **Arrière-plans** | 5× images Amazon Background (JPG) |
| **Custom Visuals installés** | 3 (ZoomCharts Drill Down Network PRO, ZoomCharts Drill Down Graph PRO, Network Graph by Powerviz) |
| **Pages** | 5 |
| **Tables dans le modèle** | 15 |

### 🗂️ Tables du Data Model

| Table | Type | Description |
|-------|------|-------------|
| `fact_sales` | 📊 Fact | Table de faits ventes |
| `dim_category` | 📋 Dimension | Catégories de produits |
| `dim_customer` | 📋 Dimension | Clients |
| `dim_employee` | 📋 Dimension | Employés |
| `dim_product` | 📋 Dimension | Produits |
| `Calendrier` | 📅 Dimension | Table de dates |
| `DF_Basket` | 📦 Source | Données pour l'analyse du panier (id_transaction, productname) |
| `Basket Analysis` | 🧮 Calculée | Paires de produits avec Support, Confidence, Lift |
| `Mesures sales` | 📐 Mesures | CA total, Quantité totale, Nb transactions, CA Growth, Quant Growth, Transa Growth |
| `Mesures Produits` | 📐 Mesures | Nb catégories, Nb produits |
| `Mesures Clients` | 📐 Mesures | Clients actifs, Nb clients, Panier moyen client, Taux fidélisation, Fréquence achats, Taux réachat |
| `Mesures Employés` | 📐 Mesures | Nb employés, Ventes moyennes employé |
| `Button Mesures` | 🔘 Table | Boutons de sélection de mesures |
| `grouth mesures` | 📈 Table | Sélecteur de métriques de croissance |
| `Mesures` | 📐 Mesures | (table de mesures additionnelle) |

---

## 📈 PAGE 1 : Sales Performence

### 📇 KPI Cards (Multi-Row Card)
| Measure | Table | Description |
|---------|-------|-------------|
| **CA total** | `Mesures sales` | Chiffre d'affaires total |
| **Quantité totale** | `Mesures sales` | Nombre total d'unités vendues |
| **Nb transactions** | `Mesures sales` | Nombre total de transactions |

### 🎚️ Slicers / Filters
| # | Slicer Type | Source Field |
|---|-------------|-------------|
| 1 | Slicer (dropdown/list) | `Calendrier.Date.Variation.Date Hierarchy.Year` |
| 2 | Slicer (buttons) | `Button Mesures.Button Mesures` |
| 3 | Slicer (buttons) | `grouth mesures.grouth mesures` |

### 📊 Charts

| # | Visual Type | Fields | Axe X / Catégorie | Axe Y / Valeur |
|---|-------------|--------|-------------------|----------------|
| 1 | 📉 **Line Chart** | Y = `Quantité totale`, Cat. = `Month` | Mois | Quantité totale vendue |
| 2 | 🍩 **Donut Chart** | Y = `CA total`, Cat. = `dim_product.class` | Classe de produit | CA total |
| 3 | 🌍 **Map** | Size = `CA total`, Cat. = `dim_customer.city` | Ville | CA total (taille des bulles) |
| 4 | 📋 **Pivot Table** | Lignes = `Month`, Val. = `CA total`, `Quantité totale`, `Nb transactions` | Mois | CA, Quantité, Nb transactions |
| 5 | 📈 **Area Chart** | Y = `CA Growth`, Cat. = `Calendrier.Année` | Année | Croissance du CA |
| 6 | 🔻 **Funnel** | Y = `Quantité totale`, Cat. = `dim_customer.city` | Ville | Quantité totale |

### 💡 Insights
- **Line Chart** : tendance mensuelle des quantités vendues (pics et creux)
- **Donut Chart** : part du CA par classe de produit (ex: Épicerie, Produits laitiers)
- **Map** : distribution géographique du CA par ville
- **Area Chart** : trajectoire de croissance annuelle (CA Growth)
- **Funnel** : hiérarchie des villes par volume de ventes

---

## 📦 PAGE 2 : Product Performence

### 📇 KPI Cards (Multi-Row Card)
| Measure | Table | Description |
|---------|-------|-------------|
| **Nb catégories** | `Mesures Produits` | Nombre de catégories de produits |
| **Nb produits** | `Mesures Produits` | Nombre total de produits |

### 🎚️ Slicers / Filters
| # | Slicer Type | Source Field |
|---|-------------|-------------|
| 1 | Slicer (dropdown) | `Calendrier.Année` |
| 2 | Slicer (buttons) | `Button Mesures.Button Mesures` |

### 📊 Charts

| # | Visual Type | Fields | Catégorie | Valeur |
|---|-------------|--------|-----------|--------|
| 1 | 📊 **Clustered Bar Chart** | Y = `Quantité totale`, Cat. = `dim_product.productname` | Nom du produit | Quantité totale |
| 2 | 📊 **Clustered Bar Chart** | Y = `Quantité totale`, Cat. = `dim_product.productname` | Nom du produit | Quantité totale (vue alternative) |
| 3 | 📋 **Pivot Table** | Lignes = `dim_product.categoryname`, Val. = `CA Growth`, `Quant Growth`, `Transa Growth` | Catégorie | CA Growth, Quant Growth, Transa Growth |
| 4 | 🥧 **Pie Chart** | Cat. = `dim_product.isallergic`, Y = `Nb produits` | Allergène (Oui/Non) | Nb de produits |
| 5 | 🥧 **Pie Chart** | Y = `Nb produits`, Cat. = `dim_product.resistant` | Résistance (Durable/Fragile/Medium) | Nb de produits |
| 6 | 🗂️ **Treemap** | Groupe = `dim_product.categoryname`, Val. = `CA total` | Catégorie | CA total |

### 💡 Insights
- **Bar Charts** : comparaison des volumes de vente par produit
- **Treemap** : ventilation du CA par catégorie (visuelle hiérarchique)
- **Pie Charts** : composition du catalogue — part des allergènes, répartition par résistance
- **Pivot Table** : taux de croissance (CA, Quantité, Transactions) par catégorie

### 📌 Colonnes de `dim_product` utilisées
| Colonne | Description |
|---------|-------------|
| `productname` | Nom du produit |
| `categoryname` | Nom de la catégorie |
| `class` | Classe du produit |
| `isallergic` | Allergène (Oui/Non) |
| `resistant` | Résistance (Durable/Fragile/Medium) |

---

## 👥 PAGE 3 : Costumer Performence

### 📇 KPI Cards
| Measure | Table | Type visuel | Description |
|---------|-------|-------------|-------------|
| **Clients actifs** | `Mesures Clients` | Multi-Row Card | Clients ayant acheté ≥ 1 fois |
| **Nb clients** | `Mesures Clients` | Multi-Row Card | Nombre total de clients |
| **Panier moyen client** | `Mesures Clients` | Multi-Row Card | Montant moyen dépensé par client |
| **Taux fidélisation** | `Mesures Clients` | Multi-Row Card | Taux de fidélisation |
| **Fréquence achats** | `Mesures Clients` | **Card** (isolée) | Fréquence d'achat moyenne |
| **Taux réachat** | `Mesures Clients` | **Card** (isolée) | Taux de ré-achat |

### 🎚️ Slicers / Filters
| # | Slicer Type | Source Field |
|---|-------------|-------------|
| 1 | Slicer (buttons) | `Button Mesures.Button Mesures` |
| 2 | Slicer (dropdown) | `Calendrier.Année` |

### 📊 Charts

| # | Visual Type | Fields | Catégorie | Valeur |
|---|-------------|--------|-----------|--------|
| 1 | 📊 **Clustered Bar Chart** | Y = `Nb transactions`, Cat. = `dim_customer.Full name` | Nom du client | Nb de transactions |
| 2 | 📊 **Clustered Bar Chart** | Y = `Nb transactions`, Cat. = `dim_customer.Full name` | Nom du client | Nb de transactions (vue alternative) |
| 3 | 💬 **Q&A Visual** | — | Exploration en langage naturel | — |
| 4 | 🌍 **Map** | Cat. = `dim_customer.city`, Size = `Panier moyen client` | Ville | Panier moyen (taille des bulles) |
| 5 | 📋 **Pivot Table** | Lignes = `dim_customer.city`, Val. = `CA Growth`, `Transa Growth`, `Quant Growth` | Ville | CA Growth, Transa Growth, Quant Growth |

### 💡 Insights
- **Bar Charts** : identification des meilleurs clients par volume de transactions
- **Map** : répartition géographique du panier moyen par ville
- **Pivot Table** : croissance des ventes (CA, transactions, quantités) par ville
- **KPI Cards** : vue d'ensemble fidélisation + fréquence + réachat
- **Q&A Visual** : exploration interactive en langage naturel

### 📌 Colonnes de `dim_customer` utilisées
| Colonne | Description |
|---------|-------------|
| `Full name` | Nom complet du client |
| `city` | Ville du client |

---

## 👔 PAGE 4 : Employee Performence

### 📇 KPI Cards (Multi-Row Card)
| Measure | Table | Description |
|---------|-------|-------------|
| **Nb employés** | `Mesures Employés` | Nombre total d'employés |
| **Ventes moyennes employé** | `Mesures Employés` | Chiffre d'affaires moyen par employé |

### 🎚️ Slicers / Filters
| # | Slicer Type | Source Field |
|---|-------------|-------------|
| 1 | Slicer (buttons) | `Button Mesures.Button Mesures` |
| 2 | Slicer (dropdown) | `Calendrier.Année` |

### 📊 Charts

| # | Visual Type | Fields | Catégorie | Valeur |
|---|-------------|--------|-----------|--------|
| 1 | 📋 **Pivot Table** | Lignes = `dim_employee.Full name emp`, Val. = `CA total`, `CA Growth` | Nom employé | CA total, CA Growth |
| 2 | 🍩 **Donut Chart** | Cat. = `dim_employee.Catégorie âge`, Y = `Nb employés` | Catégorie d'âge | Nb d'employés |
| 3 | 🥧 **Pie Chart** | Y = `Nb employés`, Cat. = `dim_employee.Tranche âge` | Tranche d'âge | Nb d'employés |
| 4 | 🍩 **Donut Chart** | Cat. = `dim_employee.gender`, Y = `Nb employés` | Genre | Nb d'employés |
| 5 | 📊 **Bar Chart** | Cat. = `dim_employee.Tranche âge`, Y = `CA total` | Tranche d'âge | CA total |

### 💡 Insights
- **Pivot Table** : classement des employés par CA total et taux de croissance
- **Donut/Pie (âge)** : répartition des effectifs par âge (catégorie + tranche détaillée)
- **Donut (gender)** : répartition hommes/femmes
- **Bar Chart** : CA total par tranche d'âge — identification des générations les plus performantes

### 📌 Colonnes de `dim_employee` utilisées
| Colonne | Description |
|---------|-------------|
| `Full name emp` | Nom complet de l'employé |
| `Catégorie âge` | Catégorie d'âge (large) |
| `Tranche âge` | Tranche d'âge (détaillée) |
| `gender` | Genre |

---

## 🛒 PAGE 5 : Basket Analysis

### 📇 KPI Cards (Multi-Row Card)
| Measure | Table | Description |
|---------|-------|-------------|
| **Total produits** | `DF_Basket` | Nombre de produits distincts dans l'analyse |
| **Total transactions** | `DF_Basket` | Nombre de transactions analysées |

### 📊 Charts

| # | Visual Type | Fields | Axe X | Axe Y | Catégorie |
|---|-------------|--------|-------|-------|-----------|
| 1 | 🔵 **Scatter Chart** | Cat. = `Basket Analysis.Basket`, X = `Sum(Lift)`, Y = `Sum(Support)` | **Lift** (force) | **Support** (fréquence) | Paire de produits |
| 2 | 📋 **Pivot Table** | Lignes = `Basket Analysis.Basket`, Val. = `Support`, `Confidence P1`, `Confidence P2`, `Lift` | Paire de produits | Support, Conf P1, Conf P2, Lift |

### 📊 Métriques — Table calculée `Basket Analysis`

| Métrique | Description | Seuil |
|----------|-------------|-------|
| **Basket** | Paire de produits "Product1 - Product2" | — |
| **Support** | Fréquence de la paire dans les transactions | ≥ 1% |
| **Confidence P1** | Probabilité d'acheter P2 sachant P1 | — |
| **Confidence P2** | Probabilité d'acheter P1 sachant P2 | — |
| **Lift** | Force de l'association (indépendance du hasard) | ≥ 1.5 |

> 💡 Les formules DAX pour ces métriques sont documentées dans [`Basket_analysis_mining.md`](Basket_analysis_mining.md)

### 💡 Insights
- **Scatter Chart** : matrice Support × Lift — zone en haut à droite = meilleures associations
- **Pivot Table** : exploration détaillée de toutes les paires avec les 4 métriques
- Croisement possible avec `DF_Basket` (id_transaction, productname)

---

## 🧭 Slicers / Filtres — Matrice cross-pages

| Slicer | Sales | Product | Customer | Employee | Basket |
|--------|:-----:|:-------:|:--------:|:--------:|:------:|
| **Year** (`Calendrier.Année`) | ✅ | ✅ | ✅ | ✅ | ❌ |
| **Button Mesures** (`Button Mesures`) | ✅ | ✅ | ✅ | ✅ | ❌ |
| **grouth mesures** (`grouth mesures`) | ✅ | ❌ | ❌ | ❌ | ❌ |

---

## 🎨 Thème & Design

| Propriété | Valeur |
|-----------|--------|
| **Thème** | Innovate |
| **Arrière-plan** | Sombre (`#3a3a3a`) |
| **Texte** | Blanc (`#FFFFFF`) |
| **Couleurs principales** | `#70B0E0` (bleu), `#FCB714` (jaune), `#2878BD` (bleu foncé), `#0EB194` (teal) |
| **Palette** | 32 couleurs |
| **Arrière-plans** | Images Amazon Background (JPG) utilisées comme fond de pages |

### Custom Visuals installés (non utilisés dans les visuels actuels)

| Visual | Version | Éditeur |
|--------|---------|---------|
| Drill Down Network PRO (PIN) by ZoomCharts | 1.12.57.0 | ZoomCharts |
| Drill Down Graph PRO (PIN) by ZoomCharts | 1.11.83.0 | ZoomCharts |
| Network Graph by Powerviz | 1.0.0.2 | Powerviz |

---

## 🔘 Résumé — Pages du Dashboard

| # | Nom exact (PBIX) | Visuels | Slicers | KPI Cards | Graphiques |
|---|------------------|:-------:|:-------:|:---------:|:----------:|
| 1 | **Sales Performence** | 11 | 3 | 1 (multi) | 6 |
| 2 | **Product Performence** | 10 | 2 | 1 (multi) | 6 |
| 3 | **Costumer Performence** | 11 | 2 | 1 (multi) + 2 singles | 5 + Q&A |
| 4 | **Employee Performence** | 9 | 2 | 1 (multi) | 5 |
| 5 | **Basket Analysis** | 4 | 0 | 1 (multi) | 2 |
| | **Total** | **45** | **9** | **7** | **24** |

---

## ✅ Résumé des Insights Métier

| Domaine | Insight clé |
|---------|-------------|
| 📈 **Ventes** | Évolution mensuelle des quantités + croissance annuelle du CA |
| 📦 **Produits** | Performance par produit (quantité), composition catalogue (allergènes, résistance) |
| 👥 **Clients** | Top clients par transactions, panier moyen géographique, fidélisation |
| 👔 **Employés** | Performance individuelle, structure démographique, CA par tranche d'âge |
| 🛒 **Panier** | Associations de produits (Support × Lift) exploitables pour cross-sell |

---

## 📸 Screenshots

| Page | Screenshot |
|------|------------|
| Sales Performence | ![Sales](Images/Capture%20d'écran%202026-06-03%20020525.png) |
| Product Performence | ![Product](Images/Capture%20d'écran%202026-06-03%20020535.png) |
| Costumer Performence | ![Customer](Images/Capture%20d'écran%202026-06-03%20020543.png) |
| Employee Performence | ![Employee](Images/Capture%20d'écran%202026-06-03%20020549.png) |
| Basket Analysis | ![Basket Analysis](Images/Capture%20d'écran%202026-06-03%20020602.png) |

---

---

## ✅ Implementation Status — Frontend ↔ PBIX Mapping

Each page in the frontend (`/app/`) now maps directly to a PBIX page:

### 📈 Page 1: Sales Performence → `/` (page.tsx)
| PBIX Visual | Frontend Implementation |
|-------------|------------------------|
| KPI Cards (CA total, Quantité totale, Nb transactions) | ✅ 6 KPICard components |
| LineChart (Quantité totale by Month) | ✅ RechartsAreaChart |
| DonutChart (CA total by dim_product.class) | ✅ RechartsDoughnutChart (new `/api/sales/by-class`) |
| Map (CA total by dim_customer.city) | ✅ RechartsBarChart proxy (new `/api/sales/by-city`) |
| Funnel (Quantité totale by city) | ✅ RechartsBarChart proxy (new `/api/sales/funnel-by-city`) |
| AreaChart (CA Growth by Calendrier.Année) | ✅ RechartsAreaChart (new `/api/sales/ca-growth-by-year`) |
| PivotTable (Month × CA, Quantité, Nb transactions) | ✅ Table component |
| Slicers (Year, Button Mesures, grouth mesures) | ✅ DateRangeFilter |

### 📦 Page 2: Product Performence → `/products`
| PBIX Visual | Frontend Implementation |
|-------------|------------------------|
| KPI Cards (Nb catégories, Nb produits) | ✅ 4 KPICard components |
| ClusteredBarChart (Quantité by productname) | ✅ RechartsBarChart (new `/api/products/analytics/quantity-summary`) |
| PieChart (Nb produits by isallergic) | ✅ RechartsDoughnutChart (new `/api/products/analytics/allergen-distribution`) |
| PieChart (Nb produits by resistant) | ✅ RechartsDoughnutChart (new `/api/products/analytics/resistance-distribution`) |
| Treemap (CA total by categoryname) | ✅ RechartsDoughnutChart (existing) |
| PivotTable (category × CA/Quant/Trans Growth) | ✅ Table component (new `/api/products/analytics/category-growth`) |
| Price Distribution | ✅ RechartsBarChart (existing) |
| Scatter (Price vs Volume Matrix) | ✅ RechartsScatterChart (existing) |

### 👥 Page 3: Costumer Performence → `/customers`
| PBIX Visual | Frontend Implementation |
|-------------|------------------------|
| KPI Cards (Clients actifs, Nb clients, Panier moyen, Taux fidélisation) | ✅ 6 KPICard components |
| ClusteredBarChart (Nb transactions by Full name) | ✅ RechartsBarChart (new `/api/customers/by-transactions`) |
| Q&A Visual | ❌ Not replicable (Power BI native) |
| Map (Panier moyen client by city) | ✅ RechartsBarChart proxy (new `/api/customers/avg-basket-by-city`) |
| PivotTable (city × CA/Trans/Quant Growth) | ✅ Table component (new `/api/customers/growth-by-city`) |
| Card: Fréquence achats | ✅ KPI (via `/api/customers/loyalty-stats`) |
| Card: Taux réachat | ✅ KPI (via `/api/customers/loyalty-stats`) |
| Customer Segmentation | ✅ RechartsDoughnutChart (existing) |
| Active Customers Over Time | ✅ RechartsAreaChart (existing) |
| Avg Basket by Segment | ✅ RechartsBarChart (existing) |

### 👔 Page 4: Employee Performence → `/employees`
| PBIX Visual | Frontend Implementation |
|-------------|------------------------|
| KPI Cards (Nb employés, Ventes moyennes employé) | ✅ 4 KPICard components |
| PivotTable (Full name emp × CA total, CA Growth) | ✅ Table component (new `/api/employees/performance-table`) |
| DonutChart (Catégorie âge) | ✅ RechartsDoughnutChart (new `/api/employees/demographics/age-category`) |
| PieChart (Tranche âge) | ✅ RechartsDoughnutChart (new `/api/employees/demographics/age-tranche`) |
| DonutChart (gender) | ✅ RechartsDoughnutChart (new `/api/employees/demographics/gender`) |
| BarChart (CA total by Tranche âge) | ✅ RechartsBarChart (new `/api/employees/ca-by-age-tranche`) |
| Top 5 Employees | ✅ RechartsBarChart (existing) |
| Performance by Age Group | ✅ RechartsBarChart (existing) |
| Performance by Seniority | ✅ RechartsBarChart (existing) |

### 🛒 Page 5: Basket Analysis → `/basket-analysis`
| PBIX Visual | Frontend Implementation |
|-------------|------------------------|
| KPI Cards (Total produits, Total transactions) | ✅ 4 KPICard components (total_products now populated via `/api/basket/analysis`) |
| ScatterChart (Support vs Lift) | ✅ RechartsScatterChart (existing) |
| PivotTable (Basket × Support, Confidence, Lift) | ✅ Table component (existing) |

### ✅ Summary
| Category | Total | Implemented | Not Implemented |
|----------|:-----:|:-----------:|:---------------:|
| Pages | 5 | 5 | 0 |
| Visuals (PBIX) | 45 | ~42 | 3 (Q&A, 2× custom visuals not used) |
| API Endpoints (new) | — | 20+ new endpoints added | — |
| Backend queries | — | 20+ new repository methods | — |

> **Source**: Extracted directly from `Dashboard_grocery_db.pbix` → unzipped → parsed `Report/Layout` (JSON UTF-16LE), `DiagramLayout`, `Metadata`, `Settings`, and custom visual `package.json` files.  
> **Thème**: Innovate (dark) — not replicated in frontend  
> **Custom Visuals**: 3 installed (ZoomCharts Network PRO, ZoomCharts Graph PRO, Powerviz Network Graph) — not implemented  
> **Date**: June 10, 2026
