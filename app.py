import streamlit as st
import pandas as pd
import os

st.set_page_config(page_title="QC Teknisi Lab", page_icon="🏗️", layout="wide")
st.title("Monitoring Jadwal Pengujian Benda Uji")
st.caption("2892 Benda Uji | RAG | Live Demo untuk Teknisi Lab")

@st.cache_data
def load_data():
    files = ["qc_clean_GITHUB_DEMO.xlsx","qc_clean_2894.xlsx","qc_clean_GITHUB_2894.xlsx"]
    for fname in files:
        if os.path.exists(fname):
            try:
                df = pd.read_excel(fname)
                return df
            except:
                continue
    return pd.DataFrame()

df = load_data()
if df.empty:
    st.error("File Excel tidak ketemu di Github. Upload qc_clean_GITHUB_DEMO.xlsx")
    st.stop()

# Status
if 'STATUS' not in df.columns and 'TGL_28HARI' in df.columns:
    df['TGL_28HARI'] = pd.to_datetime(df['TGL_28HARI'], errors='coerce')
    today = pd.Timestamp.now().normalize()
    def get_status(x):
        if pd.isna(x):
            return "TGL KOSONG"
        diff = (today - x).days
        if diff == 0:
            return "JADWAL TEST HARI INI"
        elif diff > 0:
            return f"OVERDUE {diff} HARI"
        else:
            return f"{abs(diff)} HARI LAGI"
    df['STATUS'] = df['TGL_28HARI'].apply(get_status)

c1, c2, c3 = st.columns(3)
c1.metric("Total", len(df))
c2.metric("Overdue", len(df[df['STATUS'].astype(str).str.contains('OVERDUE', case=False, na=False)]))
c3.metric("Jadwal Hari Ini", len(df[df['STATUS'].astype(str).str.contains('HARI INI', case=False, na=False)]))

st.divider()

st.subheader("Chatbot Khusus Buat Teknisi Lab")
st.caption("Contoh: Tarogong, Bukit Apit, K300, Overdue, Jadwal Hari Ini")

if "messages" not in st.session_state:
    st.session_state.messages = [{"role":"assistant","content":"Halo Pak Teknisi! Ada 2892 data benda uji. Silakan tanya: Tarogong, K300, Overdue"}]

for m in st.session_state.messages:
    with st.chat_message(m["role"]):
        st.markdown(m["content"])

if prompt := st.chat_input("Ketik pertanyaan..."):
    st.session_state.messages.append({"role":"user","content":prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    ql = prompt.lower()
    mask = pd.Series([False]*len(df))
    for col in df.columns:
        try:
            mask = mask | df[col].astype(str).str.lower().str.contains(ql, na=False)
        except:
            pass

    hasil = df[mask]

    if "overdue" in ql:
        hasil = df[df['STATUS'].astype(str).str.contains('OVERDUE', case=False, na=False)]
    if "hari ini" in ql:
        hasil = df[df['STATUS'].astype(str).str.contains('HARI INI', case=False, na=False)]

    if hasil.empty:
        ans = f"Tidak ada data untuk '{prompt}' di {len(df)} data. Coba kata lain: Tarogong, Bukit Apit, K300"
    else:
        ans = f"Ketemu {len(hasil)} data untuk '{prompt}' dari total {len(df)}"

    with st.chat_message("assistant"):
        st.markdown(ans)
        if not hasil.empty:
            st.dataframe(hasil.head(100), use_container_width=True)

    st.session_state.messages.append({"role":"assistant","content":ans})
