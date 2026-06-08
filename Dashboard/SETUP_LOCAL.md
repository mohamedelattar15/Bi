# 🚀 Setup Local (sans Docker)

## 1. Base de données PostgreSQL

```bash
# Démarrer PostgreSQL (si installé)
sudo systemctl start postgresql

# Créer la base de données
sudo -u postgres psql -c "CREATE DATABASE grocery_sales;"
sudo -u postgres psql -c "ALTER USER postgres PASSWORD 'postgres';"

# Exécuter le schéma
sudo -u postgres psql -d grocery_sales -f database/schema.sql
```

## 2. Backend FastAPI

> ⚠️ **Important** : Utilise Python 3.12 ou 3.13 (pas 3.14).
> Vérifie avec `python3 --version`. Si t'as 3.14, utilise `python3.12` à la place.

```bash
cd backend

# Créer l'environnement virtuel
python3 -m venv .venv
source .venv/bin/activate

# Installer les dépendances (sans compilation, uniquement des wheels)
pip install --only-binary :all: -r requirements.txt

# Si ça échoue (pas de wheel pour ta version Python), installe pandas/numpy en premier
# pip install --only-binary :all: pandas numpy
# pip install -r requirements.txt

# Lancer le serveur
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Le backend tourne sur **http://localhost:8000**
Documentation API : **http://localhost:8000/api/docs**

## 3. Frontend Next.js

```bash
cd frontend

# Installer les dépendances
bun install

# Lancer le serveur de dev
bun run dev
```

Le frontend tourne sur **http://localhost:3000**

## 4. Importer les données CSV

```bash
cd backend
source venv/bin/activate
python scripts/load_data.py
```

## Résumé

| Service     | URL                    | Commande                          |
|-------------|------------------------|-----------------------------------|
| Frontend    | http://localhost:3000  | `cd frontend && bun run dev`      |
| Backend     | http://localhost:8000  | `cd backend && uvicorn app.main:app --reload` |
| API Docs    | http://localhost:8000/api/docs | -                        |
| PostgreSQL  | localhost:5432         | `sudo systemctl start postgresql` |

## Pages du dashboard

- **http://localhost:3000** → Sales Dashboard
- **http://localhost:3000/products** → Product Analysis
- **http://localhost:3000/customers** → Customer Analysis
- **http://localhost:3000/employees** → Employee Analysis
- **http://localhost:3000/basket-analysis** → Basket Analysis
