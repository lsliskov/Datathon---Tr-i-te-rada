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
            title="Indeks pritiska",
            icon=":material/query_stats:",
        ),
    ],
    position="sidebar",
)

with st.sidebar:
    st.caption("Analitički pregled otvorenih podataka RH")

page.run()
