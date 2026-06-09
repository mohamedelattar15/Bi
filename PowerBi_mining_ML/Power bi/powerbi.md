# 📊 TABLEAU DE BORD POWER BI - ANALYSE COMPLÈTE

## Ce que nous avons construit dans Power BI

---

# 🎯 VUE D'ENSEMBLE

Nous avons créé un **tableau de bord interactif** qui permet d'analyser les performances commerciales sous différents angles : ventes, produits, clients et employés.

L'utilisateur peut :
- Filtrer par période (date)
- Filtrer par catégorie de produit
- Filtrer par employé
- Naviguer entre les différentes pages d'analyse

---

# 📈 PAGE 1 : ANALYSE DES VENTES (SALES DASHBOARD)

## Objectif
Visualiser la performance globale des ventes dans le temps.

## Ce que l'on voit

### En haut (KPIs principaux)
- **Chiffre d'affaires total** : Montant global des ventes (en milliards d'euros)
- **Quantité vendue totale** : Nombre d'unités écoulées
- **Nombre de transactions** : Volume total de paniers
- **Panier moyen** : Montant moyen par transaction

### Graphiques présents

**Évolution des ventes dans le temps**
- Courbe qui montre les variations du chiffre d'affaires mois par mois
- Permet d'identifier les pics (Noël, Black Friday) et les creux (vacances d'été)

**Ventes par catégorie de produit**
- Diagramme en barres montrant quelles catégories (Boulangerie, Produits laitiers, Épicerie, etc.) génèrent le plus de revenus

**Saisonnalité mensuelle**
- Graphique qui compare les ventes de chaque mois sur plusieurs années
- Met en évidence les tendances récurrentes (ex: décembre toujours le meilleur mois)

**Top 10 des meilleures ventes**
- Classement des produits les plus vendus en termes de chiffre d'affaires

## Interactions possibles
- L'utilisateur peut cliquer sur une catégorie pour filtrer tout le tableau de bord
- Un curseur permet de sélectionner une plage de dates
- Des boutons permettent de basculer entre vue "Mois", "Trimestre" ou "Année"

---

# 📦 PAGE 2 : ANALYSE DES PRODUITS (PRODUCT DASHBOARD)

## Objectif
Comprendre la performance individuelle de chaque produit et catégorie.

## Ce que l'on voit

### En haut (indicateurs produit)
- **Nombre total de produits** : Combien de références différentes
- **Prix moyen** : Prix moyen pondéré de tous les produits
- **Produits sans ventes** : Stock dormant (produits jamais commandés)
- **Catégories représentées** : Nombre de familles de produits

### Graphiques présents

**CA par produit**
- Diagramme en barres horizontal montrant les meilleurs produits
- Couleur différente selon la catégorie

**Distribution des prix**
- Histogramme montrant la répartition des prix (combien de produits à moins de 10€, entre 10-20€, etc.)

**Analyse par niveau de résistance**
- Graphique comparant les ventes selon la durabilité du produit (Durable, Fragile, Medium)
- Permet de voir si les clients préfèrent les produits résistants

**Matrice prix vs volume**
- Nuage de points où chaque point est un produit
- Axe X : prix unitaire
- Axe Y : quantité vendue
- Taille du point : chiffre d'affaires
- Permet d'identifier les produits "stars" (prix moyen, fort volume)

### Filtres spécifiques
- Sélecteur de catégorie
- Sélecteur de niveau de résistance
- Recherche de produit par nom

## Interactions possibles
- Cliquer sur un produit affiche ses détails (prix, catégorie, ventes)
- Le graphique "Matrice prix vs volume" est interactif : sélectionner une zone filtre les autres graphiques

---

# 👥 PAGE 3 : ANALYSE DES CLIENTS (CUSTOMER DASHBOARD)

## Objectif
Comprendre le comportement des clients et leur valeur.

## Ce que l'on voit

### En haut (indicateurs clients)
- **Nombre total de clients** (inscrits)
- **Clients actifs** (qui ont acheté au moins une fois)
- **Taux de conversion** (actifs / total)
- **Valeur vie client (LTV)** : CA moyen généré par client

### Graphiques présents

**Top 10 des meilleurs clients**
- Classement des clients par chiffre d'affaires généré
- Affiche le nom et le montant

**Distribution clients par pays**
- Carte géographique ou diagramme en barres
- Montre la répartition géographique de la clientèle

**Segmentation client**
- Diagramme en anneau ou en barres
- Catégories : VIP, Régulier, Occasionnel, Nouveau
- Défini selon le montant dépensé et la fréquence d'achat

**Évolution du nombre de clients actifs**
- Courbe montrant l'évolution mois par mois
- Permet de voir la croissance ou décroissance de la base client

**Panier moyen par segment**
- Comparaison du montant moyen dépensé entre VIP, Réguliers, Occasionnels

## Interactions possibles
- Cliquer sur un segment (VIP, Régulier) filtre tous les autres graphiques
- Sélectionner un pays sur la carte affiche les clients de ce pays

---

# 👔 PAGE 4 : ANALYSE DES EMPLOYÉS (EMPLOYEE DASHBOARD)

## Objectif
Évaluer la performance des vendeurs et l'impact des caractéristiques démographiques.

## Ce que l'on voit

### En haut (indicateurs RH)
- **Nombre d'employés** (total)
- **Employés actifs** (ceux qui ont fait des ventes)
- **Taux d'activité**
- **Chiffre d'affaires moyen par employé**

### Graphiques présents

**Top 5 des meilleurs vendeurs**
- Classement des employés par chiffre d'affaires généré
- Barres horizontales avec photo ou nom

**Performance par tranche d'âge**
- Graphique comparant les ventes des jeunes, matures et seniors
- Permet de voir quelle génération est la plus performante

**Performance par ancienneté**
- Analyse des ventes selon les années d'expérience
- Nouveaux (moins 1 an) / Confirmés (1-5 ans) / Sénior (5+ ans)

**Répartition des ventes par employé**
- Diagramme circulaire montrant la part de chaque vendeur

**Évolution mensuelle du CA par employé**
- Courbes multiples (une par employé) ou graphique "treillis"
- Permet de suivre la progression individuelle

### Filtres spécifiques
- Sélecteur de tranche d'âge
- Sélecteur d'ancienneté
- Sélecteur d'employé individuel

## Interactions possibles
- Sélectionner un employé affiche son évolution dans le temps
- Filtrer par tranche d'âge pour comparer les performances générationnelles

---

# 🔧 PAGE 5 : ANALYSE DU PANIER (BASKET ANALYSIS)

## Objectif
Identifier les produits souvent achetés ensemble pour faire des recommandations.

## Ce que l'on voit

### En haut (métriques)
- **Nombre total de transactions** analysées
- **Nombre de produits** analysés
- **Seuils appliqués** (Support ≥ 1%, Lift ≥ 1.5)

### Graphiques présents

**Top 10 des associations de produits**
- Classement des paires par Lift (force de l'association)
- Exemple : "Flour - Sugar : Lift 2.1"

**Matrice Support vs Lift**
- Nuage de points
- Axe X : Support (fréquence)
- Axe Y : Lift (force)
- Chaque point est une paire de produits
- Zone en haut à droite = meilleures associations (fréquentes ET fortes)

**Tableau des règles**
- Liste des paires avec Support, Confidence et Lift
- Colonnes triables

### Filtres spécifiques
- Curseur pour ajuster le Support minimum
- Curseur pour ajuster le Lift minimum
- Recherche de produit spécifique

## Interactions possibles
- Cliquer sur une paire affiche les détails (ex: 23% des transactions avec Flour contiennent Sugar)
- Ajuster les curseurs pour voir plus ou moins d'associations

---

# 🧭 NAVIGATION ET FILTRES COMMUNS

## Slicers (filtres) présents sur toutes les pages

| Filtre | Type | Utilisation |
|--------|------|-------------|
| Période (date) | Curseur ou liste déroulante | Sélectionner une plage de dates |
| Catégorie | Liste déroulante | Filtrer par famille de produits |
| Employé | Liste déroulante | Voir les ventes d'un vendeur spécifique |

## Boutons de navigation

| Page | Icône | Description |
|------|-------|-------------|
| Ventes | 📈 | Page d'analyse globale |
| Produits | 📦 | Page d'analyse produit |
| Clients | 👥 | Page d'analyse client |
| Employés | 👔 | Page d'analyse employé |
| Panier | 🛒 | Page d'analyse des associations |

---

# 📱 INTERACTIVITÉ GLOBALE

## Ce que l'utilisateur peut faire

1. **Filtrer dynamiquement** : Cliquer sur une barre dans un graphique filtre tous les autres graphiques
2. **Explorer les détails** : Double-cliquer sur un point pour voir les données sous-jacentes
3. **Exporter** : Cliquer droit sur un graphique pour exporter les données en Excel
4. **Changer de vue** : Passer de la vue mensuelle à trimestrielle ou annuelle
5. **Rechercher** : Utiliser la recherche pour trouver un produit ou client spécifique

---

# ✅ RÉSUMÉ DE L'EXPÉRIENCE UTILISATEUR

L'utilisateur final peut :

- **En un coup d'œil** : Voir la santé globale des ventes (KPIs en haut)
- **Plonger dans les détails** : Analyser chaque dimension séparément (produits, clients, employés)
- **Découvrir des insights** : Identifier les meilleures associations produits grâce au Basket Analysis
- **Prendre des décisions** :
  - Quels produits mettre en avant ?
  - Quels clients fidéliser ?
  - Quels employés récompenser ?
  - Quels produits recommander ensemble ?

---

**Le tableau de bord est conçu pour être intuitif : l'utilisateur clique et découvre, sans avoir à écrire de code ou à comprendre la technique derrière.** 🚀