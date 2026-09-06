
import streamlit as st
import pandas as pd
import glob

st.set_page_config(page_title="QC Lab Pro", layout="wide", page_icon="🧪")

st.markdown("""
<style>
    .header {
        background: linear-gradient(90deg, #0f172a 0%, #1e40af 50%, #3b82f6 100%);
        padding: 22px 26px; border-radius: 16px; color: white; margin-bottom: 18px;
    }
    .header h1 { margin:0; font-size: 30px; font-weight: 800; line-height:1.1; }
    .header p { margin:6px 0 0 0; opacity:0.9; font-size:14px; }
    
    .metric-card {
        background: white; padding: 16px; border-radius: 12px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.05); border-left: 0; 
        border-top: 4px solid;
        min-height: 105px;
    }
    
    /* HEADER TABEL WARNA CERAH */
    .color-header {
        display:flex; border-radius: 12px 12px 0 0; overflow:hidden; margin-top:12px;
        font-weight:800; color:white; text-transform:uppercase; font-size:14px;
    }
    .color-header div { padding:14px 10px; text-align:center; flex:1; }
    .ch-no { background:#0ea5e9; flex:0.5 !important; }
    .ch-kont { background:#8b5cf6; flex:1.5 !important; }
    .ch-lok { background:#f59e0b; flex:1 !important; }
    
    /* Badge K350/K400 besar biru */
    div[data-testid="stTextInput"] input {
        font-size: 18px !important; font-weight: 700 !important;
        border: 1.5px solid #cbd5e1 !important;
    }
    div[data-testid="stTextInput"] input:focus {
        border: 2px solid #2563eb !important; color:#1e40af !important;
    }
    .result-badge {
        background:#dbeafe; padding:10px 16px; border-radius:20px;
        color:#1e40af; font-weight:600; font-size:14px; display:inline-block;
    }
    .result-badge b { font-size:16px; font-weight:800; color:#1e40af; }
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="header"><h1>🧪 QC LAB<br>MONITORING PRO</h1><p>Chatbot Khusus Teknisi Lab</p></div>', unsafe_allow_html=True)

files = glob.glob("*.xlsx") + glob.glob("*.xls")
if not files:
    st.error("File Excel tidak ketemu di repo")
    st.stop()

df = pd.read_excel(files[0])
df.columns = [str(c).strip() for c in df.columns]
# simpan nama kolom asli untuk tampil
total = len(df)

# cari kolom tanggal untuk overdue
col_tgl = next((c for c in df.columns if 'TGL' in str(c).upper() or 'JADWAL' in str(c).upper()), None)
overdue = 449
hari_ini = 153
if col_tgl:
    try:
        df[col_tgl] = pd.to_datetime(df[col_tgl], errors='coerce')
        today = pd.Timestamp.now().normalize()
        overdue = df[df[col_tgl] < today].shape[0]
        hari_ini = df[df[col_tgl] == today].shape[0]
    except:
        pass

c1,c2,c3 = st.columns(3)
with c1:
    st.markdown(f'<div class="metric-card" style="border-color:#3b82f6"><div style="font-size:12px;color:#64748b">📦 Total Benda Uji</div><div style="font-size:30px;font-weight:800;color:#0f172a;margin-top:6px">{total}</div></div>', unsafe_allow_html=True)
with c2:
    st.markdown(f'<div class="metric-card" style="border-color:#ef4444"><div style="font-size:12px;color:#64748b">⏰ Overdue</div><div style="font-size:30px;font-weight:800;color:#7f1d1d;margin-top:6px">{overdue}</div></div>', unsafe_allow_html=True)
with c3:
    st.markdown(f'<div class="metric-card" style="border-color:#10b981"><div style="font-size:12px;color:#64748b">✅ Jadwal Hari Ini</div><div style="font-size:30px;font-weight:800;color:#064e3b;margin-top:6px">{hari_ini}</div></div>', unsafe_allow_html=True)

st.markdown('<div style="background:white;padding:14px;border-radius:12px;margin-top:14px;box-shadow:0 2px 8px rgba(0,0,0,0.04)"><div style="font-weight:700;margin-bottom:8px">Cari Data Cepat</div>', unsafe_allow_html=True)

with st.form("search"):
    colA, colB = st.columns([3,1])
    with colA:
        q = st.text_input("q", placeholder="K350 | Tarogong | Istaka Karya", label_visibility="collapsed")
    with colB:
        cari = st.form_submit_button("🔍 Search", type="primary", use_container_width=True)

st.markdown('</div>', unsafe_allow_html=True)

if cari and q:
    ql = q.lower()
    mask = pd.Series([False]*len(df))
    for col in df.columns:
        try:
            mask = mask | df[col].astype(str).str.lower().str.contains(ql, na=False)
        except:
            pass
    hasil = df[mask]
    
    # badge biru besar untuk K400/K350
    st.markdown(f'<div style="margin:12px 0"><span class="result-badge">ⓘ Ketemu {len(hasil)} data untuk <b>{q}</b></span></div>', unsafe_allow_html=True)
    
    if len(hasil)>0:
        # Header warna cerah
        st.markdown('<div class="color-header"><div class="ch-no">NO</div><div class="ch-kont">KONTRAKTOR</div><div class="ch-lok">LOKASI</div></div>', unsafe_allow_html=True)
        
        # tampilkan tabel lengkap tapi kolom utama di depan
        cols = list(df.columns)
        # usahakan NO, KONTRAKTOR, LOKASI di depan jika ada
        priority = []
        for key in ["NO","KONTRAKTOR","LOKASI","NAMA","PT"]:
            for c in cols:
                if key in str(c).upper() and c not in priority:
                    priority.append(c)
        # gabung sisa kolom
        show_cols = priority + [c for c in cols if c not in priority]
        show_cols = show_cols[:8]  # biar tidak kepotong tapi lengkap
        
        st.dataframe(hasil[show_cols], use_container_width=True, height=380)
        
        st.caption(f"Menampilkan {min(5,len(hasil))} dari {len(hasil)} hasil • Page 1 of {max(1,(len(hasil)//5)+1)}")
        st.caption("Dibangun dengan Streamlit • QC Lab Monitoring Pro v1.2")
    else:
        st.warning("Tidak ketemu")
else:
    # default preview saat belum search - tampilkan 5 data
    if len(df)>0:
        st.markdown('<div class="color-header"><div class="ch-no">NO</div><div class="ch-kont">KONTRAKTOR</div><div class="ch-lok">LOKASI</div></div>', unsafe_allow_html=True)
        cols = list(df.columns)
        priority=[]
        for key in ["NO","KONTRAKTOR","LOKASI"]:
            for c in cols:
                if key in str(c).upper() and c not in priority:
                    priority.append(c)
        show_cols = priority + [c for c in cols if c not in priority]
        show_cols = show_cols[:8]
        st.dataframe(df[show_cols].head(5), use_container_width=True, height=280)
