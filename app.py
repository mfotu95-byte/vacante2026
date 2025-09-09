import streamlit as st
import pandas as pd
from io import BytesIO
from datetime import datetime

st.set_page_config(page_title="Planner Zile Libere 2026", layout="centered")
st.title("🗓️ Planner Zile Libere & Vacanțe – România 2026 (interactiv)")

# ----------------------------
#  CONFIG & STATE
# ----------------------------
if "personal_days" not in st.session_state:
    st.session_state.personal_days = []  # list of dicts: {"Data":"2026-xx-xx","Motiv":"..."}

if "custom_vacations" not in st.session_state:
    st.session_state.custom_vacations = []  # list of dicts: {"Start":"2026-..","Stop":"2026-..","Descriere":"...","PTO":N}

# Zile libere legale 2026
HOLIDAYS_2026 = [
    ("2026-01-01","Anul Nou"),
    ("2026-01-02","A doua zi de Anul Nou"),
    ("2026-01-06","Boboteaza"),
    ("2026-01-07","Sf. Ioan Botezătorul"),
    ("2026-01-24","Ziua Unirii Principatelor Române"),
    ("2026-04-10","Vinerea Mare (Paște ortodox)"),
    ("2026-04-12","Paștele ortodox"),
    ("2026-04-13","A doua zi de Paște"),
    ("2026-05-01","Ziua Muncii"),
    ("2026-05-31","Rusalii (prima zi)"),
    ("2026-06-01","A doua zi de Rusalii"),
    ("2026-06-01","Ziua Copilului"),
    ("2026-08-15","Adormirea Maicii Domnului"),
    ("2026-11-30","Sf. Andrei"),
    ("2026-12-01","Ziua Națională"),
    ("2026-12-25","Crăciun – prima zi"),
    ("2026-12-26","Crăciun – a doua zi"),
]
WEEKDAY_RO = {0:"Luni",1:"Marți",2:"Miercuri",3:"Joi",4:"Vineri",5:"Sâmbătă",6:"Duminică"}

def holidays_df():
    df = pd.DataFrame(HOLIDAYS_2026, columns=["Data","Sărbătoare"])
    df["Data"] = pd.to_datetime(df["Data"])
    df["Ziua"] = df["Data"].dt.weekday.map(WEEKDAY_RO)
    return df.sort_values("Data")[["Data","Ziua","Sărbătoare"]]

DF_H = holidays_df()
HOLIDAY_DATES = set(DF_H["Data"].dt.date)

# ----------------------------
#  SIDEBAR – PTO & INFO
# ----------------------------
st.sidebar.header("⚙️ Setări")
pto_total = st.sidebar.number_input("Zile concediu disponibile (PTO)", 0, 60, 22, 1)
st.sidebar.caption("Poți schimba numărul oricând; rezumatul se actualizează automat.")

# ----------------------------
#  SECTIUNEA 1 – ZILE LIBERE LEGALE
# ----------------------------
st.subheader("🥳 Zile libere legale 2026")
st.dataframe(DF_H, use_container_width=True)

# ----------------------------
#  SECTIUNEA 2 – ZILE LIBERE PERSONALE (CUSTOM)
# ----------------------------
st.subheader("➕ Zile libere personale (nu consumă PTO)")
with st.expander("Adaugă/editează zile personale"):
    col1, col2, col3 = st.columns([1,2,1])
    with col1:
        pd_date = st.date_input("Data", format="YYYY-MM-DD", value=None)
    with col2:
        pd_reason = st.text_input("Motiv / etichetă", placeholder="Ex: Zi liberă contractuală")
    with col3:
        if st.button("Adaugă zi personală"):
            if pd_date:
                st.session_state.personal_days.append({"Data": str(pd_date), "Motiv": pd_reason or ""})
            else:
                st.warning("Alege o dată pentru ziua personală.")

    # editor pentru șters/modificat
    df_personal = pd.DataFrame(st.session_state.personal_days)
    if not df_personal.empty:
        edited = st.data_editor(
            df_personal,
            use_container_width=True,
            num_rows="dynamic",
            key="editor_personal_days"
        )
        # salvează direct modificările
        st.session_state.personal_days = edited.to_dict(orient="records")
    else:
        st.info("Nu ai adăugat încă zile personale.")

PERSONAL_DATES = { datetime.fromisoformat(r["Data"]).date() for r in st.session_state.personal_days } if st.session_state.personal_days else set()

# ----------------------------
#  SECTIUNEA 3 – PROPUNERI (BIFABILE)
# ----------------------------
st.subheader("🧩 Propuneri de mini-vacanțe (bifează ce vrei să păstrezi)")
proposals = [
    {"Interval":"2026-01-01 → 2026-01-07","Zile_PTO":1,"Detalii":"PTO: 2026-01-05 (luni)","Motiv":"Leagă 1-2 ian + weekend + 6-7 ian","Idee":"City break / munte","Include":True},
    {"Interval":"2026-04-09 → 2026-04-14","Zile_PTO":2,"Detalii":"PTO: 2026-04-09 (joi), 2026-04-14 (marți)","Motiv":"Vinerea Mare + Paște + Lunea Paștelui","Idee":"Maramureș/Bucovina sau Lisabona","Include":True},
    {"Interval":"2026-04-30 → 2026-05-03","Zile_PTO":1,"Detalii":"PTO: 2026-04-30 (joi)","Motiv":"Ziua Muncii (vineri) + weekend","Idee":"Marea/Delta; Napoli & Amalfi","Include":True},
    {"Interval":"2026-05-30 → 2026-06-02","Zile_PTO":1,"Detalii":"PTO: 2026-06-02 (marți)","Motiv":"Rusalii (duminică) + Lunea Rusaliilor & 1 Iunie","Idee":"City break nordic","Include":True},
    {"Interval":"2026-08-14 → 2026-08-16","Zile_PTO":1,"Detalii":"PTO: 2026-08-14 (vineri)","Motiv":"Sf. Maria e sâmbătă — mini-vacanță","Idee":"Mare / Thassos","Include":False},
    {"Interval":"2026-11-27 → 2026-12-02","Zile_PTO":2,"Detalii":"PTO: 2026-11-27 (vineri), 2026-12-02 (miercuri)","Motiv":"Sf. Andrei (luni) + Ziua Națională (marți)","Idee":"Târguri de Crăciun","Include":True},
    {"Interval":"2026-12-24 → 2026-12-27","Zile_PTO":1,"Detalii":"PTO: 2026-12-24 (joi)","Motiv":"Crăciun (vineri & sâmbătă) + duminică","Idee":"Acasă / city break apropiat","Include":False},
]
df_prop = pd.DataFrame(proposals)
df_prop_edit = st.data_editor(
    df_prop,
    column_config={
        "Include": st.column_config.CheckboxColumn("Include"),
    },
    hide_index=True,
    use_container_width=True,
    key="editor_proposals"
)
pto_from_props = int(df_prop_edit.loc[df_prop_edit["Include"], "Zile_PTO"].sum())

# ----------------------------
#  SECTIUNEA 4 – CONCEDIILE TALE (CUSTOM)
# ----------------------------
st.subheader("✍️ Concediile tale (intervale custom)")

def working_days_pto(start_date, end_date):
    """Calculează zile PTO între două date: luni-vineri, excludem sărbătorile legale + zilele personale."""
    if start_date > end_date:
        start_date, end_date = end_date, start_date
    rng = pd.bdate_range(start=start_date, end=end_date, freq="C")  # business days
    # remove legal holidays and personal days that fall on weekdays
    count = 0
    for dts in rng:
        d = dts.date()
        if d in HOLIDAY_DATES or d in PERSONAL_DATES:
            continue
        count += 1
    return count

with st.form("add_custom_vacation", clear_on_submit=True):
    c1, c2 = st.columns(2)
    with c1:
        start = st.date_input("Start", format="YYYY-MM-DD")
    with c2:
        stop = st.date_input("Stop", format="YYYY-MM-DD")
    descr = st.text_input("Descriere (opțional)", placeholder="Ex: Grecia iunie")
    submitted = st.form_submit_button("Adaugă interval")
    if submitted:
        if start and stop:
            pto_days = working_days_pto(start, stop)
            st.session_state.custom_vacations.append({
                "Start": str(start),
                "Stop": str(stop),
                "Descriere": descr,
                "Zile_PTO": int(pto_days)
            })
        else:
            st.warning("Alege atât data de start, cât și data de stop.")

df_custom = pd.DataFrame(st.session_state.custom_vacations)
if not df_custom.empty:
    edited_custom = st.data_editor(
        df_custom,
        use_container_width=True,
        num_rows="dynamic",
        key="editor_custom_vac"
    )
    st.session_state.custom_vacations = edited_custom.to_dict(orient="records")
    pto_from_custom = int(edited_custom["Zile_PTO"].sum())
else:
    st.info("Nu ai adăugat încă intervale custom.")
    pto_from_custom = 0

# ----------------------------
#  REZUMAT PTO
# ----------------------------
pto_planned = pto_from_props + pto_from_custom
pto_left = max(0, int(pto_total - pto_planned))
st.info(f"🔢 PTO planificat: {pto_planned} zile • PTO rămas: {pto_left} zile (din {pto_total})")

# ----------------------------
#  EXPORT EXCEL
# ----------------------------
summary_df = pd.DataFrame([
    {"Indicator":"Total PTO disponibil","Valoare":pto_total},
    {"Indicator":"PTO din propuneri selectate","Valoare":pto_from_props},
    {"Indicator":"PTO din intervale custom","Valoare":pto_from_custom},
    {"Indicator":"PTO rămas","Valoare":pto_left},
])

def to_excel_bytes(df_h, df_prop_sel, df_personal, df_custom, df_summary):
    try:
        import openpyxl  # ensure dependency
    except Exception:
        st.error("Lipsește 'openpyxl' în requirements.txt.")
        return None
    output = BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        df_h.to_excel(writer, sheet_name="Zile libere 2026", index=False)
        df_prop_sel.to_excel(writer, sheet_name="Propuneri selectate", index=False)
        df_personal.to_excel(writer, sheet_name="Zile personale", index=False)
        df_custom.to_excel(writer, sheet_name="Concedii custom", index=False)
        df_summary.to_excel(writer, sheet_name="Rezumat PTO", index=False)
    return output.getvalue()

selected_props = df_prop_edit[df_prop_edit["Include"]].copy()
selected_props = selected_props.drop(columns=["Include"])

df_personal_export = pd.DataFrame(st.session_state.personal_days) if st.session_state.personal_days else pd.DataFrame(columns=["Data","Motiv"])
df_custom_export = pd.DataFrame(st.session_state.custom_vacations) if st.session_state.custom_vacations else pd.DataFrame(columns=["Start","Stop","Descriere","Zile_PTO"])

excel_bytes = to_excel_bytes(DF_H, selected_props, df_personal_export, df_custom_export, summary_df)
st.download_button(
    label="⬇️ Descarcă Excel (toate foile)",
    data=excel_bytes,
    file_name="Planner_2026_PTO_si_Vacante.xlsx",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    disabled=(excel_bytes is None),
)


