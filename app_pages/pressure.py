import plotly.express as px
import streamlit as st

from utils.data import format_number
from utils.ui import get_dashboard_data

data = get_dashboard_data()

st.title("Indeks pritiska na tržište rada")
st.caption(
    "Kompozitni, relativni pokazatelj izrađen za ovu aplikaciju; nije službeni HZZ/MUP indeks."
)

chart_data = data.regional.sort_values("indeks_pritiska")
fig = px.bar(
    chart_data,
    x="indeks_pritiska",
    y="regija",
    orientation="h",
    color="indeks_pritiska",
    color_continuous_scale="YlOrRd",
    labels={"indeks_pritiska": "Indeks (0–100)", "regija": ""},
    hover_data={
        "oglasi_na_1000": ":.2f",
        "dozvole_na_1000": ":.2f",
        "hzz_oglasi": True,
        "mup_dozvole": True,
    },
)
fig.update_layout(height=650, coloraxis_showscale=False, yaxis={"automargin": True})
st.plotly_chart(fig, width="stretch")

table = data.regional.loc[
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
        "indeks_pritiska": "Indeks (0–100)",
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
        "Indeks (0–100)": st.column_config.NumberColumn(format="%.1f"),
        "Stanovnici": st.column_config.NumberColumn(format="%d"),
        "Oglasi / 1.000 stanovnika": st.column_config.NumberColumn(format="%.2f"),
        "Dozvole / 1.000 stanovnika": st.column_config.NumberColumn(format="%.2f"),
    },
)
st.download_button(
    "Preuzmi regionalne pokazatelje (CSV)",
    data=table.to_csv(index=False).encode("utf-8-sig"),
    file_name="labourpulse-regionalni-pokazatelji.csv",
    mime="text/csv",
    icon=":material/download:",
)

with st.expander("Metodologija i ograničenja"):
    st.markdown(
        """
        **Ulazne stope**

        - HZZ oglasi u lokalnim XML izvacima / stanovništvo × 1.000.
        - MUP-ove dozvole evidentirane do datuma posljednjeg izvještaja / stanovništvo × 1.000.
        - Stanovništvo je najnovija dostupna godišnja procjena DZS-a.

        Svaka se stopa zasebno preslikava na raspon 0–100 među prikazanim regijama
        min–max normalizacijom. Indeks je aritmetička sredina tih dviju ocjena.
        Vrijednost zato opisuje relativni položaj u ovom uzorku, a ne vjerojatnost
        manjka radnika. Na rang utječu vremenski obuhvat izvora i ekstremne vrijednosti.

        HZZ broji oglase, ne pojedinačna slobodna radna mjesta. MUP broji izdane
        dozvole do datuma izvještaja, ne trenutačno zaposlene strane radnike.
        Zagrebačka županija i Grad Zagreb spojeni su jer MUP objavljuje zajedničku
        policijsku upravu. Djelatnosti MUP-a dostupne su samo na nacionalnoj razini
        i ne ulaze zasebno u regionalni indeks.
        """
    )
    st.caption(
        f"Posljednji MUP izvještaj: {data.permit_date:%d.%m.%Y}; "
        f"godina stanovništva: {data.population_year}; "
        f"zbroj MUP dozvola: {format_number(data.regional['mup_dozvole'].sum())}."
    )
