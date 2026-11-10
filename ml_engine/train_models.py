"""
Machine Learning Training & Evaluation Pipeline
AI/ML-Powered Mining Safety and Worker Evacuation System

Trains, evaluates, and serializes 4 separate models:
1. Open-Pit: Slope Instability Model (XGBoost Classifier)
2. Open-Pit: Rockfall Risk Model (Random Forest Classifier)
3. Underground: Toxic Gas Risk Model (XGBoost Classifier)
4. Underground: Fire Hazard Risk Model (Random Forest Classifier)

Evaluates performance using Accuracy, Precision, Recall, and F1-score.
Generates confusion matrices, feature importance graphs, and comparison visualizations.
"""
import os
import json
import joblib
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    confusion_matrix,
    classification_report,
)
from sklearn.preprocessing import LabelEncoder
from xgboost import XGBClassifier

from ml_engine.data_generation import generate_and_save_all_datasets, RISK_TIERS

# Output directories
REPORTS_DIR = "ml_engine/reports"
MODELS_DIR = "ml_engine/saved_models"
os.makedirs(REPORTS_DIR, exist_ok=True)
os.makedirs(MODELS_DIR, exist_ok=True)


def plot_confusion_matrix(cm, classes, title, filename):
    """Generates and saves a clean confusion matrix heatmap using Matplotlib."""
    plt.figure(figsize=(7, 6))
    plt.imshow(cm, interpolation="nearest", cmap=plt.cm.Blues)
    plt.title(title, fontsize=12, fontweight="bold", pad=12)
    plt.colorbar()
    tick_marks = np.arange(len(classes))
    plt.xticks(tick_marks, classes, rotation=45, fontsize=10)
    plt.yticks(tick_marks, classes, fontsize=10)

    # Text annotations inside cells
    thresh = cm.max() / 2.0
    for i in range(cm.shape[0]):
        for j in range(cm.shape[1]):
            plt.text(
                j,
                i,
                f"{cm[i, j]:d}",
                horizontalalignment="center",
                color="white" if cm[i, j] > thresh else "black",
                fontsize=11,
                fontweight="bold",
            )

    plt.ylabel("True Label", fontsize=11, fontweight="semibold")
    plt.xlabel("Predicted Label", fontsize=11, fontweight="semibold")
    plt.tight_layout()
    plt.savefig(os.path.join(REPORTS_DIR, filename), dpi=200)
    plt.close()


def plot_feature_importance(importances, feature_names, title, filename, color="#2563eb"):
    """Generates and saves a horizontal bar chart of feature importances."""
    plt.figure(figsize=(8, 4.5))
    indices = np.argsort(importances)
    plt.barh(range(len(indices)), [importances[i] for i in indices], color=color, align="center", edgecolor="#1e3a8a")
    plt.yticks(range(len(indices)), [feature_names[i] for i in indices], fontsize=10)
    plt.xlabel("Relative Importance Score", fontsize=10, fontweight="semibold")
    plt.title(title, fontsize=12, fontweight="bold", pad=12)
    plt.grid(axis="x", linestyle="--", alpha=0.5)
    plt.tight_layout()
    plt.savefig(os.path.join(REPORTS_DIR, filename), dpi=200)
    plt.close()


def train_and_evaluate_all():
    print("=" * 60)
    print("AI/ML MINING SAFETY: MODEL TRAINING & BENCHMARKING")
    print("=" * 60)

    # 1. Dataset Generation
    df_op, df_ug = generate_and_save_all_datasets()

    # 2. Setup Label Encoder for 5 standard risk tiers
    label_encoder = LabelEncoder()
    label_encoder.fit(RISK_TIERS)  # ['Critical', 'High', 'Low', 'Medium', 'Safe'] in alphabet order
    joblib.dump(label_encoder, os.path.join(MODELS_DIR, "label_encoder.joblib"))

    metrics_summary = {}

    # ---------------------------------------------------------
    # MODEL 1: Open-Pit Slope Instability (XGBoost)
    # ---------------------------------------------------------
    print("\n--- Training Model 1: Open-Pit Slope Instability (XGBoost) ---")
    op_features = [
        "rainfall_intensity",
        "ground_vibration",
        "slope_displacement",
        "crack_expansion",
        "soil_moisture",
        "displacement_rate",
    ]
    X_op = df_op[op_features]
    y_slope = label_encoder.transform(df_op["slope_risk"])

    X_train_s, X_test_s, y_train_s, y_test_s = train_test_split(
        X_op, y_slope, test_size=0.20, random_state=42, stratify=y_slope
    )

    model_slope = XGBClassifier(
        n_estimators=120,
        max_depth=5,
        learning_rate=0.08,
        subsample=0.85,
        colsample_bytree=0.85,
        random_state=42,
        eval_metric="mlogloss",
    )
    model_slope.fit(X_train_s, y_train_s)
    y_pred_s = model_slope.predict(X_test_s)

    acc_s = accuracy_score(y_test_s, y_pred_s)
    prec_s = precision_score(y_test_s, y_pred_s, average="weighted")
    rec_s = recall_score(y_test_s, y_pred_s, average="weighted")
    f1_s = f1_score(y_test_s, y_pred_s, average="weighted")

    print(f"Slope Instability Model -> Accuracy: {acc_s:.4f}, Precision: {prec_s:.4f}, Recall: {rec_s:.4f}, F1: {f1_s:.4f}")
    metrics_summary["slope_instability"] = {
        "model_type": "XGBoost Classifier",
        "sector": "open_pit",
        "target": "slope_instability",
        "accuracy": round(float(acc_s), 4),
        "precision": round(float(prec_s), 4),
        "recall": round(float(rec_s), 4),
        "f1_score": round(float(f1_s), 4),
    }

    joblib.dump(model_slope, os.path.join(MODELS_DIR, "slope_instability_model.joblib"))
    cm_s = confusion_matrix(y_test_s, y_pred_s)
    plot_confusion_matrix(cm_s, label_encoder.classes_, "Confusion Matrix: Open-Pit Slope Instability", "confusion_matrix_slope.png")
    plot_feature_importance(model_slope.feature_importances_, op_features, "Feature Importance: Slope Instability", "feature_importance_slope.png", color="#059669")

    # ---------------------------------------------------------
    # MODEL 2: Open-Pit Rockfall Risk (Random Forest)
    # ---------------------------------------------------------
    print("\n--- Training Model 2: Open-Pit Rockfall Risk (Random Forest) ---")
    y_rock = label_encoder.transform(df_op["rockfall_risk"])

    X_train_r, X_test_r, y_train_r, y_test_r = train_test_split(
        X_op, y_rock, test_size=0.20, random_state=42, stratify=y_rock
    )

    model_rock = RandomForestClassifier(
        n_estimators=150,
        max_depth=8,
        min_samples_split=4,
        random_state=42,
        n_jobs=-1,
    )
    model_rock.fit(X_train_r, y_train_r)
    y_pred_r = model_rock.predict(X_test_r)

    acc_r = accuracy_score(y_test_r, y_pred_r)
    prec_r = precision_score(y_test_r, y_pred_r, average="weighted")
    rec_r = recall_score(y_test_r, y_pred_r, average="weighted")
    f1_r = f1_score(y_test_r, y_pred_r, average="weighted")

    print(f"Rockfall Risk Model -> Accuracy: {acc_r:.4f}, Precision: {prec_r:.4f}, Recall: {rec_r:.4f}, F1: {f1_r:.4f}")
    metrics_summary["rockfall_risk"] = {
        "model_type": "Random Forest Classifier",
        "sector": "open_pit",
        "target": "rockfall_risk",
        "accuracy": round(float(acc_r), 4),
        "precision": round(float(prec_r), 4),
        "recall": round(float(rec_r), 4),
        "f1_score": round(float(f1_r), 4),
    }

    joblib.dump(model_rock, os.path.join(MODELS_DIR, "rockfall_risk_model.joblib"))
    cm_r = confusion_matrix(y_test_r, y_pred_r)
    plot_confusion_matrix(cm_r, label_encoder.classes_, "Confusion Matrix: Open-Pit Rockfall Risk", "confusion_matrix_rockfall.png")
    plot_feature_importance(model_rock.feature_importances_, op_features, "Feature Importance: Rockfall Risk", "feature_importance_rockfall.png", color="#d97706")

    # ---------------------------------------------------------
    # MODEL 3: Underground Toxic Gas Hazard (XGBoost)
    # ---------------------------------------------------------
    print("\n--- Training Model 3: Underground Toxic Gas Risk (XGBoost) ---")
    ug_features = [
        "methane_ch4",
        "carbon_monoxide_co",
        "oxygen_o2",
        "temperature",
        "smoke_density",
        "ventilation_velocity",
    ]
    X_ug = df_ug[ug_features]
    y_gas = label_encoder.transform(df_ug["gas_risk"])

    X_train_g, X_test_g, y_train_g, y_test_g = train_test_split(
        X_ug, y_gas, test_size=0.20, random_state=42, stratify=y_gas
    )

    model_gas = XGBClassifier(
        n_estimators=120,
        max_depth=5,
        learning_rate=0.08,
        subsample=0.85,
        colsample_bytree=0.85,
        random_state=42,
        eval_metric="mlogloss",
    )
    model_gas.fit(X_train_g, y_train_g)
    y_pred_g = model_gas.predict(X_test_g)

    acc_g = accuracy_score(y_test_g, y_pred_g)
    prec_g = precision_score(y_test_g, y_pred_g, average="weighted")
    rec_g = recall_score(y_test_g, y_pred_g, average="weighted")
    f1_g = f1_score(y_test_g, y_pred_g, average="weighted")

    print(f"Toxic Gas Model -> Accuracy: {acc_g:.4f}, Precision: {prec_g:.4f}, Recall: {rec_g:.4f}, F1: {f1_g:.4f}")
    metrics_summary["toxic_gas"] = {
        "model_type": "XGBoost Classifier",
        "sector": "underground",
        "target": "toxic_gas_risk",
        "accuracy": round(float(acc_g), 4),
        "precision": round(float(prec_g), 4),
        "recall": round(float(rec_g), 4),
        "f1_score": round(float(f1_g), 4),
    }

    joblib.dump(model_gas, os.path.join(MODELS_DIR, "toxic_gas_model.joblib"))
    cm_g = confusion_matrix(y_test_g, y_pred_g)
    plot_confusion_matrix(cm_g, label_encoder.classes_, "Confusion Matrix: Underground Toxic Gas", "confusion_matrix_toxic_gas.png")
    plot_feature_importance(model_gas.feature_importances_, ug_features, "Feature Importance: Toxic Gas Risk", "feature_importance_toxic_gas.png", color="#2563eb")

    # ---------------------------------------------------------
    # MODEL 4: Underground Fire Hazard (Random Forest)
    # ---------------------------------------------------------
    print("\n--- Training Model 4: Underground Fire Hazard (Random Forest) ---")
    y_fire = label_encoder.transform(df_ug["fire_risk"])

    X_train_f, X_test_f, y_train_f, y_test_f = train_test_split(
        X_ug, y_fire, test_size=0.20, random_state=42, stratify=y_fire
    )

    model_fire = RandomForestClassifier(
        n_estimators=150,
        max_depth=8,
        min_samples_split=4,
        random_state=42,
        n_jobs=-1,
    )
    model_fire.fit(X_train_f, y_train_f)
    y_pred_f = model_fire.predict(X_test_f)

    acc_f = accuracy_score(y_test_f, y_pred_f)
    prec_f = precision_score(y_test_f, y_pred_f, average="weighted")
    rec_f = recall_score(y_test_f, y_pred_f, average="weighted")
    f1_f = f1_score(y_test_f, y_pred_f, average="weighted")

    print(f"Fire Hazard Model -> Accuracy: {acc_f:.4f}, Precision: {prec_f:.4f}, Recall: {rec_f:.4f}, F1: {f1_f:.4f}")
    metrics_summary["fire_hazard"] = {
        "model_type": "Random Forest Classifier",
        "sector": "underground",
        "target": "fire_hazard_risk",
        "accuracy": round(float(acc_f), 4),
        "precision": round(float(prec_f), 4),
        "recall": round(float(rec_f), 4),
        "f1_score": round(float(f1_f), 4),
    }

    joblib.dump(model_fire, os.path.join(MODELS_DIR, "fire_hazard_model.joblib"))
    cm_f = confusion_matrix(y_test_f, y_pred_f)
    plot_confusion_matrix(cm_f, label_encoder.classes_, "Confusion Matrix: Underground Fire Hazard", "confusion_matrix_fire_hazard.png")
    plot_feature_importance(model_fire.feature_importances_, ug_features, "Feature Importance: Fire Hazard Risk", "feature_importance_fire_hazard.png", color="#dc2626")

    # ---------------------------------------------------------
    # OVERALL COMPARISON VISUALIZATIONS
    # ---------------------------------------------------------
    # 1. Model Accuracy Comparison Bar Chart
    plt.figure(figsize=(9, 4.5))
    models = ["Slope Instability\n(XGBoost)", "Rockfall Risk\n(Random Forest)", "Toxic Gas\n(XGBoost)", "Fire Hazard\n(Random Forest)"]
    accuracies = [acc_s * 100, acc_r * 100, acc_g * 100, acc_f * 100]
    colors = ["#059669", "#d97706", "#2563eb", "#dc2626"]
    bars = plt.bar(models, accuracies, color=colors, width=0.55, edgecolor="#1e293b", linewidth=1.2)
    plt.ylabel("Test Accuracy (%)", fontsize=11, fontweight="semibold")
    plt.title("Comparative Performance of Mining Safety ML Models", fontsize=12, fontweight="bold", pad=12)
    plt.ylim([80, 100])
    plt.grid(axis="y", linestyle="--", alpha=0.4)

    for bar in bars:
        yval = bar.get_height()
        plt.text(bar.get_x() + bar.get_width() / 2.0, yval + 0.6, f"{yval:.2f}%", ha="center", va="bottom", fontsize=10, fontweight="bold")

    plt.tight_layout()
    plt.savefig(os.path.join(REPORTS_DIR, "model_accuracy_comparison.png"), dpi=200)
    plt.close()

    # 2. Save Metrics Summary JSON
    with open(os.path.join(REPORTS_DIR, "evaluation_metrics.json"), "w") as f:
        json.dump(metrics_summary, f, indent=2)

    print("\n" + "=" * 60)
    print(f"All 4 models trained, evaluated, and saved to {MODELS_DIR}/")
    print(f"All visualization reports saved to {REPORTS_DIR}/")
    print("=" * 60)

    return metrics_summary


if __name__ == "__main__":
    train_and_evaluate_all()
