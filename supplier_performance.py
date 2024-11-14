import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from xgboost import XGBRegressor
from sklearn.metrics import mean_absolute_error
import numpy as np

# Load the dataset
file_path = 'your_file_path.csv'  # Replace with the path to your CSV file
maintenance_data = pd.read_csv(file_path)

# Convert date columns to datetime
maintenance_data['DT_MAINT_START'] = pd.to_datetime(maintenance_data['DT_MAINT_START'], errors='coerce')
maintenance_data['DT_MAINT_END'] = pd.to_datetime(maintenance_data['DT_MAINT_END'], errors='coerce')

# Calculate target variable (TARGET_DAYS: the number of days from start to end)
maintenance_data['TARGET_DAYS'] = (maintenance_data['DT_MAINT_END'] - maintenance_data['DT_MAINT_START']).dt.days

# Filter rows with necessary columns and drop rows with missing values in TARGET_DAYS
model_data = maintenance_data[['SUP_COMPANY_CODE', 'CD_MAINT_TYPE', 'VA_MAINT_ODMT_REDN', 
                               'DT_MAINT_START', 'TARGET_DAYS']].dropna()

# Feature engineering: Extract month from start date
model_data['START_MONTH'] = model_data['DT_MAINT_START'].dt.month

# Encode categorical variables
le_vendor = LabelEncoder()
le_maint_type = LabelEncoder()
model_data['SUP_COMPANY_CODE'] = le_vendor.fit_transform(model_data['SUP_COMPANY_CODE'])
model_data['CD_MAINT_TYPE'] = le_maint_type.fit_transform(model_data['CD_MAINT_TYPE'])

# Define features and target for regression
X = model_data.drop(columns=['DT_MAINT_START', 'TARGET_DAYS'])
y = model_data['TARGET_DAYS']

# Split data into training and testing sets
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42)

# Train an XGBoost Regressor model
model_xgb = XGBRegressor(n_estimators=100, learning_rate=0.1, max_depth=5, random_state=42)
model_xgb.fit(X_train, y_train)

# Make predictions and evaluate the model
y_pred = model_xgb.predict(X_test)
mae = mean_absolute_error(y_test, y_pred)

# Display the mean absolute error to understand prediction accuracy
print("Mean Absolute Error (in days):", mae)

# Example prediction for a new job (assumes input data is similar to training data)
new_job_data = {
    'SUP_COMPANY_CODE': le_vendor.transform(['AU5674'])[0],  # Example vendor code
    'CD_MAINT_TYPE': le_maint_type.transform(['LAB'])[0],    # Example maintenance type
    'VA_MAINT_ODMT_REDN': 20000,                             # Example cost
    'START_MONTH': 7                                         # Example start month (July)
}
new_job_df = pd.DataFrame([new_job_data])

# Predict days to complete and calculate estimated work end date
predicted_days = model_xgb.predict(new_job_df)[0]
start_date = pd.to_datetime('2024-07-01')  # Example start date
estimated_end_date = start_date + pd.Timedelta(days=predicted_days)

print("Estimated Work End Date:", estimated_end_date)
