import streamlit as st
import pandas as pd
from io import BytesIO
from datetime import datetime

st.set_page_config(page_title="Planner Zile Libere 2026", layout="centered")
st.title("🗓️ Planner Zile Libere & Vacanțe – România 2026 (interactiv, CO)")

# ----------------------------
#  CONFIG & STATE
# ----------------------------
if "personal_days" not in st.session_state:
    st.session_state.personal_days = []  # {"Data":"2026-xx-xx","Motiv":"..."}

if "custom_vacations" not in st.session_state:
    st.session_state.custom_vacations = []  # {"Start":"2026-..","Stop":"2026-..","Descriere":"...","Zile_CO":N}

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
LUNI_RO = {
    1: "Ianuarie", 2: "Februarie", 3: "Martie", 4: "Aprilie",
    5: "Mai", 6: "Iunie", 7: "Iulie", 8: "August",
    9: "Septembrie", 10: "Octombrie", 11: "Noiembrie", 12: "Decembrie"
}

def format_data_ro(dt: pd.Timestamp) -> str:
    if isinstance(dt, str):
        dt = pd.to_datetime(dt)
    return f"{dt.day} {LUNI_RO[dt.month]}"

def holidays_df():
    df = pd.DataFrame(HOLIDAYS_2026, columns=["Data","Sărbătoare"])
    df["Data"] = pd.to_datetime(df["Data"])
    df["Ziua"] = df["Data"].dt.weekday.map(WEEKDAY_RO)
    return df.sort_values("Data")[["Data","Ziua","Sărbătoare"]]

DF_H = holidays_df()
HOLIDAY_DATES = set(DF_H["Data"].dt.date)

# ----------------------------
#  SIDEBAR – CO & INFO
# ----------------------------
st.sidebar.header("⚙️ Setări")
co_total = st.sidebar.number_input("Zile concediu de odihnă (CO) disponibile", 0, 60, 22, 1)
st.sidebar.caption("Poți schimba numărul oricând; rezumatul se actualizează automat.")

# ----------------------------
#  SECTIUNEA 1 – ZILE LIBERE LEGALE
# ----------------------------
st.subheader("🥳 Zile libere legale 2026")
DF_H_SHOW = DF_H.copy()
DF_H_SHOW["Data"] = DF_H_SHOW["Data"].apply(format_data_ro)
st.dataframe(DF_H_SHOW, use_container_width=True)

# ----------------------------
#  SECTIUNEA 2 – ZILE LIBERE PERSONALE (nu consumă CO)
# ----------------------------
st.subheader("➕ Zile libere personale (nu consumă CO)")
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

    df_personal = pd.DataFrame(st.session_state.personal_days)
    if not df_personal.empty:
        # coloană formatată pentru afișare
        df_personal_display = df_personal.copy()
        df_personal_display["Data"] = df_personal_display["Data"].apply(lambda s: format_data_ro(pd.to_datetime(s)))
        edited = st.data_editor(
            df_personal_display,
            use_container_width=True,
            num_rows="dynamic",
            key="editor_personal_days"
        )
        # mapăm înapoi la ISO pentru state (păstrăm formatul intern robust)
        edited_iso = edited.copy()
        edited_iso["Data"] = pd.to_datetime(edited_iso["Data"].apply(
            lambda x: pd.to_datetime(x, format="%d %B", errors="coerce")
        ), errors="coerce").apply(
            lambda dt: dt.replace(year=2026) if pd.notnull(dt) else None
        )
        # dacă parsarea e problematică, păstrăm valorile vechi
        try:
            st.session_state.personal_days = [
                {"Data": d.isoformat()[:10], "Motiv": m}
                for d, m in zip(edited_iso["Data"], edited_iso["Motiv"])
                if pd.notnull(d)
            ]
        except Exception:
            pass
    else:
        st.info("Nu ai adăugat încă zile personale.")

PERSONAL_DATES = { datetime.fromisoformat(r["Data"]).date() for r in st.session_state.personal_days } if st.session_state.personal_days else set()

# ----------------------------
#  SECTIUNEA 3 – PROPUNERI (BIFABILE)
# ----------------------------
st.subheader("🧩 Propuneri de mini-vacanțe (bifează ce vrei să păstrezi)")
proposals = [
    {"Interval":"2026-01-01 → 2026-01-07","Zile_CO":1,"Detalii":"CO: 5 Ianuarie (luni)","Motiv":"Leagă 1-2 ian + weekend + 6-7 ian","Idee":"City break / munte","Include":True},
    {"Interval":"2026-04-09 → 2026-04-14","Zile_CO":2,"Detalii":"CO: 9 Aprilie (joi), 14 Aprilie (marți)","Motiv":"Vinerea Mare + Paște + Lunea Paștelui","Idee":"Maramureș/Bucovina sau Lisabona","Include":True},
    {"Interval":"2026-04-30 → 2026-05-03","Zile_CO":1,"Detalii":"CO: 30 Aprilie (joi)","Motiv":"Ziua Muncii (vineri) + weekend","Idee":"Marea/Delta; Napoli & Amalfi","Include":True},
    {"Interval":"2026-05-30 → 2026-06-02","Zile_CO":1,"Detalii":"CO: 2 Iunie (marți)","Motiv":"Rusalii (duminică) + Lunea Rusaliilor & 1 Iunie","Idee":"City break nordic","Include":True},
    {"Interval":"2026-08-14 → 2026-08-16","Zile_CO":1,"Detalii":"CO: 14 August (vineri)","Motiv":"Sf. Maria e sâmbătă — mini-vacanță","Idee":"Mare / Thassos","Include":False},
    {"Interval":"2026-11-27 → 2026-12-02","Zile_CO":2,"Detalii":"CO: 27 Noiembrie (vineri), 2 Decembrie (miercuri)","Motiv":"Sf. Andrei (luni) + Ziua Națională (marți)","Idee":"Târguri de Crăciun","Include":True},
    {"Interval":"2026-12-24 → 2026-12-27","Zile_CO":1,"Detalii":"CO: 24 Decembrie (joi)","Motiv":"Crăciun (vineri & sâmbătă) + duminică","Idee":"Acasă / city break apropiat","Include":False},
]
df_prop = pd.DataFrame(proposals)
df_prop_edit = st.data_editor(
    df_prop,
    column_config={"Include": st.column_config.CheckboxColumn("Include")},
    hide_index=True,
    use_container_width=True,
    key="editor_proposals"
)
co_from_props = int(df_prop_edit.loc[df_prop_edit["Include"], "Zile_CO"].sum())

# ----------------------------
#  SECTIUNEA 4 – CONCEDIILE TALE (INTERVALE CUSTOM)
# ----------------------------
st.subheader("✍️ Concediile tale (intervale custom)")

def working_days_co(start_date, end_date):
    """Calculează zile CO (luni–vineri), excluzând sărbătorile legale și zilele personale."""
    if start_date > end_date:
        start_date, end_date = end_date, start_date
    rng = pd.bdate_range(start=start_date, end=end_date, freq="C")  # business days
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
            zile_co = working_days_co(start, stop)
            st.session_state.custom_vacations.append({
                "Start": str(start),
                "Stop": str(stop),
                "Descriere": descr,
                "Zile_CO": int(zile_co)
            })
        else:
            st.warning("Alege atât data de start, cât și data de stop.")

df_custom = pd.DataFrame(st.session_state.custom_vacations)
if not df_custom.empty:
    # versiune de afișare cu date formate „12 Ianuarie”
    df_custom_display = df_custom.copy()
    df_custom_display["Start"] = df_custom_display["Start"].apply(lambda s: format_data_ro(pd.to_datetime(s)))
    df_custom_display["Stop"] = df_custom_display["Stop"].apply(lambda s: format_data_ro(pd.to_datetime(s)))
    edited_custom = st.data_editor(
        df_custom_display,
        use_container_width=True,
        num_rows="dynamic",
        key="editor_custom_vac"
    )
    # păstrăm în state varianta ISO (pentru calcule)
    try:
        def parse_ro_date_to_iso(x):
            # primim "12 Ianuarie" -> facem 2026-01-12
            dt = pd.to_datetime(x, format="%d %B", errors="coerce")
            if pd.isnull(dt):
                return None
            return dt.replace(year=2026)

        start_iso = edited_custom["Start"].apply(parse_ro_date_to_iso)
        stop_iso = edited_custom["Stop"].apply(parse_ro_date_to_iso)

        st.session_state.custom_vacations = []
        for s, e, dsc, zco in zip(start_iso, stop_iso, edited_custom.get("Descriere",""), edited_custom.get("Zile_CO", 0)):
            if pd.notnull(s) and pd.notnull(e):
                st.session_state.custom_vacations.append({
                    "Start": s.isoformat()[:10],
                    "Stop": e.isoformat()[:10],
                    "Descriere": dsc,
                    "Zile_CO": int(zco) if pd.notnull(zco) else 0
                })
    except Exception:
        pass
    co_from_custom = int(pd.DataFrame(st.session_state.custom_vacations)["Zile_CO"].sum()) if st.session_state.custom_vacations else 0
else:
    st.info("Nu ai adăugat încă intervale custom.")
    co_from_custom = 0

# ----------------------------
#  REZUMAT CO
# ----------------------------
co_planned = co_from_props + co_from_custom
co_left = max(0, int(co_total - co_planned))
st.info(f"🔢 CO planificat: {co_planned} zile • CO rămas: {co_left} zile (din {co_total})")
