from pathlib import Path
from io import BytesIO

import pandas as pd
import streamlit as st

from utils.data import DashboardData, load_dashboard_data

DATA_ROOT = Path(__file__).resolve().parents[1]

PRIMARY_CHART_COLOR = "#0f766e"
SECONDARY_CHART_COLOR = "#2563eb"
ACCENT_CHART_COLOR = "#d97706"
RELATIVE_SCALE = ["#d7f0ec", "#83c9bd", "#2a9d8f", "#176b65", "#0b3d3a"]


def get_dashboard_data() -> DashboardData:
    try:
        return load_dashboard_data(str(DATA_ROOT))
    except (FileNotFoundError, ValueError, ImportError) as error:
        st.error(f"Podatke nije moguće učitati: {error}")
        st.info("Provjerite strukturu datoteka i instalirajte pakete iz requirements.txt.")
        st.stop()


def excel_bytes(table: pd.DataFrame, sheet_name: str = "Podaci") -> bytes:
    output = BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        table.to_excel(writer, index=False, sheet_name=sheet_name[:31])
    return output.getvalue()


def download_table(table: pd.DataFrame, filename: str) -> None:
    st.download_button(
        "Preuzmi",
        data=excel_bytes(table),
        file_name=filename,
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        icon=":material/download:",
        width="content",
    )
