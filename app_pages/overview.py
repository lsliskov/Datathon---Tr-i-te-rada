import plotly.express as px
import streamlit as st

from utils.data import format_number
from utils.ui import PRIMARY_CHART_COLOR, download_table, get_dashboard_data

data = get_dashboard_data()

st.title("LabourPulse RH", anchor=False)
st.caption(
    "Jednostavan pregled gdje poslodavci traže radnike, koja su zanimanja najtraženija "
    "i kako se potražnja razlikuje među hrvatskim regijama."
)
st.caption(
    f"Razdoblja: HZZ objave do {data.hzz_date:%d.%m.%Y} · "
    f"MUP izvještaj od {data.permit_date:%d.%m.%Y} · "
    f"DZS procjena stanovništva {data.population_year} · "
    "podaci preuzeti 09.11.2026."
)

latest_labor = data.national_labor.iloc[-1] if not data.national_labor.empty else None
with st.container(horizontal=True):
    st.metric("HZZ oglasi u izvatku", format_number(data.regional["hzz_oglasi"].sum()), border=True)
    st.metric(
        "MUP dozvole u izvještaju",
        format_number(data.regional["mup_dozvole"].sum()),
        border=True,
    )
    st.metric("Regija s najviše oglasa", data.regional.sort_values("hzz_oglasi", ascending=False).iloc[0]["regija"], border=True)
    if latest_labor is not None:
        st.metric("Nezaposleni u DZS seriji", format_number(latest_labor["Nezaposleni"]), border=True)

st.caption(
    f"MUP izvještaj: {data.permit_date:%d.%m.%Y} · "
    f"stanovništvo: procjena za {data.population_year}. · "
    f"HZZ izvadak: najnoviji datum objave {data.hzz_date:%d.%m.%Y}"
    if data.hzz_date
    else f"MUP izvještaj: {data.permit_date:%d.%m.%Y} · stanovništvo: procjena za {data.population_year}."
)
st.write(
    "Oglasi pokazuju gdje se trenutačno otvara najviše prilika, a dozvole daju "
    "dodatni uvid u djelatnosti koje koriste međunarodnu radnu snagu. DZS serija "
    "donosi nacionalni kontekst zaposlenosti i nezaposlenosti."
)

left, right = st.columns(2)
with left:
    st.subheader("Dozvole prema regiji")
    st.caption(f"MUP izvještaj: {data.permit_date:%d.%m.%Y}")
    chart_data = data.regional.nlargest(8, "mup_dozvole").sort_values("mup_dozvole")
    fig = px.bar(
        chart_data,
        x="mup_dozvole",
        y="regija",
        orientation="h",
        labels={"mup_dozvole": "Dozvole", "regija": ""},
        color_discrete_sequence=[PRIMARY_CHART_COLOR],
    )
    fig.update_layout(showlegend=False, coloraxis_showscale=False, height=390)
    st.plotly_chart(
        fig,
        width="stretch",
        config={"scrollZoom": False, "doubleClick": False, "displayModeBar": False},
    )

with right:
    st.subheader("MUP izvještaji kroz vrijeme")
    st.caption("Datumi na osi označavaju datum svakog MUP izvještaja.")
    fig = px.line(
        data.history,
        x="datum",
        y="izdane_dozvole",
        color="godina",
        markers=True,
        labels={"datum": "Datum izvještaja", "izdane_dozvole": "Dozvole", "godina": "Godina"},
    )
    fig.update_layout(height=390, legend_title_text="Godina")
    st.plotly_chart(
        fig,
        width="stretch",
        config={"scrollZoom": False, "doubleClick": False, "displayModeBar": False},
    )
    st.caption(
        "Brojevi su zbrojevi dozvola evidentiranih u izvještaju do njegova datuma; "
        "serija se početkom godine vraća na početnu vrijednost."
    )

st.subheader("Regije s najvećom potražnjom")
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
    alt="Pet regija s najvećim brojem HZZ oglasa",
)
download_table(leaders, "labourpulse-pregled-regija.xlsx")

if latest_labor is not None:
    st.subheader("Nacionalni kontekst radne snage")
    labor = data.national_labor.rename(columns={"razdoblje": "Razdoblje"})
    st.line_chart(
        labor.set_index("Razdoblje")[["Nezaposleni", "Zaposleni"]],
        y_label="Osobe",
        alt="Kretanje zaposlenih i nezaposlenih u nacionalnoj DZS seriji",
    )
    st.caption(
        "Serija prikazuje dostupne mjesečne i godišnje vrijednosti iz DZS-ove tablice "
        "aktivnog stanovništva prema administrativnim izvorima; zadnja dostupna "
        f"vrijednost u ovom izdanju je {latest_labor['razdoblje']}."
    )

with st.expander("Kako čitati ovaj pregled", icon=":material/info:"):
    st.write(
        "HZZ oglasi daju sliku trenutačne potražnje. MUP dozvole pokazuju opseg izdanih "
        "dozvola u odabranom izvještaju. DZS serija daje širi kontekst kretanja radne snage."
    )
