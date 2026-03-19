import streamlit as st
import pandas as pd

# ==========================================
# 1. UI & CSS Setting
# ==========================================
st.set_page_config(page_title="IV Dashboard | 3-Way Check", layout="wide", initial_sidebar_state="collapsed")

st.markdown("""
    <style>
    .stApp { background-color: #f0f4f8; }
    .header-banner { background-color: #0c4a6e; color: white; padding: 25px 30px; border-radius: 12px; margin-bottom: 25px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); border-bottom: 5px solid #e11d48; }
    .header-banner h1 { margin: 0; font-size: 1.9rem; font-weight: 800; color: white; }
    .header-banner p { margin: 5px 0 0 0; font-size: 1.1rem; opacity: 0.9; }
    
    .panel-box { background-color: white; padding: 25px; border-radius: 12px; border: 1px solid #e2e8f0; box-shadow: 0 4px 6px rgba(0,0,0,0.05); margin-bottom: 25px; }
    .section-title { color: #0f172a; font-weight: 800; border-bottom: 2px solid #e2e8f0; padding-bottom: 12px; margin-bottom: 20px; font-size: 1.3rem; display: flex; align-items: center; gap: 8px; }
    
    .status-badge { display: block; padding: 15px 20px; font-weight: 800; font-size: 1.3rem; border-radius: 6px; margin-bottom: 15px; text-align: center; }
    .status-Y { background-color: #ecfdf5; color: #059669; border: 2px solid #34d399; }
    .status-X { background-color: #fef2f2; color: #dc2626; border: 2px solid #f87171; }
    .status-C { background-color: #fefce8; color: #a16207; border: 2px solid #eab308; }
    .status-ND { background-color: #f8fafc; color: #64748b; border: 2px solid #cbd5e1; }
    
    .pair-title { font-size: 1.2rem; font-weight: 800; color: #1e293b; background-color: #e2e8f0; padding: 10px 15px; border-radius: 6px; margin-bottom: 15px; border-left: 6px solid #0ea5e9;}
    .advice-box { background-color: #fff1f2; border-left: 4px solid #e11d48; padding: 15px; border-radius: 4px; font-size: 1rem; color: #be123c; margin-bottom: 15px; line-height: 1.6; }
    
    .analyze-btn > button { background-color: #0c4a6e; color: white; font-weight: bold; width: 100%; padding: 15px; border-radius: 8px; border: none; font-size: 1.2rem; transition: 0.3s; }
    .analyze-btn > button:hover { background-color: #082f49; box-shadow: 0 4px 12px rgba(0,0,0,0.2); }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 2. Data Loading Engine
# ==========================================
@st.cache_data(ttl=30) 
def load_data():
    try:
        # ดึงข้อมูลจาก Google Sheets ของคุณโดยตรง
        url = "https://docs.google.com/spreadsheets/d/1IW7mfdOuZ84BskIWPIcgGwueUuq4g5u-4YC7ghIREX4/export?format=csv&gid=2107829411"
        df = pd.read_csv(url, index_col=0)
        df.index = df.index.astype(str).str.strip()
        df.columns = df.columns.astype(str).str.strip()
        return df, "success"
    except Exception as e:
        return None, str(e)

df, status = load_data()

# ฟังก์ชันค้นหาข้อมูลแบบสลับด้าน (A+B หรือ B+A)
def get_val(df, d1, d2):
    if d1 in df.index and d2 in df.columns:
        v = df.loc[d1, d2]
        if not pd.isna(v) and str(v).strip().lower() != 'nan' and str(v).strip() != '':
            return str(v).strip()
    if d2 in df.index and d1 in df.columns:
        v = df.loc[d2, d1]
        if not pd.isna(v) and str(v).strip().lower() != 'nan' and str(v).strip() != '':
            return str(v).strip()
    return "NO DATA"

# ==========================================
# 3. Main Interface
# ==========================================
st.markdown("""
    <div class="header-banner">
        <h1>🏥 3-Way IV Incompatibility Dashboard</h1>
        <p>งานเภสัชสารสนเทศ (DIS) • โรงพยาบาลนครพิงค์</p>
    </div>
""", unsafe_allow_html=True)

if df is not None:
    st.markdown('<div class="panel-box">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">🔍 ตรวจสอบยาพร้อมกัน (สูงสุด 3 ชนิด)</div>', unsafe_allow_html=True)
    
    # กรองขยะออกจากรายชื่อยา
    clean_drugs = sorted([d for d in df.index.tolist() if "compatibility" not in str(d).lower() and "y=" not in str(d).lower() and str(d).lower() != 'nan' and str(d) != ''])
    
    c1, c2, c3 = st.columns(3)
    with c1: drug_a = st.selectbox("💉 ยาตัวที่ 1", clean_drugs, index=0)
    with c2: drug_b = st.selectbox("💉 ยาตัวที่ 2", clean_drugs, index=1 if len(clean_drugs)>1 else 0)
    with c3: drug_c = st.selectbox("💉 ยาตัวที่ 3 (ถ้ามี)", ["- ไม่ระบุ -"] + clean_drugs, index=0)
    
    st.markdown('<div class="analyze-btn" style="margin-top:20px;">', unsafe_allow_html=True)
    check = st.button("🚀 ตรวจสอบความเข้ากันได้", use_container_width=True)
    st.markdown('</div></div>', unsafe_allow_html=True)
    
    if check:
        pairs_to_check = [(drug_a, drug_b)]
        if drug_c != "- ไม่ระบุ -":
            pairs_to_check.append((drug_a, drug_c))
            pairs_to_check.append((drug_b, drug_c))
            
        for d1, d2 in pairs_to_check:
            st.markdown('<div class="panel-box" style="padding: 20px; margin-bottom: 15px;">', unsafe_allow_html=True)
            st.markdown(f'<div class="pair-title">⚔️ {d1} + {d2}</div>', unsafe_allow_html=True)
            
            val = get_val(df, d1, d2)
            res, advice = val.split('|', 1) if '|' in val else (val, "")
            res = res.strip().upper()
            
            if 'X' in res: 
                st.markdown('<div class="status-badge status-X">❌ INCOMPATIBLE (ห้ามให้ร่วมกัน)</div>', unsafe_allow_html=True)
            elif res == 'Y': 
                st.markdown('<div class="status-badge status-Y">✅ COMPATIBLE (ให้ร่วมกันได้)</div>', unsafe_allow_html=True)
            elif any(c in res for c in ['C', 'U', 'V', 'I']): 
                st.markdown('<div class="status-badge status-C">🟡 สีเหลือง: มีเงื่อนไขเฉพาะ / ผลไม่แน่นอน</div>', unsafe_allow_html=True)
            else: 
                st.markdown('<div class="status-badge status-ND">⚪ NO DATA (ไม่มีข้อมูลในฐานข้อมูล)</div>', unsafe_allow_html=True)
            
            if advice:
                st.markdown(f'<div class="advice-box">📝 <b>คำแนะนำจาก DIS:</b><br>{advice}</div>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("""
        <div style="text-align: center; margin-top: 30px; color: #64748b; font-size: 0.95rem; border-top: 1px solid #e2e8f0; padding-top: 20px;">
            <p><strong>พัฒนาโดยงานเภสัชสารสนเทศ (DIS) โรงพยาบาลนครพิงค์</strong><br>
            ติดต่อสอบถาม: 053-999200 ต่อ 2279</p>
        </div>
    """, unsafe_allow_html=True)
else:
    st.error(f"❌ ไม่สามารถดึงข้อมูลได้: {status}")
