# ml-service/src/services/sensor_clustering.py
import pandas as pd
from sklearn.cluster import KMeans

# Let's cluster on rolling window features (e.g., mean, std)
df['rolling_mean'] = df['sensor'].rolling(window=7).mean()
df['rolling_std'] = df['sensor'].rolling(window=7).std()
features = df[['rolling_mean', 'rolling_std']].dropna()

kmeans = KMeans(n_clusters=2, random_state=42)
clusters = kmeans.fit_predict(features)
features['cluster'] = clusters

plt.figure(figsize=(8,4))
plt.scatter(features['rolling_mean'], features['rolling_std'], c=features['cluster'], cmap='viridis')
plt.xlabel('Rolling Mean')
plt.ylabel('Rolling Std')
plt.title('KMeans Clustering of Sensor Patterns')
plt.show()   