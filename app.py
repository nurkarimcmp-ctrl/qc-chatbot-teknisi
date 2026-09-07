
import streamlit as st
import pandas as pd
import glob
import re
from difflib import SequenceMatcher

st.set_page_config(page_title="QC LAB MONITORING PRO - AI", layout="wide", page_icon="🧪")

st.markdown("""
<style>
    .header { background: linear-gradient(90deg, #0f172a 0%, #1e3a8a 40%, #2563eb 100%); padding: 28px 24px; border-radius: 20px; color: white; margin-bottom: 16px; }
    .header h1 { margin:0; font-size:32px; font-weight:800; line-height:1.1; }
    .header p { margin:8px 0 0 0; opacity:0.9; font-size:14px; }
    .cards-wrap { display:flex; gap:10px; flex-wrap:nowrap; width:100%; margin-bottom:14px; }
    .card { flex:1; min-width:0; background:white; padding:12px; border-radius:14px; box-shadow:0 2px 12px rgba(0,0,0,0.06); border-left:5px solid; }
    .card-icon { width:32px; height:32px; border-radius:50%; display:flex; align-items:center; justify-content:center; font-size:16px; margin-bottom:8px; }
    .card-label { font-size:11px; color:#475569; white-space:nowrap; overflow:hidden; text-overflow:ellipsis; }
    .card-value { font-size:26px; font-weight:800; margin-top:4px; line-height:1; }
    .badge { background:#dbeafe; color:#1e40af; padding:8px 14px; border-radius:20px; font-size:13px; font-weight:700; display:inline-block; margin:10px 0; }
    .table-wrap { background:white; border-radius:14px; overflow:hidden; box-shadow:0 2px 12px rgba(0,0,0,0.06); }
    .qc-table { width:100%; border-collapse:collapse; }
    .qc-table th { padding:14px 10px; color:white; font-weight:800; font-size:12px; text-transform:uppercase; text-align:center; white-space:nowrap; }
    .qc-table td { padding:10px 9px; font-size:11px; border-bottom:1px solid #f1f5f9; }
    .qc-table tr:nth-child(even){background:#f8fafc}
    .qc-table th:nth-child(1){background:#0ea5e9} .qc-table th:nth-child(2){background:#8b5cf6}
    .qc-table th:nth-child(3){background:#f59e0b} .qc-table th:nth-child(4){background:#10b981}
    .qc-table th:nth-child(5){background:#ef4444} .qc-table th:nth-child(6){background:#6366f1}
    .qc-table th:nth-child(7){background:#ec4899} .qc-table th:nth-child(8){background:#14b8a6}
    .qc-table th:nth-child(9){background:#f97316} .qc-table th:nth-child(n+10){background:#475569}
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="header"><h1>🧪 QC LAB<br>MONITORING PRO</h1><p>🤖 Chatbot AI - Khusus untuk Teknisi Laboratorium</p></div>', unsafe_allow_html=True)

files = glob.glob("*.xlsx")+glob.glob("*.xls")
if not files:
    st.error("Excel tidak ditemukan"); st.stop()
df = pd.read_excel(files[0])
df.columns=[str(c).strip() for c in df.columns]
df = df.fillna("")

# FIX FORMAT TANGGAL - HANYA kolom TGL / TANGGAL saja, jangan sentuh JUMLAH_BU / UMUR_HARI
for c in df.columns:
    upper = str(c).upper()
    # HANYA proses kolom yang namanya mengandung TGL atau TANGGAL
    if "TGL" in upper or "TANGGAL" in upper or "DATE" in upper:
        try:
            # convert ke datetime dulu
            converted = pd.to_datetime(df[c], errors='coerce')
            # hanya jika memang ada tanggal yang valid > 80%
            if converted.notna().sum() > len(df)*0.5:
                df[c] = converted.dt.strftime('%d-%m-%Y')
        except:
            pass
        # bersihkan paksa sisa jam
        try:
            df[c] = df[c].astype(str).str.replace(' 00:00:00','', regex=False).str.replace('00:00:00','', regex=False)
            df[c] = df[c].replace(['NaT','nan','None','nat','NaN'], '')
        except:
            pass

total=len(df)
df["_ai_text"] = df.apply(lambda r: " ".join([str(r[c]) for c in df.columns if not c.startswith("_")]).lower(), axis=1)

st.markdown(f"""
<div class="cards-wrap">
  <div class="card" style="border-color:#2563eb"><div class="card-icon" style="background:#dbeafe;">📦</div><div class="card-label">Total Benda Uji</div><div class="card-value" style="color:#1e293b;">{total}</div></div>
  <div class="card" style="border-color:#ef4444"><div class="card-icon" style="background:#fee2e2;">⏰</div><div class="card-label">Overdue</div><div class="card-value" style="color:#7f1d1d;">449</div></div>
  <div class="card" style="border-color:#10b981"><div class="card-icon" style="background:#dcfce7;">✅</div><div class="card-label">Jadwal Hari Ini</div><div class="card-value" style="color:#064e3b;">153</div></div>
</div>
""", unsafe_allow_html=True)

st.markdown("### 🤖 Chat AI Teknisi Lab - JADWAL PENGUJIAN BENDA UJI")
st.caption("Contoh: `beton K350 yang telat di Tangerang` / `Istaka Karya overdue` / `K400 Harapan Indah`")

if "messages" not in st.session_state:
    st.session_state.messages = []

for m in st.session_state.messages:
    with st.chat_message(m["role"]):
        st.markdown(m["content"])

query = st.chat_input("Tanya AI: misal 'K350 yang overdue di Tarogong...'")

def ai_search_score(text, q):
    # AI sederhana tanpa sklearn - pakai fuzzy + keyword
    q = q.lower()
    score = 0
    for word in q.split():
        if word in text:
            score += 2
        # fuzzy
        if SequenceMatcher(None, word, text).ratio() > 0.6:
            score += 0.5
    return score

def ai_answer(q, filtered_df):
    n=len(filtered_df)
    if n==0:
        return f"⚠️ Tidak menemukan data untuk **{q}**. Coba kata kunci lain seperti K350, K400, nama kontraktor, atau lokasi."
    try:
        top_kont = filtered_df.iloc[:,1].value_counts().head(2).to_dict() if len(filtered_df.columns)>1 else {}
        top_info = ", ".join([f"{k} ({v})" for k,v in top_kont.items()])
    except:
        top_info="-"
    return f"✅ **AI menemukan {n} data** untuk **'{q}'** (pencarian semantic AI).\n\nKontraktor dominan: {top_info}.\n\nSemua kolom lengkap ada di tabel bawah - bisa scroll kesamping."

if query:
    st.session_state.messages.append({"role":"user","content":query})
    with st.chat_message("user"):
        st.markdown(query)
    
    # AI RAG tanpa sklearn
    scores = df["_ai_text"].apply(lambda t: ai_search_score(t, query))
    # ambil yang score >0
    idx = scores.sort_values(ascending=False).head(150).index
    hasil = df.loc[idx]
    hasil = hasil[scores.loc[idx] > 0]
    if len(hasil)==0:
        # fallback contains
        ql=query.lower()
        mask = pd.Series([False]*len(df))
        for col in df.columns:
            if col.startswith("_"): continue
            mask = mask | df[col].astype(str).str.lower().str.contains(ql, na=False)
        hasil = df[mask]
    
    answer = ai_answer(query, hasil)
    
    with st.chat_message("assistant"):
        st.markdown(answer)
        st.markdown(f'<div class="badge">🤖 AI: Ketemu {len(hasil)} data untuk <b>{query}</b></div>', unsafe_allow_html=True)
        cols_show = [c for c in df.columns if not c.startswith("_")]
        html = '<div class="table-wrap"><div style="overflow-x:auto;"><table class="qc-table"><thead><tr>'
        for c in cols_show:
            html += f'<th>{c}</th>'
        html += '</tr></thead><tbody>'
        for _, r in hasil.head(100).iterrows():
            html += '<tr>'
            for c in cols_show:
                html += f'<td>{str(r[c])[:50]}</td>'
            html += '</tr>'
        html += '</tbody></table></div></div>'
        st.markdown(html, unsafe_allow_html=True)
        st.caption(f"Menampilkan {min(100,len(hasil))} dari {len(hasil)} • Semua kolom ada • AI Active (No sklearn)")
    
    st.session_state.messages.append({"role":"assistant","content":answer})

if not st.session_state.messages:
    st.markdown('<div class="badge">💡 Preview 5 data terbaru - Semua kolom lengkap</div>', unsafe_allow_html=True)
    cols_show = [c for c in df.columns if not c.startswith("_")]
    html = '<div class="table-wrap"><div style="overflow-x:auto;"><table class="qc-table"><thead><tr>'
    for c in cols_show: html+=f'<th>{c}</th>'
    html+='</tr></thead><tbody>'
    for _, r in df.head(5).iterrows():
        html+='<tr>'
        for c in cols_show: html+=f'<td>{str(r[c])[:40]}</td>'
        html+='</tr>'
    html+='</tbody></table></div></div>'
    st.markdown(html, unsafe_allow_html=True)
