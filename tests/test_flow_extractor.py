from pathlib import Path
import pandas as pd
from app.flow_extractor import extract_flows


def test_extract_flows(tmp_path):
    csv_path = tmp_path / "sample.csv"
    pd.DataFrame({
        "src_ip": ["192.168.1.10"],
        "dst_ip": ["8.8.8.8"],
        "src_port": [54321],
        "dst_port": [443],
        "protocol": ["TCP"],
        "bytes": [15420],
        "packets": [22],
    }).to_csv(csv_path, index=False)

    df = extract_flows(str(csv_path))

    assert df is not None
    assert len(df) == 1
    assert "packets" in df.columns
