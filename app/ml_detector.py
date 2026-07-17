import os
import numpy as np
import joblib
from app.config import MODEL_PATH
from app.utils import normalize_scores, get_numeric_matrix

#Детектор на основе предобученной модели Random Forest
#Если модель не обучена — возвращает нулевые скоры (модель не до конца обучилась, надо дорабатывать((()
class MLDetector:
    def __init__(self):
        self.model = None
        if os.path.exists(MODEL_PATH):
            try:
                self.model = joblib.load(MODEL_PATH)
            except Exception:
                self.model = None
    def predict(self, df) -> np.ndarray:
        X = get_numeric_matrix(df)
        if len(X) == 0:
            return np.array([], dtype=float)

        if self.model is None or X.shape[1] == 0:
            return np.zeros(len(X), dtype=float)
        try:
            if hasattr(self.model, "predict_proba"):
                probs = self.model.predict_proba(X)
                if probs.shape[1] >= 2:
                    return normalize_scores(probs[:, 1])
                return normalize_scores(probs[:, 0])
            scores = self.model.decision_function(X)
            return normalize_scores(-scores)
        except Exception:
            return np.zeros(len(X), dty)