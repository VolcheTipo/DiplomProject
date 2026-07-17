import pandas as pd
from app.hybrid import HybridDetector


def test_scores_range():
    df = pd.DataFrame({
        "src_ip": ["192.168.1.1", "192.168.1.2", "192.168.1.3", "10.0.0.9"],
        "dst_ip": ["8.8.8.8", "8.8.4.4", "1.1.1.1", "185.12.44.1"],
        "src_port": [1234, 1235, 1236, 55555],
        "dst_port": [80, 443, 53, 4444],
        "protocol": ["TCP", "TCP", "UDP", "TCP"],
        "bytes": [100, 200, 300, 10000],
        "packets": [10, 20, 30, 1000],
    })

    detector = HybridDetector()
    result = detector.predict(df)

    assert result["anomaly_score"].between(0, 1).all()
