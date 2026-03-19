import streamlit as st
import pandas as pd
import re

# ==========================================
# 1. ตั้งค่าหน้าเพจและ CSS (กลับไปใช้สไตล์เดิมของคุณ)
# ==========================================
st.set_page_config(page_title="IV Dashboard Incompatibility | DIS Nakornping", layout="wide", initial_sidebar_state="collapsed")

st.markdown("""
    <style>
    .stApp { background-color: #f8fafc; }
    .header-banner { background-color: #004080; color: white; padding: 20px 30px; border-radius: 8px; margin-bottom: 25px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); border-bottom: 4px solid #e11d48; }
    .header-banner h1 { margin: 0; font-size: 1.8rem; font-weight: 700; color: white; }
    .header-banner p { margin: 5px 0 0 0; font-size: 1rem; opacity: 0.9; }
    .panel-box { background-color: white; padding: 25px; border-radius: 8px; border: 1px solid #e2e8f0; box-shadow: 0 2px 4px rgba(0,0,0,0.05); margin-bottom: 20px; }
    .section-title { color: #004080; font-weight: bold; border-bottom: 2px solid #e2e8f0; padding-bottom: 10px; margin-bottom: 20px; font-size: 1.2rem; display: flex; align-items: center; gap: 8px; }
    
    /* ป้ายสถานะแจ้งเตือน */
    .status-badge { display: block; padding: 15px 20px; font-weight: 800; font-size: 1.2rem; border-radius: 6px; margin-bottom: 2px; text-align: center; }
    .status-Y { background-color: #ecfdf5; color: #059669; border: 2px solid #34d399; }
    .status-X { background-color: #fef2f2; color: #dc2626; border: 2px solid #f87171; }
    .status-C { background-color: #fefce8; color: #a16207; border: 2px solid #eab308; }
    .status-ND { background-color: #f8fafc; color: #64748b; border: 2px solid #cbd5e1; }
    
    /* กล่องคำแนะนำที่ติดกับสถานะ */
    .advice-container { padding: 15px 20px; border-radius: 0 0 6px 6px; font-size: 0.95rem; line-height: 1.6; margin-bottom: 20px; }
    .advice-red { background-color: #fff1f2; border: 2px solid #f87171; border-top: none; color: #333; }
    .advice-yellow { background-color: #fffbeb; border: 2px solid #fbbf24; border-top: none; color: #333; }
    
    /* ปุ่มข้างขวา */
    .quick-btn > button { width: 100%; text-align: left; padding: 10px 15px; background-color: white; border: 1px solid #cbd5e1; color: #0f172a; border-radius: 6px; transition: all 0.2s; margin-bottom: 8px; font-weight: 500; }
    .quick-btn > button:hover { background-color: #f1f5f9; border-color: #94a3b8; transform: translateX(5px); }
    
    /* ปุ่มประมวลผลสีน้ำเงิน */
    .analyze-btn > button { background-color: #004080; color: white; font-weight: bold; width: 100%; padding: 12px; border-radius: 6px; border: none; font-size: 1.1rem; margin-top: 15px; }
    .analyze-btn > button:hover { background-color: #002b5e; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 2. ระบบจัดการข้อมูล (Google Sheet)
# ==========================================
if 'd1_key' not in st.session_state: st.session_state.d1_key = "Furosemide"
if 'd2_key' not in st.session_state: st.session_state.d2_key = "Midazolam"
if 'd3_key' not in st.session_state: st.session_state.d3_key = "- ไม่ระบุ -"

def set_quick_drugs(d1, d2):
    st.session_state.d1_key = d1
    st.session_state.d2_key = d2
    st.session_state.d3_key = "- ไม่ระบุ -"

@st.cache_data(ttl=30) 
def load_data():
    try:
        sheet_url = "https://docs.google.com/spreadsheets/d/e/2PACX-1vRVvgXF-uMZbdJXUnFoc_EbGM_JygWW53SlhMBvk4q4s2obzEviIB4nvpRjGDg1X15hOLveeih9zzuB/pub?output=csv"
        df = pd.read_csv(sheet_url, index_col=0)
        df.index = df.index.astype(str).str.strip()
        df.columns = df.columns.astype(str).str.strip()
        
        # ข้อควรระวังประจำยา (ใช้ดึงมาแสดงใต้สีแดง/เหลืองอัตโนมัติ)
        precautions = {
            "Ceftriaxone": "เสี่ยงเกิดผลึกตะกอน (Calcium-Ceftriaxone precipitate) ทันที อาจอุดตันในหลอดเลือดและเป็นอันตรายถึงชีวิต ห้ามผสมร่วมกับสารละลายที่มีแคลเซียม",
            "Calcium gluconate": "มีความเสี่ยงสูงในการเกิดตะกอนขุ่นและผลึกเมื่อสัมผัสกับยาปฏิชีวนะหลายชนิด",
            "Furosemide": "ยามีฤทธิ์เป็นด่าง จะเกิดตะกอนขุ่นขาวทันทีเมื่อสัมผัสกับยาที่มีฤทธิ์เป็นกรด ห้ามให้ผ่าน Y-site เดียวกันถ้าไม่ Flush สาย",
            "Midazolam": "ยามีฤทธิ์เป็นกรด จะตกตะกอนทันทีเมื่อเจอสารละลายที่เป็นด่าง",
            "Norepinephrine": "ยาเสื่อมสภาพได้ง่ายในสารละลายที่มีความเป็นด่างจัด",
            "Amphotericin B": "ยาไวต่อ Electrolyte สูงมาก ห้ามผสมกับ NSS เด็ดขาด ยาจะตกตะกอนทันที"
        }
        return df, precautions, "success"
    except Exception as e:
        return None, {}, str(e)

df, drug_precautions, status = load_data()

# ==========================================
# 3. UI Layout (โครงสร้างเดิมที่คุ้นเคย)
# ==========================================
st.markdown("""
    <div class="header-banner">
        <h1>🏥 IV Dashboard Incompatibility</h1>
        <p>งานเภสัชสารสนเทศ (DIS) • โรงพยาบาลนครพิงค์</p>
    </div>
""", unsafe_allow_html=True)

if df is not None:
    col_main, col_side = st.columns([3, 1.2]) 
    
    # --- แถบขวา: ปุ่มลัดคู่ยาที่พบบ่อย (กลับมาแล้ว!) ---
    with col_side:
        st.markdown('<div class="panel-box" style="background-color: #f8fafc;">', unsafe_allow_html=True)
        st.markdown('<div class="section-title">⚡ คู่ยาที่พบบ่อย</div>', unsafe_allow_html=True)
        pairs = [
            ("Furosemide", "Midazolam"),
            ("Ceftriaxone", "Calcium gluconate"),
            ("Norepinephrine", "Sodium bicarbonate"),
            ("Furosemide", "Potassium phosphate"),
            ("Vancomycin", "Cefazolin"),
            ("Norepinephrine", "Piperacillin-tazobactam")
        ]
        for d1, d2 in pairs:
            st.markdown('<div class="quick-btn">', unsafe_allow_html=True)
            st.button(f"🚨 {d1} + {d2}", on_click=set_quick_drugs, args=(d1, d2), key=f"q_{d1}_{d2}")
            st.markdown('</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    # --- ส่วนกลาง: ตรวจสอบยา ---
    with col_main:
        st.markdown('<div class="panel-box">', unsafe_allow_html=True)
        st.markdown('<div class="section-title">🔍 ตรวจสอบความเข้ากันได้ของยาฉีด (สูงสุด 3 ชนิด)</div>', unsafe_allow_html=True)
        
        all_drugs = sorted(list(set([str(d) for d in df.index.tolist() + df.columns.tolist() if "compatibility" not in str(d).lower() and str(d).lower() != 'nan'])))
        
        c1, c2, c3 = st.columns(3)
        with c1: drug_a = st.selectbox("💉 ยาตัวที่ 1", all_drugs, key="d1_key")
        with c2: drug_b = st.selectbox("💉 ยาตัวที่ 2", all_drugs, key="d2_key")
        with c3: drug_c = st.selectbox("💉 ยาตัวที่ 3", ["- ไม่ระบุ -"] + all_drugs, key="d3_key")
        
        st.markdown('<div class="analyze-btn">', unsafe_allow_html=True)
        check = st.button("ประมวลผลความเข้ากันได้", use_container_width=True)
        st.markdown('</div></div>', unsafe_allow_html=True)
        
        if check:
            def get_data(d1, d2):
                def find(name, lst):
                    for i in lst:
                        if str(name).lower() == str(i).lower(): return i
                    return None
                r, c = find(d1, df.index), find(d2, df.columns)
                if r and c and not pd.isna(df.loc[r, c]): return str(df.loc[r, c]).strip()
                r2, c2 = find(d2, df.index), find(d1, df.columns)
                if r2 and c2 and not pd.isna(df.loc[r2, c2]): return str(df.loc[r2, c2]).strip()
                return ""

            pairs = [(drug_a, drug_b)]
            if drug_c != "- ไม่ระบุ -":
                pairs.extend([(drug_a, drug_c), (drug_b, drug_c)])
            
            st.markdown(f"### 📊 ผลการตรวจสอบ ({len(pairs)} คู่ยา)")
            
            for d1, d2 in pairs:
                if d1 == d2: continue
                val = get_data(d1, d2)
                res, advice = val.split('|', 1) if '|' in val else (val.strip().upper(), "")
                
                st.markdown(f'<div class="panel-box" style="padding:20px; border-left:5px solid #004080;">', unsafe_allow_html=True)
                st.markdown(f'**⚔️ {d1} + {d2}**')
                
                # ฟังก์ชันสร้าง Badge และคำแนะนำรวม
                def render_result(label, codes_to_find, drug_names):
                    status_ui, advice_class = "", ""
                    found_code = ""
                    for c in codes_to_find:
                        if c in res: found_code = c; break
                    
                    if found_code in ['X', 'I']:
                        status_ui = f'<div class="status-badge status-X">🔴 INCOMPATIBLE ({label})</div>'
                        advice_class = "advice-red"
                    elif found_code in ['V', 'U']:
                        status_ui = f'<div class="status-badge status-C">🟡 Uncertain/Variable Results ({label})</div>'
                        advice_class = "advice-yellow"
                    elif found_code in ['Y', 'C']:
                        status_ui = f'<div class="status-badge status-Y">🟢 COMPATIBLE ({label})</div>'
                    else:
                        status_ui = f'<div class="status-badge status-ND">⚪ NO DATA ({label})</div>'
                    
                    st.markdown(status_ui, unsafe_allow_html=True)
                    
                    # ถ้าเป็นแดงหรือเหลือง ให้ดึงคำแนะนำจาก Sheet + ข้อควรระวังประจำยา มาโชว์
                    if advice_class:
                        combined_advice = f"<b>💡 คำแนะนำ:</b> {advice if advice else 'ห้ามผสมหรือให้ร่วมกันโดยเด็ดขาด'}"
                        for dname in drug_names:
                            if dname in drug_precautions:
                                combined_advice += f"<br>⚠️ <b>[{dname}]:</b> {drug_precautions[dname]}"
                        
                        st.markdown(f'<div class="advice-container {advice_class}">{combined_advice}</div>', unsafe_allow_html=True)

                # แยกแสดงผล Y-Site และ Admixture
                render_result("Y-Site Compatibility", ['X', 'V', 'Y'], [d1, d2])
                render_result("IV Admixture", ['I', 'U', 'C'], [d1, d2])
                st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<p style="text-align:center; color:#64748b; margin-top:30px;">พัฒนาโดยงานเภสัชสารสนเทศ โรงพยาบาลนครพิงค์ | 053-999200 ต่อ 2279</p>', unsafe_allow_html=True)