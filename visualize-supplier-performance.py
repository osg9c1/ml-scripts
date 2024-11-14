import pandas as pd
import matplotlib.pyplot as plt

# Load data and calculate delay days
file_path = 'path_to_your_large_file.csv'  # Replace with your file path
selected_columns = ['SUP_COMPANY_CODE', 'DT_MAINT_START', 'DT_MAINT_END']
maintenance_data = pd.read_csv(file_path, usecols=selected_columns)

# Convert date columns to datetime
maintenance_data['DT_MAINT_START'] = pd.to_datetime(maintenance_data['DT_MAINT_START'], errors='coerce')
maintenance_data['DT_MAINT_END'] = pd.to_datetime(maintenance_data['DT_MAINT_END'], errors='coerce')

# Calculate delay days and filter data for delayed jobs
maintenance_data['DELAY_DAYS'] = (maintenance_data['DT_MAINT_END'] - maintenance_data['DT_MAINT_START']).dt.days
maintenance_data = maintenance_data.dropna()

# Group data by supplier to calculate average delay and delay frequency
supplier_performance = maintenance_data.groupby('SUP_COMPANY_CODE')['DELAY_DAYS'].agg(
    count_delays='size',
    avg_delay='mean',
    max_delay='max'
).sort_values(by='count_delays', ascending=False)

# Display top suppliers by frequency and average delay
print(supplier_performance.head())

# Plotting
plt.figure(figsize=(14, 8))

# Plotting Average Delay Duration
plt.subplot(1, 2, 1)
supplier_performance['avg_delay'].plot(kind='bar', color='skyblue')
plt.title('Average Delay Duration by Supplier')
plt.xlabel('Supplier')
plt.ylabel('Average Delay (days)')

# Plotting Frequency of Delays
plt.subplot(1, 2, 2)
supplier_performance['count_delays'].plot(kind='bar', color='salmon')
plt.title('Frequency of Delays by Supplier')
plt.xlabel('Supplier')
plt.ylabel('Number of Delayed Jobs')

plt.tight_layout()
plt.show()
