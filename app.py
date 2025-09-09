import streamlit as st
import pandas as pd
from io import BytesIO
from datetime import datetime

st.set_page_config(page_title="Planner Zile Libere 2026", layout="centered")
st.title("🗓️ Planner Zile Libere & Vacanțe – România 2026 (interactiv, CO)")

# ----------------------------
#  STATE
# ----------------------------
if "personal_days" not in st.session_state:
    st.session_state.personal_days = []  # {"Data":"2026-xx-xx","Motiv":"..."}
if "custom_vacations" not in st.session_state:
    st.session_state.custom_vacations = []  # {"Start":"2026-..","Stop":"2026-..","Descriere":"...","Zile_CO":N}

# ----------------------------
#  CONSTANTE & UTILS
# ----------------------------
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

def fmt_ro(dt) -> str:
    """'2026-01-12' / Timestamp -> '12 Ianuarie' """
    if isinstance(dt, str):
        dt = pd.to_datetime(dt)
    return f"{dt.day} {LUNI_RO[dt.month]}"

def holidays_df():
    df = pd.DataFrame(HOLIDAYS_2026, columns=["DataISO","Sărbătoare"])
    df["DataISO"] = pd.to_datetime(df["DataISO"])
    df["Ziua"] = df["DataISO"].dt.weekday.map(WEEKDAY_RO)
    df["Data"] = df["DataISO"].apply(fmt_ro)  # pentru afișare
    return df[["DataISO","Data","Ziua","Sărbătoare"]].sort_values("DataISO")

DF_H = holidays_df()
HOLIDAY_DATES = set(DF_H["DataISO"].dt.date)

# ----------------------------
#  SIDEBAR – CO
# ----------------------------
st.sidebar.header("⚙️ Setări")
co_total = st.sidebar.number_input("Zile concediu de odihnă (CO) disponibile", 0, 60, 22, 1)

# ----------------------------
#  1) ZILE LEGALE – AFIȘARE CU LUNA ÎN CUVINTE
# ----------------------------
st.subheader("🥳 Zile libere legale 2026")
st.dataframe(
    DF_H[["Data","Ziua","Sărbătoare"]],  # doar coloanele formătate
    use_container_width=True
)

# ----------------------------
#  2) ZILE PERSONALE – DATĂ AFIȘATĂ „12 Ianuarie”
# ----------------------------
st.subheader("➕ Zile libere personale (nu consumă CO)")
with st.expander("Adaugă zi personală"):
    c1, c2, c3 = st.columns([1,2,1])
    with c1:
        pd_date = st.date_input("Data (calendar)", format="YYYY-MM-DD", value=None)
    with c2:
        pd_reason = st.text_input("Motiv / etichetă", placeholder="Ex: Zi liberă contractuală")
    with c3:
        if st.button("Adaugă"):
            if pd_date:
                st.session_state.personal_days.append({"DataISO": str(pd_date), "Motiv": pd_reason or ""})
            else:
                st.warning("Alege o dată.")

# tabel de afișare cu „Data (RO)” blocată ca text
df_personal = pd.DataFrame(st.session_state.personal_days)
if not df_personal.empty:
    df_personal_show = df_personal.copy()
    df_personal_show["Data (RO)"] = df_personal_show["DataISO"].apply(fmt_ro)
    df_personal_show = df_personal_show[["Data (RO)","Motiv"]]  # arătăm frumos
    st.caption("Poți edita câmpul 'Motiv'. Pentru ștergere, folosește butonul de mai jos.")
    edited = st.data_editor(
        df_personal_show,
        column_config={
            "Data (RO)": st.column_config.TextColumn(disabled=True),
            "Motiv": st.column_config.TextColumn(),
        },
        hide_index=False,
        use_container_width=True,
        key="editor_personal_days"
    )
    # sincronizăm doar motivul, păstrăm intern ISO
    for i, row in edited.iterrows():
        st.session_state.personal_days[i]["Motiv"] = row["Motiv"]

    # buton de ștergere pe rând selectat prin index
    del_idx = st.number_input("Index pentru ștergere (rând)", min_value=0, max_value=len(edited)-1, value=0, step=1)
    if st.button("Șterge rândul selectat"):
        st.session_state.personal_days.pop(del_idx)
        st.rerun()
else:
    st.info("Nu ai adăugat încă zile personale.")

PERSONAL_DATES = { datetime.fromisoformat(r["DataISO"]).date() for r in st.session_state.personal_days } if st.session_state.personal_days else set()

# ----------------------------
#  3) PROPUNERI – CU CO & DATE FORMATE
# ----------------------------
st.subheader("🧩 Propuneri de mini-vacanțe (bifează ce vrei)")
proposals = [
    {"Interval":"1–7 Ianuarie","Zile_CO":1,"Detalii":"CO: 5 Ianuarie (luni)","Motiv":"Leagă 1-2 ian + weekend + 6-7 ian","Idee":"City break / munte","Include":True},
    {"Interval":"9–14 Aprilie","Zile_CO":2,"Detalii":"CO: 9 Aprilie (joi), 14 Aprilie (marți)","Motiv":"Vinerea Mare + Paște + Lunea Paștelui","Idee":"Maramureș/Bucovina sau Lisabona","Include":True},
    {"Interval":"30 Aprilie – 3 Mai","Zile_CO":1,"Detalii":"CO: 30 Aprilie (joi)","Motiv":"Ziua Muncii (vineri) + weekend","Idee":"Marea/Delta; Napoli & Amalfi","Include":True},
    {"Interval":"30 Mai – 2 Iunie","Zile_CO":1,"Detalii":"CO: 2 Iunie (marți)","Motiv":"Rusalii + 1 Iunie","Idee":"City break nordic","Include":True},
    {"Interval":"14–16 August","Zile_CO":1,"Detalii":"CO: 14 August (vineri)","Motiv":"Sf. Maria e sâmbătă — mini-vacanță","Idee":"Mare / Thassos","Include":False},
    {"Interval":"27 Nov – 2 Dec","Zile_CO":2,"Detalii":"CO: 27 Noiembrie (vineri), 2 Decembrie (miercuri)","Motiv":"Sf. Andrei + 1 Decembrie","Idee":"Târguri de Crăciun","Include":True},
    {"Interval":"24–27 Decembrie","Zile_CO":1,"Detalii":"CO: 24 Decembrie (joi)","Motiv":"Crăciun + weekend","Idee":"Acasă / city break apropiat","Include":False},
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
#  4) CONCEDII CUSTOM – AFIȘARE „12 Ianuarie”
# ----------------------------
st.subheader("✍️ Concediile tale (intervale custom)")
def working_days_co(start_date, end_date):
    """CO (luni–vineri), scăzând legale & personale."""
    if start_date > end_date:
        start_date, end_date = end_date, start_date
    rng = pd.bdate_range(start=start_date, end=end_date, freq="C")
    cnt = 0
    for dts in rng:
        d = dts.date()
        if d in HOLIDAY_DATES or d in PERSONAL_DATES:
            continue
        cnt += 1
    return cnt

with st.form("add_custom_vacation", clear_on_submit=True):
    c1, c2 = st.columns(2)
    with c1:
        start = st.date_input("Start (calendar)", format="YYYY-MM-DD")
    with c2:
        stop = st.date_input("Stop (calendar)", format="YYYY-MM-DD")
    descr = st.text_input("Descriere (opțional)", placeholder="Ex: Grecia iunie")
    submitted = st.form_submit_button("Adaugă interval")
    if submitted:
        if start and stop:
            zile_co = working_days_co(start, stop)
            st.session_state.custom_vacations.append({
                "StartISO": str(start),
                "StopISO": str(stop),
                "Descriere": descr,
                "Zile_CO": int(zile_co)
            })
        else:
            st.warning("Alege atât data de start, cât și de stop.")

df_custom = pd.DataFrame(st.session_state.custom_vacations)
if not df_custom.empty:
    df_custom_show = df_custom.copy()
    df_custom_show["Start"] = df_custom_show["StartISO"].apply(fmt_ro)
    df_custom_show["Stop"]  = df_custom_show["StopISO"].apply(fmt_ro)
    df_custom_show = df_custom_show[["Start","Stop","Descriere","Zile_CO"]]
    st.dataframe(df_custom_show, use_container_width=True)
    # opțional: ștergere prin index
    del_idx2 = st.number_input("Index pentru ștergere (interval custom)", min_value=0, max_value=len(df_custom_show)-1, value=0, step=1)
    if st.button("Șterge intervalul selectat"):
        st.session_state.custom_vacations.pop(del_idx2)
        st.rerun()
    co_from_custom = int(df_custom["Zile_CO"].sum())
else:
    st.info("Nu ai adăugat încă intervale custom.")
    co_from_custom = 0

# ----------------------------
#  REZUMAT CO
# ----------------------------
co_planned = co_from_props + co_from_custom
co_left = max(0, int(co_total - co_planned))
st.info(f"🔢 CO planificat: {co_planned} zile • CO rămas: {co_left} zile (din {co_total})")
