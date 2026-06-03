# 🛒 Projet ETL - Grocery Sales Data Warehouse

## 📌 Description du projet

Ce projet consiste à construire un **entrepôt de données (Data Warehouse)** à partir d'un fichier CSV contenant **6,6 millions de lignes** de ventes de produits alimentaires.

Les données sont :
- **Extraites** depuis un fichier CSV
- **Transformées** (nettoyage, dédoublonnage, calculs)
- **Chargées** dans PostgreSQL
- **Visualisées** dans Power BI

---

## 🏗️ Architecture technique

| Composant | Rôle |
|-----------|------|
| **Apache Hop** | ETL (Extraction, Transformation, Chargement) |
| **PostgreSQL** | Base de données cible |
| **Power BI** | Analyse et visualisation des données |

---

## 📊 Structure de la base de données

### 1. DIM_CATEGORY (2 colonnes)

| Colonne | Type | Description |
|---------|------|-------------|
| `categoryid` | INTEGER | Identifiant unique de la catégorie (PK) |
| `categoryname` | VARCHAR(100) | Nom de la catégorie |

---

### 2. DIM_PRODUCT (10 colonnes)

| Colonne | Type | Description |
|---------|------|-------------|
| `productid` | INTEGER | Identifiant unique du produit (PK) |
| `productname` | VARCHAR(200) | Nom du produit |
| `price` | NUMERIC(12,2) | Prix unitaire |
| `categoryid` | INTEGER | Référence vers la catégorie |
| `class` | VARCHAR(50) | Classe du produit |
| `modifydate` | DATE | Date de modification |
| `resistant` | VARCHAR(50) | Résistance du produit |
| `isallergic` | VARCHAR(10) | Allergène (Oui/Non) |
| `vitalitydays` | NUMERIC(8,2) | Durée de vie (jours) |
| `categoryname` | VARCHAR(100) | Nom de la catégorie (dénormalisé) |

---

### 3. DIM_CUSTOMER (11 colonnes)

| Colonne | Type | Description |
|---------|------|-------------|
| `customerid` | INTEGER | Identifiant unique du client (PK) |
| `customerfirstname` | VARCHAR(100) | Prénom du client |
| `middleinitial` | VARCHAR(1) | Initiale du deuxième prénom |
| `customerlastname` | VARCHAR(100) | Nom du client |
| `address` | VARCHAR(200) | Adresse postale |
| `cityid` | INTEGER | Identifiant de la ville |
| `city` | VARCHAR(100) | Nom de la ville |
| `zipcode` | VARCHAR(20) | Code postal |
| `countryid` | INTEGER | Identifiant du pays |
| `country` | VARCHAR(100) | Nom du pays |
| `countrycode` | VARCHAR(2) | Code pays (ISO) |

---

### 4. DIM_EMPLOYEE (8 colonnes)

| Colonne | Type | Description |
|---------|------|-------------|
| `employeeid` | INTEGER | Identifiant unique de l'employé (PK) |
| `employeefirstname` | VARCHAR(100) | Prénom de l'employé |
| `employeelastname` | VARCHAR(100) | Nom de l'employé |
| `birthdate` | DATE | Date de naissance |
| `gender` | VARCHAR(20) | Genre |
| `hiredate` | DATE | Date d'embauche |
| `city` | VARCHAR(100) | Ville de résidence |
| `cityid` | INTEGER | Identifiant de la ville |

---

### 5. FACT_SALES (10 colonnes)

| Colonne | Type | Description |
|---------|------|-------------|
| `salesid` | BIGINT | Identifiant unique de la vente (PK) |
| `employeeid` | INTEGER | Référence vers l'employé |
| `customerid` | INTEGER | Référence vers le client |
| `productid` | INTEGER | Référence vers le produit |
| `date` | DATE | Date de la vente |
| `quantity` | INTEGER | Quantité vendue |
| `discount` | NUMERIC(10,2) | Remise appliquée |
| `totalprice` | NUMERIC(14,2) | Prix total après remise |
| `transactionnumber` | VARCHAR(50) | Numéro de transaction unique |
| `time` | VARCHAR(10) | Heure de la vente |

---

## 📈 Statistiques

| Table | Nombre de colonnes | Volume estimé |
|-------|-------------------|---------------|
| dim_category | 2 | ~10 lignes |
| dim_product | 10 | ~450 lignes |
| dim_customer | 11 | ~100,000 lignes |
| dim_employee | 8 | ~50 lignes |
| fact_sales | 10 | ~6,690,599 lignes |

---

## 🚀 Scripts SQL

### Création des tables

```sql
DROP TABLE IF EXISTS fact_sales CASCADE;
DROP TABLE IF EXISTS dim_product CASCADE;
DROP TABLE IF EXISTS dim_customer CASCADE;
DROP TABLE IF EXISTS dim_employee CASCADE;
DROP TABLE IF EXISTS dim_category CASCADE;

CREATE TABLE dim_category (
    categoryid INTEGER PRIMARY KEY,
    categoryname VARCHAR(100)
);

CREATE TABLE dim_product (
    productid INTEGER PRIMARY KEY,
    productname VARCHAR(200),
    price NUMERIC(12,2),
    categoryid INTEGER,
    class VARCHAR(50),
    modifydate DATE,
    resistant VARCHAR(50),
    isallergic VARCHAR(10),
    vitalitydays NUMERIC(8,2),
    categoryname VARCHAR(100)
);

CREATE TABLE dim_customer (
    customerid INTEGER PRIMARY KEY,
    customerfirstname VARCHAR(100),
    middleinitial VARCHAR(1),
    customerlastname VARCHAR(100),
    address VARCHAR(200),
    cityid INTEGER,
    city VARCHAR(100),
    zipcode VARCHAR(20),
    countryid INTEGER,
    country VARCHAR(100),
    countrycode VARCHAR(2)
);

CREATE TABLE dim_employee (
    employeeid INTEGER PRIMARY KEY,
    employeefirstname VARCHAR(100),
    employeelastname VARCHAR(100),
    birthdate DATE,
    gender VARCHAR(20),
    hiredate DATE,
    city VARCHAR(100),
    cityid INTEGER
);

CREATE TABLE fact_sales (
    salesid BIGINT PRIMARY KEY,
    employeeid INTEGER,
    customerid INTEGER,
    productid INTEGER,
    date DATE,
    quantity INTEGER,
    discount NUMERIC(10,2),
    totalprice NUMERIC(14,2),
    transactionnumber VARCHAR(50),
    time VARCHAR(10)
);