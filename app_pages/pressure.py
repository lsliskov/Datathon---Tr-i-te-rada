import plotly.express as px
import streamlit as st

from utils.data import format_number
from utils.ui import RELATIVE_SCALE, download_table, get_dashboard_data

data = get_dashboard_data()

st.title("Regionalna potražnja i intenzitet dozvola", anchor=False)
st.caption(
    "Relativni pokazatelj uspoređuje regionalnu vidljivost HZZ oglasa i izdanih "
    "MUP-ovih dozvola po 1.000 stanovnika."
)
st.caption(
    f"HZZ objave do {data.hzz_date:%d.%m.%Y} · MUP izvještaj {data.permit_date:%d.%m.%Y} · "
    f"stanovništvo {data.population_year} · podaci preuzeti 09.11.2026."
)
st.write(
    "Pokazatelj daje brz pregled regija s najizraženijom kombinacijom oglasa i "
    "izdanih dozvola. Za detaljnije objašnjenje potražnje koristite stranice "
    "Regionalna analiza i Zanimanja i djelatnosti."
)

chart_data = data.regional.sort_values("indeks_pritiska", ascending=True)
fig = px.bar(
    chart_data,
    x="indeks_pritiska",
    y="regija",
    orientation="h",
    color="indeks_pritiska",
    color_continuous_scale=RELATIVE_SCALE,
    labels={"indeks_pritiska": "Relativni pokazatelj (0–100)", "regija": ""},
    hover_data={
        "oglasi_na_1000": ":.2f",
        "dozvole_na_1000": ":.2f",
        "hzz_oglasi": True,
        "mup_dozvole": True,
    },
)
fig.update_layout(height=650, coloraxis_showscale=False, yaxis={"automargin": True})
st.plotly_chart(
    fig,
    width="stretch",
    config={"scrollZoom": False, "doubleClick": False, "displayModeBar": False},
)

table = data.regional.sort_values("indeks_pritiska", ascending=False).loc[
    :,
    [
        "regija",
        "indeks_pritiska",
        "hzz_oglasi",
        "mup_dozvole",
        "stanovnici",
        "oglasi_na_1000",
        "dozvole_na_1000",
    ],
].rename(
    columns={
        "regija": "Regija",
        "indeks_pritiska": "Pokazatelj (0–100)",
        "hzz_oglasi": "HZZ oglasi",
        "mup_dozvole": "MUP dozvole",
        "stanovnici": "Stanovnici",
        "oglasi_na_1000": "Oglasi / 1.000 stanovnika",
        "dozvole_na_1000": "Dozvole / 1.000 stanovnika",
    }
)
st.dataframe(
    table,
    hide_index=True,
    column_config={
        "Pokazatelj (0–100)": st.column_config.NumberColumn(format="%.1f"),
        "Stanovnici": st.column_config.NumberColumn(format="%d"),
        "HZZ oglasi": st.column_config.NumberColumn(format="%d"),
        "MUP dozvole": st.column_config.NumberColumn(format="%d"),
        "Oglasi / 1.000 stanovnika": st.column_config.NumberColumn(format="%.2f"),
        "Dozvole / 1.000 stanovnika": st.column_config.NumberColumn(format="%.2f"),
    },
    alt="Regionalni pokazatelj oglasa i izdanih dozvola",
)
download_table(table, "labourpulse-pokazatelji.xlsx")

with st.expander("Kako nastaje pokazatelj", icon=":material/functions:"):
    st.markdown(
        """
        - HZZ oglasi / stanovništvo × 1.000.
        - MUP-ove dozvole evidentirane do datuma izvještaja / stanovništvo × 1.000.
        - Svaka stopa preslikava se na raspon 0–100 među prikazanim regijama.
        - Pokazatelj je aritmetička sredina dviju ocjena.

        Viša vrijednost znači višu relativnu vrijednost kombiniranih stopa u prikazanom skupu.
        Zagrebačka županija i Grad Zagreb prikazani su zajedno prema obuhvatu MUP-ove
        policijske uprave.
        """
    )
    st.caption(
        f"Posljednji MUP izvještaj: {data.permit_date:%d.%m.%Y}; "
        f"godina stanovništva: {data.population_year}; "
        f"zbroj MUP dozvola: {format_number(data.regional['mup_dozvole'].sum())}."
    )
