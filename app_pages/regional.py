import plotly.express as px
import pandas as pd
import streamlit as st

from utils.data import REGION_COORDINATES, find_similar_regions, format_number
from utils.ui import (
    RELATIVE_SCALE,
    download_table,
    get_dashboard_data,
)

data = get_dashboard_data()
regions = data.regional["regija"].tolist()
with st.sidebar:
    st.subheader("Filteri")
    selected_region = st.selectbox("Odabrana regija", regions)
    first_region = st.selectbox("Prva regija", regions, index=0)
    second_region = st.selectbox(
        "Druga regija",
        regions,
        index=min(1, len(regions) - 1),
    )
    similar_limit = st.slider(
        "Broj sličnih regija",
        min_value=1,
        max_value=min(5, len(regions) - 1),
        value=min(3, len(regions) - 1),
    )
selected = data.regional.loc[data.regional["regija"] == selected_region].iloc[0]

st.title("Regionalna analiza", anchor=False)
st.caption(
    "Istraži kako se broj oglasa i dozvola razlikuje među regijama. Odaberi regiju "
    "u filtru sa strane da vidiš njezine brojke i usporedi je s drugim područjima."
)
st.caption(
    f"HZZ objave do {data.hzz_date:%d.%m.%Y} · MUP izvještaj {data.permit_date:%d.%m.%Y} · "
    f"stanovništvo {data.population_year} · podaci preuzeti 09.11.2026."
)

map_data = data.regional.copy()
map_data["lat"] = map_data["regija"].map(
    lambda region: REGION_COORDINATES[region][0]
)
map_data["lon"] = map_data["regija"].map(
    lambda region: REGION_COORDINATES[region][1]
)
map_data["velicina"] = map_data["hzz_oglasi"].clip(lower=1)
fig = px.scatter_geo(
    map_data,
    lat="lat",
    lon="lon",
    color="indeks_pritiska",
    size="velicina",
    hover_name="regija",
    hover_data={
        "lat": False,
        "lon": False,
        "velicina": False,
        "indeks_pritiska": ":.1f",
        "hzz_oglasi": True,
        "mup_dozvole": True,
        "stanovnici": ":,",
    },
    color_continuous_scale=RELATIVE_SCALE,
    labels={
        "indeks_pritiska": "Relativni pokazatelj",
        "hzz_oglasi": "HZZ oglasi",
        "mup_dozvole": "MUP dozvole",
        "stanovnici": "Stanovnici",
    },
    projection="mercator",
    size_max=24,
)
fig.update_geos(
    scope="europe",
    center={"lat": 45.3, "lon": 16.4},
    lataxis_range=[42.2, 46.7],
    lonaxis_range=[13.2, 19.6],
    showland=True,
    landcolor="#f4f6f7",
    showcountries=True,
    countrycolor="#9aa5ad",
    showocean=True,
    oceancolor="#eaf2f8",
)
fig.update_layout(height=600, margin={"l": 0, "r": 0, "t": 15, "b": 0})

left, right = st.columns([1.5, 1])
with left:
    st.plotly_chart(
        fig,
        width="stretch",
        config={"scrollZoom": False, "doubleClick": False, "displayModeBar": False},
    )
    st.caption(
        "Veća točka znači više dostupnih HZZ oglasa. Boja prikazuje relativni "
        "pokazatelj koji spaja oglase i dozvole po broju stanovnika; točke su "
        "približna mjesta regija, ne granice županija."
    )

with right:
    st.subheader(selected_region)
    with st.container(border=True):
        st.metric("HZZ oglasi", format_number(selected["hzz_oglasi"]))
        st.metric("MUP dozvole u izvještaju", format_number(selected["mup_dozvole"]))
        st.metric(
            "Relativni pokazatelj",
            f"{selected['indeks_pritiska']:.1f} / 100",
            help="Kombinacija dviju stopa prilagođenih broju stanovnika, preslikana na ljestvicu 0–100 unutar prikazanih regija. Nije službena stopa manjka radnika.",
        )
    st.write(
        f"Na 1.000 stanovnika: **{selected['oglasi_na_1000']:.2f}** HZZ oglasa i "
        f"**{selected['dozvole_na_1000']:.2f}** izdanih dozvola."
    )
    st.caption(
        "Oglasi i dozvole na 1.000 stanovnika olakšavaju usporedbu područja različite "
        "veličine. Grad Zagreb i Zagrebačka županija spojeni su jer MUP objavljuje "
        "zajednički podatak za to područje."
    )

st.subheader("Usporedite dvije regije")
st.caption(
    "Usporedni grafikon prikazuje ukupan broj oglasa i dozvola. Za usporedbu "
    "intenziteta potražnje uzmite u obzir i stope na 1.000 stanovnika u tablici ispod."
)
comparison = data.regional.set_index("regija").loc[
    [first_region, second_region],
    ["hzz_oglasi", "mup_dozvole", "oglasi_na_1000", "dozvole_na_1000"],
].T.rename(
    columns={
        first_region: first_region,
        second_region: second_region,
    }
)
comparison.index = [
    "HZZ oglasi",
    "MUP dozvole",
    "HZZ oglasi / 1.000 stanovnika",
    "MUP dozvole / 1.000 stanovnika",
]
st.bar_chart(
    comparison.iloc[:2],
    y_label="Broj",
    stack=False,
    alt="Usporedba HZZ oglasa i MUP-ovih dozvola za dvije odabrane regije",
)

st.subheader("Regije s najsličnijim profilom")
st.caption(
    "Ovdje su regije čiji su oglasi i dozvole po stanovniku najsličniji odabranoj "
    "regiji. Slične regije ne moraju biti susjedne."
)
similar = find_similar_regions(data.regional, selected_region, similar_limit)
similar_display = similar.loc[
    :,
    ["regija", "oglasi_na_1000", "dozvole_na_1000", "indeks_pritiska"],
].rename(
    columns={
        "regija": "Regija",
        "oglasi_na_1000": "Oglasi / 1.000 stanovnika",
        "dozvole_na_1000": "Dozvole / 1.000 stanovnika",
        "indeks_pritiska": "Relativni pokazatelj",
    }
)
st.dataframe(
    similar_display,
    height=min(300, 38 + 35 * len(similar_display)),
    hide_index=True,
    column_config={
        "Oglasi / 1.000 stanovnika": st.column_config.NumberColumn(format="%.2f"),
        "Dozvole / 1.000 stanovnika": st.column_config.NumberColumn(format="%.2f"),
        "Relativni pokazatelj": st.column_config.NumberColumn(format="%.1f"),
    },
    alt="Regije s najsličnijim profilom odabranoj regiji",
)
similar_chart = pd.concat(
    [
        data.regional.loc[
            data.regional["regija"] == selected_region,
            ["regija", "oglasi_na_1000", "dozvole_na_1000"],
        ],
        similar.loc[:, ["regija", "oglasi_na_1000", "dozvole_na_1000"]],
    ]
).melt(id_vars="regija", var_name="pokazatelj", value_name="vrijednost")
similar_chart["pokazatelj"] = similar_chart["pokazatelj"].map(
    {
        "oglasi_na_1000": "Oglasi / 1.000 stanovnika",
        "dozvole_na_1000": "Dozvole / 1.000 stanovnika",
    }
)
st.bar_chart(
    similar_chart,
    x="regija",
    y="vrijednost",
    color="pokazatelj",
    stack=False,
    sort=False,
    y_label="Vrijednost na 1.000 stanovnika",
    alt="Usporedba odabrane i najsličnijih regija prema stopama",
)

regional_table = data.regional.sort_values("hzz_oglasi", ascending=False).loc[
    :,
    [
        "regija",
        "hzz_oglasi",
        "oglasi_na_1000",
        "mup_dozvole",
        "dozvole_na_1000",
        "stanovnici",
    ],
].rename(
    columns={
        "regija": "Regija",
        "hzz_oglasi": "HZZ oglasi",
        "oglasi_na_1000": "Oglasi / 1.000 stanovnika",
        "mup_dozvole": "MUP dozvole",
        "dozvole_na_1000": "Dozvole / 1.000 stanovnika",
        "stanovnici": "Stanovnici",
    }
)
st.subheader("Usporedni regionalni podaci")
st.caption(
    "Tablica sadrži izvorne brojeve i stope po 1.000 stanovnika. Odaberite redak "
    "za brojčani kontekst; izvoz preuzima cijelu usporednu tablicu."
)
st.dataframe(
    regional_table,
    hide_index=True,
    column_config={
        "HZZ oglasi": st.column_config.NumberColumn(format="%d"),
        "MUP dozvole": st.column_config.NumberColumn(format="%d"),
        "Stanovnici": st.column_config.NumberColumn(format="%d"),
        "Oglasi / 1.000 stanovnika": st.column_config.NumberColumn(format="%.2f"),
        "Dozvole / 1.000 stanovnika": st.column_config.NumberColumn(format="%.2f"),
    },
    alt="Regionalni pregled oglasa, dozvola i stanovništva",
)
download_table(regional_table, "labourpulse-regionalni-podaci.xlsx")
