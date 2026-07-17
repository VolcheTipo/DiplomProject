import numpy as np
from app.utils import normalize_scores, get_numeric_matrix

#Статистический
class StatisticalDetector:
    def predict(self, df) -> np.ndarray:
        x = get_numeric_matrix(df)
        if x.size == 0 or len(x) == 0:
            return np.array([], dtype=float)
        if x.shape[1] == 0:
            return np.zeros(len(df), dtype=float)
        mean = x.mean(axis=0)
        std = x.std(axis=0)
        std[std == 0] = 1e-9  # избегаем деления на 0
        z_scores = np.abs((x - mean) / std)
        max_z = z_scores.max(axis=1)
        return normalize_scores(max_z)
