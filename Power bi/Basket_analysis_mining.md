# 🛒 Data Mining : Basket Analysis (Analyse du panier)

## 📌 Description

Le **Basket Analysis** (ou Market Basket Analysis) est une technique de data mining permettant d'identifier les **produits fréquemment achetés ensemble**.

**Objectif :** recommander des produits complémentaires aux clients ("Les clients qui ont acheté X ont aussi acheté Y").

**Exemple :** si un client achète "Flour - Whole Wheat", il y a 23 % de chances qu'il achète aussi "Sugar" ; cette association est 1,5 fois plus forte que le hasard.

---

## 📊 Métriques utilisées

| Métrique | Formule | Signification | Exemple |
|----------|---------|---------------|---------|
| **Support** | Nb transactions avec X et Y / Nb total transactions | Fréquence de la paire | 2,3 % des transactions contiennent Flour ET Sugar |
| **Confidence** | Support(X,Y) / Support(X) | Probabilité d'acheter Y sachant X | 23 % des clients qui achètent Flour achètent aussi Sugar |
| **Lift** | Support(X,Y) / (Support(X) × Support(Y)) | Force de l'association | 1,53 (association positive) |

### Interprétation du Lift

| Lift | Signification | Décision commerciale |
|------|---------------|----------------------|
| < 1 | Corrélation négative | Ne pas recommander ensemble |
| = 1 | Pas de corrélation | Recommandation aléatoire |
| 1 - 1.5 | Association faible | À surveiller |
| 1.5 - 2 | Bonne association | Recommandation croisée |
| > 2 | Très forte association | Offre packagée |

**Seuil recommandé :** Lift ≥ 1,5

---

## 🏗️ Structure des données

### Table source : `DF_Basket`

Cette table doit contenir chaque produit acheté dans chaque transaction.

| Colonne | Type | Exemple | Description |
|---------|------|---------|-------------|
| `id_transaction` | INTEGER | 1001 | Identifiant unique du panier |
| `productname` | VARCHAR | whole milk | Nom du produit |

**Exemple de données :**

| id_transaction | productname |
|----------------|-------------|
| 1 | whole milk |
| 1 | eggs |
| 1 | bread |
| 2 | whole milk |
| 2 | butter |
| 3 | coffee |
| 3 | sugar |

### Table d'analyse : `Basket Analysis`

Cette table contient les paires possibles de produits et leurs métriques.

| Colonne | Type | Description |
|---------|------|-------------|
| `Product1` | VARCHAR | Premier produit (ordre alphabétique) |
| `Product2` | VARCHAR | Deuxième produit |
| `Basket` | VARCHAR | "Product1 - Product2" (affichage) |
| `Support` | DECIMAL | Fréquence de la paire (0 à 1) |
| `Confidence P1` | DECIMAL | Probabilité d'acheter P2 sachant P1 |
| `Confidence P2` | DECIMAL | Probabilité d'acheter P1 sachant P2 |
| `Lift` | DECIMAL | Force de l'association |

---

## 📝 Code DAX (pas à pas)

### Étape 1 — Vérifications de base

```dax
-- Nombre total de transactions uniques
Total Transactions = DISTINCTCOUNT(DF_Basket[id_transaction])

-- Nombre de produits uniques
NbProduits = DISTINCTCOUNT(DF_Basket[productname])
```

### Étape 2 — Créer la table des couples produits

```dax
Basket Analysis =
FILTER(
    CROSSJOIN(
        SELECTCOLUMNS(VALUES(DF_Basket[productname]), "Product1", DF_Basket[productname]),
        SELECTCOLUMNS(VALUES(DF_Basket[productname]), "Product2", DF_Basket[productname])
    ),
    [Product1] > [Product2]
)
```

### Étape 3 — Colonne d'affichage

```dax
Basket = 'Basket Analysis'[Product1] & " - " & 'Basket Analysis'[Product2]
```

### Étape 4 — Calcul du Support

```dax
Support =
VAR Prod1 = 'Basket Analysis'[Product1]
VAR Prod2 = 'Basket Analysis'[Product2]

VAR TransP1 =
    CALCULATETABLE(
        VALUES(DF_Basket[id_transaction]),
        DF_Basket[productname] = Prod1
    )

VAR TransP2 =
    CALCULATETABLE(
        VALUES(DF_Basket[id_transaction]),
        DF_Basket[productname] = Prod2
    )

VAR BothTrans = INTERSECT(TransP1, TransP2)
VAR NbBoth = COUNTROWS(BothTrans)
VAR TotalTrans = DISTINCTCOUNT(DF_Basket[id_transaction])

RETURN DIVIDE(NbBoth, TotalTrans, 0)
```

### Étape 5 — Calcul de la Confidence (P1 → P2)

```dax
Confidence P1 =
VAR Prod1 = 'Basket Analysis'[Product1]
VAR Prod2 = 'Basket Analysis'[Product2]

VAR TransP1 =
    CALCULATETABLE(VALUES(DF_Basket[id_transaction]), DF_Basket[productname] = Prod1)

VAR BothTrans =
    INTERSECT(
        TransP1,
        CALCULATETABLE(VALUES(DF_Basket[id_transaction]), DF_Basket[productname] = Prod2)
    )

VAR NbP1 = COUNTROWS(TransP1)
VAR NbBoth = COUNTROWS(BothTrans)

RETURN IF(NbP1 = 0, BLANK(), DIVIDE(NbBoth, NbP1, 0))
```

### Étape 6 — Calcul de la Confidence (P2 → P1)

```dax
Confidence P2 =
VAR Prod1 = 'Basket Analysis'[Product1]
VAR Prod2 = 'Basket Analysis'[Product2]

VAR TransP2 =
    CALCULATETABLE(VALUES(DF_Basket[id_transaction]), DF_Basket[productname] = Prod2)

VAR BothTrans =
    INTERSECT(
        TransP2,
        CALCULATETABLE(VALUES(DF_Basket[id_transaction]), DF_Basket[productname] = Prod1)
    )

VAR NbP2 = COUNTROWS(TransP2)
VAR NbBoth = COUNTROWS(BothTrans)

RETURN IF(NbP2 = 0, BLANK(), DIVIDE(NbBoth, NbP2, 0))
```

### Étape 7 — Calcul du Lift

```dax
Lift =
VAR Prod1 = 'Basket Analysis'[Product1]
VAR Prod2 = 'Basket Analysis'[Product2]

VAR TransP1 = CALCULATETABLE(VALUES(DF_Basket[id_transaction]), DF_Basket[productname] = Prod1)
VAR TransP2 = CALCULATETABLE(VALUES(DF_Basket[id_transaction]), DF_Basket[productname] = Prod2)
VAR BothTrans = INTERSECT(TransP1, TransP2)
VAR TotalTrans = DISTINCTCOUNT(DF_Basket[id_transaction])

VAR SupportP1 = DIVIDE(COUNTROWS(TransP1), TotalTrans, 0)
VAR SupportP2 = DIVIDE(COUNTROWS(TransP2), TotalTrans, 0)
VAR SupportBoth = DIVIDE(COUNTROWS(BothTrans), TotalTrans, 0)

RETURN IF(SupportP1 * SupportP2 = 0, BLANK(), DIVIDE(SupportBoth, SupportP1 * SupportP2, 0))
```
