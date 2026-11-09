import plotly.express as px
import streamlit as st

from utils.data import REGION_COORDINATES, format_number
from utils.ui import download_table, get_dashboard_data

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
selected = data.regional.loc[data.regional["regija"] == selected_region].iloc[0]

st.title("Regionalna analiza", anchor=False)
st.caption(
    "Istraži HZZ oglase i MUP-ove izdane dozvole kao odvojene pokazatelje. "
    "Odaberi regiju za usporedbu brojeva i stopa po stanovniku."
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
    color="oglasi_na_1000",
    size="velicina",
    hover_name="regija",
    hover_data={
        "lat": False,
        "lon": False,
        "velicina": False,
        "oglasi_na_1000": ":.2f",
        "hzz_oglasi": True,
        "mup_dozvole": True,
        "stanovnici": ":,",
    },
    color_continuous_scale="Teal",
    labels={
        "oglasi_na_1000": "HZZ oglasi / 1.000 stanovnika",
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
        "Veća točka znači više dostupnih HZZ oglasa, a boja prikazuje HZZ oglase "
        "na 1.000 stanovnika. MUP-ove dozvole prikazane su odvojeno u podacima "
        "za odabranu regiju; točke su približna mjesta regija, ne granice županija."
    )

with right:
    st.subheader(selected_region)
    with st.container(border=True):
        st.metric("HZZ oglasi", format_number(selected["hzz_oglasi"]))
        st.metric(
            "HZZ oglasi / 1.000 stanovnika",
            f"{selected['oglasi_na_1000']:.2f}",
            help="Broj trenutno dostupnih HZZ oglasa u odnosu na procijenjeni broj stanovnika. Oglas nije nužno jedno slobodno radno mjesto.",
        )
        st.metric(
            "HZZ oglasi / 1.000 stanovnika 15–64",
            f"{selected['oglasi_na_1000_15_64']:.2f}",
            help=f"Demografski nazivnik iz {data.demographic_year}; dobna skupina 15–64 nije isto što i aktivna radna snaga.",
        )
    st.caption(
        f"Demografski podaci odnose se na {data.demographic_year}, dok su oglasi "
        f"dostupni do {data.hzz_date:%d.%m.%Y}. Dob 15–64 nije isto što i aktivna radna snaga."
    )

with st.expander("Dodatni kontekst: MUP-ove izdane dozvole", icon=":material/info:"):
    st.write(
        "MUP-ove dozvole prikazane su odvojeno od oglasa. One predstavljaju "
        "izdane dozvole, a ne broj stranih radnika koji su trenutačno zaposleni."
    )
    st.metric("Izdane dozvole u izvještaju", format_number(selected["mup_dozvole"]))
    st.write(
        f"Izdane dozvole na 1.000 stanovnika: **{selected['dozvole_na_1000']:.2f}**."
    )
    st.caption(
        "Grad Zagreb i Zagrebačka županija spojeni su jer MUP objavljuje zajednički "
        "podatak za to područje."
    )

st.subheader("Demografski pregled regija")
st.caption(
    f"Udio stanovništva u dobi 15–64 i 65+ prema DZS procjeni za "
    f"{data.demographic_year}. Dobne skupine opisuju stanovništvo, a ne aktivnu radnu snagu."
)
demography = data.regional.sort_values("udio_15_64", ascending=False).loc[
    :,
    ["regija", "udio_15_64", "udio_65_plus", "stanovnici_15_64", "stanovnici_65_plus"],
].rename(
    columns={
        "regija": "Regija",
        "udio_15_64": "Udio 15–64 (%)",
        "udio_65_plus": "Udio 65+ (%)",
        "stanovnici_15_64": "Stanovnici 15–64",
        "stanovnici_65_plus": "Stanovnici 65+",
    }
)
st.dataframe(
    demography,
    hide_index=True,
    column_config={
        "Udio 15–64 (%)": st.column_config.NumberColumn(format="%.1f"),
        "Udio 65+ (%)": st.column_config.NumberColumn(format="%.1f"),
        "Stanovnici 15–64": st.column_config.NumberColumn(format="%d"),
        "Stanovnici 65+": st.column_config.NumberColumn(format="%d"),
    },
)
download_table(demography, "labourpulse-demografija-regija.xlsx")

st.subheader("Usporedite dvije regije")
st.caption(
    "Usporedba zanimanja i oglasa je u prvom planu. MUP-ove dozvole ostaju dodatni "
    "kontekst: oglas nije isto što i jedno slobodno radno mjesto, a dozvola ne znači "
    "da je osoba i dalje zaposlena."
)
comparison_regions = data.regional.set_index("regija").loc[
    [first_region, second_region]
]
hzz_comparison = comparison_regions[["hzz_oglasi"]].rename(
    columns={"hzz_oglasi": "Dostupni HZZ oglasi"}
)
st.bar_chart(hzz_comparison, y_label="Broj oglasa")
hzz_rate_comparison = comparison_regions[["oglasi_na_1000"]].rename(
    columns={"oglasi_na_1000": "HZZ oglasi / 1.000 stanovnika"}
)
st.bar_chart(hzz_rate_comparison, y_label="Oglasi na 1.000 stanovnika")
permit_comparison = comparison_regions[["mup_dozvole"]].rename(
    columns={"mup_dozvole": "MUP izdane dozvole"}
)
st.bar_chart(permit_comparison, y_label="Broj dozvola")
permit_rate_comparison = comparison_regions[["dozvole_na_1000"]].rename(
    columns={"dozvole_na_1000": "MUP dozvole / 1.000 stanovnika"}
)
st.bar_chart(permit_rate_comparison, y_label="Dozvole na 1.000 stanovnika")

regional_table = data.regional.sort_values("hzz_oglasi", ascending=False).loc[
    :,
    [
        "regija",
        "hzz_oglasi",
        "oglasi_na_1000",
        "oglasi_na_1000_15_64",
        "udio_15_64",
        "udio_65_plus",
        "stanovnici",
    ],
].rename(
    columns={
        "regija": "Regija",
        "hzz_oglasi": "HZZ oglasi",
        "oglasi_na_1000": "Oglasi / 1.000 stanovnika",
        "oglasi_na_1000_15_64": "Oglasi / 1.000 stanovnika 15–64",
        "udio_15_64": "Udio 15–64 (%)",
        "udio_65_plus": "Udio 65+ (%)",
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
        "Stanovnici": st.column_config.NumberColumn(format="%d"),
        "Oglasi / 1.000 stanovnika": st.column_config.NumberColumn(format="%.2f"),
        "Oglasi / 1.000 stanovnika 15–64": st.column_config.NumberColumn(format="%.2f"),
        "Udio 15–64 (%)": st.column_config.NumberColumn(format="%.1f"),
        "Udio 65+ (%)": st.column_config.NumberColumn(format="%.1f"),
    },
)
download_table(regional_table, "labourpulse-regionalni-podaci.xlsx")
