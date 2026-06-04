"""
════════════════════════════════════════════════════════════════
NIVEAU 1 — BASELINE STATISTIQUE : SARIMA + Holt-Winters
════════════════════════════════════════════════════════════════
Objectif : établir une baseline solide avant les modèles ML
"""

import warnings
warnings.filterwarnings("ignore")

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from statsmodels.tsa.statespace.sarimax import SARIMAX
from statsmodels.tsa.holtwinters import ExponentialSmoothing
from statsmodels.tsa.stattools import adfuller
from sklearn.metrics import mean_absolute_error, mean_squared_error
import psycopg2

# ─── CONFIG ──────────────────────────────────────────────────
DB_CONFIG = {
    "grocery_db": "grocery_db", "user": "postgres",
    "password": "2002", "host": "localhost", "port": 5432,
}
FIGSIZE = (14, 5)

# ═══════════════════════════════════════════════════════════════
# 1. CHARGEMENT ET PRÉPARATION DES DONNÉES
# ═══════════════════════════════════════════════════════════════

def load_daily_revenue():
    """Charge le revenue journalier depuis PostgreSQL."""
    query = """
        SELECT
            f.date,
            SUM((p.price * f.quantity) - f.discount) AS revenue
        FROM fact_sales f
        JOIN dim_product p USING (productid)
        GROUP BY f.date
        ORDER BY f.date
    """
    print("📥 Chargement des données depuis PostgreSQL...")
    conn = psycopg2.connect(**DB_CONFIG)
    df = pd.read_sql(query, conn, parse_dates=["date"])
    conn.close()

    df = df.set_index("date").asfreq("D")
    df["revenue"] = df["revenue"].fillna(df["revenue"].median())
    df["revenue"] = df["revenue"].astype(float)

    print(f"   → {len(df):,} jours chargés ({df.index.min().date()} → {df.index.max().date()})")
    return df


def train_test_split(df):
    """Split : Train 2018-2021 / Test 2022."""
    train = df[df.index.year < 2022]
    test  = df[df.index.year == 2022]
    print(f"   Train : {len(train):,} jours | Test : {len(test):,} jours")
    return train, test


def mape(y_true, y_pred):
    y_true, y_pred = np.array(y_true), np.array(y_pred)
    mask = y_true != 0
    return np.mean(np.abs((y_true[mask] - y_pred[mask]) / y_true[mask])) * 100


def evaluate(name, y_true, y_pred):
    mae  = mean_absolute_error(y_true, y_pred)
    rmse = np.sqrt(mean_squared_error(y_true, y_pred))
    mape_val = mape(y_true, y_pred)
    print(f"\n📊 {name}")
    print(f"   MAE  : {mae:>12,.2f}")
    print(f"   RMSE : {rmse:>12,.2f}")
    print(f"   MAPE : {mape_val:>11.2f}%")
    return {"model": name, "MAE": mae, "RMSE": rmse, "MAPE": mape_val}


# ═══════════════════════════════════════════════════════════════
# 2. TEST DE STATIONNARITÉ
# ═══════════════════════════════════════════════════════════════

def check_stationarity(series):
    print("\n🔬 Test ADF de stationnarité...")
    result = adfuller(series.dropna())
    print(f"   Statistique ADF : {result[0]:.4f}")
    print(f"   p-value         : {result[1]:.4f}")
    if result[1] < 0.05:
        print("   ✅ Série STATIONNAIRE (p < 0.05)")
    else:
        print("   ⚠️  Série NON-STATIONNAIRE → différenciation nécessaire")


# ═══════════════════════════════════════════════════════════════
# 3. HOLT-WINTERS (Triple Exponential Smoothing)
# ═══════════════════════════════════════════════════════════════

def run_holt_winters(train, test):
    print("\n" + "═"*60)
    print("📈 HOLT-WINTERS (Triple Exponential Smoothing)")
    print("═"*60)

    # Agréger en hebdomadaire pour Holt-Winters (plus stable)
    train_w = train["revenue"].resample("W").sum()
    test_w  = test["revenue"].resample("W").sum()

    model = ExponentialSmoothing(
        train_w,
        trend="add",
        seasonal="add",
        seasonal_periods=52,   # saisonnalité annuelle (52 semaines)
        damped_trend=True,
    )
    fit = model.fit(optimized=True, use_brute=True)

    forecast = fit.forecast(len(test_w))

    metrics = evaluate("Holt-Winters (hebdo)", test_w, forecast)

    # Plot
    fig, ax = plt.subplots(figsize=FIGSIZE)
    train_w.plot(ax=ax, label="Train", color="#2196F3", alpha=0.7)
    test_w.plot(ax=ax, label="Test réel", color="#4CAF50", linewidth=2)
    forecast.plot(ax=ax, label="Prévision HW", color="#FF5722",
                  linestyle="--", linewidth=2)
    ax.set_title("Holt-Winters — Revenue hebdomadaire", fontsize=14, fontweight="bold")
    ax.set_xlabel("Date")
    ax.set_ylabel("Revenue (€)")
    ax.legend()
    ax.grid(alpha=0.3)
    plt.tight_layout()
    plt.savefig("niveau1_holtwinters.png", dpi=120)
    plt.close()
    print("   💾 Graphique → niveau1_holtwinters.png")

    return metrics, fit


# ═══════════════════════════════════════════════════════════════
# 4. SARIMA
# ═══════════════════════════════════════════════════════════════

def run_sarima(train, test):
    print("\n" + "═"*60)
    print("📈 SARIMA (Seasonal ARIMA)")
    print("═"*60)
    print("   ⏳ Entraînement SARIMA... (peut prendre 2-5 min)")

    # Agrégation mensuelle pour SARIMA (plus rapide et stable)
    train_m = train["revenue"].resample("MS").sum()
    test_m  = test["revenue"].resample("MS").sum()

    # Paramètres SARIMA(1,1,1)(1,1,1)[12]
    # p,d,q = ordre ARIMA | P,D,Q,s = ordre saisonnier mensuel
    model = SARIMAX(
        train_m,
        order=(1, 1, 1),
        seasonal_order=(1, 1, 1, 12),
        enforce_stationarity=False,
        enforce_invertibility=False,
    )
    fit = model.fit(disp=False)
    print(f"   AIC : {fit.aic:.2f}")

    forecast = fit.forecast(len(test_m))
    forecast.index = test_m.index

    metrics = evaluate("SARIMA (mensuel)", test_m, forecast)

    # Plot
    fig, axes = plt.subplots(2, 1, figsize=(14, 9))

    # Graphique principal
    ax = axes[0]
    train_m.plot(ax=ax, label="Train", color="#2196F3", alpha=0.7)
    test_m.plot(ax=ax, label="Test réel", color="#4CAF50", linewidth=2)
    forecast.plot(ax=ax, label="Prévision SARIMA", color="#9C27B0",
                  linestyle="--", linewidth=2)
    # Intervalle de confiance
    pred_ci = fit.get_forecast(len(test_m)).conf_int()
    ax.fill_between(pred_ci.index,
                    pred_ci.iloc[:, 0], pred_ci.iloc[:, 1],
                    alpha=0.15, color="#9C27B0", label="IC 95%")
    ax.set_title("SARIMA — Revenue mensuel", fontsize=14, fontweight="bold")
    ax.legend()
    ax.grid(alpha=0.3)

    # Résidus
    ax2 = axes[1]
    residuals = fit.resid
    ax2.plot(residuals, color="#607D8B", alpha=0.7)
    ax2.axhline(0, color="red", linestyle="--")
    ax2.set_title("Résidus SARIMA")
    ax2.grid(alpha=0.3)

    plt.tight_layout()
    plt.savefig("niveau1_sarima.png", dpi=120)
    plt.close()
    print("   💾 Graphique → niveau1_sarima.png")

    return metrics, fit


# ═══════════════════════════════════════════════════════════════
# 5. MAIN
# ═══════════════════════════════════════════════════════════════

def main():
    print("╔══════════════════════════════════════════════════════════╗")
    print("║         NIVEAU 1 — BASELINE STATISTIQUE                 ║")
    print("╚══════════════════════════════════════════════════════════╝")

    df = load_daily_revenue()
    check_stationarity(df["revenue"])
    train, test = train_test_split(df)

    results = []
    metrics_hw, _  = run_holt_winters(train, test)
    metrics_sa, _  = run_sarima(train, test)

    results.extend([metrics_hw, metrics_sa])

    # Tableau comparatif
    print("\n" + "═"*50)
    print("📊 RÉSUMÉ NIVEAU 1")
    print("═"*50)
    df_res = pd.DataFrame(results)
    df_res = df_res.set_index("model")
    print(df_res.round(2).to_string())
    df_res.to_csv("niveau1_resultats.csv")
    print("\n✅ Résultats sauvegardés → niveau1_resultats.csv")
    print("→ Utiliser ces métriques comme baseline pour les niveaux 2 et 3")


if __name__ == "__main__":
    main()
