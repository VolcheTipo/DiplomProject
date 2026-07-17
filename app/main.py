#FastAPI (НЕДОРАБОТАН, ИСПОЛЬЗУЕТСЯ СТРИМЛИТ)
#предполагалось что запуск: python run.py  или  uvicorn app.main:app --reload
import os
import tempfile
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from app.flow_extractor import extract_flows
from app.hybrid import HybridDetector
from app.config import DEFAULT_THRESHOLD

app = FastAPI(
    title="Network Anomaly Detector",
    description="Гибридная система обнаружения аномалий в сетевом трафике",
    version="1.0.0",
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)
detector = HybridDetector()


@app.get("/")
def root():
    return {"status": "ok", "message": "Network Anomaly Detector API"}


@app.post("/analyze")
async def analyze(file: UploadFile = File(...)):
    #Принимает PCAP или CSV файл, возвращает результаты анализа
    ext = os.path.splitext(file.filename)[1].lower()
    if ext not in (".pcap", ".pcapng", ".csv"):
        raise HTTPException(
            status_code=400,
            detail=f"Неподдерживаемый формат: {ext}. Используйте .pcap или .csv"
        )

    with tempfile.NamedTemporaryFile(delete=False, suffix=ext) as tmp:
        tmp.write(await file.read())
        tmp_path = tmp.name

    try:
        df = extract_flows(tmp_path)
    except Exception as e:
        raise HTTPException(status_code=422, detail=str(e))
    finally:
        if os.path.exists(tmp_path):
            os.unlink(tmp_path)

    if df.empty:
        raise HTTPException(status_code=422, detail="Файл не содержит данных о потоках")

    result = detector.predict(df)
    anomalies = result[result["is_anomaly"]]

    return {
        "total_flows": len(result),
        "anomaly_count": int(result["is_anomaly"].sum()),
        "threshold": DEFAULT_THRESHOLD,
        "rows": result.to_dict(orient="records"),
        "anomalies": anomalies[[
            "src_ip", "dst_ip", "src_port", "dst_port",
            "protocol", "bytes", "packets",
            "bad_packet_score", "anomaly_score",
        ]].to_dict(orient="records"),
    }


@app.get("/health")
def health():
    return {"status": "healthy"}
