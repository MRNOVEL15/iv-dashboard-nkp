import streamlit as st
import pandas as pd

# ==========================================
# 1. ตั้งค่าหน้าตาแอป (UI & CSS)
# ==========================================
st.set_page_config(page_title="IV Compatibility Dashboard", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: #f4f6f9; }
    .header-banner { background-color: #0c4a6e; color: white; padding: 25px 30px; border-radius: 12px; margin-bottom: 25px; border-bottom: 5px solid #e11d48; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }
    .header-banner h1 { margin: 0; font-size: 2rem; font-weight: 800; }
    .header-banner p { margin: 5px 0 0 0; font-size: 1.1rem; opacity: 0.9; }
    .panel-box { background-color: white; padding: 25px; border-radius: 12px; border: 1px solid #e2e8f0; margin-bottom: 20px; box-shadow: 0 2px 5px rgba(0,0,0,0.05); }
    .status-badge { display: block; padding: 15px; font-weight: 800; font-size: 1.3rem; border-radius: 8px; text-align: center; letter-spacing: 0.5px; }
    .status-Y { background-color: #ecfdf5; color: #059669; border: 2px solid #34d399; }
    .status-X { background-color: #fef2f2; color: #dc2626; border: 2px solid #f87171; }
    .status-C { background-color: #fefce8; color: #a16207; border: 2px solid #eab308; }
    .status-ND { background-color: #f8fafc; color: #64748b; border: 2px solid #cbd5e1; }
    .advice-box { background-color: #fdf2f8; border-left: 5px solid #db2777; padding: 15px 20px; margin-top: 15px; color: #9d174d; border-radius: 0 8px 8px 0; font-size: 1.05rem; line-height: 1.6; }
    .pair-title { font-size: 1.3rem; font-weight: 800; color: #1e293b; background-color: #f1f5f9; padding: 10px 15px; border-radius: 6px; margin-bottom: 15px; border-left: 6px solid #0ea5e9; }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 2. โหลดข้อมูลแบบ Real-time พร้อมจับ Error
# ==========================================
@st.cache_data(ttl=15)
def load_data():
    try:
        url = "https://docs.google.com/spreadsheets/d/1IW7mfdOuZ84BskIWPIcgGwueUuq4g5u-4YC7ghIREX4/export?format=csv&gid=2107829411"
        df = pd.read_csv(url, index_col=0)
        df.index = df.index.astype(str).str.strip()
        df.columns = df.columns.astype(str).str.strip()
        return df, "Success"
    except Exception as e:
        return None, str(e)

df, status_msg = load_data()

# ==========================================
# 3. ฟังก์ชันค้นหาอัจฉริยะ
# ==========================================
def get_val_robust(df, d1, d2):
    def find_match(name, target_list):
        for item in target_list:
            if str(name).lower() == str(item).lower():
                return item
        return None

    r1, c1 = find_match(d1, df.index), find_match(d2, df.columns)
    if r1 and c1:
        v = df.loc[r1, c1]
        if not pd.isna(v) and str(v).strip() != '': return str(v).strip()
    
    r2, c2 = find_match(d2, df.index), find_match(d1, df.columns)
    if r2 and c2:
        v = df.loc[r2, c2]
        if not pd.isna(v) and str(v).strip() != '': return str(v).strip()
        
    return "NO DATA"

# ==========================================
# 4. หน้าจอหลักของแอป
# ==========================================
st.markdown('<div class="header-banner"><h1>🏥 IV Compatibility Dashboard</h1><p>ตรวจสอบความเข้ากันได้ของยาฉีด | งานเภสัชสารสนเทศ โรงพยาบาลนครพิงค์</p></div>', unsafe_allow_html=True)

if df is not None:
    clean_drugs = sorted([str(d).strip() for d in df.index.tolist() if "compatibility" not in str(d).lower() and str(d).lower() != 'nan' and str(d).strip() != ''])
    
    st.markdown('<div class="panel-box">', unsafe_allow_html=True)
    st.markdown('### 🔍 เลือกระบุยาและสารน้ำ (สูงสุด 3 ชนิด)')
    col1, col2, col3 = st.columns(3)
    with col1: drug_a = st.selectbox("💉 ยา/สารน้ำ ชนิดที่ 1", clean_drugs, key="d1")
    with col2: drug_b = st.selectbox("💉 ยา/สารน้ำ ชนิดที่ 2", clean_drugs, key="d2")
    with col3: drug_c = st.selectbox("💉 ยา/สารน้ำ ชนิดที่ 3 (ไม่บังคับ)", ["- ไม่ระบุ -"] + clean_drugs, key="d3")
    
    check = st.button("🚀 ประมวลผลความเข้ากันได้", use_container_width=True, type="primary")
    st.markdown('</div>', unsafe_allow_html=True)
    
    if check:
        pairs = [(drug_a, drug_b)]
        if drug_c != "- ไม่ระบุ -":
            pairs.append((drug_a, drug_c))
            pairs.append((drug_b, drug_c))
            
        st.markdown(f"### 📊 ผลการตรวจสอบ ({len(pairs)} คู่ยา)")
        for d1, d2 in pairs:
            if d1 == d2: continue
            
            st.markdown(f'<div class="panel-box"><div class="pair-title">⚔️ {d1} + {d2}</div>', unsafe_allow_html=True)
            val = get_val_robust(df, d1, d2)
            
            if '|' in val:
                parts = val.split('|', 1)
                res, advice = parts[0].strip().upper(), parts[1].strip()
            else:
                res, advice = val.strip().upper(), ""
            
            if 'X' in res: st.markdown('<div class="status-badge status-X">❌ INCOMPATIBLE (ห้ามให้ร่วมกัน)</div>', unsafe_allow_html=True)
            elif 'Y' in res: st.markdown('<div class="status-badge status-Y">✅ COMPATIBLE (ให้ร่วมกันได้)</div>', unsafe_allow_html=True)
            elif any(c in res for c in ['C', 'U', 'V', 'I']): st.markdown('<div class="status-badge status-C">🟡 CAUTION (มีเงื่อนไข / ผลไม่แน่นอน)</div>', unsafe_allow_html=True)
            else: st.markdown('<div class="status-badge status-ND">⚪ NO DATA (ยังไม่มีข้อมูลในระบบ)</div>', unsafe_allow_html=True)
            
            if advice: 
                advice = advice.replace("Y-site", "**Y-site**").replace("Y-Site", "**Y-Site**").replace("Admixture", "**Admixture**").replace("Admix", "**Admixture**")
                st.markdown(f'<div class="advice-box">💡 <b>คำแนะนำจาก DIS:</b><br>{advice}</div>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)

else:
    st.error("❌ ไม่สามารถดึงข้อมูลจาก Google Sheets ได้")
    st.warning(f"สาเหตุ: {status_msg}")
    st.info("💡 วิธีแก้: กรุณาเข้าไปที่ตาราง Google Sheets ของคุณ -> เลือกเมนู ไฟล์ (File) -> แชร์ (Share) -> เผยแพร่ไปยังเว็บ (Publish to web) แล้วกดปุ่ม 'เผยแพร่'")

st.markdown('<p style="text-align:center; color:#64748b; margin-top:40px;">ติดต่อหน่วยงานเภสัชกรรม 053-999200 ต่อ 2279</p>', unsafe_allow_html=True)