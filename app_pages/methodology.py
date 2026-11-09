import streamlit as st

from utils.ui import download_table, get_dashboard_data

data = get_dashboard_data()

st.title("Podaci i metodologija", anchor=False)
st.caption(
    "Ovdje su objašnjeni izvori, razdoblja i način na koji se podaci pretvaraju "
    "u razumljive pokazatelje."
)
st.caption(
    "Datoteke u projektu preuzete su 09.11.2026.; izvori se mogu osvježavati "
    "nakon tog datuma."
)

st.subheader("Što projekt pokazuje")
st.write(
    "LabourPulse RH povezuje tri javna izvora. HZZ daje sliku potražnje kroz oglase, "
    "MUP daje sliku izdanih dozvola za boravak i rad, a DZS daje demografski i "
    "nacionalni kontekst radne snage."
)

st.subheader("Izvori i kvaliteta podataka")
st.dataframe(
    data.quality,
    hide_index=True,
    column_config={
        "Ponovno preuzimanje": st.column_config.LinkColumn(
            "Ponovno preuzimanje",
            display_text="Otvori izvor",
        )
    },
    alt="Pregled izvora i kvalitete podataka",
)
download_table(data.quality, "labourpulse-kvaliteta-podataka.xlsx")

st.subheader("Kako čitati stranice")
with st.container(border=True):
    st.markdown(
        """
        **Pregled tržišta** povezuje najvažnije brojke u jednu početnu sliku.

        **Regionalna analiza** uspoređuje oglase, dozvole i stanovništvo među
        usporedivim regionalnim jedinicama.

        **Zanimanja i djelatnosti** prikazuje najtraženije skupine zanimanja prema
        HZZ-u i djelatnosti s najviše MUP-ovih dozvola.

        **Regionalna potražnja i intenzitet dozvola** koristi relativni pokazatelj
        za brzo rangiranje regija.
        """
    )

st.subheader("Metodološke bilješke")
st.markdown(
    """
    - HZZ podatke prikazuje po županiji i skupini zanimanja.
    - MUP podatke prikazuje po policijskoj upravi i djelatnosti.
    - DZS stanovništvo služi kao nazivnik za stope na 1.000 stanovnika.
    - DZS tablica zaposlenosti i nezaposlenosti daje nacionalnu vremensku seriju.
    - Sve regionalne tablice sortirane su prema vrijednosti pokazatelja koji prikazuju.
    - MUP djelatnosti i HZZ zanimanja ostaju odvojene klasifikacije, pa svaka zadržava
      svoje izvorno značenje.
    """
)

with st.expander("Izvorne datoteke", icon=":material/source:"):
    st.write(
        "Projekt koristi datoteke u direktorijima `data/dzs`, `data/hzz_zupanije`, "
        "`data/hzz_zanimanja`, `dozvole` i `stanovništvo`. Popis poveznica nalazi se "
        "u datoteci `data/SOURCES.txt`."
    )
