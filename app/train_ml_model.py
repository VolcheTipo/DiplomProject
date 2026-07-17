
#Обучение модели Random Forest на датасете data/dataset.csv
#Запуск: python -m app.train_ml_model

import os
import pandas as pd
import joblib
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report

from app.config import MODEL_PATH
from app.utils import logger


def train():
    dataset_path = os.path.join(os.path.dirname(__file__), "..", "data", "dataset.csv")

    if not os.path.exists(dataset_path):
        raise FileNotFoundError(
            f"Датасет не найден: {dataset_path}\n"
            "Сначала запустите: python data/generate_samples.py"
        )

    df = pd.read_csv(dataset_path)
    logger.info(f"Датасет загружен: {len(df)} строк")

    if "label" not in df.columns:
        raise ValueError("В датасете нет колонки 'label'")

    # Убираем нечисловые признаки (IP-адреса, протокол)
    X = df.select_dtypes(include=["number"]).drop(columns=["label"], errors="ignore")
    y = df["label"]

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    model = RandomForestClassifier(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)

    y_pred = model.predict(X_test)
    report = classification_report(y_test, y_pred, target_names=["Normal", "Anomaly"])
    logger.info(f"Результаты на тестовой выборке:\n{report}")

    os.makedirs(os.path.dirname(MODEL_PATH), exist_ok=True)
    joblib.dump(model, MODEL_PATH)
    logger.info(f"Модель сохранена: {MODEL_PATH}")


if __name__ == "__main__":
    train()