import plotly.express as px
import streamlit as st

from utils.data import format_number
from utils.ui import (
    PRIMARY_CHART_COLOR,
    SECONDARY_CHART_COLOR,
    download_table,
    get_dashboard_data,
)

data = get_dashboard_data()

st.title("Zanimanja i djelatnosti", anchor=False)
st.caption(
    "Ova stranica pokazuje koje skupine zanimanja poslodavci najčešće traže "
    "i u kojim djelatnostima se izdaje najviše dozvola."
)
st.caption(
    f"HZZ oglasi dostupni do {data.hzz_date:%d.%m.%Y} · "
    f"MUP dozvole iz izvještaja {data.permit_date:%d.%m.%Y}."
)

region_options = ["Cijela Hrvatska", *data.regional["regija"].tolist()]
selected_region = st.selectbox("HZZ regija", region_options)
search = st.text_input(
    "Pretražite zanimanje",
    placeholder="npr. vozač, kuhar, građevina",
    label_visibility="collapsed",
)
top_n = st.slider("Broj zanimanja na grafikonu", min_value=5, max_value=20, value=12)
vacancy_records = data.occupations
if selected_region == "Cijela Hrvatska":
    vacancy_records = (
        vacancy_records.groupby("zanimanje", as_index=False)["oglasi"]
        .sum()
        .sort_values("oglasi", ascending=False)
    )
else:
    vacancy_records = vacancy_records.loc[
        vacancy_records["regija"] == selected_region
    ].drop(columns="regija")
    vacancy_records = vacancy_records.sort_values("oglasi", ascending=False)

unclassified_count = int(
    vacancy_records.loc[vacancy_records["zanimanje"] == "Nerazvrstano", "oglasi"].sum()
)
total_count = int(vacancy_records["oglasi"].sum())
st.caption(
    f"Za {format_number(total_count - unclassified_count)} oglasa dostupna je "
    "prepoznata skupina zanimanja."
)
vacancy_records = vacancy_records.loc[vacancy_records["zanimanje"] != "Nerazvrstano"]
if search.strip():
    vacancy_records = vacancy_records.loc[
        vacancy_records["zanimanje"].str.contains(search.strip(), case=False, na=False)
    ]
if vacancy_records.empty:
    st.info("Za odabrani pojam nema oglasa u dostupnom izvatku.", icon=":material/search_off:")
    st.stop()

left, right = st.columns(2)
with left:
    st.subheader("HZZ skupine zanimanja")
    occupation_chart = vacancy_records.head(top_n).sort_values("oglasi")
    fig = px.bar(
        occupation_chart,
        x="oglasi",
        y="zanimanje",
        orientation="h",
        labels={"oglasi": "Broj oglasa", "zanimanje": ""},
        color_discrete_sequence=[SECONDARY_CHART_COLOR],
    )
    fig.update_layout(
        height=490,
        showlegend=False,
        coloraxis_showscale=False,
        yaxis={"automargin": True},
    )
    st.plotly_chart(
        fig,
        width="stretch",
        config={"scrollZoom": False, "doubleClick": False, "displayModeBar": False},
    )

with right:
    st.subheader("MUP djelatnosti")
    sector_chart = data.sectors.sort_values("dozvole")
    fig = px.bar(
        sector_chart,
        x="dozvole",
        y="djelatnost",
        orientation="h",
        labels={"dozvole": "Dozvole", "djelatnost": ""},
        color_discrete_sequence=[PRIMARY_CHART_COLOR],
    )
    fig.update_layout(
        height=490,
        showlegend=False,
        coloraxis_showscale=False,
        yaxis={"automargin": True},
    )
    st.plotly_chart(
        fig,
        width="stretch",
        config={"scrollZoom": False, "doubleClick": False, "displayModeBar": False},
    )
    st.caption(
        f"MUP djelatnosti su nacionalni zbrojevi iz izvještaja od "
        f"{data.permit_date:%d.%m.%Y}; prikazane su kao nacionalna slika potražnje."
    )

st.info(
    "HZZ koristi skupine zanimanja, a MUP koristi djelatnosti. Zajedničko čitanje "
    "grafikona daje dvije korisne perspektive iste teme.",
    title="Kako čitati prikaz",
    icon=":material/lightbulb:",
)

occupation_table = vacancy_records.sort_values("oglasi", ascending=False).rename(
    columns={"regija": "Regija", "zanimanje": "Zanimanje", "oglasi": "Oglasi"}
)
occupation_table = occupation_table.head(top_n)
st.dataframe(
    occupation_table,
    height=min(600, 38 + 35 * len(occupation_table)),
    hide_index=True,
    alt="Oglasi po odabranoj regiji i skupini zanimanja",
)
download_table(
    occupation_table,
    "labourpulse-zanimanja.xlsx",
)
