import streamlit as st
import pandas as pd

# ==========================================
# 1. ตั้งค่าหน้าเพจและ CSS 
# ==========================================
st.set_page_config(page_title="IV Dashboard Incompatibility | DIS Nakornping", layout="wide", initial_sidebar_state="collapsed")

st.markdown("""
    <style>
    /* พื้นหลังและ Header */
    .stApp { background-color: #f8fafc; }
    .header-banner { background-color: #004080; color: white; padding: 20px 30px; border-radius: 8px; margin-bottom: 25px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); border-bottom: 4px solid #e11d48; }
    .header-banner h1 { margin: 0; font-size: 1.8rem; font-weight: 700; color: white; }
    .header-banner p { margin: 5px 0 0 0; font-size: 1rem; opacity: 0.9; }
    
    /* กล่องเนื้อหา */
    .panel-box { background-color: white; padding: 25px; border-radius: 8px; border: 1px solid #e2e8f0; box-shadow: 0 2px 4px rgba(0,0,0,0.05); margin-bottom: 20px; }
    .section-title { color: #004080; font-weight: bold; border-bottom: 2px solid #e2e8f0; padding-bottom: 10px; margin-bottom: 20px; font-size: 1.2rem; display: flex; align-items: center; gap: 8px; }
    
    /* ป้ายสถานะผลลัพธ์ */
    .status-badge { display: block; padding: 15px 20px; font-weight: 800; font-size: 1.5rem; border-radius: 6px; margin-bottom: 20px; text-align: center; letter-spacing: 0.5px; }
    .status-Y { background-color: #ecfdf5; color: #059669; border: 2px solid #34d399; }
    .status-X { background-color: #fef2f2; color: #dc2626; border: 2px solid #f87171; }
    .status-C { background-color: #fffbeb; color: #d97706; border: 2px solid #fbbf24; }
    
    /* กล่องข้อควรระวังและคำแนะนำ */
    .precaution-container { background-color: #fff1f2; padding: 15px 20px; border-left: 5px solid #e11d48; border-radius: 4px; margin-top: 10px; font-size: 0.95rem; line-height: 1.6; color: #333; }
    .drug-name-title { font-weight: 700; color: #be123c; font-size: 1.1rem; margin-bottom: 8px; border-bottom: 1px solid #fecdd3; padding-bottom: 5px; }
    
    /* ปุ่มต่างๆ */
    .quick-btn > button { width: 100%; text-align: left; padding: 10px 15px; background-color: white; border: 1px solid #cbd5e1; color: #0f172a; border-radius: 6px; transition: all 0.2s; margin-bottom: 8px; font-weight: 500; }
    .quick-btn > button:hover { background-color: #f1f5f9; border-color: #94a3b8; transform: translateX(5px); }
    .analyze-btn > button { background-color: #004080; color: white; font-weight: bold; width: 100%; padding: 12px; border-radius: 6px; border: none; font-size: 1.1rem; }
    .analyze-btn > button:hover { background-color: #002b5e; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 2. ระบบ Session State และโหลดข้อมูล
# ==========================================
if 'drug_a' not in st.session_state: st.session_state.drug_a = None
if 'drug_b' not in st.session_state: st.session_state.drug_b = None

def set_quick_drugs(d1, d2):
    st.session_state.drug_a = d1
    st.session_state.drug_b = d2

@st.cache_data(ttl=30) 
def load_data():
    try:
        sheet_url = "https://docs.google.com/spreadsheets/d/e/2PACX-1vRVvgXF-uMZbdJXUnFoc_EbGM_JygWW53SlhMBvk4q4s2obzEviIB4nvpRjGDg1X15hOLveeih9zzuB/pub?output=csv"
        
        df = pd.read_csv(sheet_url, index_col=0)
        df.index = df.index.astype(str).str.strip()
        df.columns = df.columns.astype(str).str.strip()
        
        drug_precautions = {
            "Ceftriaxone": "<b>ข้อควรระวัง:</b> เสี่ยงเกิดผลึกตะกอน (Calcium-Ceftriaxone precipitate) ทันที ซึ่งอาจไปอุดตันในหลอดเลือดและเป็นอันตรายถึงชีวิตในเด็กแรกเกิด<br><b>คำแนะนำ:</b> ห้ามผสมหรือให้ร่วมกับสารละลายที่มีแคลเซียมเด็ดขาด ต้องใช้สายแยกหรือ Flush สายให้สะอาดด้วย NSS",
            "Calcium gluconate": "<b>ข้อควรระวัง:</b> มีความเสี่ยงสูงในการเกิดตะกอนขุ่นและผลึกเมื่อสัมผัสกับยาปฏิชีวนะหลายชนิด<br><b>คำแนะนำ:</b> ตรวจสอบความเข้ากันได้ทุกครั้งก่อนให้ยาร่วมกับยาอื่น",
            "Phenytoin": "<b>ข้อควรระวัง:</b> ยามีความเป็นด่างสูงมาก ตกตะกอนขุ่นขาวทันทีเมื่อผสมใน D5W หรือยาที่มีฤทธิ์เป็นกรด<br><b>คำแนะนำ:</b> ต้องเจือจางใน NSS เท่านั้น และ Flush สายด้วย NSS ก่อนและหลังให้ยาทุกครั้ง",
            "Furosemide": "<b>ข้อควรระวัง:</b> ยามีฤทธิ์เป็นด่าง จะเกิดตะกอนขุ่นขาว (White precipitate) ทันทีเมื่อสัมผัสกับยาที่มีฤทธิ์เป็นกรด (เช่น Amiodarone, Midazolam)<br><b>คำแนะนำ:</b> ห้ามให้ผ่าน Y-site เดียวกัน หากเลี่ยงไม่ได้ต้อง Flush สายให้สะอาดหมดจดก่อนให้ยา",
            "Amiodarone": "<b>ข้อควรระวัง:</b> เกิดตะกอนขุ่นเมื่อผสมกับ Heparin หรือ Sodium Bicarbonate<br><b>คำแนะนำ:</b> ควรเจือจางใน D5W และแนะนำให้ใช้ In-line filter ขนาด 0.22 micron ในการบริหารยา",
            "Amphotericin B": "<b>ข้อควรระวัง:</b> ยาไวต่อ Electrolyte สูงมาก ห้ามผสมกับ NSS เด็ดขาด เพราะยาจะแตกตัวและตกตะกอนทันที<br><b>คำแนะนำ:</b> ต้องเจือจางและ Flush สายด้วย D5W เท่านั้น"
        }
        return df, drug_precautions, "success"
    except Exception as e:
        return None, {}, str(e)

df, drug_precautions, status = load_data()

# ==========================================
# 3. วาดหน้าจอ (UI Layout)
# ==========================================
st.markdown("""
    <div class="header-banner">
        <h1>🏥 IV Dashboard Incompatibility</h1>
        <p>งานเภสัชสารสนเทศ (DIS) • โรงพยาบาลนครพิงค์</p>
    </div>
""", unsafe_allow_html=True)

if df is not None:
    col_main, col_side = st.columns([3, 1.2]) 
    
    with col_side:
        st.markdown('<div class="panel-box" style="background-color: #f8fafc;">', unsafe_allow_html=True)
        st.markdown('<div class="section-title">⚡ คู่ยาที่พบบ่อย (Quick Links)</div>', unsafe_allow_html=True)
        
        pairs = [
            ("Ceftriaxone", "Calcium gluconate"), 
            ("Amiodarone", "Furosemide"), 
            ("Phenytoin", "Dextrose/water"), 
            ("Amphotericin B", "Normal saline")
        ]
        
        for d1, d2 in pairs:
            if d1 in df.index and d2 in df.columns:
                st.markdown('<div class="quick-btn">', unsafe_allow_html=True)
                st.button(f"🚨 {d1} + {d2}", on_click=set_quick_drugs, args=(d1, d2), key=f"{d1}_{d2}")
                st.markdown('</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with col_main:
        st.markdown('<div class="panel-box">', unsafe_allow_html=True)
        st.markdown('<div class="section-title">🔍 ตรวจสอบความเข้ากันได้ของยาฉีด (Admixture & Y-Site)</div>', unsafe_allow_html=True)
        
        # --- ระบบสกัดคำอธิบายออกจากการเป็นชื่อยา ---
        # กรองเอาคำว่า Incompatibility, Y= หรือค่าว่าง (nan) ออกจากรายการ
        clean_drugs_a = [d for d in df.index.tolist() if "compatibility" not in str(d).lower() and "y=" not in str(d).lower() and str(d).lower() != 'nan']
        clean_drugs_b = [d for d in df.columns.tolist() if "compatibility" not in str(d).lower() and "y=" not in str(d).lower() and str(d).lower() != 'nan']
        
        idx_a = clean_drugs_a.index(st.session_state.drug_a) if st.session_state.drug_a in clean_drugs_a else 0
        idx_b = clean_drugs_b.index(st.session_state.drug_b) if st.session_state.drug_b in clean_drugs_b else 0
        
        c1, c2 = st.columns(2)
        with c1: drug_a = st.selectbox("💉 ยาตัวที่ 1 (สารละลายหลัก / ยาหลัก)", clean_drugs_a, index=idx_a)
        with c2: drug_b = st.selectbox("💉 ยาตัวที่ 2 (ยาที่ให้ร่วม / ยาให้ผ่าน Y-Site)", clean_drugs_b, index=idx_b)
        
        st.markdown('<div class="analyze-btn">', unsafe_allow_html=True)
        check = st.button("ตรวจสอบความเข้ากันได้", use_container_width=True)
        st.markdown('</div></div>', unsafe_allow_html=True)
        
        if check:
            val = str(df.loc[drug_a, drug_b]).strip() if pd.notna(df.loc[drug_a, drug_b]) else "NO DATA"
            
            if '|' in val:
                res, quick_advice = val.split('|', 1)
                res, quick_advice = res.strip().upper(), quick_advice.strip()
            else:
                res, quick_advice = val.upper(), ""
                
            st.markdown('<div class="panel-box">', unsafe_allow_html=True)
            st.markdown(f'<div class="section-title">📊 ผลการตรวจสอบ: {drug_a} + {drug_b}</div>', unsafe_allow_html=True)
            
            if res == 'Y': 
                st.markdown('<div class="status-badge status-Y">✅ COMPATIBLE (สามารถให้ร่วมกันได้)</div>', unsafe_allow_html=True)
            elif res == 'X': 
                st.markdown('<div class="status-badge status-X">❌ INCOMPATIBLE (ห้ามผสมหรือให้ผ่านสายเดียวกัน)</div>', unsafe_allow_html=True)
            elif res in ['C', 'U', 'V', 'I', 'VC', 'YC']: 
                st.markdown(f'<div class="status-badge status-C">⚠️ CAUTION / VARIABLE (สถานะ {res} : โปรดตรวจสอบเงื่อนไขความเข้มข้น)</div>', unsafe_allow_html=True)
            else: 
                st.markdown('<div class="status-badge" style="background-color:#f8fafc; border:2px solid #cbd5e1; color:#475569;">⚪ NO DATA (ไม่มีข้อมูลในฐานข้อมูล)</div>', unsafe_allow_html=True)
            
            if quick_advice:
                st.error(f"**📝 หมายเหตุจากฐานข้อมูล:** {quick_advice}")
                
            st.markdown("<hr style='margin: 25px 0;'>", unsafe_allow_html=True)
            
            st.markdown("#### ⚠️ ข้อควรระวังและคำแนะนำเพิ่มเติม")
            
            col_ref1, col_ref2 = st.columns(2)
            with col_ref1:
                if drug_a in drug_precautions:
                    st.markdown(f'<div class="precaution-container"><div class="drug-name-title">💉 {drug_a}</div>{drug_precautions[drug_a]}</div>', unsafe_allow_html=True)
                else:
                    st.markdown(f'<div class="precaution-container" style="background-color:#f1f5f9; border-color:#94a3b8;"><div class="drug-name-title" style="color:#475569; border-color:#cbd5e1;">💉 {drug_a}</div><span style="color:#64748b;">(ไม่มีข้อควรระวังพิเศษในฐานข้อมูล)</span></div>', unsafe_allow_html=True)
            
            with col_ref2:
                if drug_b in drug_precautions:
                    st.markdown(f'<div class="precaution-container"><div class="drug-name-title">💉 {drug_b}</div>{drug_precautions[drug_b]}</div>', unsafe_allow_html=True)
                else:
                    st.markdown(f'<div class="precaution-container" style="background-color:#f1f5f9; border-color:#94a3b8;"><div class="drug-name-title" style="color:#475569; border-color:#cbd5e1;">💉 {drug_b}</div><span style="color:#64748b;">(ไม่มีข้อควรระวังพิเศษในฐานข้อมูล)</span></div>', unsafe_allow_html=True)
                
            st.markdown('</div>', unsafe_allow_html=True)
else:
    st.error(f"❌ ระบบไม่สามารถเชื่อมต่อฐานข้อมูลได้: {status}")
    st.info("โปรดตรวจสอบลิงก์ Google Sheets และการตั้งค่าเผยแพร่ทางเว็บ")