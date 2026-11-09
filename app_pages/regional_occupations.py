import plotly.express as px
import streamlit as st

from utils.data import _ascii_key, format_number
from utils.ui import download_table, get_dashboard_data

data = get_dashboard_data()
classified = data.occupations.loc[
    data.occupations["zanimanje"] != "Nerazvrstano"
]
category_totals = (
    classified.groupby("zanimanje")["oglasi"].sum().sort_values(ascending=False)
)
raw_categories = category_totals.index.tolist()
categories = []
category_aliases = {}
for category in raw_categories:
    key = _ascii_key(category)
    candidates = [
        candidate
        for candidate in raw_categories
        if len(_ascii_key(candidate)) > len(key)
        and _ascii_key(candidate).startswith(key)
    ]
    canonical = max(candidates, key=len) if candidates else category
    category_aliases[category] = canonical
    if canonical not in categories:
        categories.append(canonical)
category_totals = (
    classified.assign(zanimanje=classified["zanimanje"].map(category_aliases))
    .groupby("zanimanje")["oglasi"]
    .sum()
    .sort_values(ascending=False)
)
categories = category_totals.index.tolist()
default_categories = categories[: min(8, len(categories))]

with st.sidebar:
    st.subheader("Filteri")
    selected_categories = st.pills(
        "Skupine zanimanja",
        categories,
        default=default_categories,
        selection_mode="multi",
        help="Odaberi skupine za usporedbu. Nerazvrstani oglasi nisu uključeni u analizu zanimanja.",
    )
    measure = st.selectbox(
        "Prikaz",
        [
            "Broj HZZ oglasa",
            "HZZ oglasi na 1.000 stanovnika",
            "HZZ oglasi na 1.000 stanovnika 15–64",
        ],
        help="Stopa po stanovniku služi za usporedbu regija različite veličine; ne predstavlja broj slobodnih radnih mjesta.",
    )

st.title("Zanimanja po regijama", anchor=False)
st.caption(
    "Usporedi koje se skupine zanimanja oglašavaju u pojedinim regijama. "
    "HZZ oglasi prikazani su kao zaseban izvor potražnje, bez spajanja s MUP-ovim dozvolama."
)
st.caption(
    f"HZZ oglasi dostupni do {data.hzz_date:%d.%m.%Y} · "
    f"demografski nazivnik: {data.demographic_year}."
)
st.info(
    "Broj HZZ oglasa nije isto što i broj slobodnih radnih mjesta: jedan oglas "
    "može obuhvatiti više radnika, a oglas može biti ponovno objavljen. "
    "Ova usporedba opisuje oglase u spremljenom izvatku."
)
st.caption(
    f"Stopa oglasa na 1.000 stanovnika 15–64 koristi demografski podatak za "
    f"{data.demographic_year}. Dobna skupina 15–64 nije isto što i broj aktivnih "
    "radnika ili radne snage."
)

if not selected_categories:
    st.info("Odaberite barem jednu skupinu zanimanja.")
else:
    matrix = (
        classified.assign(
            zanimanje=classified["zanimanje"].map(category_aliases)
        )
        .loc[lambda frame: frame["zanimanje"].isin(selected_categories)]
        .pivot_table(
            index="regija",
            columns="zanimanje",
            values="oglasi",
            aggfunc="sum",
            fill_value=0,
        )
        .reindex(index=data.regional["regija"], columns=selected_categories, fill_value=0)
    )
    if measure in {
        "HZZ oglasi na 1.000 stanovnika",
        "HZZ oglasi na 1.000 stanovnika 15–64",
    }:
        denominator = (
            "stanovnici_15_64"
            if measure.endswith("15–64")
            else "stanovnici"
        )
        population = data.regional.set_index("regija")[denominator]
        matrix = matrix.div(population.reindex(matrix.index), axis=0).mul(1000)
        colorbar_title = measure
        text_format = ".2f"
    else:
        colorbar_title = "Broj oglasa"
        text_format = ".0f"

    chart_data = matrix.sort_index()
    fig = px.imshow(
        chart_data,
        labels={
            "x": "Skupina zanimanja",
            "y": "Regija",
            "color": colorbar_title,
        },
        color_continuous_scale="Teal",
        aspect="auto",
        text_auto=text_format,
    )
    fig.update_layout(
        height=680,
        xaxis={"side": "top", "tickangle": -25},
        coloraxis_colorbar={"title": colorbar_title},
        margin={"l": 10, "r": 10, "t": 110, "b": 10},
    )
    st.plotly_chart(
        fig,
        width="stretch",
        config={"scrollZoom": False, "doubleClick": False, "displayModeBar": False},
    )

    display_matrix = matrix.rename_axis("Regija").reset_index()
    st.subheader("Podaci za odabrane skupine")
    st.caption(
        "Tablica prikazuje broj oglasa ili stopu na 1.000 stanovnika prema odabranom filtru."
    )
    st.dataframe(display_matrix, hide_index=True)
    download_table(display_matrix, "labourpulse-zanimanja-po-regijama.xlsx")

    unclassified = int((data.vacancies["zanimanje"] == "Nerazvrstano").sum())
    st.caption(
        f"U spremljenom izvatku ima {format_number(unclassified)} oglasa bez "
        "pouzdano prepoznate skupine; oni nisu uključeni u prikaz po zanimanjima."
    )
