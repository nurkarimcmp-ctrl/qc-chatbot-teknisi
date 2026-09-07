
import streamlit as st
import pandas as pd
import glob
import re
from difflib import SequenceMatcher

st.set_page_config(page_title="QC LAB MONITORING PRO - AI", layout="wide", page_icon="🧪")

st.markdown("""
<style>
    .header { background: linear-gradient(90deg, #0f172a 0%, #1e3a8a 40%, #2563eb 100%); padding: 12px 16px; border-radius: 14px; color: white; margin-bottom: 10px; }
    .header h1 { margin:0; font-size:20px; font-weight:800; line-height:1.1; }
    .header p { margin:4px 0 0 0; opacity:0.9; font-size:12px; }
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

st.markdown('<div class="header"><h1>🧪 QC-LAB<br>MONITORING PRO</h1><p>🤖 Chatbot AI - Khusus Teknisi Lab</p></div>', unsafe_allow_html=True)

files = glob.glob("*.xlsx")+glob.glob("*.xls")
if not files:
    st.error("Excel tidak ditemukan"); st.stop()
df = pd.read_excel(files[0])
df.columns=[str(c).strip() for c in df.columns]
df = df.fillna("")

# FIX FORMAT TANGGAL - HANYA kolom TGL / TANGGAL
for c in df.columns:
    upper = str(c).upper()
    if "TGL" in upper or "TANGGAL" in upper or "DATE" in upper:
        try:
            converted = pd.to_datetime(df[c], errors='coerce')
            if converted.notna().sum() > len(df)*0.5:
                df[c] = converted.dt.strftime('%d-%m-%Y')
        except:
            pass
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

st.markdown("### 🤖 Chat AI Lab - Jadwal Pengujian Benda Uji")
st.caption("Contoh: `beton K350 yang telat` / `Semua proyek dengan mutu K250` / `Istaka Karya overdue`")

if "messages" not in st.session_state:
    st.session_state.messages = []

for m in st.session_state.messages:
    with st.chat_message(m["role"]):
        st.markdown(m["content"])

query = st.chat_input("Tanya AI: misal 'Semua proyek dengan mutu K250'")

# ===== AI INTENT EXTRACTION - INI KUNCINYA BIAR JADI CHATBOT AI BENERAN =====
GENERIC_WORDS = {"semua","proyek","project","dengan","mutu","yang","untuk","dan","di","ke","dari","adalah","ada","tampilkan","tampil","cari","carikan","lihat","tolong","data","kontraktor","pt","pt.","cv","tbk","karya","berapa","list","daftar","punya","milik"}

def extract_core_tokens(q):
    q = q.lower()
    tokens = []
    # 1. Cari mutu beton Kxxx - INI PALING PENTING
    k_matches = re.findall(r'k\s*-?\s*\d+', q)
    for km in k_matches:
        clean = re.sub(r'[^k0-9]', '', km.replace(' ', ''))
        # jadi k250
        if clean.startswith('k'):
            tokens.append(clean)
    # 2. Cari angka mutu lain seperti 250, 350 jika didahului kata mutu
    if "mutu" in q and not tokens:
        nums = re.findall(r'\b(\d{3,4})\b', q)
        for n in nums:
            tokens.append(f"k{n}")
    
    # 3. Cari nama kontraktor penting - istaka, hutama, waskita, dll
    # ambil kata yang bukan generic dan panjang >3
    words = [w.strip(".,()") for w in q.split()]
    for w in words:
        wl = w.lower()
        if wl in GENERIC_WORDS:
            continue
        if len(wl) < 3:
            continue
        # kalau sudah ada di tokens Kxxx jangan duplikat
        if wl.startswith('k') and wl[1:].isdigit():
            continue
        # kata penting seperti istaka, hutama, tangerang, lokasi
        if wl not in tokens:
            tokens.append(wl)
    
    # Kalau setelah filter kosong, ambil kata terpanjang sebagai fallback
    if not tokens:
        words2 = [w for w in q.split() if len(w) > 2]
        if words2:
            tokens = [words2[-1].lower()]
    return tokens

def ai_search_score(text, q):
    q_lower = q.lower().strip()
    text = text.lower()
    score = 0
    
    core_tokens = extract_core_tokens(q_lower)
    if not core_tokens:
        return 0
    
    # Jika ada token Kxxx, itu WAJIB ada
    k_tokens = [t for t in core_tokens if t.startswith('k') and t[1:].isdigit()]
    other_tokens = [t for t in core_tokens if t not in k_tokens]
    
    # Cek K tokens dulu
    if k_tokens:
        # semua K harus ada (biasanya cuma 1)
        for kt in k_tokens:
            # toleransi: k250 bisa tertulis "K-250" atau "K 250" atau "K250"
            pattern = kt[1:]  # 250
            if kt in text or pattern in text or f"k-{pattern}" in text or f"k {pattern}" in text:
                score += 50
            else:
                return 0  # K tidak cocok -> gagal
    
    # Cek token lain (istaka, hutama, dll)
    if other_tokens:
        # untuk kontraktor, semua token penting harus ada
        # tapi kalau tokennya cuma "karya" yang generic, sudah dihapus
        for ot in other_tokens:
            if ot in text:
                score += 20
            else:
                # kalau cari istaka karya, istaka wajib ada
                if ot in ["istaka","hutama","waskita","adhi","wika","pp","wasita"]:
                    return 0
    
    # Bonus exact phrase
    if q_lower in text:
        score += 30
    
    return score

def ai_answer(q, filtered_df):
    n=len(filtered_df)
    if n==0:
        return f"⚠️ Tidak menemukan data untuk **{q}**. Coba kata kunci lain seperti K250, K350, K400, Istaka Karya, dll."
    try:
        top_kont = filtered_df.iloc[:,1].value_counts().head(2).to_dict() if len(filtered_df.columns)>1 else {}
        top_info = ", ".join([f"{k} ({v})" for k,v in top_kont.items()])
    except:
        top_info="-"
    cores = extract_core_tokens(q)
    return f"✅ **AI menemukan {n} data** untuk **'{q}'**\n\nKata kunci inti yang dipahami AI: **{', '.join(cores)}**\n\nKontraktor dominan: {top_info}."

if query:
    st.session_state.messages.append({"role":"user","content":query})
    with st.chat_message("user"):
        st.markdown(query)
    
    core = extract_core_tokens(query)
    scores = df["_ai_text"].apply(lambda t: ai_search_score(t, query))
    idx = scores.sort_values(ascending=False).head(300).index
    hasil = df.loc[idx]
    hasil = hasil[scores.loc[idx] > 0]
    
    # Fallback super pintar: kalau score 0, coba cari pakai core tokens langsung
    if len(hasil)==0 and core:
        mask = pd.Series([True]*len(df))
        for token in core:
            if token.startswith('k'):
                num = token[1:]
                mask_token = pd.Series([False]*len(df))
                for col in df.columns:
                    if col.startswith("_"): continue
                    mask_token = mask_token | df[col].astype(str).str.lower().str.contains(token, na=False) | df[col].astype(str).str.lower().str.contains(num, na=False)
                mask = mask & mask_token
            else:
                mask_token = pd.Series([False]*len(df))
                for col in df.columns:
                    if col.startswith("_"): continue
                    mask_token = mask_token | df[col].astype(str).str.lower().str.contains(token, na=False)
                mask = mask & mask_token
        hasil = df[mask]
    
    answer = ai_answer(query, hasil)
    
    with st.chat_message("assistant"):
        st.markdown(answer)
        st.markdown(f'<div class="badge">🤖 AI Intent: {", ".join(core)} • Ketemu {len(hasil)} data</div>', unsafe_allow_html=True)
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
        st.caption(f"Menampilkan {min(100,len(hasil))} dari {len(hasil)}")
    
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
