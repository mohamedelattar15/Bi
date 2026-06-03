# 🛒 BI Project — Grocery Sales & Analysis

## 📋 Table des matières

1. [Aperçu](#aperçu)
2. [Structure du projet](#structure-du-projet)
3. [Schéma de la base de données](#schéma-de-la-base-de-données)
4. [Fichiers & Ressources](#fichiers--ressources)
5. [Pipelines & Processus](#pipelines--processus)
6. [Analyses & Techniques](#analyses--techniques)
7. [Guide de démarrage](#guide-de-démarrage)
8. [Prérequis](#prérequis)
9. [Contribuer](#contribuer)

---

## Aperçu

Le **Projet BI — Grocery Sales** est un environnement d'analyse décisionnel complet combinant :

- **Base de données relationnelle** : schéma normalisé avec transactions, clients, produits, géographie.
- **Données dénormalisées** : fichiers CSV enrichis pour analyses directes.
- **Pipelines ETL** : Apache Hop pour extraire, transformer et charger les dimensions.
- **Techniques de Data Mining** : Basket Analysis et Market Basket analysis (apriori, règles d'association).

Idéal pour data analysts, data scientists et BI practitioners visant à explorer les tendances de ventes, comportements clients et insights métier.

---

## Structure du projet

```
bi/
├── README.md                                    # Ce fichier (documentation principale)
├── Basket_analysis_mining.md                    # Guide complet : Market Basket Analysis + DAX
├── Basket_analysis_mining_README.md             # (si créé) Documentation technique
├── Dimension_Pipline.hpl                        # Pipeline Apache Hop (dimension loading)
├── Dimension_Pipline_README.md                  # Documentation : exécution & variables
├── grocery_sales_denormalized.csv               # Dataset dénormalisé (>50MB)
├── grocery_sales_denormalized_README.md         # Documentation : colonnes & nettoyage
├── groceries_long.csv                           # Dataset alternatif (format long)
├── SQL_Scripts.txt                              # Scripts SQL utiles
├── work.md                                      # Notes de travail / journal
└── Images/                                     # Captures d'écran dashboards & pipeline
```

---

## Captures d'écran

### Dashboards Power BI

Voici les trois dashboards Power BI présents dans le projet :

- `Images/Capture d'écran 2026-06-03 020543.png` — Dashboard Customer Performance
- `Images/Capture d'écran 2026-06-03 020549.png` — Dashboard Employee Performance
- `Images/Capture d'écran 2026-06-03 020602.png` — Dashboard Basket Analysis

![Customer Performance Dashboard](Images/Capture%20d'écran%202026-06-03%20020543.png)

![Employee Performance Dashboard](Images/Capture%20d'écran%202026-06-03%20020549.png)

![Basket Analysis Dashboard](Images/Capture%20d'écran%202026-06-03%20020602.png)

### Pipeline Apache Hop

Capture du pipeline Apache Hop utilisé pour charger les dimensions et préparer les données.

![Pipeline Apache Hop](Images/Capture%20d'écran%202026-06-03%20012115.png)

## Schéma de la base de données

### Vue d'ensemble

The **Grocery Sales Database** is a structured relational dataset designed for analyzing sales transactions, customer demographics, product details, employee records, and geographical information across multiple cities and countries. This dataset is ideal for data analysts, data scientists, and machine learning practitioners looking to explore sales trends, customer behaviors, and business insights.

## Database Schema
![Database Schema](Capture%20d'écran%202026-05-15%20162014.png)

The dataset consists of seven interconnected tables:

| File Name | Description |
| :--- | :--- |
| `categories.csv` | Defines the categories of the products. |
| `cities.csv` | Contains city-level geographic data. |
| `countries.csv` | Stores country-related metadata. |
| `customers.csv` | Contains information about the customers who make purchases. |
| `employees.csv` | Stores details of employees handling sales transactions. |
| `products.csv` | Stores details about the products being sold. |
| `sales.csv` | Contains transactional data for each sale. |

## Table Descriptions

### 1. categories
| Key | Column Name | Data Type | Description |
| :--- | :--- | :--- | :--- |
| **PK** | `CategoryID` | INT | Unique identifier for each product category. |
| | `CategoryName` | VARCHAR(45) | Name of the product category. |

### 2. cities
| Key | Column Name | Data Type | Description |
| :--- | :--- | :--- | :--- |
| **PK** | `CityID` | INT | Unique identifier for each city. |
| | `CityName` | VARCHAR(45) | Name of the city. |
| | `Zipcode` | DECIMAL(5,0) | Population of the city. |
| **FK** | `CountryID` | INT | Reference to the corresponding country. |

### 3. countries
| Key | Column Name | Data Type | Description |
| :--- | :--- | :--- | :--- |
| **PK** | `CountryID` | INT | Unique identifier for each country. |
| | `CountryName` | VARCHAR(45) | Name of the country. |
| | `CountryCode` | VARCHAR(2) | Two-letter country code. |

### 4. customers
| Key | Column Name | Data Type | Description |
| :--- | :--- | :--- | :--- |
| **PK** | `CustomerID` | INT | Unique identifier for each customer. |
| | `FirstName` | VARCHAR(45) | First name of the customer. |
| | `MiddleInitial` | VARCHAR(1) | Middle initial of the customer. |
| | `LastName` | VARCHAR(45) | Last name of the customer. |
| **FK** | `cityID` | INT | City of the customer. |
| | `Address` | VARCHAR(90) | Residential address of the customer. |

### 5. employees
| Key | Column Name | Data Type | Description |
| :--- | :--- | :--- | :--- |
| **PK** | `EmployeeID` | INT | Unique identifier for each employee. |
| | `FirstName` | VARCHAR(45) | First name of the employee. |
| | `MiddleInitial` | VARCHAR(1) | Middle initial of the employee. |
| | `LastName` | VARCHAR(45) | Last name of the employee. |
| | `BirthDate` | DATE | Date of birth of the employee. |
| | `Gender` | VARCHAR(10) | Gender of the employee. |
| **FK** | `CityID` | INT | Unique identifier for city. |
| | `HireDate` | DATE | Date when the employee was hired. |

### 6. products
| Key | Column Name | Data Type | Description |
| :--- | :--- | :--- | :--- |
| **PK** | `ProductID` | INT | Unique identifier for each product. |
| | `ProductName` | VARCHAR(45) | Name of the product. |
| | `Price` | DECIMAL(4,0) | Price per unit of the product. |
| | `CategoryID` | INT | Unique category identifier. |
| | `Class` | VARCHAR(15) | Classification of the product. |
| | `ModifyDate` | DATE | Last modified date. |
| | `Resistant` | VARCHAR(15) | Product resistance category. |
| | `IsAllergic` | VARCHAR | Indicates whether the item is an allergen. |
| | `VitalityDays` | DECIMAL(3,0) | Product vital type classification. |

### 7. sales
| Key | Column Name | Data Type | Description |
| :--- | :--- | :--- | :--- |
| **PK** | `SalesID` | INT | Unique identifier for each sale. |
| **FK** | `SalesPersonID` | INT | Employee responsible for the sale. |
| **FK** | `CustomerID` | INT | Customer making the purchase. |
| **FK** | `ProductID` | INT | Product being sold. |
| | `Quantity` | INT | Number of units sold. |
| | `Discount` | DECIMAL(10,2) | Discount applied to the sale. |
| | `TotalPrice` | DECIMAL(10,2) | Final sale price after discounts. |
| | `SalesDate` | DATETIME | Date and time of the sale. |
| | `TransactionNumber` | VARCHAR(25) | Unique identifier for the transaction. |

## Use Cases
Despite being a four-month snapshot and existing independently of external data sources, this dataset offers a rich environment for aspiring data scientists to practice and enhance their SQL skills.

### 1. Monthly Sales Performance
*   **Objective:** Analyze sales performance within the four-month period to identify trends and patterns.
*   **Tasks:**
    *   Calculate total sales for each month.
    *   Compare sales performance across different product categories each month.

### 2. Top Products Identification
*   **Objective:** Determine which products are the best and worst performers within the dataset timeframe.
*   **Tasks:**
    *   Rank products based on total sales revenue.
    *   Analyze sales quantity and revenue to identify high-demand products.
    *   Examine the impact of product classifications on sales performance.

### 3. Customer Purchase Behavior
*   **Objective:** Understand how customers interact with products during the four-month period.
*   **Tasks:**
    *   Segment customers based on their purchase frequency and total spend.
    *   Identify repeat customers versus one-time buyers.
    *   Analyze average order value and basket size.

### 4. Salesperson Effectiveness
*   **Objective:** Evaluate the performance of sales personnel in driving sales.
*   **Tasks:**
    *   Calculate total sales attributed to each salesperson.
    *   Identify top-performing and underperforming sales staff.
    *   Analyze sales trends based on individual salesperson contributions over time.

### 5. Geographical Sales Insights
*   **Objective:** Explore how sales are distributed across different cities and countries within the dataset.
*   **Tasks:**
    *   Map sales data to specific cities and countries to identify high-performing regions.
    *   Compare sales volumes between various geographical areas.
    *   Assess the effectiveness of regional sales strategies.

## Data Relationships
*   **Sales:** Each sale is linked to a Product, Customer, and Employee through their respective IDs. Each sale is linked to a location via the customer.
*   **Customers:** Associated with a City and a Country to provide geographic context.
*   **Employees:** Manage sales and are uniquely identified by `EmployeeID`.
*   **Products:** Categorized under specific Categories to organize the inventory.
*   **Geography:** Cities belong to Countries, offering higher-level geographic segmentation.

---

## 📁 Fichiers & Ressources

| Fichier | Type | Description |
|---------|------|-------------|
| [Basket_analysis_mining.md](Basket_analysis_mining.md) | 📊 Guide | Techniques Market Basket Analysis + formules Support/Confidence/Lift + code DAX |
| [Dimension_Pipline.hpl](Dimension_Pipline.hpl) | 🔄 Pipeline | Pipeline Apache Hop pour chargement dimensions |
| [Dimension_Pipline_README.md](Dimension_Pipline_README.md) | 📖 Documentation | Instructions exécution pipeline Hop (GUI, CLI, variables) |
| [grocery_sales_denormalized.csv](grocery_sales_denormalized.csv) | 📈 Dataset | Données dénormalisées (~50MB+) : une ligne par article de panier |
| [grocery_sales_denormalized_README.md](grocery_sales_denormalized_README.md) | 📖 Documentation | Colonnes, encodage, nettoyage, exemples pandas/SQL |
| [groceries_long.csv](groceries_long.csv) | 📈 Dataset | Format long alternatif |
| [SQL_Scripts.txt](SQL_Scripts.txt) | 💾 Scripts | Requêtes SQL utiles |
| [work.md](work.md) | 📝 Notes | Journal & notes de travail |

---

## 🔄 Pipelines & Processus

### 1. Dimension Pipeline (Apache Hop)

La pipeline `Dimension_Pipline.hpl` automatise :
- ✅ Extraction des sources (CSV, base de données)
- ✅ Nettoyage & normalisation
- ✅ Enrichissements & transformations
- ✅ Chargement vers tables de dimension

**Lancer :** voir [Dimension_Pipline_README.md](Dimension_Pipline_README.md)

### 2. Données Dénormalisées

Le fichier `grocery_sales_denormalized.csv` contient toutes les ventes avec détails complets :
- `id_transaction`, `product_id`, `productname`
- `quantity`, `unit_price`, `total_price`
- `transaction_date`, `category`, etc.

**Utiliser :** voir [grocery_sales_denormalized_README.md](grocery_sales_denormalized_README.md)

---

## 📊 Analyses & Techniques

### Market Basket Analysis (Panier de consommation)

Identifier les produits fréquemment achetés ensemble : utiliser apriori ou association rules.

**Métriques clés :**
- **Support** = P(X ∧ Y)
- **Confidence** = P(Y|X)
- **Lift** = Confidence / P(Y)

**Implémentation :** DAX (Power BI/Tabular) ou Python (mlxtend, apyori)

→ Consultez [Basket_analysis_mining.md](Basket_analysis_mining.md) pour formules + code DAX complet.

### Cas d'usage

1. **Performance mensuelle** — Analyser tendances ventes par mois/catégorie
2. **Produits vedettes** — Classer produits par revenu et volume
3. **Comportement clients** — Segmenter (RFM, fréquence, panier moyen)
4. **Efficacité vendeurs** — Évaluer contribution par vendeur
5. **Insights géographiques** — Comparer villes/pays

---

## 🚀 Guide de démarrage

### 1. Charger les données

**Pour Power BI / Analyse Services :**
```
Importer grocery_sales_denormalized.csv → Transformer → Charger modèle
```

**Pour base SQL :**
```sql
LOAD DATA INFILE 'grocery_sales_denormalized.csv' 
INTO TABLE sales_raw 
FIELDS TERMINATED BY ',' ENCLOSED BY '"' 
LINES TERMINATED BY '\n' 
IGNORE 1 ROWS;
```

### 2. Exécuter la pipeline Dimension

```bash
# Apache Hop CLI
hop-run.sh -file="Dimension_Pipline.hpl" \
  -param:SRC_PATH="/path/to/data" \
  -param:DB_HOST="localhost"
```

### 3. Analyser le panier

Implémenter les formules DAX du fichier [Basket_analysis_mining.md](Basket_analysis_mining.md) dans Power BI ou reproduire en Python.

---

## 📋 Prérequis

- **Python** 3.8+ (pandas, numpy, mlxtend optionnel)
- **Apache Hop** 2.x+ (pour pipelines ETL)
- **Base de données** : PostgreSQL, MySQL, SQL Server (selon config)
- **Power BI** (optionnel, pour dashboards & DAX)
- **Java Runtime** (JRE/JDK pour Hop)

---

## 🤝 Contribuer

1. Vérifier [work.md](work.md) pour tâches en cours
2. Tester les pipelines sur un sous-ensemble avant commit
3. Documenter les nouveaux scripts ou analyses dans un README spécifique
4. Externaliser les paramètres d'environnement (éviter hardcoding)
5. Respecter la structure : un fichier README par ressource majeure

---

## 📞 Support

Questions ou bugs ? Ouvrez une issue ou consultez les README spécifiques liés à votre question :
- **Pipeline Hop** → [Dimension_Pipline_README.md](Dimension_Pipline_README.md)
- **Dataset CSV** → [grocery_sales_denormalized_README.md](grocery_sales_denormalized_README.md)
- **Basket Analysis** → [Basket_analysis_mining.md](Basket_analysis_mining.md)

---

## 📝 Licence & Auteur

Projet BI pour analyses de ventes et mining de données.  
Généré et documenté : Juin 2026

