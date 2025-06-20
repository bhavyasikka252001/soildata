import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from sklearn.preprocessing import MinMaxScaler

# Sample data (replace with your scraped DataFrame)
data = {
    'State': ['ANDHRA PRADESH', 'ARUNACHAL PRADESH', 'ASSAM', 'BIHAR', 'CHHATTISGARH'],
    'Nitrogen_High': [35, 0, 4649, 38, 553],
    'Nitrogen_Med': [4891, 0, 3165, 1506, 3626],
    'Nitrogen_Low': [10350, 1, 173, 4888, 15388],
    'Phosphorous_High': [3387, 0, 5766, 5045, 1312],
    'Phosphorous_Med': [8280, 0, 1608, 1216, 13944],
    'Phosphorous_Low': [3616, 1, 613, 172, 4309],
    'Potassium_High': [11200, 0, 556, 1236, 9549],
    'Potassium_Med': [3609, 0, 2681, 4786, 8583],
    'Potassium_Low': [482, 1, 4750, 411, 1440],
    'OC_High': [5094, 1, 5581, 729, 4639],
    'OC_Med': [4276, 0, 1488, 3216, 7054],
    'OC_Low': [5872, 1, 918, 2486, 7862],
    'EC_Saline': [1101, 1, 1, 58, 37],
    'EC_Non_Saline': [14140, 0, 7986, 6375, 19503],
    'EC_Acidic': [95, 1, 5028, 27, 2765]
}

# Load into DataFrame
df = pd.DataFrame(data)
df.set_index('State', inplace=True)

# Normalize
scaler = MinMaxScaler()
df_normalized = pd.DataFrame(scaler.fit_transform(df), columns=df.columns, index=df.index)

# Correlation Heatmap
plt.figure(figsize=(14, 10))
sns.heatmap(df.corr(), annot=True, fmt=".2f", cmap='coolwarm', square=True)
plt.title('Correlation Heatmap of Soil Nutrient Data')
plt.xticks(rotation=45, ha='right')
plt.yticks(rotation=0)
plt.tight_layout()
plt.show()

# Cluster Heatmap
sns.clustermap(df_normalized, cmap='viridis', figsize=(14, 10), metric='euclidean', method='ward')
plt.suptitle("Cluster Heatmap of Soil Health Parameters", y=1.02)
plt.show()

# Barplot: Nitrogen Levels
df_reset = df.reset_index()
df_melted = df_reset.melt(id_vars='State', value_vars=['Nitrogen_High', 'Nitrogen_Med', 'Nitrogen_Low'],
                          var_name='Nitrogen_Level', value_name='Count')

plt.figure(figsize=(12, 6))
sns.barplot(data=df_melted, x='State', y='Count', hue='Nitrogen_Level')
plt.xticks(rotation=45, ha='right')
plt.title("Nitrogen Levels Across States")
plt.tight_layout()
plt.show()
