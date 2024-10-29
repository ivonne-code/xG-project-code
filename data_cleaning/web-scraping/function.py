import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, r2_score

# Load the datasets
france_data_path = 'data_cleaning/web-scraping/france_player_stats_pt.csv'
argentina_data_path = 'data_cleaning/web-scraping/argentina_player_stats_pt.csv'
france_data = pd.read_csv(france_data_path)
argentina_data = pd.read_csv(argentina_data_path)
combined_data = pd.concat([france_data, argentina_data])

# Data cleaning and preparation
# Convert columns to numeric and drop rows with any NaN values in these columns
numeric_columns = ['Min', 'Gls', 'Ast', 'PK', 'PKatt', 'SoT', 'Touches', 'Tkl', 'Int', 'Blocks', 'xG', 'npxG', 'xAG']
combined_data[numeric_columns] = combined_data[numeric_columns].apply(pd.to_numeric, errors='coerce')
combined_data.dropna(subset=numeric_columns, inplace=True)

# Feature Selection
# Choosing features that have shown some reasonable correlation or theoretical relevance
features = ['Min', 'Gls', 'SoT', 'Touches', 'Tkl', 'Blocks']

# Target variable
target = 'xG'

# Splitting data
X = combined_data[features]
y = combined_data[target]
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Model Building
model = LinearRegression()
model.fit(X_train, y_train)

# Making predictions and evaluating the model
y_pred = model.predict(X_test)
mse = mean_squared_error(y_test, y_pred)
r2 = r2_score(y_test, y_pred)

# Output the coefficients of the model
coefficients = model.coef_
intercept = model.intercept_

print("Mean Squared Error:", mse)
print("R^2 Score:", r2)
print("Model Coefficients:", coefficients)
print("Model Intercept:", intercept)

# Function derived from the model
print("\nDerived Function for xG:")
print(f"xG = {intercept:.4f} + ", end="")
print(" + ".join([f"{coeff:.4f}*{feat}" for coeff, feat in zip(coefficients, features)]))
