# README — grocery_sales_denormalized.csv

## Vue d'ensemble

Fichier: `grocery_sales_denormalized.csv`

Ce fichier contient les ventes dénormalisées du projet (une ligne par unité/ligne de vente). Il sert de source principale pour les analyses transactionnelles (basket analysis), les KPI de ventes, et la construction des dimensions/mesures du datawarehouse.

> Remarque : le fichier est volumineux et n'a pas été ouvert entièrement ici (taille > 50MB). Les commandes ci-dessous permettent d'inspecter un extrait localement.

## Colonnes attendues (exemples courants)

Le fichier dénormalisé contient typiquement les colonnes suivantes — vérifiez le header réel avant usage :

- `id_transaction` — identifiant unique de la transaction/panier
- `transaction_date` / `date` — date-heure de la transaction
- `customer_id` — identifiant client (si présent)
- `store_id` / `location` — point de vente
- `product_id` — identifiant produit
- `productname` — libellé du produit
- `quantity` — quantité vendue
- `unit_price` — prix unitaire
- `total_price` — prix total de la ligne (quantity × unit_price)
- `category` / `department` — catégorie produit
- champs d'enrichissement possibles : `promotion_flag`, `coupon_id`, `payment_type`

Si votre jeu a des colonnes différentes, adaptez les étapes ci-dessous.

## Comment inspecter rapidement le fichier

PowerShell (head) :

```powershell
Get-Content -Path "grocery_sales_denormalized.csv" -TotalCount 20
```

Linux / WSL :

```bash
head -n 20 grocery_sales_denormalized.csv
```

Python (pandas) — afficher le header et 10 lignes :

```python
import pandas as pd
df = pd.read_csv('grocery_sales_denormalized.csv', nrows=10)
print(df.columns.tolist())
print(df.head(10))
```

Charger seulement les types minimaux pour obtenir les colonnes (évite OOM) :

```python
cols = pd.read_csv('grocery_sales_denormalized.csv', nrows=0).columns.tolist()
print(cols)
```

## Encodage et séparateur

- Par défaut le fichier est supposé comma-separated (`,`). Si le séparateur est `;` ou autre, précisez `sep=';'` dans `read_csv`.
- Si vous avez des problèmes d'encodage, essayez `encoding='utf-8'` puis `encoding='latin-1'`.

## Nettoyage recommandé

- Normaliser les noms de colonnes (minuscules, underscores).
- Vérifier et parser les dates : `pd.to_datetime()` avec `errors='coerce'`.
- Gérer les valeurs manquantes (`quantity`, `unit_price`) : imputation ou suppression selon contexte.
- Supprimer les lignes avec `quantity <= 0` si non pertinentes.
- Vérifier les doublons d'`id_transaction` + `product_id` et agréger si nécessaire.
- Contrôler les outliers sur `unit_price` et `total_price`.

## Colonnes dérivées utiles

- `line_total = quantity * unit_price` (si absent)
- `year`, `month`, `day`, `week` extraite de `transaction_date`
- `basket_size` par `id_transaction` (nombre de lignes ou somme(quantity))
- `basket_value` par `id_transaction` (somme(line_total))

## Analyses recommandées

- Market/Basket analysis (apriori, association rules) — utiliser `productname` ou `product_id` groupés par `id_transaction`.
- RFM (recency, frequency, monetary) par `customer_id`.
- Série temporelle des ventes (agrégations journalières/hebdomadaires).
- Segmentations produit / ABC analysis par chiffre d'affaires.

## Exemples d'usage (pandas)

Calculer la valeur du panier et le nombre d'articles par transaction :

```python
import pandas as pd
chunks = pd.read_csv('grocery_sales_denormalized.csv', chunksize=100000)
agg_list = []
for chunk in chunks:
    chunk['line_total'] = chunk['quantity'] * chunk['unit_price']
    grp = chunk.groupby('id_transaction').agg({'line_total':'sum','quantity':'sum'})
    agg_list.append(grp)

summary = pd.concat(agg_list).groupby(level=0).sum()
summary.head()
```

Extraire un échantillon aléatoire de 10k lignes sans charger tout le fichier :

```bash
# Linux
shuf -n 10000 grocery_sales_denormalized.csv > sample_10k.csv
```

Ou en Python, échantillonnage sur chunks.

## Chargement vers une base (exemple PostgreSQL)

Utiliser `COPY` ou `psql` pour charger efficacement :

```sql
-- Avec psql (CSV sans header adapté)
\copy dim_raw FROM 'grocery_sales_denormalized.csv' CSV HEADER
```

Ou via Python avec sqlalchemy en chunks.

## Qualité & confidentialité

- Vérifier la présence de données personnelles (`customer_id`, adresses). Si présentes, appliquer anonymisation si nécessaire.
- Vérifier et documenter la fréquence de mise à jour du fichier.

## Notes finales

- Je n'ai pas ouvert complètement le fichier ici (limite de taille). Si vous voulez, je peux extraire les 50 premières lignes localement ou créer un petit script d'extraction et le déposer dans le repo.

---

Fichier généré : grocery_sales_denormalized_README.md
