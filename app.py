import streamlit as st
import pandas as pd

# 1. ตั้งค่าหน้าตาแอป
st.set_page_config(page_title="IV Dashboard | 3-Way Check", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: #f0f4f8; }
    .header-banner { background-color: #0c4a6e; color: white; padding: 25px; border-radius: 12px; margin-bottom: 25px; border-bottom: 5px solid #e11d48; }
    .panel-box { background-color: white; padding: 20px; border-radius: 12px; border: 1px solid #e2e8f0; margin-bottom: 20px; }
    .status-badge { display: block; padding: 15px; font-weight: bold; font-size: 1.2rem; border-radius: 8px; text-align: center; }
    .status-Y { background-color: #ecfdf5; color: #059669; border: 2px solid #34d399; }
    .status-X { background-color: #fef2f2; color: #dc2626; border: 2px solid #f87171; }
    .status-C { background-color: #fefce8; color: #a16207; border: 2px solid #eab308; }
    .advice-box { background-color: #fff1f2; border-left: 4px solid #e11d48; padding: 15px; margin-top: 10px; color: #be123c; }
    </style>
""", unsafe_allow_html=True)

# 2. โหลดข้อมูลจาก Google Sheets (gid=2107829411)
@st.cache_data(ttl=30)
def load_data():
    try:
        url = "https://docs.google.com/spreadsheets/d/1IW7mfdOuZ84BskIWPIcgGwueUuq4g5u-4YC7ghIREX4/export?format=csv&gid=2107829411"
        df = pd.read_csv(url, index_col=0)
        df.index = df.index.astype(str).str.strip()
        df.columns = df.columns.astype(str).str.strip()
        return df
    except:
        return None

df = load_data()

# ฟังก์ชันค้นหาสลับแกน (A+B หรือ B+A)
def get_val(df, d1, d2):
    if d1 in df.index and d2 in df.columns:
        v = df.loc[d1, d2]
        if not pd.isna(v) and str(v).strip() != '': return str(v).strip()
    if d2 in df.index and d1 in df.columns:
        v = df.loc[d2, d1]
        if not pd.isna(v) and str(v).strip() != '': return str(v).strip()
    return "NO DATA"

# 3. หน้าจอหลัก
st.markdown('<div class="header-banner"><h1>🏥 IV Dashboard (3-Way Check)</h1><p>งานเภสัชสารสนเทศ โรงพยาบาลนครพิงค์</p></div>', unsafe_allow_html=True)

if df is not None:
    # กรองรายชื่อยา
    clean_drugs = sorted([d for d in df.index.tolist() if "compatibility" not in str(d).lower() and str(d) != 'nan' and str(d).strip() != ''])
    
    col1, col2, col3 = st.columns(3)
    with col1: drug_a = st.selectbox("💉 ยาตัวที่ 1", clean_drugs, index=0)
    with col2: drug_b = st.selectbox("💉 ยาตัวที่ 2", clean_drugs, index=1 if len(clean_drugs)>1 else 0)
    with col3: drug_c = st.selectbox("💉 ยาตัวที่ 3 (ถ้ามี)", ["- ไม่ระบุ -"] + clean_drugs, index=0)
    
    if st.button("🚀 ตรวจสอบความเข้ากันได้", use_container_width=True):
        pairs = [(drug_a, drug_b)]
        if drug_c != "- ไม่ระบุ -":
            pairs.append((drug_a, drug_c))
            pairs.append((drug_b, drug_c))
            
        for d1, d2 in pairs:
            st.markdown(f'<div class="panel-box"><b>⚔️ {d1} + {d2}</b>', unsafe_allow_html=True)
            val = get_val(df, d1, d2)
            res, advice = val.split('|', 1) if '|' in val else (val, "")
            res = res.strip().upper()
            
            if 'X' in res: st.markdown('<div class="status-badge status-X">❌ INCOMPATIBLE</div>', unsafe_allow_html=True)
            elif 'Y' in res: st.markdown('<div class="status-badge status-Y">✅ COMPATIBLE</div>', unsafe_allow_html=True)
            elif any(c in res for c in ['C', 'U', 'V']): st.markdown('<div class="status-badge status-C">🟡 CAUTION / VARIABLE</div>', unsafe_allow_html=True)
            else: st.markdown('<div class="status-badge">⚪ NO DATA</div>', unsafe_allow_html=True)
            
            if advice: st.markdown(f'<div class="advice-box">📝 {advice}</div>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)

st.markdown('<p style="text-align:center; color:#64748b;">ติดต่อหน่วยงานเภสัชกรรม 053-999200 ต่อ 2279</p>', unsafe_allow_html=True)
