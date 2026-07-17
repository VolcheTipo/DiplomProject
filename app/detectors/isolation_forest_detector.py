from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
import numpy as np
from app.utils import normalize_scores, get_numeric_matrix

#Стандартный лес изоляции, подстраиваемый под нашу задачу
class IsolationForestDetector:
    def __init__(self, contamination: float = 0.1):
        self.contamination = contamination
    def predict(self, df) -> np.ndarray:
        x = get_numeric_matrix(df)
        if x.size == 0 or len(x) < 2:
            return np.zeros(len(df), dtype=float)

        x_scaled = StandardScaler().fit_transform(x)
        model = IsolationForest(
            n_estimators=100,
            contamination=self.contamination,
            random_state=42,
        )
        model.fit(x_scaled)
        scores = -model.decision_function(x_scaled)
        return normalize_scores(scores)
