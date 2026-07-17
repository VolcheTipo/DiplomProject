from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
import numpy as np
from app.utils import normalize_scores, get_numeric_matrix

#Метод к-средних
class KMeansDetector:
    def __init__(self, n_clusters: int = 3):
        self.n_clusters = n_clusters
    def predict(self, df) -> np.ndarray:
        x = get_numeric_matrix(df)
        if x.size == 0 or len(x) < 2:
            return np.zeros(len(df), dtype=float)

        n_clusters = max(1, min(self.n_clusters, len(x)))
        if n_clusters == 1:
            return np.zeros(len(x), dtype=float)

        x_scaled = StandardScaler().fit_transform(x)
        model = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
        labels = model.fit_predict(x_scaled)
        centers = model.cluster_centers_
        distances = np.linalg.norm(x_scaled - centers[labels], axis=1)
        return normalize_scores(distances)
