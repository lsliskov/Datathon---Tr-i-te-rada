import pandas as pd
import plotly.express as px
import streamlit as st

from utils.data import format_number
from utils.ui import PRIMARY_CHART_COLOR, download_table, get_dashboard_data

data = get_dashboard_data()
mup_years = sorted(
    pd.to_datetime(data.history["datum"], errors="coerce")
    .dt.year.dropna()
    .astype(int)
    .unique()
    .tolist()
)
dzs_years_by_row = pd.to_numeric(
    data.national_labor["razdoblje"].str.extract(r"(20\d{2})", expand=False),
    errors="coerce",
)
dzs_years = sorted(dzs_years_by_row.dropna().astype(int).unique().tolist())
with st.sidebar:
    st.subheader("Filteri sažetka")
    selected_mup_years = st.multiselect(
        "Godina MUP izvještaja",
        mup_years,
        default=mup_years,
        help="Filtrira povijesnu seriju MUP-ovih kumulativnih izvještaja.",
    )
    selected_dzs_years = st.multiselect(
        "Godina DZS podataka",
        dzs_years,
        default=dzs_years,
        help="Filtrira nacionalnu DZS seriju zaposlenih i nezaposlenih.",
    )

st.title("Sažetak tržišta rada", anchor=False)
st.caption(
    "Ovdje možeš brzo vidjeti koja se zanimanja traže i kako se oglasi razlikuju "
    "među regijama. Demografija daje kontekst za usporedbu regionalnih stopa."
)
st.caption(
    f"Razdoblja: HZZ objave do {data.hzz_date:%d.%m.%Y} · "
    f"MUP izvještaj od {data.permit_date:%d.%m.%Y} · "
    f"DZS procjena stanovništva {data.population_year} · "
    "podaci preuzeti 09.11.2026."
)

filtered_labor = data.national_labor.loc[
    dzs_years_by_row.isin(selected_dzs_years)
]
latest_labor = filtered_labor.iloc[-1] if not filtered_labor.empty else None
top_hzz_region = data.regional.sort_values(
    "hzz_oglasi", ascending=False
).iloc[0]["regija"]
with st.container(horizontal=True):
    st.metric(
        "Dostupni HZZ oglasi",
        format_number(data.regional["hzz_oglasi"].sum()),
        border=True,
        help="Broj oglasa koji su dostupni u spremljenom HZZ RSS izvatku. Oglas ne mora odgovarati samo jednom radnom mjestu.",
    )
    st.metric(
        "Najviše oglasa",
        top_hzz_region,
        border=True,
        help="Regija s najviše trenutno dostupnih HZZ oglasa u izvatku.",
    )
    st.metric("Prosječni udio 15–64", f"{data.regional['udio_15_64'].mean():.1f} %", border=True)
    if latest_labor is not None:
        st.metric(
            "Nezaposleni prema DZS-u",
            format_number(latest_labor["Nezaposleni"]),
            border=True,
            help=f"Nacionalni broj nezaposlenih u odabranom DZS razdoblju: {latest_labor['razdoblje']}.",
        )

st.caption(
    "HZZ prikazuje trenutno dostupne oglase u RSS izvatku; izvor ne sadrži "
    "povijesnu arhivu za usporedbu godina."
)
st.caption(
    f"MUP izvještaj: {data.permit_date:%d.%m.%Y} · "
    f"stanovništvo: procjena za {data.population_year}. · "
    f"HZZ izvadak: najnoviji datum objave {data.hzz_date:%d.%m.%Y}"
    if data.hzz_date
    else f"MUP izvještaj: {data.permit_date:%d.%m.%Y} · stanovništvo: procjena za {data.population_year}."
)
st.write(
    "Broj oglasa govori gdje su trenutno objavljene prilike, a demografski podaci "
    f"pomažu razumjeti regionalni kontekst. Demografski nazivnik odnosi se na "
    f"{data.demographic_year}, dok su oglasi noviji; dob 15–64 nije isto što i "
    "aktivna radna snaga."
)

left, right = st.columns(2)
with left:
    st.subheader("U kojim regijama je najviše oglasa?")
    chart_data = data.regional.nlargest(8, "hzz_oglasi").sort_values("hzz_oglasi")
    fig = px.bar(
        chart_data,
        x="hzz_oglasi",
        y="regija",
        orientation="h",
        labels={"hzz_oglasi": "HZZ oglasi", "regija": ""},
        color_discrete_sequence=[PRIMARY_CHART_COLOR],
    )
    fig.update_layout(showlegend=False, coloraxis_showscale=False, height=390)
    st.plotly_chart(
        fig,
        width="stretch",
        config={"scrollZoom": False, "doubleClick": False, "displayModeBar": False},
    )
with right:
    st.subheader("Demografski kontekst regija")
    st.caption(
        f"Udio stanovništva 15–64 i 65+ prema DZS procjeni za {data.demographic_year}. "
        "Dobna skupina nije isto što i aktivna radna snaga."
    )
    demographic_chart = data.regional.nlargest(8, "udio_15_64").sort_values("udio_15_64")
    fig = px.bar(
        demographic_chart,
        x="udio_15_64",
        y="regija",
        orientation="h",
        labels={"udio_15_64": "Udio stanovništva 15–64 (%)", "regija": ""},
        color_discrete_sequence=[PRIMARY_CHART_COLOR],
    )
    fig.update_layout(showlegend=False, coloraxis_showscale=False, height=390)
    st.plotly_chart(
        fig,
        width="stretch",
        config={"scrollZoom": False, "doubleClick": False, "displayModeBar": False},
    )

with st.expander("Dodatni kontekst: MUP-ove izdane dozvole", icon=":material/info:"):
    st.caption(
        f"Zadnji MUP izvještaj: {data.permit_date:%d.%m.%Y}. Vrijednosti su "
        "kumulativne izdane dozvole, ne broj trenutačno zaposlenih stranih radnika."
    )
    history = data.history.loc[
        data.history["godina"].astype(int).isin(selected_mup_years)
    ]
    if history.empty:
        st.info("Odaberite barem jednu godinu MUP-ovih izvještaja.")
    else:
        fig = px.line(
            history,
            x="datum",
            y="izdane_dozvole",
            color="godina",
            markers=True,
            labels={"datum": "Datum izvještaja", "izdane_dozvole": "Izdane dozvole", "godina": "Godina"},
        )
        fig.update_layout(height=390, legend_title_text="Godina")
        st.plotly_chart(
            fig,
            width="stretch",
            config={"scrollZoom": False, "doubleClick": False, "displayModeBar": False},
        )

st.subheader("Gdje je najviše dostupnih oglasa?")
st.caption(
    "Tablica uspoređuje ukupan broj oglasa i broj oglasa na 1.000 stanovnika. "
    "Druga vrijednost pomaže usporediti veće i manje regije."
)
leaders = data.regional.sort_values("hzz_oglasi", ascending=False).head(5).loc[
    :, ["regija", "hzz_oglasi", "oglasi_na_1000", "mup_dozvole"]
].rename(
    columns={
        "regija": "Regija",
        "hzz_oglasi": "HZZ oglasi",
        "oglasi_na_1000": "HZZ oglasi / 1.000 stanovnika",
        "mup_dozvole": "MUP dozvole",
    }
)
st.dataframe(
    leaders,
    hide_index=True,
    column_config={
        "HZZ oglasi": st.column_config.NumberColumn(format="%d"),
        "HZZ oglasi / 1.000 stanovnika": st.column_config.NumberColumn(format="%.2f"),
        "MUP dozvole": st.column_config.NumberColumn(format="%d"),
    },
)
download_table(leaders, "labourpulse-pregled-regija.xlsx")

if not data.national_labor.empty:
    st.subheader("Nacionalni kontekst radne snage")
    if latest_labor is None:
        st.info("Odaberite barem jednu godinu DZS podataka.")
    else:
        labor = filtered_labor.rename(columns={"razdoblje": "Razdoblje"})
        st.line_chart(
            labor.set_index("Razdoblje")[["Nezaposleni", "Zaposleni"]],
            y_label="Osobe",
        )
        st.caption(
            "Serija prikazuje dostupne mjesečne vrijednosti iz DZS-ove tablice "
            "aktivnog stanovništva prema administrativnim izvorima; zadnja dostupna "
            f"vrijednost u odabranim godinama je {latest_labor['razdoblje']}."
        )

with st.expander("Kako čitati ovaj pregled", icon=":material/info:"):
    st.write(
        "HZZ oglasi daju sliku trenutačne potražnje. MUP dozvole pokazuju opseg izdanih "
        "dozvola u odabranom izvještaju. DZS serija daje širi kontekst kretanja radne snage. "
        "Broj oglasa nije isto što i broj slobodnih radnih mjesta, a izdana dozvola "
        "ne znači nužno da je osoba još zaposlena."
    )
