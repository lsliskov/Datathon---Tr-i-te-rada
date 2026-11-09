import pandas as pd
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
    "Pronađi oglase po regiji ili nazivu posla i vidi koje su skupine najčešće "
    "tražene. Desni grafikon prikazuje djelatnosti za koje su izdane MUP-ove dozvole."
)
st.caption(
    f"HZZ oglasi dostupni do {data.hzz_date:%d.%m.%Y} · "
    f"MUP dozvole iz izvještaja {data.permit_date:%d.%m.%Y}."
)

region_options = ["Cijela Hrvatska", *data.regional["regija"].tolist()]
with st.sidebar:
    st.subheader("Filteri")
    selected_region = st.selectbox("HZZ regija", region_options)
    search = st.text_input(
        "Traži naziv oglasa ili kategoriju",
        placeholder="npr. keramičar, doktor, vozač",
        help="Pretražuje i naziv pojedinog oglasa i njegovu prepoznatu HZZ kategoriju.",
    )
    top_n = st.slider("Broj zanimanja na grafikonu", min_value=5, max_value=20, value=12)
matching_vacancies = data.vacancies
if selected_region != "Cijela Hrvatska":
    matching_vacancies = matching_vacancies.loc[
        matching_vacancies["regija"] == selected_region
    ]

if search.strip():
    search_term = search.strip()
    matching_vacancies = matching_vacancies.loc[
        matching_vacancies["naziv_oglasa"].str.contains(
            search_term, case=False, na=False
        )
        | matching_vacancies["zanimanje"].str.contains(
            search_term, case=False, na=False
        )
    ]

unclassified_count = int(
    (matching_vacancies["zanimanje"] == "Nerazvrstano").sum()
)
total_count = len(matching_vacancies)
st.caption(
    f"Za {format_number(total_count - unclassified_count)} od "
    f"{format_number(total_count)} oglasa prepoznata je kategorija. "
    "Oglas nije nužno jedno radno mjesto; može tražiti više radnika."
)
vacancy_records = (
    matching_vacancies.loc[matching_vacancies["zanimanje"] != "Nerazvrstano"]
    .groupby("zanimanje", as_index=False)
    .size()
    .rename(columns={"size": "oglasi"})
    .sort_values("oglasi", ascending=False)
)

left, right = st.columns(2)
with left:
    st.subheader("Koje se vrste poslova traže?")
    st.caption(
        "Broj oglasa po HZZ kategoriji u odabranoj regiji. Pretraži konkretan naziv "
        "posla u filtru, npr. „keramičar” ili „doktor”."
    )
    if vacancy_records.empty:
        st.info(
            "Za odabrani pojam nema oglasa s prepoznatom skupinom zanimanja.",
            icon=":material/search_off:",
        )
    else:
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
    st.subheader("U kojim su djelatnostima izdane dozvole?")
    st.caption(
        "MUP-ov nacionalni zbroj iz najnovijeg izvještaja. Ovo su djelatnosti, "
        "a ne zanimanja iz oglasa s lijevog grafikona."
    )
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
    "Lijevo vidiš koje se vrste poslova oglašavaju. Desno vidiš u kojim su "
    "gospodarskim djelatnostima izdane dozvole. To su različite klasifikacije "
    "pa grafikoni daju kontekst, ali nisu izravna usporedba istih skupina.",
    title="Kako čitati prikaz",
    icon=":material/lightbulb:",
)

if not vacancy_records.empty:
    occupation_table = vacancy_records.head(top_n).rename(
        columns={"zanimanje": "Zanimanje", "oglasi": "Oglasi"}
    )
    st.dataframe(
        occupation_table,
        height=min(600, 38 + 35 * len(occupation_table)),
        hide_index=True,
    )
    download_table(
        occupation_table,
        "labourpulse-zanimanja.xlsx",
    )

with st.expander("Provjerite pojedinačne oglase", icon=":material/search:"):
    st.caption(
        "Ovdje možeš provjeriti na kojem je nazivu oglasa i kategoriji utemeljen "
        "grafikon. „Prikazana kategorija” može biti normalizirana radi čitljivosti; "
        "izvorna oznaka i način određivanja ostaju navedeni pored nje."
    )
    listing_table = matching_vacancies.assign(
        datum_objave=pd.to_datetime(
            matching_vacancies["datum_objave"], errors="coerce"
        )
    ).sort_values("datum_objave", ascending=False, na_position="last")
    listing_table = listing_table.loc[
        :,
        [
            "naziv_oglasa",
            "zanimanje",
            "izvorna_kategorija",
            "izvor_kategorije",
            "regija",
            "datum_objave",
        ],
    ].rename(
        columns={
            "naziv_oglasa": "Naziv oglasa",
            "zanimanje": "Prikazana kategorija",
            "izvorna_kategorija": "Kategorija u opisu HZZ-a",
            "izvor_kategorije": "Izvor kategorije",
            "regija": "Regija",
            "datum_objave": "Datum objave",
        }
    )
    listing_table["Kategorija u opisu HZZ-a"] = listing_table[
        "Kategorija u opisu HZZ-a"
    ].replace({"Nerazvrstano": "Nije navedena"})
    st.dataframe(
        listing_table.head(200),
        hide_index=True,
        column_config={
            "Datum objave": st.column_config.DateColumn(format="DD.MM.YYYY"),
        },
    )
    if len(listing_table) > 200:
        st.caption(
            "Radi preglednosti prikazano je prvih 200 oglasa. Gumb za preuzimanje "
            "sprema cijeli rezultat pretrage."
        )
    download_table(listing_table, "labourpulse-pojedinacni-oglasi.xlsx")
