#Извлекаем сетевые потоки из pcap или csv файлов
import os
import pandas as pd

#Экстрактор: из .pcap и .pcapng идет парсинг через scapy , .csv  читается напрямую
def extract_flows(path: str) -> pd.DataFrame:
    ext = os.path.splitext(path)[1].lower()
    if ext in (".pcap", ".pcapng"):
        return _extract_from_pcap(path)
    elif ext == ".csv":
        return _extract_from_csv(path)
    else:
        raise ValueError(f"Неподдерживаемый формат файла: {ext}")


def _extract_from_pcap(path: str) -> pd.DataFrame:
    try:
        from scapy.all import rdpcap, IP, TCP, UDP
    except ImportError:
        raise ImportError("Установите scapy: pip install scapy") #прорабатываем исключения на всякий случай

    packets = rdpcap(path)
    flows: dict = {}

    for pkt in packets:
        if IP not in pkt:
            continue
        src = pkt[IP].src
        dst = pkt[IP].dst
        proto = "OTHER"
        sport = 0
        dport = 0
        if TCP in pkt:
            proto = "TCP"
            sport = pkt[TCP].sport
            dport = pkt[TCP].dport
        elif UDP in pkt:
            proto = "UDP"
            sport = pkt[UDP].sport
            dport = pkt[UDP].dport
        key = (src, dst, sport, dport, proto)
        if key not in flows:
            flows[key] = {"bytes": 0, "packets": 0}
        flows[key]["bytes"] += len(pkt)
        flows[key]["packets"] += 1
    rows = []
    for k, v in flows.items():
        rows.append({
            "src_ip": k[0],
            "dst_ip": k[1],
            "src_port": k[2],
            "dst_port": k[3],
            "protocol": k[4],
            "bytes": v["bytes"],
            "packets": v["packets"],
        })

    return pd.DataFrame(rows)


def _extract_from_csv(path: str) -> pd.DataFrame:
    # Ожидаем колонки в csv: src_ip =  source ip (адрес отпр.), dst_ip = destination ip(адрес получ.), src_port = source port (порт отпр), dst_port = destination port (порт получ.),
    #protocol =  протокол (tcp, icmp, udp), bytes = объем данных, packets =  кол-во пакетов
    required = {"src_ip", "dst_ip", "src_port", "dst_port", "protocol", "bytes", "packets"}
    df = pd.read_csv(path)
    missing = required - set(df.columns)
    if missing:
        raise ValueError(f"В csv отсутствуют колонки: {missing}") #тоже прорабатываем важные исключения, чтобы понять, какие пакеты данных можно грузить
    return df