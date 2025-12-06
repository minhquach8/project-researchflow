"""
COMPLETE MACHINE LEARNING PIPELINE (English Comments)
- Data loading
- Exploratory Data Analysis (EDA)
- Preprocessing
- Train/Test split
- Model training (Random Forest + XGBoost)
- Full evaluation with prints and figures
- Save best model, scaler, label encoders
- Inference function ready to use

Author: Grok 4 (xAI)
Date  : December 06, 2025
"""

import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import joblib

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    classification_report,
    confusion_matrix,
    roc_auc_score,
)
import xgboost as xgb

# ========================================================
# 1. CONFIGURATION
# ========================================================
DATA_PATH = "data/your_dataset.csv"  # Change this to your CSV file path
MODEL_DIR = "models"
FIGURE_DIR = "figures"
RANDOM_STATE = 42
TEST_SIZE = 0.2

# Create necessary folders
os.makedirs(MODEL_DIR, exist_ok=True)
os.makedirs(FIGURE_DIR, exist_ok=True)

print("=" * 60)
print("STARTING FULL ML PIPELINE")
print("=" * 60)

# ========================================================
# 2. LOAD DATA
# ========================================================
print(f"\nLoading data from: {DATA_PATH}")
if not os.path.exists(DATA_PATH):
    raise FileNotFoundError(f"File not found: {DATA_PATH}")

df = pd.read_csv(DATA_PATH)
print(f"Dataset shape: {df.shape}")
print(f"\nFirst 5 rows:")
print(df.head())

print(f"\nDataset info:")
print(df.info())

print(f"\nMissing values per column:")
print(df.isnull().sum())

# ========================================================
# 3. EXPLORATORY DATA ANALYSIS (EDA) - Save figures
# ========================================================
print(f"\nGenerating EDA plots...")

# Target distribution (assume last column is target)
target_col = df.columns[-1]
print(f"\nTarget column detected: '{target_col}'")

plt.figure(figsize=(8, 5))
sns.countplot(data=df, x=target_col, palette="viridis")
plt.title(f"Target Distribution - {target_col}")
plt.xlabel(target_col)
plt.ylabel("Count")
plt.tight_layout()
plt.savefig(os.path.join(FIGURE_DIR, "target_distribution.png"), dpi=300)
plt.close()
print("Saved: target_distribution.png")

# Correlation heatmap (only numeric columns)
numeric_df = df.select_dtypes(include=[np.number])
if len(numeric_df.columns) > 1:
    plt.figure(figsize=(12, 10))
    corr = numeric_df.corr()
    sns.heatmap(corr, annot=True, cmap="coolwarm", fmt=".2f", linewidths=0.5)
    plt.title("Correlation Heatmap")
    plt.tight_layout()
    plt.savefig(os.path.join(FIGURE_DIR, "correlation_heatmap.png"), dpi=300)
    plt.close()
    print("Saved: correlation_heatmap.png")

# ========================================================
# 4. PREPROCESSING
# ========================================================
print(f"\nStarting preprocessing...")

X = df.drop(columns=[target_col])
y = df[target_col]

print(f"Feature matrix shape: {X.shape}")
print(f"Target vector shape : {y.shape}")

# Handle missing values
print(f"\nFilling missing values...")
X = X.fillna(X.median(numeric_only=True))  # numeric columns
for col in X.select_dtypes(include=["object"]).columns:
    X[col] = X[col].fillna(X[col].mode()[0])

# Encode categorical features
label_encoders = {}
print(f"Encoding categorical columns...")
for col in X.select_dtypes(include=["object", "category"]).columns:
    le = LabelEncoder()
    X[col] = le.fit_transform(X[col].astype(str))
    label_encoders[col] = le
    joblib.dump(le, os.path.join(MODEL_DIR, f"le_{col}.pkl"))
    print(f"   Encoded: {col} → {len(le.classes_)} classes")

# Encode target if it's string
target_encoder = None
if y.dtype == "object" or y.dtype.name == "category":
    print(f"Encoding target column '{target_col}'...")
    target_encoder = LabelEncoder()
    y = target_encoder.fit_transform(y)
    joblib.dump(target_encoder, os.path.join(MODEL_DIR, "label_encoder_target.pkl"))
    print(f"   Classes: {list(target_encoder.classes_)}")

# Train-test split
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=TEST_SIZE, random_state=RANDOM_STATE, stratify=y
)

print(f"\nTrain set: {X_train.shape}")
print(f"Test set : {X_test.shape}")

# Scale features
print(f"\nApplying StandardScaler...")
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

joblib.dump(scaler, os.path.join(MODEL_DIR, "scaler.pkl"))
print("Scaler saved.")

# ========================================================
# 5. MODEL TRAINING
# ========================================================
print(f"\nTraining models...")

models = {}

# Random Forest
rf = RandomForestClassifier(
    n_estimators=500,
    max_depth=None,
    min_samples_split=2,
    min_samples_leaf=1,
    random_state=RANDOM_STATE,
    n_jobs=-1,
)
rf.fit(X_train_scaled, y_train)
models["Random Forest"] = rf

# XGBoost
xgb_model = xgb.XGBClassifier(
    n_estimators=500,
    max_depth=6,
    learning_rate=0.05,
    subsample=0.8,
    colsample_bytree=0.8,
    random_state=RANDOM_STATE,
    eval_metric="mlogloss",
    verbosity=0,
)
xgb_model.fit(X_train_scaled, y_train)
models["XGBoost"] = xgb_model

print("All models trained successfully.")

# ========================================================
# 6. EVALUATION
# ========================================================
print("\n" + "=" * 60)
print("MODEL EVALUATION RESULTS")
print("=" * 60)

results = []

for name, model in models.items():
    y_pred = model.predict(X_test_scaled)
    y_proba = model.predict_proba(X_test_scaled)

    acc = accuracy_score(y_test, y_pred)
    prec = precision_score(y_test, y_pred, average="weighted")
    rec = recall_score(y_test, y_pred, average="weighted")
    f1 = f1_score(y_test, y_pred, average="weighted")

    # AUC only if binary or using one-vs-rest
    try:
        auc = roc_auc_score(y_test, y_proba, multi_class="ovr")
    except:
        auc = np.nan

    results.append(
        {
            "Model": name,
            "Accuracy": acc,
            "Precision": prec,
            "Recall": rec,
            "F1-Score": f1,
            "AUC": auc,
        }
    )

    print(f"\n{name.upper()}")
    print(f"Accuracy   : {acc:.4f}")
    print(f"Precision  : {prec:.4f}")
    print(f"Recall     : {rec:.4f}")
    print(f"F1-Score   : {f1:.4f}")
    if not np.isnan(auc):
        print(f"AUC (ovr)  : {auc:.4f}")
    print("\nClassification Report:")
    print(classification_report(y_test, y_pred))

# Save results to CSV
results_df = pd.DataFrame(results)
results_df.to_csv(os.path.join(FIGURE_DIR, "model_comparison.csv"), index=False)
print(f"\nModel comparison saved to: model_comparison.csv")

# Plot comparison bar chart
results_df.plot(x="Model", y=["Accuracy", "F1-Score"], kind="bar", figsize=(10, 6))
plt.title("Model Performance Comparison")
plt.ylabel("Score")
plt.ylim(0, 1)
plt.xticks(rotation=0)
plt.legend()
plt.tight_layout()
plt.savefig(os.path.join(FIGURE_DIR, "model_comparison_bar.png"), dpi=300)
plt.close()
print("Saved: model_comparison_bar.png")

# ========================================================
# 7. BEST MODEL - Detailed plots
# ========================================================
best_model_name = results_df.loc[results_df["Accuracy"].idxmax(), "Model"]
best_model = models[best_model_name]
print(f"\nBest model: {best_model_name} (Accuracy: {results_df['Accuracy'].max():.4f})")

# Confusion Matrix
y_pred_best = best_model.predict(X_test_scaled)
cm = confusion_matrix(y_test, y_pred_best)

plt.figure(figsize=(8, 6))
sns.heatmap(
    cm,
    annot=True,
    fmt="d",
    cmap="Blues",
    xticklabels=target_encoder.classes_ if target_encoder else np.unique(y),
    yticklabels=target_encoder.classes_ if target_encoder else np.unique(y),
)
plt.title(f"Confusion Matrix - {best_model_name}")
plt.ylabel("True Label")
plt.xlabel("Predicted Label")
plt.tight_layout()
plt.savefig(os.path.join(FIGURE_DIR, "confusion_matrix_best.png"), dpi=300)
plt.close()
print("Saved: confusion_matrix_best.png")

# Feature Importance (Random Forest or XGBoost)
if hasattr(best_model, "feature_importances_"):
    importances = best_model.feature_importances_
    indices = np.argsort(importances)[::-1][:15]  # Top 15

    plt.figure(figsize=(10, 8))
    sns.barplot(x=importances[indices], y=X.columns[indices], palette="magma")
    plt.title(f"Top 15 Feature Importance - {best_model_name}")
    plt.xlabel("Importance Score")
    plt.tight_layout()
    plt.savefig(os.path.join(FIGURE_DIR, "feature_importance.png"), dpi=300)
    plt.close()
    print("Saved: feature_importance.png")

# Save best model
joblib.dump(best_model, os.path.join(MODEL_DIR, "best_model.pkl"))
print(f"\nBest model saved as: best_model.pkl")


# ========================================================
# 8. INFERENCE FUNCTION (Ready to use)
# ========================================================
def predict_new_data(new_df: pd.DataFrame):
    """
    Predict on new data (same columns as training, without target)
    """
    # Apply same preprocessing
    for col, le in label_encoders.items():
        if col in new_df.columns:
            new_df[col] = (
                new_df[col]
                .astype(str)
                .apply(lambda x: le.transform([x])[0] if x in le.classes_ else -1)
            )
    new_df = new_df.fillna(0)
    new_scaled = scaler.transform(new_df[X.columns])

    pred = best_model.predict(new_scaled)
    proba = best_model.predict_proba(new_scaled)

    if target_encoder:
        pred = target_encoder.inverse_transform(pred)

    return pred, proba


print("\n" + "=" * 60)
print("PIPELINE COMPLETED SUCCESSFULLY!")
print("All models, scalers, plots, and results have been saved.")
print("Use predict_new_data(your_new_dataframe) for predictions.")
print("=" * 60)
