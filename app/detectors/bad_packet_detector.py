import numpy as np
from app.utils import normalize_scores, get_numeric_matrix


class BadPacketDetector:
    #Правиловой детектор подозрительных потоков/пакетов
    # Смотрит на порт, протокол, количество пакетов и переданных байт
    fishy_ports = {21, 22, 23, 25, 110, 135, 139, 143, 445, 3389, 4444, 5555, 8080, 9999, 12345, 31337}
    def predict(self, df) -> np.ndarray:
        if df is None or len(df) == 0:
            return np.array([], dtype=float)
        x = get_numeric_matrix(df)
        bytes_idx = None
        packets_idx = None
        cols = list(df.select_dtypes(include=[np.number]).columns)
        if "bytes" in cols:
            bytes_idx = cols.index("bytes")
        elif "byte_count" in cols:
            bytes_idx = cols.index("byte_count")
        if "packets" in cols:
            packets_idx = cols.index("packets")
        elif "packet_count" in cols:
            packets_idx = cols.index("packet_count")
        scores = np.zeros(len(df), dtype=float)
        for i, (_, row) in enumerate(df.iterrows()):
            score = 0.0
            dst_port = int(row.get("dst_port", 0) or 0)
            src_port = int(row.get("src_port", 0) or 0)
            protocol = str(row.get("protocol", "")).upper()
            if dst_port in self.fishy_ports:
                score += 0.25
            if src_port in self.fishy_ports:
                score += 0.10
            if protocol not in {"TCP", "UDP", "ICMP", "OTHER"}:
                score += 0.10
            if bytes_idx is not None and packets_idx is not None:
                bytes_val = float(x[i, bytes_idx])
                packets_val = float(x[i, packets_idx])
                if packets_val <= 3 and bytes_val <= 200:
                    score += 0.35
                if packets_val >= 1000 or bytes_val >= 1_000_000:
                    score += 0.35
                if packets_val > 0 and bytes_val / packets_val > 50_000:
                    score += 0.20
            scores[i] = min(score, 1.0)
        return normalize_scores(scores)
