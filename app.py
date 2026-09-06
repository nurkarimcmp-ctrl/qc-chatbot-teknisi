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
if df.empty:
    st.stop()

# Status
if 'STATUS' not in df.columns and 'TGL_28HARI' in df.columns:
    try:
        df['TGL_28HARI'] = pd.to_datetime(df['TGL_28HARI'], errors='coerce')
        today = pd.Timestamp.now().normalize()
        df['STATUS'] = df['TGL_28HARI'].apply(lambda x: "JADWAL TEST HARI INI" if pd.notna(x) and (today - x).days==0 else f"OVERDUE {(today - x).days} HARI" if pd.notna(x) and (today - x).days>0 else f"{abs((today - x).days)} HARI LAGI" if pd.notna(x) else "TGL KOSONG")
    except:
        pass

c1,c2,c3 = st.columns(3)
total = len(df)
overdue = len(df[df['STATUS'].astype(str).str.contains('OVERDUE', case=False, na=False)]) if 'STATUS' in df.columns else 0
today_count = len(df[df['STATUS'].astype(str).str.contains('HARI INI', case=False, na=False)]) if 'STATUS' in df.columns else 0

c1.metric("Total", total)
c2.metric("Overdue", overdue)
c3.metric("Jadwal Hari Ini", today_count)

st.divider()

# JUDUL BARU SESUAI REQUEST
st.subheader("Chatbot Khusus Buat Teknisi Lab")
st.caption("Tanya: Tarogong ada berapa? / K300 overdue mana? / jadwal hari ini")

if "messages" not in st.session_state:
    st.session_state.messages = [{"role":"assistant","content": f"Halo Pak Teknisi! Ada {total} data benda uji siap. Silakan tanya jadwal, lokasi, atau mutu."}]

for m in st.session_state.messages:
    with st.chat_message(m["role"]):
        st.markdown(m["content"])

if prompt := st.chat_input("Ketik pertanyaan teknisi..."):
    st.session_state.messages.append({"role":"user","content":prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    ql = prompt.lower()
    mask = pd.Series([False]*len(df))
    keywords = ql.split()
    for kw in keywords:
        if len(kw) < 2:
            continue
        for col in df.columns:
            try:
                mask = mask | df[col].astype(str).str.lower().str.contains(kw, na=False)
            except:
                pass
    
    hasil = df[mask] if mask.any() else pd.DataFrame()
    if "overdue" in ql and 'STATUS' in df.columns:
        f_over = df[df['STATUS'].astype(str).str.contains('OVERDUE', case=False, na=False)]
        hasil = f_over if hasil.empty else hasil[hasil['STATUS'].astype(str).str.contains('OVERDUE', case=False, na=False)]
    if "hari ini" in ql and 'STATUS' in df.columns:
        f_today = df[df['STATUS'].astype(str).str.contains('HARI INI', case=False, na=False)]
        hasil = f_today if hasil.empty else hasil[hasil['STATUS'].astype(str).str.contains('HARI INI', case=False, na=False)]

    if hasil.empty:
        ans = f"Tidak ada data untuk '{prompt}' di {total} data. Coba kata: Tarogong, Bukit Apit, K300, Overdue, Jadwal Hari Ini."
    else:
        ans = f"Ketemu {len(hasil)} data untuk '{prompt}' dari total {total}\n\n"
        if 'LOKASI_SIMPLE' in hasil.columns:
            top = hasil['LOKASI_SIMPLE'].value_counts().head(3)
            ans += f"Lokasi: {', '.join([f'{k} ({v})' for k,v in top.items()])}. "
        if 'MUTU' in hasil.columns:
            topm = hasil['MUTU'].value_counts().head(3)
            ans += f"Mutu: {', '.join([f'{k} ({v})' for k,v in topm.items()])}."

    with st.chat_message("assistant"):
        st.markdown(ans)
        if not hasil.empty:
            st.dataframe(hasil.head(100), use_container_width=True)

    st.session_state.messages.append({"role":"assistant","content":ans})

st.sidebar.success(f"LIVE {len(df)} Data")
st.sidebar.caption("Chatbot Khusus Buat Teknisi Lab - Anti Halu RAG")
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
