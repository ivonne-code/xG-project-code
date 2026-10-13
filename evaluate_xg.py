"""Evaluate the xG logistic regression model with 5-fold CV against a base-rate baseline."""
import json, numpy as np, pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import make_pipeline
from sklearn.model_selection import StratifiedKFold, cross_val_predict
from sklearn.metrics import roc_auc_score, brier_score_loss, log_loss

df = pd.DataFrame(json.load(open('data_cleaning/shot_data.json')))
y = df['goal'].values
features = ['x', 'y', 'distance', 'angle']
cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)

base = np.full(len(y), y.mean())
model = make_pipeline(StandardScaler(), LogisticRegression(max_iter=1000))
pred = cross_val_predict(model, df[features], y, cv=cv, method='predict_proba')[:, 1]

print(f"Shots: {len(df):,}  Goal rate: {y.mean():.3f}")
print(f"Baseline  AUC 0.500  LogLoss {log_loss(y, base):.4f}  Brier {brier_score_loss(y, base):.4f}")
print(f"Model     AUC {roc_auc_score(y, pred):.3f}  LogLoss {log_loss(y, pred):.4f}  Brier {brier_score_loss(y, pred):.4f}")

model.fit(df[features], y)
for f, c in zip(features, model[-1].coef_[0]):
    print(f"  {f:10s} {c:+.3f}")
print(f"  intercept  {model[-1].intercept_[0]:+.3f}")
