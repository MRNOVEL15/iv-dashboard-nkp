import streamlit as st
import pandas as pd

# ==========================================
# 1. ตั้งค่าหน้าเพจและ CSS 
# ==========================================
st.set_page_config(page_title="IV Dashboard Incompatibility | DIS Nakornping", layout="wide", initial_sidebar_state="collapsed")

st.markdown("""
    <style>
    .stApp { background-color: #f4f7f9; }
    .main .block-container { padding: 1rem 0.5rem; }

    /* Header โรงพยาบาล */
    .header-banner { background-color: #004080; color: white; padding: 20px 30px; border-radius: 8px; margin-bottom: 25px; border-bottom: 4px solid #e11d48; }
    .header-banner h1 { margin: 0; font-size: 1.8rem; font-weight: 700; color: white !important; }
    .header-banner p { margin: 5px 0 0 0; font-size: 1rem; opacity: 0.9; color: white !important; }
    
    /* กล่องแผงควบคุม */
    .panel-box { background-color: white; padding: 15px; border-radius: 12px; border: 1px solid #e2e8f0; margin-bottom: 20px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); }

    /* 🔥 กล่องชื่อคู่ยา (บังคับสีเข้มสู้ Dark Mode) */
    .pair-title-box {
        background-color: #e2e8f0 !important;
        color: #0f172a !important; /* บังคับตัวหนังสือสีดำ/น้ำเงินเข้ม */
        padding: 15px;
        border-radius: 8px;
        text-align: center;
        font-size: 1.3rem;
        font-weight: 900;
        border-bottom: 4px solid #004080;
        margin-top: 20px;
        margin-bottom: 15px;
    }

    /* ป้ายสถานะ */
    .status-badge { display: block; padding: 12px; font-weight: 800; font-size: 1.1rem; border-radius: 8px; text-align: center; margin-bottom: 2px; }
    .bg-green { background-color: #ecfdf5 !important; color: #059669 !important; border: 2px solid #34d399; }
    .bg-red { background-color: #fef2f2 !important; color: #dc2626 !important; border: 2px solid #f87171; }
    .bg-yellow { background-color: #fefce8 !important; color: #b45309 !important; border: 2px solid #fbbf24; }
    .bg-gray { background-color: #f8fafc !important; color: #64748b !important; border: 2px solid #cbd5e1; }
    
    /* 🔥 กล่องคำแนะนำ (บังคับตัวหนังสือสีเข้มทับ Dark Mode) */
    .advice-container { padding: 15px; border-radius: 0 0 8px 8px; font-size: 0.95rem; line-height: 1.6; margin-bottom: 15px; border: 2px solid transparent; border-top: none; }
    .advice-container b, .advice-container span, .advice-container div { color: #0f172a !important; } /* บังคับทุกอย่างข้างในเป็นสีเข้ม */
    .advice-red { background-color: #fff1f2 !important; border-color: #f87171 !important; color: #0f172a !important; }
    .advice-yellow { background-color: #fffbeb !important; border-color: #fbbf24 !important; color: #0f172a !important; }
    
    /* ปุ่มวิเคราะห์สีน้ำเงิน */
    .analyze-btn > button { background-color: #004080 !important; color: white !important; font-weight: bold; width: 100%; padding: 15px; border-radius: 10px; border: none; font-size: 1.2rem; margin-top: 10px; }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 2. ระบบจัดการข้อมูล (Google Sheet)
# ==========================================
if 'd1_key' not in st.session_state: st.session_state.d1_key = "Amiodarone"
if 'd2_key' not in st.session_state: st.session_state.d2_key = "Heparin"
if 'd3_key' not in st.session_state: st.session_state.d3_key = "- ไม่ระบุ -"

def set_quick(a, b):
    st.session_state.d1_key, st.session_state.d2_key, st.session_state.d3_key = a, b, "- ไม่ระบุ -"

@st.cache_data(ttl=30)
def load_data():
    try:
        url = "https://docs.google.com/spreadsheets/d/e/2PACX-1vRVvgXF-uMZbdJXUnFoc_EbGM_JygWW53SlhMBvk4q4s2obzEviIB4nvpRjGDg1X15hOLveeih9zzuB/pub?output=csv"
        df = pd.read_csv(url, index_col=0)
        df.index = df.index.astype(str).str.strip()
        df.columns = df.columns.astype(str).str.strip()
        
        # ข้อควรระวังเฉพาะตัวยา (โชว์เฉพาะเคสสีแดง)
        notes = {
            "Ceftriaxone": "ห้ามผสมกับแคลเซียมเด็ดขาด เสี่ยงเกิดผลึกอุดตันในหลอดเลือดและเป็นอันตรายถึงชีวิต",
            "Calcium gluconate": "เสี่ยงเกิดตะกอนสูงเมื่อสัมผัสกับยาปฏิชีวนะหลายชนิด",
            "Furosemide": "เป็นด่างสูง เกิดตะกอนขุ่นขาวทันทีเมื่อเจอสารละลายกรด หากเลี่ยงไม่ได้ต้อง Flush สาย",
            "Midazolam": "เป็นกรด ตกตะกอนทันทีเมื่อเจอสารละลายด่าง",
            "Norepinephrine": "เสื่อมสภาพได้ง่ายในสารละลายที่มีความเป็นด่างจัด",
            "Amphotericin B": "ห้ามผสม NSS เด็ดขาด ยาจะตกตะกอนทันที"
        }
        return df, notes, "OK"
    except: return None, {}, "Error"

df, drug_notes, status = load_data()

# ==========================================
# 3. ส่วนการทำงานหลัก
# ==========================================
st.markdown("""
    <div class="header-banner">
        <h1>🏥 IV Dashboard Incompatibility</h1>
        <p>งานเภสัชสารสนเทศ (DIS) • โรงพยาบาลนครพิงค์</p>
    </div>
""", unsafe_allow_html=True)

if df is not None:
    st.markdown('<div class="panel-box">', unsafe_allow_html=True)
    all_drugs = sorted(list(set([str(d) for d in df.index.tolist() + df.columns.tolist() if "compat" not in str(d).lower() and str(d) != 'nan'])))
    
    d1_sel = st.selectbox("💉 ยาตัวที่ 1", all_drugs, key="d1_key")
    d2_sel = st.selectbox("💉 ยาตัวที่ 2", all_drugs, key="d2_key")
    d3_sel = st.selectbox("💉 ยาตัวที่ 3 (ถ้ามี)", ["- ไม่ระบุ -"] + all_drugs, key="d3_key")
    
    st.markdown('<div class="analyze-btn">', unsafe_allow_html=True)
    check = st.button("ประมวลผลความเข้ากันได้", use_container_width=True)
    st.markdown('</div></div>', unsafe_allow_html=True)

    if check:
        pairs = [(d1_sel, d2_sel)]
        if d3_sel != "- ไม่ระบุ -":
            pairs.extend([(d1_sel, d3_sel), (d2_sel, d3_sel)])
        
        for p1, p2 in pairs:
            if p1 == p2: continue
            
            raw = ""
            if p1 in df.index and p2 in df.columns: raw = str(df.loc[p1, p2])
            elif p2 in df.index and p1 in df.columns: raw = str(df.loc[p2, p1])
            
            res, sheet_advice = (raw.split('|', 1) + [""])[:2] if '|' in raw else (raw, "")
            res = res.strip().upper()
            sheet_advice = sheet_advice.strip()

            # --- ชื่อคู่ยา (ไม่อิโมจิ บังคับสีเข้ม) ---
            st.markdown(f'<div class="pair-title-box">{p1} + {p2}</div>', unsafe_allow_html=True)
            
            st.markdown('<div class="panel-box" style="margin-top:-10px;">', unsafe_allow_html=True)
            
            def render_route(label, codes, drug_names):
                code = next((c for c in codes if c in res), "ND")
                mapping = {
                    "X": ("bg-red", "🔴 INCOMPATIBLE", "advice-red"),
                    "I": ("bg-red", "🔴 INCOMPATIBLE", "advice-red"),
                    "V": ("bg-yellow", "🟡 Uncertain/Variable Results", "advice-yellow"),
                    "U": ("bg-yellow", "🟡 Uncertain/Variable Results", "advice-yellow"),
                    "Y": ("bg-green", "🟢 COMPATIBLE", ""),
                    "C": ("bg-green", "🟢 COMPATIBLE", ""),
                    "ND": ("bg-gray", "⚪ NO DATA", "")
                }
                cls, txt, adv_cls = mapping.get(code, ("bg-gray", "⚪ NO DATA", ""))

                st.markdown(f'<div style="color:#475569; font-weight:bold; font-size:0.95rem; margin-bottom:5px;">{label}</div>', unsafe_allow_html=True)
                st.markdown(f'<div class="status-badge {cls}">{txt}</div>', unsafe_allow_html=True)
                
                # --- จัดการกล่องคำแนะนำ (แดง vs เหลือง) ---
                if adv_cls == "advice-red":
                    # สีแดง: ดึงจาก Sheet + เติมข้อควรระวังเฉพาะยา
                    full_txt = f"<b>💡 คำแนะนำ:</b> {sheet_advice if sheet_advice else 'ห้ามผสมหรือให้ร่วมกันโดยเด็ดขาด'}"
                    for dn in drug_names:
                        if dn in drug_notes:
                            full_txt += f"<br>⚠️ <b>[{dn}]:</b> {drug_notes[dn]}"
                    st.markdown(f'<div class="advice-container {adv_cls}">{full_txt}</div>', unsafe_allow_html=True)
                
                elif adv_cls == "advice-yellow":
                    # สีเหลือง: โชว์แค่สิ่งที่พิมพ์ใน Google Sheet เท่านั้น
                    if sheet_advice:
                        full_txt = f"<b>💡 คำแนะนำ:</b> {sheet_advice}"
                        st.markdown(f'<div class="advice-container {adv_cls}">{full_txt}</div>', unsafe_allow_html=True)

            render_route("Y-Site Compatibility", ["X", "V", "Y"], [p1, p2])
            st.markdown('<hr style="margin: 15px 0; border-color: #f1f5f9;">', unsafe_allow_html=True)
            render_route("IV Admixture (ผสมถุง)", ["I", "U", "C"], [p1, p2])
            
            st.markdown('</div>', unsafe_allow_html=True)

    with st.expander("⚡ คู่ยาที่พบบ่อย (Quick Select)"):
        q_pairs = [("Amiodarone", "Heparin"), ("Dobutamine", "Furosemide"), ("Norepinephrine", "Sodium bicarbonate")]
        for a, b in q_pairs:
            st.button(f"🚨 {a} + {b}", on_click=set_quick, args=(a, b), use_container_width=True, key=f"q_{a}_{b}")

st.markdown('<p style="text-align:center; color:#94a3b8; font-size:0.8rem; margin-top:20px;">งานเภสัชสารสนเทศ โรงพยาบาลนครพิงค์</p>', unsafe_allow_html=True)