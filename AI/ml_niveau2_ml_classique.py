"""
════════════════════════════════════════════════════════════════
NIVEAU 2 — ML CLASSIQUE : XGBoost + LightGBM
════════════════════════════════════════════════════════════════
Objectif : battre la baseline avec du feature engineering riche
"""

import warnings
warnings.filterwarnings("ignore")

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.preprocessing import StandardScaler
import lightgbm as lgb
import xgboost as xgb
from data_loader import load_daily_enriched_data
import joblib

# ═══════════════════════════════════════════════════════════════
# 1. CHARGEMENT
# ═══════════════════════════════════════════════════════════════

# ═══════════════════════════════════════════════════════════════
# 2. FEATURE ENGINEERING
# ═══════════════════════════════════════════════════════════════

def create_features(df):
    """Crée toutes les features temporelles et lag pour ML."""
    print("\n⚙️  Feature Engineering...")
    df = df.copy()
    idx = df.index

    # ── Features temporelles ──
    df["year"]         = idx.year
    df["month"]        = idx.month
    df["day"]          = idx.day
    df["dayofweek"]    = idx.dayofweek          # 0=Lundi
    df["dayofyear"]    = idx.dayofyear
    df["weekofyear"]   = idx.isocalendar().week.astype(int)
    df["quarter"]      = idx.quarter
    df["is_weekend"]   = (idx.dayofweek >= 5).astype(int)
    df["is_month_end"] = idx.is_month_end.astype(int)
    df["is_month_start"] = idx.is_month_start.astype(int)

    # ── Encodage cyclique (sin/cos) pour mois et jour ──
    df["month_sin"]  = np.sin(2 * np.pi * df["month"] / 12)
    df["month_cos"]  = np.cos(2 * np.pi * df["month"] / 12)
    df["dow_sin"]    = np.sin(2 * np.pi * df["dayofweek"] / 7)
    df["dow_cos"]    = np.cos(2 * np.pi * df["dayofweek"] / 7)

    # ── Flags spéciaux ──
    df["is_december"]    = (df["month"] == 12).astype(int)
    df["is_summer"]      = df["month"].isin([6, 7, 8]).astype(int)
    df["is_blackfriday"] = (
        (df["month"] == 11) & (df["dayofweek"] == 4) &
        (df["day"] >= 22) & (df["day"] <= 28)
    ).astype(int)

    # ── Flag COVID ──
    df["covid_flag"] = (
        (df["year"] == 2020) &
        (df["month"].isin([3, 4, 5, 6]))
    ).astype(int)

    # ── Lag features (valeurs passées du revenue) ──
    for lag in [1, 2, 3, 7, 14, 21, 28, 30, 90, 365]:
        df[f"lag_{lag}"] = df["revenue"].shift(lag)

    # ── Rolling statistics ──
    for window in [7, 14, 30, 90]:
        df[f"rolling_mean_{window}"] = df["revenue"].shift(1).rolling(window).mean()
        df[f"rolling_std_{window}"]  = df["revenue"].shift(1).rolling(window).std()
        df[f"rolling_max_{window}"]  = df["revenue"].shift(1).rolling(window).max()
        df[f"rolling_min_{window}"]  = df["revenue"].shift(1).rolling(window).min()

    # ── Ratio / tendance ──
    df["mom_change"]  = df["revenue"].pct_change(30)   # variation mois/mois
    df["wow_change"]  = df["revenue"].pct_change(7)    # variation semaine/semaine
    df["yoy_change"]  = df["revenue"].pct_change(365)  # variation année/année

    # Tendance linéaire (numéro du jour depuis le début)
    df["trend"] = np.arange(len(df))

    feature_cols = [c for c in df.columns if c != "revenue"]
    print(f"   → {len(feature_cols)} features créées")
    return df, feature_cols


# ═══════════════════════════════════════════════════════════════
# 3. SPLIT ET NETTOYAGE
# ═══════════════════════════════════════════════════════════════

def prepare_sets(df, feature_cols):
    # Supprimer les lignes avec NaN (dues aux lags)
    df_clean = df.dropna()
    print(f"   Lignes après suppression NaN : {len(df_clean):,}")

    train = df_clean[df_clean.index.year < 2022]
    test  = df_clean[df_clean.index.year == 2022]

    X_train = train[feature_cols]
    y_train = train["revenue"]
    X_test  = test[feature_cols]
    y_test  = test["revenue"]

    print(f"   Train : {len(X_train):,} | Test : {len(X_test):,}")
    return X_train, y_train, X_test, y_test


# ═══════════════════════════════════════════════════════════════
# 4. MÉTRIQUES
# ═══════════════════════════════════════════════════════════════

def mape(y_true, y_pred):
    y_true, y_pred = np.array(y_true), np.array(y_pred)
    mask = y_true != 0
    return np.mean(np.abs((y_true[mask] - y_pred[mask]) / y_true[mask])) * 100


def evaluate(name, y_true, y_pred):
    mae  = mean_absolute_error(y_true, y_pred)
    rmse = np.sqrt(mean_squared_error(y_true, y_pred))
    r2   = r2_score(y_true, y_pred)
    mape_val = mape(y_true, y_pred)
    print(f"\n📊 {name}")
    print(f"   MAE  : {mae:>14,.2f}")
    print(f"   RMSE : {rmse:>14,.2f}")
    print(f"   R2   : {r2:>14.4f}")
    print(f"   MAPE : {mape_val:>13.2f}%")
    return {"model": name, "MAE": mae, "RMSE": rmse, "R2": r2, "MAPE": mape_val}


# ═══════════════════════════════════════════════════════════════
# 5. XGBOOST
# ═══════════════════════════════════════════════════════════════

def run_xgboost(X_train, y_train, X_test, y_test):
    print("\n" + "═"*60)
    print("🚀 XGBOOST")
    print("═"*60)

    model = xgb.XGBRegressor(
        n_estimators=500,
        learning_rate=0.05,
        max_depth=6,
        subsample=0.8,
        colsample_bytree=0.8,
        reg_alpha=0.1,
        reg_lambda=1.0,
        random_state=42,
        early_stopping_rounds=30,
        eval_metric="rmse",
        verbosity=0,
    )

    model.fit(
        X_train, y_train,
        eval_set=[(X_test, y_test)],
        verbose=False,
    )

    pred = model.predict(X_test)
    metrics = evaluate("XGBoost", y_test, pred)

    # Feature importance
    fi = pd.Series(model.feature_importances_, index=X_train.columns)
    fi = fi.sort_values(ascending=False).head(20)

    # Sauvegarde
    joblib.dump(model, "model_xgboost.pkl")
    print("   💾 Modèle → model_xgboost.pkl")

    return metrics, model, pred, fi


# ═══════════════════════════════════════════════════════════════
# 6. LIGHTGBM
# ═══════════════════════════════════════════════════════════════

def run_lightgbm(X_train, y_train, X_test, y_test):
    print("\n" + "═"*60)
    print("⚡ LIGHTGBM")
    print("═"*60)

    train_data = lgb.Dataset(X_train, label=y_train)
    val_data   = lgb.Dataset(X_test,  label=y_test, reference=train_data)

    params = {
        "objective":        "regression",
        "metric":           "rmse",
        "learning_rate":    0.05,
        "num_leaves":       63,
        "max_depth":        -1,
        "feature_fraction": 0.8,
        "bagging_fraction": 0.8,
        "bagging_freq":     5,
        "reg_alpha":        0.1,
        "reg_lambda":       1.0,
        "min_child_samples": 20,
        "verbose":          -1,
        "seed":             42,
    }

    callbacks = [
        lgb.early_stopping(stopping_rounds=30, verbose=False),
        lgb.log_evaluation(period=-1),
    ]

    model = lgb.train(
        params,
        train_data,
        num_boost_round=500,
        valid_sets=[val_data],
        callbacks=callbacks,
    )

    pred = model.predict(X_test)
    metrics = evaluate("LightGBM", y_test, pred)

    # Feature importance
    fi = pd.Series(
        model.feature_importance(importance_type="gain"),
        index=model.feature_name()
    ).sort_values(ascending=False).head(20)

    # Sauvegarde
    model.save_model("model_lightgbm.txt")
    print("   💾 Modèle → model_lightgbm.txt")

    return metrics, model, pred, fi


# ═══════════════════════════════════════════════════════════════
# 7. VISUALISATIONS
# ═══════════════════════════════════════════════════════════════

def plot_results(y_test, pred_xgb, pred_lgb, fi_xgb, fi_lgb):
    fig = plt.figure(figsize=(16, 12))
    gs = gridspec.GridSpec(3, 2, figure=fig)

    # ── Prévisions XGBoost ──
    ax1 = fig.add_subplot(gs[0, :])
    ax1.plot(y_test.index, y_test.values, label="Réel", color="#2196F3", linewidth=1.5)
    ax1.plot(y_test.index, pred_xgb, label="XGBoost", color="#FF9800",
             linestyle="--", alpha=0.85)
    ax1.plot(y_test.index, pred_lgb, label="LightGBM", color="#9C27B0",
             linestyle="-.", alpha=0.85)
    ax1.set_title("Prévisions vs Réel — 2022 (Test Set)", fontsize=13, fontweight="bold")
    ax1.legend()
    ax1.grid(alpha=0.3)
    ax1.set_ylabel("Revenue (€)")

    # ── Erreurs XGBoost ──
    ax2 = fig.add_subplot(gs[1, 0])
    err_xgb = y_test.values - pred_xgb
    ax2.plot(y_test.index, err_xgb, color="#FF9800", alpha=0.7)
    ax2.axhline(0, color="red", linestyle="--")
    ax2.set_title("Résidus XGBoost")
    ax2.grid(alpha=0.3)

    # ── Erreurs LightGBM ──
    ax3 = fig.add_subplot(gs[1, 1])
    err_lgb = y_test.values - pred_lgb
    ax3.plot(y_test.index, err_lgb, color="#9C27B0", alpha=0.7)
    ax3.axhline(0, color="red", linestyle="--")
    ax3.set_title("Résidus LightGBM")
    ax3.grid(alpha=0.3)

    # ── Feature Importance XGBoost ──
    ax4 = fig.add_subplot(gs[2, 0])
    fi_xgb.plot(kind="barh", ax=ax4, color="#FF9800")
    ax4.set_title("Top 20 Features — XGBoost")
    ax4.invert_yaxis()

    # ── Feature Importance LightGBM ──
    ax5 = fig.add_subplot(gs[2, 1])
    fi_lgb.plot(kind="barh", ax=ax5, color="#9C27B0")
    ax5.set_title("Top 20 Features — LightGBM")
    ax5.invert_yaxis()

    plt.suptitle("NIVEAU 2 — ML Classique : XGBoost vs LightGBM",
                 fontsize=15, fontweight="bold", y=1.01)
    plt.tight_layout()
    plt.savefig("niveau2_ml_classique.png", dpi=120, bbox_inches="tight")
    plt.close()
    print("\n   💾 Graphique → niveau2_ml_classique.png")


def plot_monthly_comparison(y_test, pred_xgb, pred_lgb):
    """Comparaison mensuelle agrégée."""
    df_cmp = pd.DataFrame({
        "reel":    y_test,
        "xgboost": pred_xgb,
        "lightgbm": pred_lgb,
    }, index=y_test.index)

    df_m = df_cmp.resample("MS").sum()

    fig, ax = plt.subplots(figsize=(12, 5))
    x = np.arange(len(df_m))
    w = 0.25
    ax.bar(x - w, df_m["reel"],      width=w, label="Réel",      color="#2196F3")
    ax.bar(x,     df_m["xgboost"],   width=w, label="XGBoost",   color="#FF9800")
    ax.bar(x + w, df_m["lightgbm"],  width=w, label="LightGBM",  color="#9C27B0")
    ax.set_xticks(x)
    ax.set_xticklabels([d.strftime("%b %Y") for d in df_m.index], rotation=45)
    ax.set_title("Revenue mensuel agrégé — 2022", fontsize=13, fontweight="bold")
    ax.set_ylabel("Revenue (€)")
    ax.legend()
    ax.grid(alpha=0.3, axis="y")
    plt.tight_layout()
    plt.savefig("niveau2_mensuel.png", dpi=120)
    plt.close()
    print("   💾 Graphique → niveau2_mensuel.png")


# ═══════════════════════════════════════════════════════════════
# 8. MAIN
# ═══════════════════════════════════════════════════════════════

def main():
    print("╔══════════════════════════════════════════════════════════╗")
    print("║      NIVEAU 2 — ML CLASSIQUE : XGBoost + LightGBM       ║")
    print("╚══════════════════════════════════════════════════════════╝")

    df = load_daily_enriched_data()
    df, feature_cols = create_features(df)
    X_train, y_train, X_test, y_test = prepare_sets(df, feature_cols)

    metrics_xgb, _, pred_xgb, fi_xgb = run_xgboost(X_train, y_train, X_test, y_test)
    metrics_lgb, _, pred_lgb, fi_lgb = run_lightgbm(X_train, y_train, X_test, y_test)

    plot_results(y_test, pred_xgb, pred_lgb, fi_xgb, fi_lgb)
    plot_monthly_comparison(y_test, pred_xgb, pred_lgb)

    # Résumé
    print("\n" + "═"*55)
    print("📊 RÉSUMÉ NIVEAU 2")
    print("═"*55)
    results = pd.DataFrame([metrics_xgb, metrics_lgb]).set_index("model")
    print(results.round(2).to_string())
    results.to_csv("niveau2_resultats.csv")

    best = results["MAPE"].idxmin()
    print(f"\n🏆 Meilleur modèle Niveau 2 : {best}")
    print(f"   MAPE : {results.loc[best, 'MAPE']:.2f}%")
    print("\n→ Comparer avec Niveau 1 (niveau1_resultats.csv)")


if __name__ == "__main__":
    main()
