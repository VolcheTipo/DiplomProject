import pandas as pd
from app.hybrid import HybridDetector

def test_anomaly_detection():
    df = pd.DataFrame({
        "src_ip": ["192.168.1.10", "192.168.1.11", "10.0.0.8", "5.6.7.8"],
        "dst_ip": ["8.8.8.8", "8.8.4.4", "1.1.1.1", "185.12.44.1"],
        "src_port": [1234, 1235, 1236, 54321],
        "dst_port": [80, 443, 53, 4444],
        "protocol": ["TCP", "TCP", "UDP", "TCP"],
        "bytes": [100, 120, 110, 20000],
        "packets": [10, 12, 11, 5000],
    })
    detector = HybridDetector()
    result = detector.predict(df)
    assert result["anomaly_score"].iloc[-1] > result["anomaly_score"].iloc[0]
