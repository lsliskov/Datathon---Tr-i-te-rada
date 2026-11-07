import plotly.express as px
import streamlit as st

from utils.data import format_number
from utils.ui import get_dashboard_data

data = get_dashboard_data()

st.title("Zanimanja i djelatnosti")
st.caption(
    "Dvije usporedne perspektive: HZZ-ove skupine zanimanja i MUP-ove djelatnosti."
)

region_options = ["Cijela Hrvatska", *data.regional["regija"].tolist()]
selected_region = st.selectbox("HZZ regija", region_options)
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
    f"Skupina zanimanja nije dostupna ili se ne može pouzdano iščitati za "
    f"{format_number(unclassified_count)} od {format_number(total_count)} oglasa; "
    "nerazvrstani oglasi izostavljeni su iz grafikona zanimanja."
)
vacancy_records = vacancy_records.loc[vacancy_records["zanimanje"] != "Nerazvrstano"]

left, right = st.columns(2)
with left:
    st.subheader("HZZ skupine zanimanja")
    occupation_chart = vacancy_records.head(12).sort_values("oglasi")
    fig = px.bar(
        occupation_chart,
        x="oglasi",
        y="zanimanje",
        orientation="h",
        labels={"oglasi": "Broj oglasa", "zanimanje": ""},
        color="oglasi",
        color_continuous_scale="Blues",
    )
    fig.update_layout(
        height=490,
        showlegend=False,
        coloraxis_showscale=False,
        yaxis={"automargin": True},
    )
    st.plotly_chart(fig, width="stretch")

with right:
    st.subheader("MUP djelatnosti")
    sector_chart = data.sectors.sort_values("dozvole")
    fig = px.bar(
        sector_chart,
        x="dozvole",
        y="djelatnost",
        orientation="h",
        labels={"dozvole": "Dozvole", "djelatnost": ""},
        color="dozvole",
        color_continuous_scale="Teal",
    )
    fig.update_layout(
        height=490,
        showlegend=False,
        coloraxis_showscale=False,
        yaxis={"automargin": True},
    )
    st.plotly_chart(fig, width="stretch")
    st.caption(
        f"MUP djelatnosti su nacionalni zbrojevi iz izvještaja od "
        f"{data.permit_date:%d.%m.%Y}; regionalna razrada po djelatnosti nije dostupna."
    )

st.info(
    "HZZ vodi oglase po skupinama zanimanja, a MUP dozvole po djelatnostima. "
    "Ove grafikone zato treba čitati usporedno, ne kao izravno uparene kategorije."
)
