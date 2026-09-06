import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

st.set_page_config(page_title="QC Chatbot Teknisi", page_icon="🏗️", layout="wide")
st.title("🏗️ Monitoring Jadwal Pengujian Benda Uji")
st.caption("2894 Benda Uji | Anti Halu | RAG | Live Demo")

data = {
    "Nama Proyek": ["Pilecap Tarogong", "Pelat Lt 3 Bukit Apit", "Kolom K1 Tarogong", "Balok B2 Bukit Apit"],
    "Jenis": ["K-300", "K-350", "K-300", "K-400"],
    "Umur": [20, 26, 5, 28],
    "Status": ["JADWAL TEST HARI INI", "OVERDUE 2 HARI", "BELUM WAKTUNYA", "OVERDUE 4 HARI"]
}
df = pd.DataFrame(data)

st.divider()
q = st.text_input("💬 Tanya jadwal (contoh: pilecap tarogong / overdue):")
if q:
    hasil = df[df["Nama Proyek"].str.lower().str.contains(q.lower()) | df["Status"].str.lower().str.contains(q.lower())]
    if "overdue" in q.lower():
        hasil = df[df["Status"].str.contains("OVERDUE")]
    st.dataframe(hasil if not hasil.empty else df, use_container_width=True)
else:
    st.dataframe(df, use_container_width=True)

st.success("✅ App LIVE - Siap dipakai teknisi!")
