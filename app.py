import streamlit as st
import pandas as pd
import os
import glob

st.set_page_config(page_title="QC Teknisi Lab", layout="wide")

st.title("Monitoring Jadwal Pengujian Benda Uji")
st.caption("Live Demo untuk Teknisi Lab")

@st.cache_data
def load_data():
    files = glob.glob("*.xlsx")
    if not files:
        return pd.DataFrame()
    # ambil file terbesar (yang 2892)
    files = sorted(files, key=lambda p: os.path.getsize(p), reverse=True)
    for fname in files:
        try:
            df = pd.read_excel(fname)
            return df
        except:
            continue
    return pd.DataFrame()

df = load_data()

if df.empty:
    st.error("File Excel tidak ketemu. Upload file .xlsx")
    st.stop()

# Buat status simpel tanpa f-string rumit
if "STATUS" not in df.columns:
    if "TGL_28HARI" in df.columns:
        df["TGL_28HARI"] = pd.to_datetime(df["TGL_28HARI"], errors="coerce")
        today = pd.Timestamp.now().normalize()
        def buat_status(tgl):
            if pd.isna(tgl):
                return "TGL KOSONG"
            selisih = (today - tgl).days
            if selisih == 0:
                return "JADWAL TEST HARI INI"
            if selisih > 0:
                return "OVERDUE"
            return "HARI LAGI"
        df["STATUS"] = df["TGL_28HARI"].apply(buat_status)

total = len(df)
overdue = len(df[df["STATUS"].astype(str).str.contains("OVERDUE", case=False, na=False)]) if "STATUS" in df.columns else 0
hari_ini = len(df[df["STATUS"].astype(str).str.contains("HARI INI", case=False, na=False)]) if "STATUS" in df.columns else 0

c1, c2, c3 = st.columns(3)
c1.metric("Total", total)
c2.metric("Overdue", overdue)
c3.metric("Jadwal Hari Ini", hari_ini)

st.divider()

st.subheader("Chatbot Khusus Buat Teknisi Lab")
st.caption("Tanya: Tarogong, K300, Overdue, Hari Ini")

if "messages" not in st.session_state:
    st.session_state.messages = []
    st.session_state.messages.append({"role": "assistant", "content": f"Halo! Ada {total} data siap. Tanya lokasi atau mutu."})

for m in st.session_state.messages:
    with st.chat_message(m["role"]):
        st.markdown(m["content"])

prompt = st.chat_input("Ketik pertanyaan...")

if prompt:
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    ql = prompt.lower()
    mask = pd.Series([False]*len(df))
    for col in df.columns:
        try:
            mask = mask | df[col].astype(str).str.lower().str.contains(ql.split()[0], na=False)
        except:
            pass

    hasil = df[mask] if mask.any() else pd.DataFrame()

    if hasil.empty:
        ans = f"Tidak ketemu untuk '{prompt}'. Coba Tarogong / K300 / Overdue."
    else:
        ans = f"Ketemu {len(hasil)} data untuk '{prompt}' dari total {total}."

    with st.chat_message("assistant"):
        st.markdown(ans)
        if not hasil.empty:
            st.dataframe(hasil.head(100), use_container_width=True)

    st.session_state.messages.append({"role": "assistant", "content": ans})

st.sidebar.success(f"LIVE {total} Data")
                
