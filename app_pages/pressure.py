import plotly.express as px
import streamlit as st

from utils.data import format_number
from utils.ui import RELATIVE_SCALE, download_table, get_dashboard_data

data = get_dashboard_data()

st.title("Usporedba regionalne potražnje", anchor=False)
st.caption(
    "Ova stranica rangira regije prema zajedničkom pokazatelju oglasa i dozvola, "
    "uzimajući u obzir i broj stanovnika."
)
st.caption(
    f"HZZ objave do {data.hzz_date:%d.%m.%Y} · MUP izvještaj {data.permit_date:%d.%m.%Y} · "
    f"stanovništvo {data.population_year} · podaci preuzeti 09.11.2026."
)
st.write(
    "Veća vrijednost znači da su oglasi i izdane dozvole po stanovniku visoki "
    "u usporedbi s drugim prikazanim regijama. To je alat za snalaženje i "
    "usporedbu, a ne službena procjena manjka radnika."
)

st.subheader("Kako se regije rangiraju?")
st.caption(
    "Grafikon prikazuje rezultat na ljestvici 0–100. Odaberi ili prijeđi preko "
    "regije da vidiš broj oglasa, dozvola i njihove stope po stanovniku."
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

st.subheader("Brojevi iza pokazatelja")
st.caption(
    "Tablica pokazuje i apsolutne brojeve i stope na 1.000 stanovnika kako bi "
    "bilo jasno što utječe na rang svake regije."
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
        1. Za svaku regiju računamo broj HZZ oglasa i MUP-ovih dozvola na
           1.000 stanovnika.
        2. Svaku od tih stopa zasebno uspoređujemo s najnižom i najvišom
           vrijednošću među regijama i pretvaramo u raspon 0–100.
        3. Konačni rezultat je prosjek dviju ocjena.

        Zato se rezultat može promijeniti ako se promijene regije ili podaci
        u usporedbi. Zagrebačka županija i Grad Zagreb spojeni su jer MUP za njih
        objavljuje zajednički podatak.
        """
    )
    st.caption(
        f"Posljednji MUP izvještaj: {data.permit_date:%d.%m.%Y}; "
        f"godina stanovništva: {data.population_year}; "
        f"zbroj MUP dozvola: {format_number(data.regional['mup_dozvole'].sum())}."
    )
