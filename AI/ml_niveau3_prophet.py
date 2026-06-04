"""
════════════════════════════════════════════════════════════════
NIVEAU 3 — DEEP / ADVANCED : Prophet + Comparaison Finale
════════════════════════════════════════════════════════════════
Objectif : Prophet avec gestion COVID + comparaison des 3 niveaux
"""

import warnings
warnings.filterwarnings("ignore")

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from sklearn.metrics import mean_absolute_error, mean_squared_error
from prophet import Prophet
from prophet.plot import plot_plotly, plot_components_plotly
from data_loader import load_daily_revenue
import joblib

# ═══════════════════════════════════════════════════════════════
# 1. CHARGEMENT
# ═══════════════════════════════════════════════════════════════

# ═══════════════════════════════════════════════════════════════
# 2. MÉTRIQUES
# ═══════════════════════════════════════════════════════════════

def mape(y_true, y_pred):
    y_true, y_pred = np.array(y_true), np.array(y_pred)
    mask = y_true != 0
    return np.mean(np.abs((y_true[mask] - y_pred[mask]) / y_true[mask])) * 100


def evaluate(name, y_true, y_pred):
    mae  = mean_absolute_error(y_true, y_pred)
    rmse = np.sqrt(mean_squared_error(y_true, y_pred))
    mape_val = mape(y_true, y_pred)
    print(f"\n📊 {name}")
    print(f"   MAE  : {mae:>14,.2f}")
    print(f"   RMSE : {rmse:>14,.2f}")
    print(f"   MAPE : {mape_val:>13.2f}%")
    return {"model": name, "MAE": mae, "RMSE": rmse, "MAPE": mape_val}


# ═══════════════════════════════════════════════════════════════
# 3. PROPHET
# ═══════════════════════════════════════════════════════════════

def build_covid_lockdowns():
    """Définit les périodes COVID comme 'holidays' pour Prophet."""
    lockdowns = pd.DataFrame({
        "holiday": "covid_lockdown",
        "ds": pd.to_datetime([
            "2020-03-01", "2020-04-01", "2020-05-01", "2020-06-01"
        ]),
        "lower_window": 0,
        "upper_window": 30,
    })
    return lockdowns


def build_special_events():
    """Fêtes et événements spéciaux."""
    events = []
    for year in range(2018, 2023):
        events += [
            {"holiday": "christmas",     "ds": f"{year}-12-25", "lower_window": -5, "upper_window": 1},
            {"holiday": "new_year",      "ds": f"{year}-01-01", "lower_window": -1, "upper_window": 1},
            {"holiday": "black_friday",  "ds": pd.Timestamp(f"{year}-11-01") + pd.offsets.Week(weekday=3) * 4,
             "lower_window": -1, "upper_window": 1},
        ]
    df_events = pd.DataFrame(events)
    df_events["ds"] = pd.to_datetime(df_events["ds"])
    return df_events


def run_prophet(df):
    print("\n" + "═"*60)
    print("🔮 PROPHET (Meta) — avec COVID + Saisonnalité")
    print("═"*60)

    # Format Prophet : colonnes ds (date) et y (valeur)
    df_prophet = df.reset_index().rename(columns={"date": "ds", "revenue": "y"})

    train = df_prophet[df_prophet["ds"].dt.year < 2022]
    test  = df_prophet[df_prophet["ds"].dt.year == 2022]

    # Combiner COVID + fêtes
    holidays = pd.concat([
        build_covid_lockdowns(),
        build_special_events()
    ], ignore_index=True)

    # Modèle Prophet
    model = Prophet(
        holidays=holidays,
        yearly_seasonality=True,
        weekly_seasonality=True,
        daily_seasonality=False,
        seasonality_mode="multiplicative",   # adapté aux données avec tendance
        changepoint_prior_scale=0.1,         # flexibilité de la tendance
        seasonality_prior_scale=10,
        holidays_prior_scale=10,
        interval_width=0.95,
    )

    # Ajouter saisonnalité mensuelle custom
    model.add_seasonality(
        name="monthly",
        period=30.5,
        fourier_order=5,
    )

    print("   ⏳ Entraînement Prophet...")
    model.fit(train)

    # Prévisions sur la période test
    future = model.make_future_dataframe(periods=len(test), freq="D")
    forecast = model.predict(future)

    # Récupérer uniquement les prévisions test
    forecast_test = forecast[forecast["ds"].dt.year == 2022].set_index("ds")
    y_test = test.set_index("ds")["y"]

    # Aligner les index
    common_idx = y_test.index.intersection(forecast_test.index)
    y_true_aligned = y_test.loc[common_idx]
    y_pred_aligned = forecast_test.loc[common_idx, "yhat"].clip(lower=0)

    metrics = evaluate("Prophet", y_true_aligned, y_pred_aligned)

    # ── Graphique 1 : Prévisions complètes ──
    fig1, ax = plt.subplots(figsize=(14, 6))
    ax.plot(df_prophet["ds"], df_prophet["y"],
            label="Historique", color="#2196F3", alpha=0.5, linewidth=1)
    ax.plot(forecast_test.index, y_pred_aligned,
            label="Prévision Prophet 2022", color="#E91E63", linewidth=2)
    ax.fill_between(
        forecast_test.index,
        forecast_test.loc[common_idx, "yhat_lower"].clip(lower=0),
        forecast_test.loc[common_idx, "yhat_upper"],
        alpha=0.2, color="#E91E63", label="IC 95%"
    )
    ax.plot(common_idx, y_true_aligned,
            label="Réel 2022", color="#4CAF50", linewidth=1.5)
    # Zone COVID
    ax.axvspan(pd.Timestamp("2020-03-01"), pd.Timestamp("2020-06-30"),
               alpha=0.1, color="red", label="COVID Q2 2020")
    ax.set_title("Prophet — Revenue journalier 2018-2022", fontsize=13, fontweight="bold")
    ax.legend(loc="upper left")
    ax.grid(alpha=0.3)
    ax.set_ylabel("Revenue (€)")
    plt.tight_layout()
    plt.savefig("niveau3_prophet_forecast.png", dpi=120)
    plt.close()
    print("   💾 Graphique → niveau3_prophet_forecast.png")

    # ── Graphique 2 : Composantes ──
    fig2 = model.plot_components(forecast)
    fig2.suptitle("Prophet — Décomposition : Tendance + Saisonnalités",
                  fontsize=13, fontweight="bold")
    plt.tight_layout()
    fig2.savefig("niveau3_prophet_components.png", dpi=120)
    plt.close()
    print("   💾 Composantes → niveau3_prophet_components.png")

    # Sauvegarde
    joblib.dump(model, "model_prophet.pkl")
    print("   💾 Modèle → model_prophet.pkl")

    return metrics, model, y_pred_aligned, common_idx


# ═══════════════════════════════════════════════════════════════
# 4. COMPARAISON FINALE DES 3 NIVEAUX
# ═══════════════════════════════════════════════════════════════

def final_comparison(metrics_prophet):
    """Charge les résultats des niveaux 1 et 2 et crée un tableau comparatif."""
    print("\n" + "═"*60)
    print("🏆 COMPARAISON FINALE — 3 NIVEAUX")
    print("═"*60)

    all_results = []

    # Niveau 1
    try:
        df1 = pd.read_csv("niveau1_resultats.csv", index_col="model")
        df1["niveau"] = "Niveau 1 - Statistique"
        all_results.append(df1)
        print("   ✅ Niveau 1 chargé")
    except FileNotFoundError:
        print("   ⚠️  niveau1_resultats.csv non trouvé — lancer ml_niveau1_baseline.py d'abord")

    # Niveau 2
    try:
        df2 = pd.read_csv("niveau2_resultats.csv", index_col="model")
        df2["niveau"] = "Niveau 2 - ML Classique"
        all_results.append(df2)
        print("   ✅ Niveau 2 chargé")
    except FileNotFoundError:
        print("   ⚠️  niveau2_resultats.csv non trouvé — lancer ml_niveau2_ml_classique.py d'abord")

    # Niveau 3 (Prophet)
    df3 = pd.DataFrame([metrics_prophet]).set_index("model")
    df3["niveau"] = "Niveau 3 - Advanced"
    all_results.append(df3)

    if not all_results:
        print("   ❌ Aucun résultat à comparer")
        return

    df_all = pd.concat(all_results)
    df_all = df_all.sort_values("MAPE")

    print("\n" + df_all[["niveau", "MAE", "RMSE", "MAPE"]].round(2).to_string())
    df_all.to_csv("comparaison_finale.csv")

    # ── Graphique comparatif ──
    fig, axes = plt.subplots(1, 3, figsize=(15, 6))
    colors = plt.cm.Set2(np.linspace(0, 1, len(df_all)))

    for ax, metric in zip(axes, ["MAE", "RMSE", "MAPE"]):
        bars = ax.bar(df_all.index, df_all[metric], color=colors)
        ax.set_title(metric, fontsize=13, fontweight="bold")
        ax.set_ylabel(metric + (" (%)" if metric == "MAPE" else " (€)"))
        ax.tick_params(axis="x", rotation=45)
        ax.grid(alpha=0.3, axis="y")
        # Annoter les valeurs
        for bar, val in zip(bars, df_all[metric]):
            ax.text(bar.get_x() + bar.get_width() / 2,
                    bar.get_height() * 1.01,
                    f"{val:.1f}", ha="center", va="bottom", fontsize=9)

    plt.suptitle("Comparaison Finale — Tous les Modèles",
                 fontsize=15, fontweight="bold")
    plt.tight_layout()
    plt.savefig("comparaison_finale.png", dpi=120)
    plt.close()
    print("\n   💾 Graphique → comparaison_finale.png")

    best = df_all["MAPE"].idxmin()
    print(f"\n🥇 Meilleur modèle global : {best}")
    print(f"   MAPE : {df_all.loc[best, 'MAPE']:.2f}%")
    print(f"   MAE  : {df_all.loc[best, 'MAE']:,.2f}")
    print(f"   RMSE : {df_all.loc[best, 'RMSE']:,.2f}")

    return df_all


# ═══════════════════════════════════════════════════════════════
# 5. FORECAST FUTUR (2023)
# ═══════════════════════════════════════════════════════════════

def forecast_2023(model_prophet, df):
    """Prévision pour 2023 avec le meilleur modèle (Prophet)."""
    print("\n" + "═"*60)
    print("🔭 PRÉVISION 2023 avec Prophet")
    print("═"*60)

    future = model_prophet.make_future_dataframe(
        periods=365, freq="D", include_history=False
    )
    forecast = model_prophet.predict(future)
    forecast_2023 = forecast[forecast["ds"].dt.year == 2023]

    # Agrégation mensuelle
    forecast_2023_m = forecast_2023.set_index("ds").resample("MS").sum()

    fig, ax = plt.subplots(figsize=(12, 5))
    ax.bar(forecast_2023_m.index,
           forecast_2023_m["yhat"].clip(lower=0),
           color="#E91E63", alpha=0.7, label="Prévision 2023")
    ax.fill_between(
        forecast_2023_m.index,
        forecast_2023_m["yhat_lower"].clip(lower=0),
        forecast_2023_m["yhat_upper"],
        alpha=0.2, color="#E91E63", label="IC 95%"
    )
    ax.set_title("Prévision Revenue mensuel — 2023", fontsize=13, fontweight="bold")
    ax.set_ylabel("Revenue (€)")
    ax.legend()
    ax.grid(alpha=0.3)
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig("niveau3_forecast_2023.png", dpi=120)
    plt.close()

    print("   Prévisions mensuelles 2023 :")
    for _, row in forecast_2023_m.iterrows():
        print(f"   {row.name.strftime('%B %Y')} : {row['yhat']:>12,.0f} €"
              f"  [IC: {row['yhat_lower']:,.0f} – {row['yhat_upper']:,.0f}]")
    print("   💾 Graphique → niveau3_forecast_2023.png")


# ═══════════════════════════════════════════════════════════════
# 6. MAIN
# ═══════════════════════════════════════════════════════════════

def main():
    print("╔══════════════════════════════════════════════════════════╗")
    print("║   NIVEAU 3 — ADVANCED : Prophet + Comparaison Finale    ║")
    print("╚══════════════════════════════════════════════════════════╝")

    df = load_daily_revenue()

    # Prophet
    metrics_prophet, model_prophet, pred, idx = run_prophet(df)

    # Comparaison finale
    df_comparison = final_comparison(metrics_prophet)

    # Forecast 2023
    forecast_2023(model_prophet, df)

    print("\n" + "═"*60)
    print("✅ PIPELINE COMPLET TERMINÉ")
    print("═"*60)
    print("   Fichiers générés :")
    print("   📊 niveau3_prophet_forecast.png")
    print("   📊 niveau3_prophet_components.png")
    print("   📊 niveau3_forecast_2023.png")
    print("   📊 comparaison_finale.png")
    print("   📄 comparaison_finale.csv")
    print("   🤖 model_prophet.pkl")
    print("\n   Pour utiliser le meilleur modèle en production :")
    print("   → Charger model_lightgbm.txt ou model_prophet.pkl")
    print("   → Générer les features avec create_features()")
    print("   → model.predict(X_new)")


if __name__ == "__main__":
    main()
