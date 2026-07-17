# Streamlit UI для системы обнаружения аномалий в сетевом трафике
# Запуск: streamlit run ui/streamlit_app.py

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from app.flow_extractor import extract_flows
from app.hybrid import HybridDetector
from app.config import DEFAULT_THRESHOLD


# Настройки страницы
st.set_page_config(
    page_title="Network Anomaly Detector",
    page_icon="🛡",
    layout="wide",
)

st.title("Система обнаружения аномалий в сетевом трафике")
st.markdown(
    "Загрузите файл сетевого трафика (**.csv** или **.pcap**) "
    "для анализа гибридным детектором аномалий."
)


# Боковая панель
with st.sidebar:
    st.header("Настройки")
    threshold = st.slider(
        "Порог аномальности",
        min_value=0.1,
        max_value=1.0,
        value=DEFAULT_THRESHOLD,
        step=0.05,
        help="Потоки с оценкой выше порога считаются аномальными",
    )
    st.divider()
    st.markdown("**Детекторы:**")
    st.markdown("🔵 KMeans (расстояние до кластера)")
    st.markdown("🟠 Isolation Forest")
    st.markdown("🟢 One-Class SVM")
    st.markdown("🔴 Статистический (Z-score)")
    st.markdown("🟣 Random Forest (ML)")
    st.divider()
    st.markdown("**Формат CSV:**")
    st.code(
        "src_ip, dst_ip, src_port,\n"
        "dst_port, protocol,\n"
        "bytes, packets",
        language="text",
    )


# Загрузка файла
uploaded_file = st.file_uploader(
    "Загрузите файл трафика",
    type=["csv", "pcap", "pcapng"],
    help="Поддерживаются форматы CSV и PCAP",
)

col_example, col_spacer = st.columns([2, 5])
with col_example:
    use_example = st.checkbox("Использовать пример (attack_traffic.csv)")

# Загрузка данных
@st.cache_data(show_spinner=False)
def load_and_analyze(file_bytes: bytes, filename: str, thresh: float) -> pd.DataFrame:
    import tempfile
    ext = os.path.splitext(filename)[1].lower()
    with tempfile.NamedTemporaryFile(delete=False, suffix=ext) as tmp:
        tmp.write(file_bytes)
        tmp_path = tmp.name
    try:
        df = extract_flows(tmp_path)
        detector = HybridDetector()
        result = detector.predict(df)
        result["is_anomaly"] = result["anomaly_score"] >= thresh
        return result
    finally:
        if os.path.exists(tmp_path):
            os.unlink(tmp_path)


df = None
if use_example:
    example_path = os.path.join(os.path.dirname(__file__), "..", "data", "attack_traffic.csv")
    if os.path.exists(example_path):
        with open(example_path, "rb") as f:
            file_bytes = f.read()
        with st.spinner("Анализируем пример трафика..."):
            df = load_and_analyze(file_bytes, "attack_traffic.csv", threshold)
    else:
        st.warning("Файл примера не найден. Запустите: `python data/generate_samples.py`")

elif uploaded_file is not None:
    with st.spinner("Анализируем трафик..."):
        df = load_and_analyze(uploaded_file.getvalue(), uploaded_file.name, threshold)


# Отображение результатов
if df is not None:
    anomalies = df[df["is_anomaly"]]
    normal = df[~df["is_anomaly"]]

    # Метрики
    st.divider()
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Всего потоков", len(df))
    m2.metric("Аномалий", len(anomalies), delta=f"{len(anomalies)/len(df)*100:.1f}%")
    m3.metric("Нормальных", len(normal))
    m4.metric("Средняя оценка", f"{df['anomaly_score'].mean():.3f}")

    st.divider()

    # Графики
    tab1, tab2, tab3, tab4 = st.tabs(
        ["📈 Оценки аномальности", "📊 Сравнение методов", "🌐 Трафик", "🔍 Детали"]
    )

    with tab1:
        st.subheader("Распределение гибридной оценки аномальности")
        fig = go.Figure()
        fig.add_trace(go.Histogram(
            x=normal["anomaly_score"],
            name="Нормальный",
            marker_color="#2ecc71",
            opacity=0.75,
            nbinsx=40,
        ))
        fig.add_trace(go.Histogram(
            x=anomalies["anomaly_score"],
            name="Аномалия",
            marker_color="#e74c3c",
            opacity=0.75,
            nbinsx=40,
        ))
        fig.add_vline(
            x=threshold,
            line_dash="dash",
            line_color="orange",
            annotation_text=f"Порог ({threshold})",
            annotation_position="top right",
        )
        fig.update_layout(
            barmode="overlay",
            xaxis_title="Оценка аномальности",
            yaxis_title="Количество потоков",
            legend=dict(orientation="h", yanchor="bottom", y=1.02),
            height=400,
        )
        st.plotly_chart(fig, use_container_width=True)

        # График по индексу потока
        st.subheader("Оценка аномальности по потокам")
        df_plot = df.reset_index(drop=True)
        colors = df_plot["is_anomaly"].map({True: "#e74c3c", False: "#3498db"})
        fig2 = go.Figure()
        fig2.add_trace(go.Scatter(
            x=df_plot.index,
            y=df_plot["anomaly_score"],
            mode="markers",
            marker=dict(color=colors, size=5, opacity=0.7),
            text=df_plot.apply(
                lambda r: f"{r['src_ip']}→{r['dst_ip']} | {r['protocol']} | score={r['anomaly_score']:.3f}",
                axis=1,
            ),
            hovertemplate="%{text}<extra></extra>",
        ))
        fig2.add_hline(
            y=threshold,
            line_dash="dash",
            line_color="orange",
            annotation_text="Порог",
        )
        fig2.update_layout(
            xaxis_title="Индекс потока",
            yaxis_title="Оценка аномальности",
            height=350,
        )
        st.plotly_chart(fig2, use_container_width=True)
    with tab2:
        st.subheader("Сравнение оценок всех методов")
        score_cols = ["kmeans_score", "iforest_score", "svm_score", "stat_score", "bad_packet_score", "ml_score", "anomaly_score"]
        labels = ["KMeans", "Isolation Forest", "SVM", "Statistical", "Bad Packet", "ML (Random Forest)", "Hybrid Score"]
        colors_box = ["#3498db", "#e67e22", "#2ecc71", "#e74c3c", "#8e44ad", "#9b59b6", "#f39c12"]
        fig3 = go.Figure()
        for col, label, color in zip(score_cols, labels, colors_box):
            fig3.add_trace(go.Box(
                y=df[col],
                name=label,
                marker_color=color,
                boxmean=True,
            ))
        fig3.update_layout(
            yaxis_title="Оценка аномальности [0–1]",
            height=450,
            showlegend=False,
        )
        st.plotly_chart(fig3, use_container_width=True)
        st.subheader("🏆 Рейтинг методов (интегральная оценка)")
        ranking_data = []

        for col, label in zip(score_cols, labels):
            mean_score = df[col].mean()
            std_score = df[col].std()
            anomaly_ratio = (df[col] >= threshold).mean()

            # Итоговый score
            score = (
                    0.5 * mean_score +        # насколько подозрительный метод
                    0.3 * anomaly_ratio -     # сколько аномалий находит
                    0.2 * std_score           # штраф за нестабильность
            )

            ranking_data.append({
                "Метод": label,
                "Mean": round(mean_score, 3),
                "Std": round(std_score, 3),
                "Anomaly %": round(anomaly_ratio * 100, 1),
                "Score": round(score, 3)
            })

        #
        ranking_df = pd.DataFrame(ranking_data).sort_values("Score", ascending=False)

        # Таблица рейтинга
        st.dataframe(ranking_df, use_container_width=True)

        # Бар-чарт рейтинга
        fig_rank = px.bar(
            ranking_df,
            x="Метод",
            y="Score",
            color="Score",
            color_continuous_scale="Viridis",
            text="Score",
            height=400,
        )

        fig_rank.update_layout(
            yaxis_title="Итоговый рейтинг",
            xaxis_title="Метод",
        )

        st.plotly_chart(fig_rank, use_container_width=True)

        ##########################################################################################################
        # Тепловая карта корреляций между методами
        st.subheader("Корреляция между методами")
        corr = df[score_cols].corr()
        fig4 = px.imshow(
            corr,
            text_auto=".2f",
            color_continuous_scale="RdBu_r",
            zmin=-1,
            zmax=1,
            labels=dict(color="Корреляция"),
            x=labels,
            y=labels,
        )
        fig4.update_layout(height=400)
        st.plotly_chart(fig4, use_container_width=True)

    with tab3:


        # Распределение по протоколам
        col_a, col_b = st.columns(2)
        with col_a:
            st.subheader("По протоколам (аномалии)")
            if not anomalies.empty:
                proto_counts = anomalies["protocol"].value_counts()
                fig6 = px.pie(
                    values=proto_counts.values,
                    names=proto_counts.index,
                    color_discrete_sequence=["#e74c3c", "#e67e22", "#9b59b6"],
                    height=320,
                )
                st.plotly_chart(fig6, use_container_width=True)

        with col_b:
            st.subheader("Bytes vs Packets (scatter)")
            df_scatter = df.copy()
            df_scatter["Тип"] = df_scatter["is_anomaly"].map(
                {True: "Аномалия", False: "Нормальный"}
            )
            fig7 = px.scatter(
                df_scatter,
                x="packets",
                y="bytes",
                color="Тип",
                color_discrete_map={"Аномалия": "#e74c3c", "Нормальный": "#3498db"},
                opacity=0.6,
                log_x=True,
                log_y=True,
                labels={"packets": "Пакеты (log)", "bytes": "Байты (log)"},
                height=320,
            )
            st.plotly_chart(fig7, use_container_width=True)

    with tab4:
        st.subheader("Аномальные потоки")
        if not anomalies.empty:
            display_cols = [
                "src_ip", "dst_ip", "src_port", "dst_port", "protocol",
                "bytes", "packets", "anomaly_score",
                "kmeans_score", "iforest_score", "svm_score", "stat_score", "bad_packet_score", "ml_score",
            ]
            st.dataframe(
                anomalies[display_cols].sort_values("anomaly_score", ascending=False).reset_index(drop=True),
                use_container_width=True,
                height=400,
            )
            csv_data = anomalies[display_cols].to_csv(index=False).encode("utf-8")
            st.download_button(
                "⬇️ Скачать аномалии (CSV)",
                data=csv_data,
                file_name="anomalies.csv",
                mime="text/csv",
            )
        else:
            st.success("Аномалии не обнаружены, трафик выглядит нормальным")

        st.subheader("Все потоки")
        st.dataframe(
            df.reset_index(drop=True),
            use_container_width=True,
            height=350,
        )

else:
    st.info("Загрузите файл трафика или выберите пример для начала анализа")

    # Пример структуры CSV
    st.subheader("Пример структуры CSV файла")
    example_df = pd.DataFrame({
        "src_ip":   ["192.168.1.10", "10.0.0.5",   "192.168.1.99"],
        "dst_ip":   ["8.8.8.8",      "192.168.1.1", "185.12.44.1"],
        "src_port": [54321,           1024,          45000],
        "dst_port": [443,             80,            4444],
        "protocol": ["TCP",           "TCP",         "TCP"],
        "bytes":    [15420,           800,           9500000],
        "packets":  [22,              5,             15000],
    })
    st.dataframe(example_df, use_container_width=True)
    st.caption("Последняя строка - типичная аномалия (утечка данных): большой объём на нестандартный порт 4444")