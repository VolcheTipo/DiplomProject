from sklearn.svm import OneClassSVM
from sklearn.preprocessing import StandardScaler
import numpy as np
from app.utils import normalize_scores, get_numeric_matrix

# метод опорных векторов; обучается только на нормальных данных
class SVMDetector:
    def __init__(self, nu: float = 0.1):
        self.nu = nu
    def predict(self, df) -> np.ndarray:
        x = get_numeric_matrix(df)
        if x.size == 0 or len(x) < 2:
            return np.zeros(len(df), dtype=float)
        x_scaled = StandardScaler().fit_transform(x)
        model = OneClassSVM(kernel="rbf", gamma="scale", nu=self.nu)
        model.fit(x_scaled)
        scores = -model.decision_function(x_scaled)
        return normalize_scores(scores)
