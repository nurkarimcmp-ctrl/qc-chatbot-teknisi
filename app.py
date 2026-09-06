
import streamlit as st
import pandas as pd
import os

st.set_page_config(page_title="QC Teknisi Lab - 2892", page_icon="🏗️", layout="wide")

st.title("🏗️ Monitoring Jadwal Pengujian Benda Uji")
st.caption("2892 Benda Uji | RAG | Live Demo untuk Teknisi Lab")

@st.cache_data
def load_data():
    today = pd.Timestamp.now().normalize()
    possible = ["qc_clean_GITHUB_DEMO.xlsx","qc_clean_2894.xlsx","qc_clean_GITHUB_2894.xlsx","qc_clean_2894_FINAL.xlsx"]
    df = None
    used = ""
    for fname in possible:
        if os.path.exists(fname):
            try:
                df = pd.read_excel(fname)
                used = fname
                break
            except:
                continue
    if df is None:
        st.error("⚠️ File xlsx tidak ketemu! Upload file qc_clean_GITHUB_DEMO.xlsx ke Github")
        return pd.DataFrame()
    return df

df = load_data()
if df.empty:
    st.stop()

# Pastikan kolom ada
if 'STATUS' not in df.columns and 'TGL_28HARI' in df.columns:
    df['TGL_28HARI'] = pd.to_datetime(df['TGL_28HARI'], errors='coerce')
    today = pd.Timestamp.now().normalize()
    df['STATUS'] = df['TGL_28HARI'].apply(lambda x: "JADWAL TEST HARI INI" if pd.notna(x) and (today - x).days==0 else f"OVERDUE {(today - x).days} HARI" if pd.notna(x) and (today - x).days>0 else f"{abs((today - x).days)} HARI LAGI" if pd.notna(x) else "TGL KOSONG")

c1,c2,c3 = st.columns(3)
c1.metric("Total", len(df))
c2.metric("Overdue", len(df[df['STATUS'].astype(str).str.contains('OVERDUE', case=False, na=False)]))
c3.metric("Jadwal Hari Ini", len(df[df['STATUS'].astype(str).str.contains('HARI INI', case=False, na=False)]))

st.divider()

# INI YANG SUDAH DIGANTI - Sesuai request kamu
st.subheader("💬 Chatbot Khusus Buat Teknisi Lab")
st.caption("Tanya pakai bahasa natural: 'Tarogong ada berapa?' / 'K300 yang overdue mana?' / 'jadwal hari ini'")

if "messages" not in st.session_state:
    st.session_state.messages = [{"role":"assistant","content":"Halo Pak Teknisi! Saya chatbot khusus buat teknisi lab. Ada 2892 data benda uji siap. Silakan tanya jadwal, lokasi, atau mutu. Contoh: ketik Tarogong"}]

for m in st.session_state.messages:
    with st.chat_message(m["role"]):
        st.markdown(m["content"])

if prompt := st.chat_input("Ketik pertanyaan teknisi..."):
    st.session_state.messages.append({"role":"user","content":prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    ql = prompt.lower()
    # RAG Filter
    mask = pd.Series([False]*len(df))
    for col in df.columns:
        try:
            mask = mask | df[col].astype(str).str.lower().str.contains(ql.split()[0], na=False)
        except:
            pass
    # kata kunci tambahan
    for kw in ["tarogong","bukit","k300","k250","k225","overdue","hari ini","pilecap","sloof"]:
        if kw in ql:
            mask = mask | df.apply(lambda r: r.astype(str).str.lower().str.contains(kw, na=False).any(), axis=1)
    
    hasil = df[mask] if mask.any() else pd.DataFrame()
    if "overdue" in ql:
        hasil = df[df['STATUS'].astype(str).str.contains('OVERDUE', case=False, na=False)] if hasil.empty else hasil[hasil['STATUS'].astype(str).str.contains('OVERDUE', case=False, na=False)]
    if "hari ini" in ql:
        hasil = df[df['STATUS'].astype(str).str.contains('HARI INI', case=False, na=False)] if hasil.empty else hasil[hasil['STATUS'].astype(str).str.contains('HARI INI', case=False, na=False)]

    if hasil.empty:
        ans = f"❌ Tidak ada data untuk '{prompt}' di {len(df)} data. Coba kata: Tarogong, Bukit Apit, K300, Overdue, Jadwal Hari Ini. (Saya tidak mengarang)"
    else:
        ans = f"✅ **Ketemu {len(hasil)} data untuk '{prompt}' dari total {len(df)}**\n\n"
        if 'LOKASI_SIMPLE' in hasil.columns:
            top = hasil['LOKASI_SIMPLE'].value_counts().head(2)
            ans += f"Lokasi: {', '.join([f'{k} ({v})' for k,v in top.items()])}. "
        if 'MUTU' in hasil.columns:
            topm = hasil['MUTU'].value_counts().head(2)
            ans += f"Mutu dominan: {', '.join([f'{k} ({v})' for k,v in topm.items()])}."
        ans += "\n\n📋 Detail tabel di bawah."

    with st.chat_message("assistant"):
        st.markdown(ans)
        if not hasil.empty:
            st.dataframe(hasil.head(100), use_container_width=True, height=350)

    st.session_state.messages.append({"role":"assistant","content":ans})

st.sidebar.success(f"✅ LIVE {len(df)} Data")
st.sidebar.caption("Chatbot Khusus Buat Teknisi Lab - Anti Halu RAG")
    st.subheader("💬 Chatbot Khusus untuk Teknisi Lab")
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
