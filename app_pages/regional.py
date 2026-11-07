import plotly.express as px
import streamlit as st

from utils.data import REGION_COORDINATES, format_number
from utils.ui import get_dashboard_data

data = get_dashboard_data()
regions = data.regional["regija"].tolist()
selected_region = st.selectbox("Odaberite regiju", regions)
selected = data.regional.loc[data.regional["regija"] == selected_region].iloc[0]

st.title("Regionalna analiza")
st.caption(
    "Usporedite HZZ oglase i MUP-ove izdane dozvole prema usporedivim regionalnim jedinicama."
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
    color_continuous_scale="YlOrRd",
    labels={
        "indeks_pritiska": "Indeks pritiska",
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
    st.plotly_chart(fig, width="stretch")
    st.caption(
        "Točke su približna središta regija; karta ne prikazuje službene granice. "
        "Veličina točke označava broj HZZ oglasa, boja kompozitni indeks."
    )

with right:
    st.subheader(selected_region)
    with st.container(border=True):
        st.metric("HZZ oglasi", format_number(selected["hzz_oglasi"]))
        st.metric("MUP dozvole u izvještaju", format_number(selected["mup_dozvole"]))
        st.metric("Indeks pritiska", f"{selected['indeks_pritiska']:.1f} / 100")
    st.write(
        f"Na 1.000 stanovnika: **{selected['oglasi_na_1000']:.2f}** HZZ oglasa i "
        f"**{selected['dozvole_na_1000']:.2f}** izdanih dozvola."
    )
    st.caption(
        "Za MUP je Zagrebačka županija objedinjena s Gradom Zagrebom jer izvještaj "
        "ne razdvaja njihovu policijsku upravu."
    )
