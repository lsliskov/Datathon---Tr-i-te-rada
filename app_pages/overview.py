import plotly.express as px
import streamlit as st

from utils.data import format_number
from utils.ui import get_dashboard_data

data = get_dashboard_data()
top_region = data.regional.iloc[0]

st.title("LabourPulse RH")
st.caption(
    "Pregled HZZ oglasa, MUP-ovih dozvola i demografskog konteksta po regijama."
)

with st.container(horizontal=True):
    st.metric("HZZ oglasi u izvatku", format_number(data.regional["hzz_oglasi"].sum()), border=True)
    st.metric(
        "Dozvole u posljednjem MUP izvještaju",
        format_number(data.regional["mup_dozvole"].sum()),
        border=True,
    )
    st.metric("Najviši relativni indeks", top_region["regija"], border=True)

st.caption(
    f"MUP izvještaj: {data.permit_date:%d.%m.%Y} · "
    f"stanovništvo: procjena za {data.population_year}. · "
    f"HZZ izvadak: najnoviji datum objave {data.hzz_date:%d.%m.%Y}"
    if data.hzz_date
    else f"MUP izvještaj: {data.permit_date:%d.%m.%Y} · stanovništvo: procjena za {data.population_year}."
)

left, right = st.columns(2)
with left:
    st.subheader("Dozvole prema regiji")
    chart_data = data.regional.nlargest(8, "mup_dozvole").sort_values("mup_dozvole")
    fig = px.bar(
        chart_data,
        x="mup_dozvole",
        y="regija",
        orientation="h",
        labels={"mup_dozvole": "Dozvole", "regija": ""},
        color="mup_dozvole",
        color_continuous_scale="Teal",
    )
    fig.update_layout(showlegend=False, coloraxis_showscale=False, height=390)
    st.plotly_chart(fig, width="stretch")

with right:
    st.subheader("MUP izvještaji kroz vrijeme")
    fig = px.line(
        data.history,
        x="datum",
        y="izdane_dozvole",
        color="godina",
        markers=True,
        labels={"datum": "Datum izvještaja", "izdane_dozvole": "Dozvole", "godina": "Godina"},
    )
    fig.update_layout(height=390, legend_title_text="Godina")
    st.plotly_chart(fig, width="stretch")
    st.caption(
        "Brojevi su zbrojevi dozvola evidentiranih u izvještaju do njegova datuma; "
        "serija se početkom godine vraća na početnu vrijednost."
    )

st.subheader("Regije s najvišim indeksom")
leaders = data.regional.head(5).loc[
    :, ["regija", "indeks_pritiska", "oglasi_na_1000", "dozvole_na_1000"]
].rename(
    columns={
        "regija": "Regija",
        "indeks_pritiska": "Indeks",
        "oglasi_na_1000": "HZZ oglasi / 1.000 stanovnika",
        "dozvole_na_1000": "MUP dozvole / 1.000 stanovnika",
    }
)
st.dataframe(
    leaders,
    hide_index=True,
    column_config={
        "Indeks": st.column_config.NumberColumn(format="%.1f"),
        "HZZ oglasi / 1.000 stanovnika": st.column_config.NumberColumn(format="%.2f"),
        "MUP dozvole / 1.000 stanovnika": st.column_config.NumberColumn(format="%.2f"),
    },
)

with st.expander("Kako čitati podatke"):
    st.write(
        "HZZ broj predstavlja oglase iz lokalnih RSS izvadaka, a ne broj otvorenih "
        "radnih mjesta. MUP-ovi regionalni podaci odnose se na izdane dozvole "
        "evidentirane do datuma izvještaja, a ne na broj trenutačno zaposlenih "
        "stranih radnika. Djelatnosti MUP-a dostupne su samo za Hrvatsku ukupno."
    )
