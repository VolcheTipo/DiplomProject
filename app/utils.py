import logging
import numpy as np


def setup_logger():
    logger = logging.getLogger("IDS")
    logger.setLevel(logging.INFO)
    if not logger.handlers:
        ch = logging.StreamHandler()
        formatter = logging.Formatter("%(asctime)s | %(levelname)s | %(message)s")
        ch.setFormatter(formatter)
        logger.addHandler(ch)
    return logger
logger = setup_logger()


def get_numeric_matrix(df) -> np.ndarray:
    #Безопасно возвращает числовую матрицу признаков
    if df is None:
        return np.empty((0, 0))
    X = df.select_dtypes(include=[np.number]).to_numpy(dtype=float, copy=False)
    if X.ndim == 1:
        X = X.reshape(-1, 1)
    return X


def normalize_scores(scores: np.ndarray) -> np.ndarray:
    #Нормализация оценок аномальности в диапазон от 0 до 1
    scores = np.asarray(scores, dtype=float)
    if scores.size == 0:
        return scores
    finite = scores[np.isfinite(scores)]
    if finite.size == 0:
        return np.zeros_like(scores, dtype=float)
    min_val = finite.min()
    max_val = finite.max()
    if max_val - min_val == 0:
        return np.zeros_like(scores, dtype=float)
    scores = np.nan_to_num(scores, nan=min_val, posinf=max_val, neginf=min_val)
    return (scores - min_val) / (max_val - min_val)
