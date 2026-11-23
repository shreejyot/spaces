import hmac
import os

import streamlit as st

from sector_config import load_sectors_dataframe, save_sectors_dataframe


st.set_page_config(page_title="Sector Admin", layout="wide")
st.title("Sector Admin")
st.caption("Edit the ticker, description, and asset class used by the dashboard.")

admin_password = os.environ.get("ADMIN_PASSWORD", "admin123")  # Default password for testing
if not admin_password:
    st.warning("Set the ADMIN_PASSWORD environment variable to enable saving.")

sectors = load_sectors_dataframe()
with st.form("sector_editor"):
    edited_sectors = st.data_editor(
        sectors,
        column_config={
            "Ticker": st.column_config.TextColumn("Ticker", required=True),
            "Description": st.column_config.TextColumn("Description", required=True),
            "AssetClass": st.column_config.TextColumn("AssetClass", required=True),
        },
        num_rows="dynamic",
        hide_index=True,
        use_container_width=True,
    )
    submitted_password = st.text_input("Admin password", type="password")
    submitted = st.form_submit_button("Save sectors")

if submitted:
    if not admin_password:
        st.error("Saving is disabled because ADMIN_PASSWORD is not configured.")
    elif not hmac.compare_digest(submitted_password, admin_password):
        st.error("Incorrect admin password.")
    else:
        try:
            save_sectors_dataframe(edited_sectors)
        except ValueError as error:
            st.error(str(error))
        except OSError as error:
            st.error(f"Could not save sectors: {error}")
        else:
            st.success("Sector list saved.")
            st.rerun()
