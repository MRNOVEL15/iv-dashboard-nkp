import streamlit as st
import pandas as pd

# ==========================================
# 1. ตั้งค่าหน้าเพจและ CSS (Dark Mode Resistant)
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
    
    /* ปุ่มวิเคราะห์ */
    .analyze-btn > button { background-color: #004080 !important; color: white !important; font-weight: bold; width: 100%; padding: 15px; border-radius: 10px; border: none; font-size: 1.2rem; margin-top: 10px; }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 2. ระบบจัดการข้อมูล (Google Sheet)
# ==========================================
if 'd1_key' not in st.session_state: st.session_state.d1_key = "Amiodarone"
if 'd2_key' not in st.session_state: st.session_state.d2_key = "Heparin sodium"
if 'd3_key' not in st.session_state: st.session_state.d3_key = "- ไม่ระบุ -"

def set_quick(a, b):
    st.session_state.d1_key, st.session_state.d2_key, st.session_state.d3_key = a, b, "- ไม่ระบุ -"

@st.cache_data(ttl=30)
def load_data():
    try:
        # 1. ดึงข้อมูลตารางหลัก (Grid)
        main_url = "https://docs.google.com/spreadsheets/d/1IW7mfdOuZ84BskIWPIcgGwueUuq4g5u-4YC7ghIREX4/export?format=csv&gid=2107829411"
        df = pd.read_csv(main_url, index_col=0)
        
        df.index = df.index.astype(str).str.strip().str.capitalize()
        df.columns = df.columns.astype(str).str.strip().str.capitalize()
        
        # 2. ดึงข้อมูลตารางข้อควรระวัง (Sheet 2) แยกเป็น เหลือง และ แดง
        notes = {}
        try:
            notes_url = "https://docs.google.com/spreadsheets/d/1IW7mfdOuZ84BskIWPIcgGwueUuq4g5u-4YC7ghIREX4/export?format=csv&gid=1919782501"
            df_notes = pd.read_csv(notes_url)
            
            for _, row in df_notes.iterrows():
                drug_name = str(row.iloc[0]).strip().capitalize()
                
                # เช็คว่ามีคอลัมน์ B (เหลือง) และ C (แดง) หรือไม่ เพื่อป้องกัน Error
                yellow_note = str(row.iloc[1]).strip() if df_notes.shape[1] > 1 else "nan"
                red_note = str(row.iloc[2]).strip() if df_notes.shape[1] > 2 else "nan"
                
                if pd.notna(drug_name) and drug_name.lower() != 'nan':
                    notes[drug_name] = {}
                    
                    if pd.notna(yellow_note) and yellow_note.lower() != 'nan':
                        notes[drug_name]['yellow'] = yellow_note
                        
                    if pd.notna(red_note) and red_note.lower() != 'nan':
                        notes[drug_name]['red'] = red_note
        except Exception as sheet_err:
            print(f"Notes warning: {sheet_err}") # ไม่ให้แอปพังถ้า Sheet 2 ยังไม่ได้ทำโครงสร้างนี้
            
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
            <span class="legend-text"><b>🟡 สีเหลือง (Uncertain):</b> ข้อมูลไม่ชัดเจน มีเงื่อนไขเฉพาะ หรือผลลัพธ์แปรผันตามความเข้มข้น โปรดระมัดระวัง</span>
        </div>
        <div class="legend-item">
            <div class="legend-color bg-green"></div>
            <span class="legend-text"><b>🟢 สีเขียว (Compatible):</b> ยาเข้ากันได้ สามารถผสมกันหรือให้ร่วมกันได้</span>
        </div>
    </div>
""", unsafe_allow_html=True)

if df is not None:
    st.markdown('<div class="panel-box">', unsafe_allow_html=True)
    
    all_drugs = sorted(list(set([str(d) for d in df.index.tolist() + df.columns.tolist() if "compat" not in str(d).lower() and str(d).lower() != 'nan'])))
    
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

            st.markdown(f'<div class="pair-title-box">{p1} + {p2}</div>', unsafe_allow_html=True)
            
            st.markdown('<div class="panel-box" style="margin-top:-10px;">', unsafe_allow_html=True)
            
            def render_route(label, codes, drug_names):
                code = next((c for c in codes if c in res), "ND")
                mapping = {
                    "X": ("bg-red", "🔴 INCOMPATIBLE", "advice-red"),
                    "I": ("bg-red", "🔴 INCOMPATIBLE", "advice-red"),
                    "V": ("bg-yellow", "🟡 UNCERTAIN", "advice-yellow"),
                    "U": ("bg-yellow", "🟡 UNCERTAIN", "advice-yellow"),
                    "Y": ("bg-green", "🟢 COMPATIBLE", ""),
                    "C": ("bg-green", "🟢 COMPATIBLE", ""),
                    "ND": ("bg-gray", "⚪ NO DATA", "")
                }
                cls, txt, adv_cls = mapping.get(code, ("bg-gray", "⚪ NO DATA", ""))

                st.markdown(f'<div style="color:#475569; font-weight:bold; font-size:0.95rem; margin-bottom:5px;">{label}</div>', unsafe_allow_html=True)
                st.markdown(f'<div class="status-badge {cls}">{txt}</div>', unsafe_allow_html=True)
                
                # --- จัดการดึงคำแนะนำแยกตามสี (จาก Sheet 2) ---
                if adv_cls == "advice-red":
                    full_txt = f"<b>💡 คำแนะนำ:</b> {sheet_advice if sheet_advice else 'ยาเข้ากันไม่ได้ ห้ามผสมกันหรือห้ามให้ร่วมกันโดยเด็ดขาด'}"
                    for dn in drug_names:
                        # เช็คว่ามียาตัวนี้ใน Sheet 2 และมีคำเตือนในคอลัมน์ C (red) หรือไม่
                        if dn in drug_notes and 'red' in drug_notes[dn]:
                            full_txt += f"<br>⚠️ <b>[{dn}]:</b> {drug_notes[dn]['red']}"
                    st.markdown(f'<div class="advice-container {adv_cls}">{full_txt}</div>', unsafe_allow_html=True)
                
                elif adv_cls == "advice-yellow":
                    full_txt = f"<b>💡 คำแนะนำ:</b> {sheet_advice if sheet_advice else 'ข้อมูลแปรผันตามเงื่อนไข โปรดระมัดระวัง'}"
                    for dn in drug_names:
                        # เช็คว่ามียาตัวนี้ใน Sheet 2 และมีคำเตือนในคอลัมน์ B (yellow) หรือไม่
                        if dn in drug_notes and 'yellow' in drug_notes[dn]:
                            full_txt += f"<br>⚠️ <b>[{dn}]:</b> {drug_notes[dn]['yellow']}"
                    st.markdown(f'<div class="advice-container {adv_cls}">{full_txt}</div>', unsafe_allow_html=True)

            render_route("Y-Site Compatibility", ["X", "V", "Y"], [p1, p2])
            st.markdown('<hr style="margin: 15px 0; border-color: #f1f5f9;">', unsafe_allow_html=True)
            render_route("IV Admixture (ผสมถุง)", ["I", "U", "C"], [p1, p2])
            
            st.markdown('</div>', unsafe_allow_html=True)

    with st.expander("⚡ คู่ยาที่พบบ่อย (Quick Select)"):
        q_pairs = [("Amiodarone", "Heparin sodium"), ("Dobutamine", "Furosemide"), ("Norepinephrine", "Sodium bicarbonate")]
        for a, b in q_pairs:
            st.button(f"🚨 {a} + {b}", on_click=set_quick, args=(a, b), use_container_width=True, key=f"q_{a}_{b}")

st.markdown('<p style="text-align:center; color:#94a3b8; font-size:0.8rem; margin-top:20px;">งานเภสัชสนเทศ (DIS) โรงพยาบาลนครพิงค์</p>', unsafe_allow_html=True)