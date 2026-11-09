import plotly.express as px
import streamlit as st

from utils.ui import download_table, get_dashboard_data

data = get_dashboard_data()

st.title("Regionalne stope oglasa i dozvola", anchor=False)
st.caption(
    "Ova stranica prikazuje HZZ oglase i MUP-ove izdane dozvole kao dva odvojena "
    "pokazatelja, preračunata na 1.000 stanovnika."
)
st.caption(
    f"HZZ objave do {data.hzz_date:%d.%m.%Y} · MUP izvještaj {data.permit_date:%d.%m.%Y} · "
    f"stanovništvo {data.population_year} · podaci preuzeti 09.11.2026."
)
st.write(
    "Odvojeni pokazatelji omogućuju jasnu usporedbu regionalnih razlika bez "
    "spajanja oglasa i dozvola u jedan indeks."
)

st.subheader("HZZ oglasi na 1.000 stanovnika")
st.caption(
    "Regije su poredane prema stopi HZZ oglasa. Broj oglasa ne mora odgovarati "
    "broju stvarnih slobodnih radnih mjesta."
)
chart_data = data.regional.sort_values("oglasi_na_1000", ascending=True)
fig = px.bar(
    chart_data,
    x="oglasi_na_1000",
    y="regija",
    orientation="h",
    color="oglasi_na_1000",
    color_continuous_scale="Teal",
    labels={"oglasi_na_1000": "HZZ oglasi / 1.000 stanovnika", "regija": ""},
    hover_data={
        "hzz_oglasi": True,
        "oglasi_na_1000": ":.2f",
    },
)
fig.update_layout(height=650, coloraxis_showscale=False, yaxis={"automargin": True})
st.plotly_chart(
    fig,
    width="stretch",
    config={"scrollZoom": False, "doubleClick": False, "displayModeBar": False},
)

st.subheader("Regionalni podaci")
st.caption(
    "Tablica prikazuje apsolutne brojeve i stope na 1.000 stanovnika."
)
table = data.regional.sort_values("oglasi_na_1000", ascending=False).loc[
    :,
    [
        "regija",
        "hzz_oglasi",
        "mup_dozvole",
        "stanovnici",
        "oglasi_na_1000",
        "dozvole_na_1000",
    ],
].rename(
    columns={
        "regija": "Regija",
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
        "Stanovnici": st.column_config.NumberColumn(format="%d"),
        "HZZ oglasi": st.column_config.NumberColumn(format="%d"),
        "MUP dozvole": st.column_config.NumberColumn(format="%d"),
        "Oglasi / 1.000 stanovnika": st.column_config.NumberColumn(format="%.2f"),
        "Dozvole / 1.000 stanovnika": st.column_config.NumberColumn(format="%.2f"),
    },
    alt="Regionalni podaci o oglasima i izdanim dozvolama",
)
download_table(table, "labourpulse-pokazatelji.xlsx")
