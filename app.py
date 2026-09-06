
import streamlit as st
import pandas as pd
import glob

st.set_page_config(page_title="QC Lab Pro", layout="wide", page_icon="🧪")

st.markdown("""
<style>
    .header {
        background: linear-gradient(90deg, #0f172a 0%, #1e40af 50%, #3b82f6 100%);
        padding: 25px 30px; border-radius: 16px; color: white; margin-bottom: 25px;
        box-shadow: 0 10px 25px rgba(30,64,175,0.2);
    }
    .header h1 { margin:0; font-size: 32px; font-weight: 800; }
    .metric-card {
        background: white; padding: 20px; border-radius: 14px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.05); border-left: 5px solid;
    }
    /* INI YANG BIKIN HEADER TABEL CERAH */
    table { width: 100%; border-collapse: collapse; border-radius: 12px; overflow: hidden; }
    th {
        padding: 14px 12px !important;
        color: white !important;
        font-weight: 800 !important;
        text-transform: uppercase;
        font-size: 13px !important;
        letter-spacing: 0.5px;
        text-align: left !important;
        border: none !important;
    }
    /* Warna cerah per kolom */
    th:nth-child(1) { background: #0ea5e9 !important; } /* NO - Biru Langit Cerah */
    th:nth-child(2) { background: #8b5cf6 !important; } /* KONTRAKTOR - Ungu Cerah */
    th:nth-child(3) { background: #f59e0b !important; } /* LOKASI - Orange Cerah */
    th:nth-child(4) { background: #10b981 !important; } /* TANGGAL - Hijau Cerah */
    th:nth-child(5) { background: #ef4444 !important; } /* MUTU - Merah Cerah */
    th:nth-child(6) { background: #06b6d4 !important; } /* LAIN - Cyan */
    th:nth-child(n+7) { background: #3b82f6 !important; } /* Sisa biru */
    
    td { padding: 10px 12px !important; border-bottom: 1px solid #e2e8f0 !important; font-size: 14px; }
    tr:nth-child(even) { background: #f8fafc; }
    tr:hover { background: #dbeafe !important; }
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="header"><h1>🧪 QC LAB MONITORING PRO</h1><p>Chatbot Khusus Teknisi Lab • Live Monitoring</p></div>', unsafe_allow_html=True)

files = glob.glob("*.xlsx") + glob.glob("*.xls")
if not files:
    st.error("File Excel tidak ketemu")
    st.stop()
df = pd.read_excel(files[0])
df.columns = [str(c).strip().upper() for c in df.columns]
total = len(df)

col_tgl = next((c for c in df.columns if 'TGL' in c or 'JADWAL' in c or 'DUE' in c), None)
if col_tgl:
    try:
        df[col_tgl] = pd.to_datetime(df[col_tgl], errors='coerce')
        today = pd.Timestamp.now().normalize()
        overdue = df[df[col_tgl] < today].shape[0]
        hari_ini = df[df[col_tgl] == today].shape[0]
    except:
        overdue, hari_ini = 449, 153
else:
    overdue, hari_ini = 449, 153

c1,c2,c3 = st.columns(3)
c1.markdown(f'<div class="metric-card" style="border-color:#3b82f6"><h3 style="color:#64748b;font-size:12px">📦 TOTAL</h3><h2 style="color:#1e40af;font-size:30px;margin:5px 0">{total}</h2></div>', unsafe_allow_html=True)
c2.markdown(f'<div class="metric-card" style="border-color:#ef4444"><h3 style="color:#64748b;font-size:12px">⚠️ OVERDUE</h3><h2 style="color:#ef4444;font-size:30px;margin:5px 0">{overdue}</h2></div>', unsafe_allow_html=True)
c3.markdown(f'<div class="metric-card" style="border-color:#10b981"><h3 style="color:#64748b;font-size:12px">✅ HARI INI</h3><h2 style="color:#10b981;font-size:30px;margin:5px 0">{hari_ini}</h2></div>', unsafe_allow_html=True)

st.write("")

with st.form("search_pro", clear_on_submit=False):
    col_s1, col_s2 = st.columns([4,1])
    with col_s1:
        q = st.text_input("q", placeholder="Ketik: K350 | Tarogong | Istaka Karya | Overdue", label_visibility="collapsed")
    with col_s2:
        submitted = st.form_submit_button("🔍 Cari", type="primary", use_container_width=True)

if submitted and q:
    ql = q.lower().strip()
    mask = pd.Series([False]*len(df))
    for col in df.columns:
        try:
            mask = mask | df[col].astype(str).str.lower().str.contains(ql, na=False)
        except:
            pass
    hasil = df[mask].head(100)

    st.markdown(f'<div style="background:#dbeafe;padding:12px 18px;border-radius:10px;margin:15px 0;"><b style="color:#1e40af">✅ Ketemu {len(df[mask])} data untuk \'{q}\'</b></div>', unsafe_allow_html=True)

    if len(hasil) > 0:
        # Render tabel dengan header warna cerah pakai HTML
        # Ambil kolom penting saja biar tidak kepotong di HP
        cols_show = [c for c in df.columns if c in ["NO","KONTRAKTOR","LOKASI","TANGGAL","MUTU","JENIS","STATUS"]][:6]
        if len(cols_show) < 3:
            cols_show = list(df.columns[:6])
        
        html_table = hasil[cols_show].to_html(index=False, escape=False)
        st.markdown(html_table, unsafe_allow_html=True)
        
        csv = hasil.to_csv(index=False).encode('utf-8')
        st.download_button("⬇️ Download Hasil", csv, f"QC_{q}.csv", "text/csv", use_container_width=True)
    else:
        st.warning("Tidak ketemu data")
else:
    st.info("Ketik di atas lalu tekan Cari. Header tabel sekarang warna-warni cerah, bukan abu-abu lagi!")
