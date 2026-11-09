import streamlit as st

from utils.data import format_number
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
)
download_table(data.quality, "labourpulse-kvaliteta-podataka.xlsx")

st.subheader("Kako čitati stranice")
with st.container(border=True):
    st.markdown(
        """
        **Zanimanja po regijama** stavlja usporedbu skupina zanimanja među
        regijama u prvi plan. Možeš birati broj oglasa, oglase na 1.000
        stanovnika ili oglase na 1.000 stanovnika 15–64.

        **Regionalna analiza** uspoređuje oglase i demografski kontekst među
        usporedivim regionalnim jedinicama, dok su MUP-ove dozvole dodatni odvojeni
        kontekst.

        **Zanimanja i djelatnosti** prikazuje HZZ kategorije, omogućuje pretragu
        pojedinačnih naziva oglasa i prikazuje djelatnosti s najviše MUP-ovih dozvola.

        **Zanimanja po regijama** uspoređuje HZZ oglase po skupinama zanimanja
        među regijama, kao broj oglasa ili oglase na 1.000 stanovnika.
        """
    )

st.subheader("Metodološke bilješke")
st.markdown(
    """
    - HZZ podatke prikazuje po županiji i kategoriji. Nepotpune oznake se
      povezuju s potpunijim oznakama iz istog izvatka; nedvosmisleni nazivi
      „doktor/doktorica medicine” (ne veterinarske medicine) i
      „keramičar/keramičarka” imaju izričito pravilo normalizacije. Izvorna
      kategorija i pravilo vidljivi su uz pojedinačni oglas.
    - Pravila iz naslova deterministička su i nisu neovisno validirana prema
      stručno označenom uzorku; mogu pogrešno razvrstati pojedinačni oglas.
      Kategorije su šire skupine, ne precizan stručni profil svakog posla.
    - MUP podatke prikazuje po policijskoj upravi i djelatnosti.
    - DZS stanovništvo služi kao nazivnik za stope na 1.000 stanovnika.
    - Regionalni demografski nazivnik odnosi se na procjenu za 2024. godinu.
      Oglasi su noviji, a dob 15–64 nije isto što i aktivna radna snaga.
    - Prikaz oglasa na 1.000 stanovnika 15–64 opisuje odnos oglasa prema
      veličini dobne skupine; ne predstavlja broj slobodnih radnih mjesta po
      aktivnom radniku.
    - DZS tablica zaposlenosti i nezaposlenosti daje nacionalnu vremensku seriju.
    - Regionalni prikaz zanimanja uključuje oglase s pouzdano prepoznatom
      kategorijom; broj nerazvrstanih oglasa naveden je uz prikaz.
    - MUP djelatnosti i HZZ zanimanja ostaju odvojene klasifikacije, pa svaka
      zadržava svoje izvorno značenje.
    - MUP-ove dozvole prikazuju se kao dodatni kontekst. One su izdane dozvole,
      ne broj trenutačno zaposlenih stranih radnika.
    """
)

unclassified_count = int((data.vacancies["zanimanje"] == "Nerazvrstano").sum())
unclassified_share = (
    unclassified_count / len(data.vacancies) * 100 if len(data.vacancies) else 0
)
st.subheader("Ograničenja sustava")
st.markdown(
    f"""
    - Aplikacija obrađuje lokalno spremljene datoteke; izvori se ne osvježavaju
      automatski putem API-ja.
    - HZZ RSS izvadak prikazuje trenutno dostupne oglase, ne arhivu svih oglasa.
      Kategorije se preuzimaju iz opisa oglasa ili povezanog HZZ RSS-a zanimanja;
      {format_number(unclassified_count)} od {format_number(len(data.vacancies))}
      oglasa u ovom izvatku ({unclassified_share:.1f} %) nema pouzdano dostupnu
      kategoriju. Izvorni naslov i oznaka kategorije mogu se provjeriti na stranici
      zanimanja.
    - Deduplikacija koristi ključ regija + GUID; ako GUID nedostaje, koristi
      poveznicu, a ako nedostaju oba, naziv oglasa i datum objave. Ponovna objava
      s drugim identifikatorom može ostati zasebno; jedan oglas može tražiti više
      radnika. Nerazvrstani oglasi nisu uključeni u agregate zanimanja.
    - MUP-ove dozvole su kumulativne vrijednosti za tekuću godinu do datuma
      izvještaja, a ne broj osoba kojima je dozvola trenutačno aktivna ili
      trenutačno zaposlenih stranih radnika; one bilježe izdane dozvole.
    - MUP prikazuje Grad Zagreb i Zagrebačku županiju zajedno; zato su i HZZ
      oglasi u regionalnoj usporedbi objedinjeni.
    - Regionalni nazivnik stanovništva iznosi procjenu za {data.population_year}.
      Usporedba s novijim oglasima i dozvolama zato ne predstavlja potpuno
      vremenski usklađen pokazatelj.
    - DZS podaci o radnoj snazi su nacionalni i privremeni, do razdoblja
      {data.national_labor['razdoblje'].iloc[-1] if not data.national_labor.empty else "nedostupno"};
      nisu regionalno usporedivi s HZZ oglasima.
    - DZS podaci o nezaposlenosti dostupni u ovom projektu samo su nacionalni,
      pa nema usporedivih regionalnih podataka za omjer slobodnih radnih mjesta
      i nezaposlenih. Aplikacija zato ne izračunava indeks ponude i potražnje.
    """
)

st.subheader("Budući razvoj")
st.markdown(
    """
    - Automatizirati osvježavanje HZZ, MUP i DZS podataka uz bilježenje verzije,
      datuma, izvora i promjena u strukturi datoteka.
    - Održavati potpuniju povijest HZZ oglasa te mjeriti i postupno smanjivati
      udio oglasa bez pouzdane kategorije, bez prešućivanja izvorne klasifikacije.
    - Uskladiti vremenski obuhvat regionalnog stanovništva s najnovijim dostupnim
      procjenama i povezati dodatne regionalne DZS pokazatelje.
    - Dodati provjere kvalitete pri uvozu (duplikati, prazne vrijednosti,
      nepoznate kategorije i zbrojevi) te automatizirane testove izvora.
    - Izložiti strojno čitljive rezultate kroz dokumentirano sučelje i pripremiti
      interoperabilan izvoz za druge javne sustave.
    """
)

with st.expander("Izvorne datoteke", icon=":material/source:"):
    st.write(
        "Projekt koristi datoteke u direktorijima `data/dzs`, `data/hzz_zupanije`, "
        "`data/hzz_zanimanja`, `dozvole` i `stanovništvo`. Popis poveznica nalazi se "
        "u datoteci `data/SOURCES.txt`."
    )
