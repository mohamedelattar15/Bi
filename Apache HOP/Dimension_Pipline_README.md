# Dimension_Pipeline — Apache Hop

## Vue d'ensemble

Ce pipeline Apache Hop réalise l'extraction, la transformation et le chargement (ETL) de données depuis un fichier CSV dénormalisé vers un schéma en étoile dans une base de données PostgreSQL (`grocery_db`). Il alimente 4 tables de dimensions et 1 table de faits.

**Fichier source** : `grocery_sales_denormalized.csv`  
**Base de données cible** : PostgreSQL — connexion `grocery_db`, schéma `public`

---

## Architecture du pipeline

Le pipeline part d'une unique source CSV, puis se divise en 5 branches parallèles indépendantes :

```
CSV file input
├── Sort rows → Unique rows → Select values → Table output   →  dim_category
├── Sort rows 2 → Unique rows 2 → Select values 2 → Table output 2  →  dim_product
├── Sort rows 3 → Unique rows 3 → Select values 3 → Table output 3  →  dim_customer
├── Sort rows 4 → Unique rows 4 → Select values 4 → Table output 4  →  dim_employee
└── Select values 5 → PostgreSQL Bulk Loader  →  fact_sales
```

---

## Description des branches

### Branche 1 — `dim_category`

| Étape | Type | Rôle |
|---|---|---|
| Sort rows | SortRows | Trie par `CategoryID` (ascendant) |
| Unique rows | Unique | Déduplique sur `CategoryID` |
| Select values | SelectValues | Renomme en minuscules : `categoryid`, `categoryname` |
| Table output | TableOutput | Insère dans `public.dim_category` |

**Colonnes chargées** : `categoryid`, `categoryname`

---

### Branche 2 — `dim_product`

| Étape | Type | Rôle |
|---|---|---|
| Sort rows 2 | SortRows | Trie par `ProductID` (ascendant) |
| Unique rows 2 | Unique | Déduplique sur `ProductID` |
| Select values 2 | SelectValues | Renomme 10 colonnes en minuscules |
| Table output 2 | TableOutput | Insère dans `public.dim_product` |

**Colonnes chargées** : `productid`, `productname`, `price`, `categoryid`, `class`, `modifydate`, `resistant`, `isallergic`, `vitalitydays`, `categoryname`

---

### Branche 3 — `dim_customer`

| Étape | Type | Rôle |
|---|---|---|
| Sort rows 3 | SortRows | Trie par `CustomerID` (ascendant) |
| Unique rows 3 | Unique | Déduplique sur `CustomerID` |
| Select values 3 | SelectValues | Renomme 11 colonnes en minuscules |
| Table output 3 | TableOutput | Insère dans `public.dim_customer` |

**Colonnes chargées** : `customerid`, `customerfirstname`, `middleinitial`, `customerlastname`, `address`, `cityid`, `city`, `zipcode`, `countryid`, `country`, `countrycode`

---

### Branche 4 — `dim_employee`

| Étape | Type | Rôle |
|---|---|---|
| Sort rows 4 | SortRows | Trie par `EmployeeID` (ascendant) |
| Unique rows 4 | Unique | Déduplique sur `EmployeeID` |
| Select values 4 | SelectValues | Renomme 8 colonnes en minuscules |
| Table output 4 | TableOutput | Insère dans `public.dim_employee` |

**Colonnes chargées** : `employeeid`, `employeefirstname`, `employeelastname`, `birthdate`, `gender`, `hiredate`, `city`, `cityid`

---

### Branche 5 — `fact_sales`

| Étape | Type | Rôle |
|---|---|---|
| Select values 5 | SelectValues | Sélectionne et renomme les 10 colonnes de faits |
| PostgreSQL Bulk Loader | PGBulkLoader | Charge en masse dans `public.fact_sales` (INSERT) |

**Colonnes chargées** : `salesid`, `employeeid`, `customerid`, `productid`, `date`, `quantity`, `discount`, `totalprice`, `transactionnumber`, `time`

> Le champ `date` utilise le masque `DATE` côté PostgreSQL Bulk Loader.

---

## Schéma des champs source (CSV)

Le fichier CSV contient les champs suivants, lus par le transform `CSV file input` :

| Champ | Type Hop | Format |
|---|---|---|
| SalesID, SalesPersonID, CustomerID, ProductID | Integer | `#` |
| Quantity | Integer | `#` |
| Discount, TotalPrice, Price, VitalityDays | Number | `#.#` |
| SalesDate | Date | `yyyy-MM-dd HH:mm:ss` |
| Date | Date | `yyyy-MM-dd` |
| ModifyDate, BirthDate, HireDate | Date | `yyyy-MM-dd HH:mm:ss.SSS` |
| DateID | Integer | `yyyyMMdd` |
| TransactionNumber, Time, ProductName, Class, ... | String | — |

---

## Prérequis

- Apache Hop installé
- PostgreSQL accessible avec la connexion nommée `grocery_db`
- Tables cibles créées au préalable dans le schéma `public` :
  - `dim_category`
  - `dim_product`
  - `dim_customer`
  - `dim_employee`
  - `fact_sales`
- Fichier source présent à l'emplacement configuré dans le transform `CSV file input`

---

## Notes techniques

- Le pipeline utilise `lazy_conversion: Y` sur la lecture CSV pour optimiser les performances.
- Toutes les branches de dimensions appliquent un pattern **Sort → Unique** pour garantir l'unicité avant l'insertion (pas de gestion de doublons côté base).
- Les `Table output` utilisent un commit par lots de 1000 lignes (`commit: 1000`).
- Le `PostgreSQL Bulk Loader` utilise un chargement de type `INSERT` sans arrêt sur erreur (`stop_on_error: N`).
- Le paramètre `truncate: N` sur toutes les sorties signifie que les tables ne sont **pas vidées** avant l'insertion — vérifier l'idempotence si le pipeline est relancé.

---

## Auteur et dates

| | |
|---|---|
| Créé le | 2026-06-01 |
| Modifié le | 2026-06-01 |
| Créé par | — |