import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error
import os
print("Current working directory:", os.getcwd())

# Since the script and CSV are in the same directory, directly use the filename
france_data = pd.read_csv('france_player_stats_pt.csv')
argentina_data = pd.read_csv('argentina_player_stats_pt.csv')

# Combine the data
combined_data = pd.concat([france_data, argentina_data])

# Data cleaning
combined_data = combined_data.replace('-', np.nan)  # Replace hyphens with NaN
combined_data = combined_data.dropna()  # Drop rows with missing values
combined_data = combined_data[combined_data.columns[1:]]  # Drop the first column if it's duplicate header or irrelevant

# Convert relevant columns to numeric
numeric_columns = ['Min', 'Gls', 'Ast', 'PK', 'PKatt', 'SoT', 'Touches', 'Tkl', 'Int', 'Blocks', 'xG', 'npxG', 'xAG']
combined_data[numeric_columns] = combined_data[numeric_columns].apply(pd.to_numeric, errors='coerce')

# Correlation matrix
corr_matrix = combined_data[numeric_columns].corr()
print(corr_matrix['xG'].sort_values(ascending=False))  # Show correlation with xG

# Heatmap of correlations
plt.figure(figsize=(10, 8))
sns.heatmap(corr_matrix, annot=True, cmap='coolwarm')
plt.title('Correlation Matrix')
plt.show()

# Regression model
X = combined_data[['Min', 'SoT', 'Touches', 'Tkl', 'Blocks']]  # Selecting some predictors for simplicity
y = combined_data['xG']

# Splitting the data into training and testing sets
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Fit the model
model = LinearRegression()
model.fit(X_train, y_train)

# Predicting and evaluating the model
y_pred = model.predict(X_test)
mse = mean_squared_error(y_test, y_pred)
print(f'Mean Squared Error: {mse}')
