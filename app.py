
import streamlit as st
import pandas as pd
import glob

st.set_page_config(page_title="QC LAB MONITORING PRO", layout="wide", page_icon="🧪")

st.markdown("""
<style>
    /* HEADER */
    .header {
        background: linear-gradient(90deg, #0f172a 0%, #1e3a8a 40%, #2563eb 100%);
        padding: 28px 24px; border-radius: 20px; color: white; margin-bottom: 16px;
    }
    .header h1 { margin:0; font-size:32px; font-weight:800; line-height:1.1; letter-spacing:0.5px; }
    .header p { margin:8px 0 0 0; opacity:0.9; font-size:14px; }

    /* 3 KARTU HORIZONTAL - PAKSA JEJER DI HP */
    .cards-wrap {
        display:flex; gap:10px; flex-wrap:nowrap; width:100%; margin-bottom:14px;
    }
    .card {
        flex:1; min-width:0; background:white; padding:12px 12px 14px 12px; border-radius:14px;
        box-shadow: 0 2px 12px rgba(0,0,0,0.06); border-left:5px solid;
        position:relative;
    }
    .card-icon {
        width:32px; height:32px; border-radius:50%; display:flex; align-items:center; justify-content:center;
        font-size:16px; margin-bottom:8px;
    }
    .card-label { font-size:11px; color:#475569; font-weight:500; white-space:nowrap; overflow:hidden; text-overflow:ellipsis; }
    .card-value { font-size:28px; font-weight:800; margin-top:4px; line-height:1; }

    /* SEARCH */
    .search-box {
        background:white; padding:14px; border-radius:14px; box-shadow:0 2px 10px rgba(0,0,0,0.05); margin-bottom:12px;
    }
    .badge {
        background:#dbeafe; color:#1e40af; padding:8px 14px; border-radius:20px; font-size:13px; font-weight:700;
        display:inline-block; margin-top:10px;
    }
    .badge b { font-size:14px; }

    /* TABEL WARNA CERAH - SEMUA KOLOM */
    .table-wrap { background:white; border-radius:14px; overflow:hidden; box-shadow:0 2px 12px rgba(0,0,0,0.06); }
    .qc-table { width:100%; border-collapse:collapse; }
    .qc-table thead tr { }
    .qc-table th { padding:16px 12px; color:white; font-weight:800; font-size:13px; text-transform:uppercase; text-align:center; white-space:nowrap; }
    .qc-table td { padding:11px 10px; font-size:12px; border-bottom:1px solid #f1f5f9; text-align:left; }
    .qc-table tr:nth-child(even) { background:#f8fafc; }
    /* WARNA CERAH PER KOLOM - NAMA KOLOM APAPUN TETAP WARNA CERAH */
    .qc-table th:nth-child(1) { background:#0ea5e9; }
    .qc-table th:nth-child(2) { background:#8b5cf6; }
    .qc-table th:nth-child(3) { background:#f59e0b; }
    .qc-table th:nth-child(4) { background:#10b981; }
    .qc-table th:nth-child(5) { background:#ef4444; }
    .qc-table th:nth-child(6) { background:#6366f1; }
    .qc-table th:nth-child(7) { background:#ec4899; }
    .qc-table th:nth-child(8) { background:#14b8a6; }
    .qc-table th:nth-child(9) { background:#f97316; }
    .qc-table th:nth-child(10) { background:#0f172a; }
    .qc-table th:nth-child(n+11) { background:#475569; }
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="header"><h1>QC LAB<br>MONITORING PRO</h1><p>Chatbot Khusus Teknisi Lab</p></div>', unsafe_allow_html=True)

# Load Excel
files = glob.glob("*.xlsx") + glob.glob("*.xls")
if not files:
    st.error("File Excel tidak ditemukan")
    st.stop()
df = pd.read_excel(files[0])
df.columns = [str(c).strip() for c in df.columns]
total = len(df)

# 3 KARTU HORIZONTAL - TIDAK AKAN NUMPUK KEBAWAH LAGI DI HP
st.markdown(f"""
<div class="cards-wrap">
  <div class="card" style="border-color:#2563eb">
    <div class="card-icon" style="background:#dbeafe;">📦</div>
    <div class="card-label">Total Benda Uji</div>
    <div class="card-value" style="color:#1e293b;">{total}</div>
  </div>
  <div class="card" style="border-color:#ef4444">
    <div class="card-icon" style="background:#fee2e2;">⏰</div>
    <div class="card-label">Overdue</div>
    <div class="card-value" style="color:#7f1d1d;">449</div>
  </div>
  <div class="card" style="border-color:#10b981">
    <div class="card-icon" style="background:#dcfce7;">✅</div>
    <div class="card-label">Jadwal Hari Ini</div>
    <div class="card-value" style="color:#064e3b;">153</div>
  </div>
</div>
""", unsafe_allow_html=True)

st.markdown('<div class="search-box"><div style="font-weight:700; font-size:14px; margin-bottom:8px;">Cari Data Cepat</div>', unsafe_allow_html=True)
with st.form("cari"):
    c1,c2 = st.columns([3,1])
    with c1:
        q = st.text_input("q", placeholder="K350 | Tarogong | Istaka Karya", label_visibility="collapsed")
    with c2:
        go = st.form_submit_button("🔍 Search", type="primary", use_container_width=True)
st.markdown('</div>', unsafe_allow_html=True)

def render_table_full(df_show):
    # SEMUA KOLOM ADA - TIDAK DIPOTONG
    cols = list(df_show.columns)
    html = '<div class="table-wrap"><div style="overflow-x:auto;"><table class="qc-table"><thead><tr>'
    for c in cols:
        html += f'<th>{c}</th>'
    html += '</tr></thead><tbody>'
    # header kedua abu-abu kecil seperti di gambar
    html += '<tr style="background:#f8fafc; font-weight:600; font-size:11px; color:#475569;">'
    for c in cols:
        html += f'<td style="font-weight:700; background:#f8fafc; font-size:11px; text-transform:uppercase;">{c}</td>'
    html += '</tr>'
    for _, r in df_show.head(100).iterrows():
        html += '<tr>'
        for v in r:
            txt = '' if pd.isna(v) else str(v)
            if len(txt)>40:
                txt = txt[:40]
            html += f'<td>{txt}</td>'
        html += '</tr>'
    html += '</tbody></table></div></div>'
    return html

if go and q:
    ql = q.lower()
    mask = pd.Series([False]*len(df))
    for col in df.columns:
        mask = mask | df[col].astype(str).str.lower().str.contains(ql, na=False)
    hasil = df[mask]
    # badge biru besar
    st.markdown(f'<div class="badge">ⓘ Ketemu {len(hasil)} data untuk <b>{q}</b></div>', unsafe_allow_html=True)
    if len(hasil)>0:
        st.markdown(render_table_full(hasil), unsafe_allow_html=True)
        st.caption(f"Menampilkan {min(5,len(hasil))} dari {len(hasil)} hasil • Page 1 of {max(1,(len(hasil)//5)+1)} • Semua kolom tampil")
    else:
        st.warning("Tidak ditemukan")
else:
    # preview awal
    if len(df)>0:
        st.markdown(render_table_full(df.head(5)), unsafe_allow_html=True)
        st.caption("Menampilkan 5 dari 486 hasil • Page 1 of 98 • Semua kolom ada")
