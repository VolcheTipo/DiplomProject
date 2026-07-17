#Гибридный детектор аномалий: объединяет метод к-средних, лес изоляции,
#метод опорных векторов, статистику, логическое программирование (Rule-based) и ML детекторы через нечёткую логику
import pandas as pd
from app.detectors.kmeans_detector import KMeansDetector
from app.detectors.isolation_forest_detector import IsolationForestDetector
from app.detectors.svm_detector import SVMDetector
from app.detectors.statistical_detector import StatisticalDetector
from app.detectors.bad_packet_detector import BadPacketDetector
from app.ml_detector import MLDetector
from app.fuzzy_logic import fuzzy_score
from app.config import DEFAULT_THRESHOLD


class HybridDetector:
    def __init__(self):
        self.kmeans = KMeansDetector()
        self.iforest = IsolationForestDetector()
        self.svm = SVMDetector()
        self.stat = StatisticalDetector()
        self.bad_packets = BadPacketDetector()
        self.ml = MLDetector()
    def predict(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()
        if df.empty:
            for col in [
                "kmeans_score", "iforest_score", "svm_score",
                "stat_score", "bad_packet_score", "ml_score",
                "anomaly_score", "is_anomaly",
            ]:
                df[col] = []
            return df

        df["kmeans_score"] = self.kmeans.predict(df)
        df["iforest_score"] = self.iforest.predict(df)
        df["svm_score"] = self.svm.predict(df)
        df["stat_score"] = self.stat.predict(df)
        df["bad_packet_score"] = self.bad_packets.predict(df)
        df["ml_score"] = self.ml.predict(df)
        df["anomaly_score"] = df.apply(
            lambda row: fuzzy_score(
                row["kmeans_score"],
                row["iforest_score"],
                row["svm_score"],
                row["stat_score"],
                row["ml_score"],
                row["bad_packet_score"],
            ),
            axis=1,
        )

        df["is_anomaly"] = df["anomaly_score"] >= DEFAULT_THRESHOLD

        return df
