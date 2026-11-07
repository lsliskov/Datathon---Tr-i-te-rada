from pathlib import Path

import streamlit as st

from utils.data import DashboardData, load_dashboard_data

DATA_ROOT = Path(__file__).resolve().parents[1]


def get_dashboard_data() -> DashboardData:
    try:
        return load_dashboard_data(str(DATA_ROOT))
    except (FileNotFoundError, ValueError, ImportError) as error:
        st.error(f"Podatke nije moguće učitati: {error}")
        st.info("Provjerite strukturu datoteka i instalirajte pakete iz requirements.txt.")
        st.stop()
