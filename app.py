import streamlit as st
import pandas as pd
import itertools
import re

# ==========================================
# 1. ตั้งค่าหน้าเพจและ CSS (สู้ Dark Mode + ปรับปุ่มให้เด่นขึ้น)
# ==========================================
st.set_page_config(page_title="IV Compatibility Dashboard | DIS Nakornping", layout="wide", initial_sidebar_state="collapsed")

st.markdown("""
    <style>
    .stApp { background-color: #f4f7f9; }
    .main .block-container { padding: 1rem 0.5rem; }

    /* Header โรงพยาบาล */
    .header-banner { background-color: #004080; color: white; padding: 20px 30px; border-radius: 8px; margin-bottom: 15px; border-bottom: 4px solid #e11d48; }
    .header-banner h1 { margin: 0; font-size: 1.8rem; font-weight: 700; color: white !important; }
    .header-banner p { margin: 5px 0 0 0; font-size: 1rem; opacity: 0.9; color: white !important; }
    
    /* กล่องคำอธิบายสัญลักษณ์ (Legend) */
    .legend-box { background-color: white; padding: 15px; border-radius: 8px; border: 1px dashed #cbd5e1; margin-bottom: 20px; font-size: 0.95rem; color: #0f172a !important; box-shadow: 0 1px 2px rgba(0,0,0,0.05); }
    .legend-item { display: flex; align-items: flex-start; margin-bottom: 8px; }
    .legend-color { min-width: 18px; height: 18px; border-radius: 4px; margin-right: 10px; margin-top: 3px; border: 1px solid rgba(0,0,0,0.1); }
    .legend-text { color: #0f172a !important; line-height: 1.4; }

    /* กล่องแผงควบคุมหลัก */
    .panel-box { background-color: white; padding: 15px; border-radius: 12px; border: 1px solid #e2e8f0; margin-bottom: 20px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); }

    /* กล่องชื่อคู่ยา */
    .pair-title-box { background-color: #e2e8f0 !important; color: #0f172a !important; padding: 15px; border-radius: 8px; text-align: center; font-size: 1.3rem; font-weight: 900; border-bottom: 4px solid #004080; margin-top: 20px; margin-bottom: 15px; }

    /* ป้ายสถานะ */
    .status-badge { display: block; padding: 12px; font-weight: 800; font-size: 1.1rem; border-radius: 8px; text-align: center; margin-bottom: 2px; }
    .bg-green { background-color: #ecfdf5 !important; color: #059669 !important; border: 2px solid #34d399; }
    .bg-red { background-color: #fef2f2 !important; color: #dc2626 !important; border: 2px solid #f87171; }
    .bg-yellow { background-color: #fefce8 !important; color: #b45309 !important; border: 2px solid #fbbf24; }
    .bg-gray { background-color: #f8fafc !important; color: #64748b !important; border: 2px solid #cbd5e1; }
    
    /* กล่องคำแนะนำ */
    .advice-container { padding: 15px; border-radius: 0 0 8px 8px; font-size: 0.95rem; line-height: 1.6; margin-bottom: 15px; border: 2px solid transparent; border-top: none; }
    .advice-container b, .advice-container span, .advice-container div { color: #0f172a !important; } 
    .advice-red { background-color: #fff1f2 !important; border-color: #f87171 !important; color: #0f172a !important; }
    .advice-yellow { background-color: #fffbeb !important; border-color: #fbbf24 !important; color: #0f172a !important; }
    
    /* 🛠️ ปุ่มวิเคราะห์ (ปรับให้มีมิติ มองหาง่ายขึ้น แต่ไม่รก) */
    .analyze-btn > button { 
        background-color: #004080 !important; 
        color: white !important; 
        font-weight: bold; 
        width: 100%; 
        padding: 16px; 
        border-radius: 10px; 
        border: none; 
        font-size: 1.25rem; 
        margin-top: 15px; 
        box-shadow: 0 4px 6px rgba(0,0,0,0.15); /* เพิ่มเงาบางๆ */
        transition: all 0.2s ease-in-out; 
    }
    .analyze-btn > button:hover {
        background-color: #002b5e !important;
        box-shadow: 0 6px 12px rgba(0,0,0,0.2); /* เงาชัดขึ้นตอนชี้เมาส์ */
        transform: translateY(-2px); /* ปุ่มลอยขึ้นนิดๆ */
    }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 2. ระบบจัดการข้อมูลและตั้งค่าเริ่มต้น
# ==========================================
PLACEHOLDER = "-- เลือกยาฉีด --"
FLUID_PLACEHOLDER = "-- ไม่ระบุสารน้ำ --"

FLUID_MAPPING = {
    FLUID_PLACEHOLDER: FLUID_PLACEHOLDER,
    "Dextrose/water (D5W)": "Dextrose/water",
    "Dextrose/NSS (D5/NSS)": "Dextrose/nss",
    "Normal saline (NSS)": "Normal saline",
    "Lactated ringer (LRI)": "Lactated ringer"
}

if 'd1_key' not in st.session_state: st.session_state.d1_key = PLACEHOLDER
if 'd2_key' not in st.session_state: st.session_state.d2_key = PLACEHOLDER
if 'd3_key' not in st.session_state: st.session_state.d3_key = PLACEHOLDER
if 'd4_key' not in st.session_state: st.session_state.d4_key = PLACEHOLDER
if 'd5_key' not in st.session_state: st.session_state.d5_key = FLUID_PLACEHOLDER

def set_quick(a, b, fluid=FLUID_PLACEHOLDER):
    st.session_state.d1_key = a
    st.session_state.d2_key = b
    st.session_state.d3_key = PLACEHOLDER
    st.session_state.d4_key = PLACEHOLDER
    st.session_state.d5_key = fluid

@st.cache_data(ttl=30)
def load_data():
    try:
        main_url = "https://docs.google.com/spreadsheets/d/1IW7mfdOuZ84BskIWPIcgGwueUuq4g5u-4YC7ghIREX4/export?format=csv&gid=2107829411"
        df = pd.read_csv(main_url, index_col=0)
        
        df.index = df.index.astype(str).str.replace(r'\s+', ' ', regex=True).str.strip().str.capitalize()
        df.columns = df.columns.astype(str).str.replace(r'\s+', ' ', regex=True).str.strip().str.capitalize()
        
        notes = {}
        try:
            notes_url = "https://docs.google.com/spreadsheets/d/1IW7mfdOuZ84BskIWPIcgGwueUuq4g5u-4YC7ghIREX4/export?format=csv&gid=1919782501"
            df_notes = pd.read_csv(notes_url)
            
            for _, row in df_notes.iterrows():
                drug_name = re.sub(r'\s+', ' ', str(row.iloc[0])).strip().capitalize()
                yellow_note = str(row.iloc[1]).strip() if df_notes.shape[1] > 1 else "nan"
                red_note = str(row.iloc[2]).strip() if df_notes.shape[1] > 2 else "nan"
                
                if pd.notna(drug_name) and drug_name.lower() != 'nan':
                    notes[drug_name] = {}
                    if pd.notna(yellow_note) and yellow_note.lower() != 'nan':
                        notes[drug_name]['yellow'] = yellow_note
                    if pd.notna(red_note) and red_note.lower() != 'nan':
                        notes[drug_name]['red'] = red_note
        except Exception as sheet_err:
            pass
            
        return df, notes, "OK"
    except Exception as e:
        return None, {}, str(e)

df, drug_notes, status = load_data()

# ==========================================
# 3. ส่วนการทำงานหลักหน้าจอ
# ==========================================
st.markdown("""
    <div class="header-banner">
        <h1>🏥 IV Compatibility Dashboard</h1>
        <p>งานเภสัชสนเทศ (DIS) • โรงพยาบาลนครพิงค์</p>
    </div>
""", unsafe_allow_html=True)

st.markdown("""
    <div class="legend-box">
        <b style="color:#0f172a; font-size:1.05rem;">📌 นิยามศัพท์การแปรผล:</b>
        <div class="legend-item" style="margin-top:10px;">
            <div class="legend-color bg-red"></div>
            <span class="legend-text"><b>🔴 สีแดง (Incompatible):</b> ยาเข้ากันไม่ได้ ห้ามผสมกันหรือห้ามให้ร่วมกันโดยเด็ดขาด</span>
        </div>
        <div class="legend-item">
            <div class="legend-color bg-yellow"></div>
            <span class="legend-text"><b>🟡 สีเหลือง (Variable result):</b> มีเงื่อนไขเฉพาะทำให้ผลไม่แน่นอน (แปรผันตามความเข้มข้น, pH หรือเวลา)</span>
        </div>
        <div class="legend-item">
            <div class="legend-color bg-green"></div>
            <span class="legend-text"><b>🟢 สีเขียว (Compatible):</b> ยาเข้ากันได้ สามารถผสมกันหรือให้ร่วมกันได้</span>
        </div>
    </div>
""", unsafe_allow_html=True)

if df is not None:
    st.markdown('<div class="panel-box">', unsafe_allow_html=True)
    
    raw_fluids_to_exclude = [v for k, v in FLUID_MAPPING.items() if v != FLUID_PLACEHOLDER]
    
    drug_list = sorted(list(set([
        str(d) for d in df.index.tolist() + df.columns.tolist() 
        if "compat" not in str(d).lower() 
        and str(d).lower() != 'nan'
        and str(d) not in raw_fluids_to_exclude
    ])))
    
    all_drugs = [PLACEHOLDER] + drug_list
    
    col1, col2 = st.columns(2)
    with col1:
        d1_sel = st.selectbox("💉 ยาฉีด ตัวที่ 1", all_drugs, key="d1_key")
        d2_sel = st.selectbox("💉 ยาฉีด ตัวที่ 2 (ถ้าผสมร่วมกัน)", all_drugs, key="d2_key")
        d3_sel = st.selectbox("💉 ยาฉีด ตัวที่ 3 (ถ้าผสมร่วมกัน)", all_drugs, key="d3_key")
    with col2:
        d4_sel = st.selectbox("💉 ยาฉีด ตัวที่ 4 (ถ้าผสมร่วมกัน)", all_drugs, key="d4_key")
        d5_sel = st.selectbox("💧 สารน้ำหลัก / สารละลาย (Base Solution)", list(FLUID_MAPPING.keys()), key="d5_key")
    
    st.markdown('<div class="analyze-btn">', unsafe_allow_html=True)
    # 🛠️ เปลี่ยนข้อความและใส่ไอคอนให้ปุ่มดูชัดเจนขึ้น
    check = st.button("🔍 ประมวลผลความเข้ากันได้", use_container_width=True)
    st.markdown('</div></div>', unsafe_allow_html=True)

    if check:
        selected_drugs = [d for d in [d1_sel, d2_sel, d3_sel, d4_sel] if d != PLACEHOLDER]
        
        if d5_sel != FLUID_PLACEHOLDER:
            selected_drugs.append(FLUID_MAPPING[d5_sel])
        
        if len(selected_drugs) < 2:
            st.warning("⚠️ กรุณาเลือก ยาฉีด หรือ สารน้ำ อย่างน้อย 2 ชนิด เพื่อตรวจสอบความเข้ากันได้")
        else:
            pairs = list(itertools.combinations(selected_drugs, 2))
            
            st.markdown(f"### 📊 ผลการตรวจสอบทั้งหมด ({len(pairs)} คู่)")
            
            for p1, p2 in pairs:
                raw = ""
                if p1 in df.index and p2 in df.columns and pd.notna(df.loc[p1, p2]) and str(df.loc[p1, p2]).strip().lower() != 'nan':
                    raw = str(df.loc[p1, p2])
                
                if raw == "" and p2 in df.index and p1 in df.columns and pd.notna(df.loc[p2, p1]) and str(df.loc[p2, p1]).strip().lower() != 'nan':
                    raw = str(df.loc[p2, p1])
                
                res, sheet_advice = (raw.split('|', 1) + [""])[:2] if '|' in raw else (raw, "")
                res = res.strip().upper()
                sheet_advice = sheet_advice.strip()

                st.markdown(f'<div class="pair-title-box">{p1} + {p2}</div>', unsafe_allow_html=True)
                st.markdown('<div class="panel-box" style="margin-top:-10px;">', unsafe_allow_html=True)
                
                def render_route(label, codes, drug_names):
                    code = next((c for c in codes if c in res), "ND")
                    mapping = {
                        "X": ("bg-red", "🔴 INCOMPATIBLE", "advice-red"),
                        "I": ("bg-red", "🔴 INCOMPATIBLE", "advice-red"),
                        "V": ("bg-yellow", "🟡 Variable result (มีเงื่อนไขเฉพาะทำให้ผลไม่แน่นอน)", "advice-yellow"),
                        "U": ("bg-yellow", "🟡 Variable result (มีเงื่อนไขเฉพาะทำให้ผลไม่แน่นอน)", "advice-yellow"),
                        "Y": ("bg-green", "🟢 COMPATIBLE", ""),
                        "C": ("bg-green", "🟢 COMPATIBLE", ""),
                        "ND": ("bg-gray", "⚪ NO DATA", "")
                    }
                    cls, txt, adv_cls = mapping.get(code, ("bg-gray", "⚪ NO DATA", ""))

                    st.markdown(f'<div style="color:#475569; font-weight:bold; font-size:0.95rem; margin-bottom:5px;">{label}</div>', unsafe_allow_html=True)
                    st.markdown(f'<div class="status-badge {cls}">{txt}</div>', unsafe_allow_html=True)
                    
                    if adv_cls == "advice-red":
                        full_txt = f"<b>💡 คำแนะนำ:</b> {sheet_advice if sheet_advice else 'ยาเข้ากันไม่ได้ ห้ามผสมกันหรือห้ามให้ร่วมกันโดยเด็ดขาด'}"
                        for dn in drug_names:
                            if dn in drug_notes and 'red' in drug_notes[dn]:
                                full_txt += f"<br>⚠️ <b>[{dn}]:</b> {drug_notes[dn]['red']}"
                        st.markdown(f'<div class="advice-container {adv_cls}">{full_txt}</div>', unsafe_allow_html=True)
                    
                    elif adv_cls == "advice-yellow":
                        default_yellow_msg = "โปรดตรวจสอบเงื่อนไขเฉพาะ: ความเข้มข้น, ค่าความเป็นกรด-ด่าง (pH), หรือระยะเวลาในการให้ยา"
                        full_txt = f"<b>💡 คำแนะนำ (บังคับอ่าน):</b> {sheet_advice if sheet_advice else default_yellow_msg}"
                        
                        for dn in drug_names:
                            if dn in drug_notes and 'yellow' in drug_notes[dn]:
                                full_txt += f"<br>⚠️ <b>[{dn}]:</b> {drug_notes[dn]['yellow']}"
                        st.markdown(f'<div class="advice-container {adv_cls}">{full_txt}</div>', unsafe_allow_html=True)

                render_route("Y-Site Compatibility", ["X", "V", "Y"], [p1, p2])
                st.markdown('<hr style="margin: 15px 0; border-color: #f1f5f9;">', unsafe_allow_html=True)
                render_route("IV Admixture (ผสมถุง)", ["I", "U", "C"], [p1, p2])
                st.markdown('</div>', unsafe_allow_html=True)

    with st.expander("⚡ คู่ยาที่พบบ่อย (Quick Select)"):
        st.button("🚨 Calcium gluconate + Sodium bicarbonate", 
                  on_click=set_quick, 
                  args=("Calcium gluconate", "Sodium bicarbonate", FLUID_PLACEHOLDER), 
                  use_container_width=True)
        
        st.button("🚨 Midazolam + Furosemide", 
                  on_click=set_quick, 
                  args=("Midazolam", "Furosemide", FLUID_PLACEHOLDER), 
                  use_container_width=True)
        
        st.button("🚨 Phenytoin + D5W", 
                  on_click=set_quick, 
                  args=("Phenytoin", PLACEHOLDER, "Dextrose/water (D5W)"), 
                  use_container_width=True)
        
        st.button("🚨 Amiodarone + Heparin sodium", 
                  on_click=set_quick, 
                  args=("Amiodarone", "Heparin sodium", FLUID_PLACEHOLDER), 
                  use_container_width=True)

st.markdown('<p style="text-align:center; color:#94a3b8; font-size:0.8rem; margin-top:20px;">งานเภสัชสนเทศ (DIS) โรงพยาบาลนครพิงค์</p>', unsafe_allow_html=True)