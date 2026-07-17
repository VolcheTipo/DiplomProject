import pandas as pd
from app.detectors.kmeans_detector import KMeansDetector


def test_kmeans_detector():
    df = pd.DataFrame({
        "bytes": [100, 200, 300, 10000],
        "packets": [10, 20, 30, 1000],
    })

    detector = KMeansDetector()
    scores = detector.predict(df)

    assert len(scores) == len(df)
    assert (scores >= 0).all() and (scores <= 1).all()
