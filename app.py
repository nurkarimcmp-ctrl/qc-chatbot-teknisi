import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

st.set_page_config(page_title="QC Chatbot Teknisi", page_icon="🏗️", layout="wide")
st.title("🏗️ Monitoring Jadwal Pengujian Benda Uji")
st.caption("2894 Benda Uji | Anti Halu | RAG | Live Demo untuk Teknisi")

with st.sidebar:
    st.header("📁 Upload Data")
    uploaded = st.file_uploader("Upload Excel 2894 (.xlsx)", type=["xlsx","xls","csv"])
    st.info("Belum upload = pakai data contoh dulu")

if uploaded:
    try:
        df = pd.read_excel(uploaded) if not uploaded.name.endswith(".csv") else pd.read_csv(uploaded)
        st.sidebar.success(f"✅ {len(df)} data ter-load!")
    except Exception as e:
        st.error(f"Error: {e}")
        df = None
else:
    data = {
        "Nama Proyek": ["Pilecap Tarogong", "Pelat Lt 3 Bukit Apit", "Kolom K1 Tarogong", "Balok B2 Bukit Apit"],
        "Jenis": ["K-300", "K-350", "K-300", "K-400"],
        "Umur": [20, 26, 5, 28],
        "Status": ["JADWAL TEST HARI INI", "OVERDUE 2 HARI", "BELUM WAKTUNYA", "OVERDUE 4 HARI"]
    }
    df = pd.DataFrame(data)

if df is not None:
    st.divider()
    c1,c2,c3 = st.columns(3)
    c1.metric("Total", len(df))
    c2.metric("Overdue", len(df[df.astype(str).apply(lambda x: x.str.contains('OVERDUE', case=False, na=False)).any(axis=1)]))
    c3.metric("Jadwal Hari Ini", len(df[df.astype(str).apply(lambda x: x.str.contains('HARI INI', case=False, na=False)).any(axis=1)]))

    st.subheader("💬 Chatbot QC (Anti Halu)")
    q = st.text_input("Tanya: pilecap / overdue / bukit apit", placeholder="Ketik di sini...")

    if q:
        ql = q.lower()
        hasil = df[df.apply(lambda r: r.astype(str).str.lower().str.contains(ql, na=False).any(), axis=1)]
        if hasil.empty:
            st.error(f"❌ TIDAK ADA '{q}' di database. Saya tidak mengarang.")
        else:
            st.success(f"✅ Ketemu {len(hasil)} data untuk '{q}'")
            st.dataframe(hasil, use_container_width=True)
    else:
        st.dataframe(df, use_container_width=True)
    st.success("✅ App LIVE")
