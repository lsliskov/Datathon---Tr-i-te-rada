import streamlit as st

st.set_page_config(
    page_title="LabourPulse RH",
    page_icon=":material/monitoring:",
    layout="wide",
)

page = st.navigation(
    [
        st.Page(
            "app_pages/overview.py",
            title="Pregled tržišta",
            icon=":material/dashboard:",
            default=True,
        ),
        st.Page(
            "app_pages/regional.py",
            title="Regionalna analiza",
            icon=":material/map:",
        ),
        st.Page(
            "app_pages/occupations.py",
            title="Zanimanja i djelatnosti",
            icon=":material/work:",
        ),
        st.Page(
            "app_pages/pressure.py",
            title="Regionalna potražnja",
            icon=":material/query_stats:",
        ),
        st.Page(
            "app_pages/methodology.py",
            title="Podaci i metodologija",
            icon=":material/menu_book:",
        ),
    ],
    position="top",
)

with st.sidebar:
    st.caption("Filteri i kontekst prikaza")

page.run()
