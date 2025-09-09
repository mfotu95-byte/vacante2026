import streamlit as st
import pandas as pd
from datetime import datetime, date, timedelta

st.set_page_config(page_title="Plan Vacanțe România", page_icon="🗓️", layout="centered")

st.title("🗓️ Planner Zile Libere & Vacanțe – România 2026")
st.caption("Generează Excel cu zilele libere legale + propuneri de mini-vacanțe.")

# ---- Inputuri
year = st.number_input("An", min_value=2026, max_value=2030, value=2026, step=1)
pto_total = st.number_input("Zile concediu disponibile (PTO)", min_value=0, max_value=60, value=22, step=1)

# ---- Zile libere RO pentru 2026 (hardcodate corect)
holidays_2026 = [
    ("2026-01-01", "Anul Nou"),
    ("2026-01-02", "A doua zi de Anul Nou"),
    ("2026-01-06", "Boboteaza"),
    ("2026-01-07", "Sfântul Ioan Botezătorul"),
    ("2026-01-24", "Ziua Unirii Principatelor Române"),
    ("2026-04-10", "Vinerea Mare (Paște ortodox)"),
    ("2026-04-12", "Paștele ortodox"),
    ("2026-04-13", "A doua zi de Paște"),
    ("2026-05-01", "Ziua Muncii"),
    ("2026-05-31", "Rusaliile (Prima zi)"),
    ("2026-06-01", "A doua zi de Rusalii"),
    ("2026-06-01", "Ziua Copilului"),
    ("2026-08-15", "Adormirea Maicii Domnului (Sf. Maria)"),
    ("2026-11-30", "Sfântul Andrei"),
    ("2026-12-01", "Ziua Națională a României"),
    ("2026-12-25", "Crăciun – Prima zi"),
    ("2026-12-26", "Crăciun – A doua zi"),
]

weekday_ro = {0:"Luni",1:"Marți",2:"Miercuri",3:"Joi",4:"Vineri",5:"Sâmbătă",6:"Duminică"}

def holidays_df_for_year(y:int)->pd.DataFrame:
    if y != 2026:
        st.warning("Lista exactă e configurată pentru 2026. Pentru alt an, actualizează tabelul de sărbători.")
    df = pd.DataFrame(holidays_2026, columns=["Data","Sărbătoare"])
    df["Data"] = pd.to_datetime(df["Data"])
    df["Ziua"] = df["Data"].dt.weekday.map(weekday_ro)
    return df.sort_values("Data")[["Data","Ziua","Sărbătoare"]]

df_h = holidays_df_for_year(year)
st.subheader("🥳 Zile libere legale")
st.dataframe(df_h, use_container_width=True)

# ---- Propuneri de mini-vacanțe pentru 2026 (optimizate pe punți)
proposals = [
    {"Interval":"2026-01-01 → 2026-01-07","PTO":1,"Zile_PTO":"2026-01-05 (luni)","Motiv":"Leagă 1-2 ian + weekend + 6-7 ian","Idee":"City break european / munte"},
    {"Interval":"2026-04-09 → 2026-04-14","PTO":2,"Zile_PTO":"2026-04-09 (joi), 2026-04-14 (marți)","Motiv":"Vinerea Mare + Paște + Lunea Paștelui","Idee":"Maramureș/Bucovina sau Lisabona"},
    {"Interval":"2026-04-30 → 2026-05-03","PTO":1,"Zile_PTO":"2026-04-30 (joi)","Motiv":"Ziua Muncii (vineri) + weekend","Idee":"Marea Neagră/Delta; Napoli & Amalfi"},
    {"Interval":"2026-05-30 → 2026-06-02","PTO":1,"Zile_PTO":"2026-06-02 (marți)","Motiv":"Rusalii (duminică) + Lunea Rusaliilor & Ziua Copilului","Idee":"City break nordic"},
    {"Interval":"2026-08-14 → 2026-08-16","PTO":1,"Zile_PTO":"2026-08-14 (vineri)","Motiv":"Sf. Maria e sâmbătă — faci mini-vacanță","Idee":"Weekend la mare / Thassos"},
    {"Interval":"2026-11-27 → 2026-12-02","PTO":2,"Zile_PTO":"2026-11-27 (vineri), 2026-12-02 (miercuri)","Motiv":"Sf. Andrei (luni) + Ziua Națională (marți)","Idee":"Târguri de Crăciun (Viena/Praga)"},
    {"Interval":"2026-12-24 → 2026-12-27","PTO":1,"Zile_PTO":"2026-12-24 (joi)","Motiv":"Crăciun (vineri & sâmbătă) + duminică","Idee":"Acasă cu familia / city break apropiat"},
]
df_p = pd.DataFrame(proposals)
df_p["Zile_PTO_folosite"] = df_p["PTO"]
pto_used = int(df_p["PTO"].sum())
pto_left = max(0, int(pto_total - pto_used))

st.subheader("🧩 Propuneri de mini-vacanțe (punți smart)")
st.dataframe(df_p[["Interval","Zile_PTO","Zile_PTO_folosite","Motiv","Idee"]], use_container_width=True)

st.info(f"🔢 PTO planificat: {pto_used} zile • PTO rămas: {pto_left} zile (din {pto_total})")

# ---- Excel de descărcat
summary = pd.DataFrame([
    {"Indicator":"Total PTO disponibil","Valoare":pto_total},
    {"Indicator":"PTO planificat în propuneri","Valoare":pto_used},
    {"Indicator":"PTO rămas","Valoare":pto_left},
])

def to_excel_bytes(df_h, df_p, summary):
    from io import BytesIO
    output = BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        df_h.to_excel(writer, sheet_name="Zile libere 2026", index=False)
        df_p[["Interval","Zile_PTO","Zile_PTO_folosite","Motiv","Idee"]].to_excel(writer, sheet_name="Propuneri vacanțe", index=False)
        summary.to_excel(writer, sheet_name="Rezumat PTO", index=False)
    return output.getvalue()

excel_bytes = to_excel_bytes(df_h, df_p, summary)
st.download_button(
    label="⬇️ Descarcă Excel (zile + propuneri + PTO)",
    data=excel_bytes,
    file_name=f"Calendar_{year}_si_Propuneri.xlsx",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
)

st.caption("Date 2026 verificate după timeanddate & articole locale. Pentru alt an, actualizează tabelul de sărbători.")


