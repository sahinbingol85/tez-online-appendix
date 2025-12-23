import streamlit as st
import pandas as pd
import plotly.express as px
import os

# --- 1. PAGE CONFIGURATION ---
st.set_page_config(
    page_title="Thesis Online Appendix",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- 2. MAIN TITLE & INTRO ---
st.title("📄 Online Appendix: Demographic Data Harmonization in Türkiye")
st.markdown("""
This web application presents the **Supplementary Materials** for the study titled **"Aligning Historical Data: Harmonization of the Historical Under-5 Mortality Data in Türkiye"**.
""")

# --- 3. SIDEBAR NAVIGATION ---
st.sidebar.title("Navigation")
selection = st.sidebar.radio("Go to:",
                             ["Home",
                              "Appendix E: Harmonized Mortality Data",
                              "Appendix F: Derivation Process & Thresholds",
                              "Appendix G: Supplementary Tables & Graphs"])


# --- 4. DATA LOADING FUNCTION ---
@st.cache_data
def load_data(file_name, header_arg=0):
    """
    Loads Excel data.
    header_arg: 0 for standard files, [0, 1] for multi-row headers (Appendix F).
    """
    file_path = file_name  # Assumes files are in the same folder as app.py

    if not os.path.exists(file_path):
        return None
    try:
        df = pd.read_excel(file_path, header=header_arg)
        return df
    except Exception as e:
        st.error(f"Error reading file '{file_name}': {e}")
        return None


# --- SECTION: HOME PAGE ---
if selection == "Home":
    st.info("👈 Please use the sidebar menu to navigate through the datasets.")

    st.header("About the Study")
    st.markdown("""
    ### **Objective**
    This study reconstructs Türkiye’s historical demographic trends by harmonizing fragmented archival records into a coherent longitudinal dataset. It addresses a critical gap in historical demography: the inconsistency between **mortality records** (often limited to administrative centers) and **census data** (covering the total population).

    ### **Key Methodological Contributions**
    1.  **Digitization & Standardization:** Fragmented historical mortality records from 1931 to 2008 were digitized and reclassified into a standardized **22-age category system**.

    2.  **Addressing the "Coverage Mismatch":**
        Historical mortality statistics were predominantly **urban-centric (Province and District Centers - PDC)**, while censuses covered the entire population. 

    3.  **Ratio-Based PDC Reconstruction:**
        To resolve this, the study introduces a novel **"Ratio-Based PDC Reconstruction Method"**. This approach isolates the true urban risk pools from census data and harmonizes them with mortality registries.

    ### **Data Availability**
    The datasets provided here serve as the empirical foundation for this reconstruction.
    """)

# --- SECTION: APPENDIX E ---
elif selection == "Appendix E: Harmonized Mortality Data":
    st.header("📂 Appendix E: Harmonized Mortality Data")
    st.markdown("""
    This dataset contains the fully harmonized mortality statistics, standardized into comparable age groups.
    * **Coverage:** National Level (1950–2008) & Provincial Level (1931–2008)
    """)

    file_name = "all_deaths-by_age_province.xlsx"
    df = load_data(file_name)

    if df is not None:
        st.dataframe(df, use_container_width=True)
        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="💾 Download Data (CSV)",
            data=csv,
            file_name="harmonized_mortality_appendix_e.csv",
            mime="text/csv"
        )
    else:
        st.warning(f"⚠️ File '{file_name}' not found. Please ensure it is in the same folder.")

# --- SECTION: APPENDIX F (COMPLEX MULTI-ROW HEADER) ---
elif selection == "Appendix F: Derivation Process & Thresholds":
    st.header("📂 Appendix F: Derivation Process and Threshold Choices")
    st.markdown("""
    This section details the **step-by-step derivation logic** used to align census populations with mortality records.
    The table includes the **metadata** (Thresholds), **Step 1** (Population Denominator Reconstruction), **Step 2** (Zero-Age Numerator Reconstruction), and **Step 3** (Final Estimation).
    """)

    file_name = "derivation_threshold.xlsx"
    # Loading with [0, 1] to handle the Metadata/Step1/Step2 grouping headers
    df = load_data(file_name, header_arg=[0, 1])

    if df is not None:
        # --- 1. DOWNLOAD BUTTON (FULL DATA) ---
        # We save the full multi-index dataframe as CSV
        csv = df.to_csv(index=True).encode('utf-8')
        st.download_button(
            label="💾 Download Full Dataset (CSV)",
            data=csv,
            file_name="derivation_thresholds_appendix_f.csv",
            mime="text/csv"
        )

        st.divider()

        # --- 2. INTERACTIVE FILTERING ---
        st.subheader("🔍 Explore Calculation Steps by Province")

        # We need to find the 'Province' column within the MultiIndex structure.
        # Structure is likely: ('METADATA', 'PROVINCE') or similar.
        # We will flatten columns temporarily to find the right one for filtering.

        # Create a copy for display logic
        df_display = df.copy()

        # Helper: Find the column that contains "PROVINCE" (case insensitive)
        province_col_key = None
        for col in df_display.columns:
            # col is a tuple like ('METADATA', 'PROVINCE')
            if "PROVINCE" in str(col).upper() or "İL" in str(col).upper():
                province_col_key = col
                break

        if province_col_key:
            # Get unique provinces
            provinces_list = df_display[province_col_key].unique()
            selected_province = st.selectbox("Select Province:", provinces_list)

            # Filter Data
            filtered_df = df_display[df_display[province_col_key] == selected_province]

            # Display
            st.markdown(f"**Showing details for: {selected_province}**")
            st.dataframe(filtered_df, use_container_width=True)

            st.info("""
            **Table Legend:**
            * **METADATA:** Includes the applied threshold for the specific year/province.
            * **STEP 1 (Denominator):** Shows the raw Census Total, the Excluded Rural Population, and the final Reconstructed Urban Population.
            * **STEP 2 (Numerator):** Shows the Census Zero-Age count and the Reconstructed Urban Zero-Age count.
            * **STEP 3 (Estimation):** Shows the derived Zero-Share Ratio and the Final Estimate.
            """)
        else:
            # Fallback if column not found
            st.warning("Could not automatically detect 'Province' column for filtering. Showing full table below:")
            st.dataframe(df, use_container_width=True)

    else:
        st.warning(f"⚠️ File '{file_name}' not found. Please ensure it is in the same folder.")

# --- SECTION: APPENDIX G ---
elif selection == "Appendix G: Supplementary Tables & Graphs":
    st.header("📂 Appendix G: Province-Specific Estimates of Zero-Age Populations and Time-Series Trends")
    st.markdown(
        "This section presents the final **zero-age population estimates** derived using the Ratio-Based PDC Reconstruction Method.")

    file_name = "final_zero_age_estimates.xlsx"
    df = load_data(file_name)

    if df is not None:
        # --- TAB 1: DATA TABLE ---
        st.subheader("📊 Data Table")
        st.dataframe(df, use_container_width=True)

        col1, col2 = st.columns([1, 5])
        with col1:
            csv = df.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="💾 Download CSV",
                data=csv,
                file_name="zero_age_estimates_appendix_g.csv",
                mime="text/csv"
            )

        st.divider()

        # --- TAB 2: INTERACTIVE GRAPH ---
        with st.expander("📈 Visualize Data (Click to Open Interactive Graphs)", expanded=False):
            st.subheader("Population Trends")
            st.markdown(
                "Select a level (province or national) below to visualize the zero-age population estimates over time.")

            # Standardize column names to UPPERCASE to avoid mismatch errors
            df.columns = [str(c).upper().strip() for c in df.columns]

            # Define Expected Columns
            # User confirmed columns: Level (or Province), Year, Total, Male, Female
            # We look for keywords since user might use 'Level' or 'Province'
            col_province = next((c for c in df.columns if 'LEVEL' in c or 'PROVINCE' in c), None)
            col_year = 'YEAR'
            col_value = 'TOTAL'

            if col_province and col_year in df.columns:
                # 1. Selector
                provinces_list = df[col_province].unique()
                selected_province = st.selectbox("Select Level / Province:", provinces_list)

                # 2. Filter
                filtered_df = df[df[col_province] == selected_province]

                # 3. Determine Y-Axes (Total, Male, Female)
                y_columns = []
                if 'TOTAL' in df.columns: y_columns.append('TOTAL')
                if 'MALE' in df.columns: y_columns.append('MALE')
                if 'FEMALE' in df.columns: y_columns.append('FEMALE')

                # Fallback
                if not y_columns and col_value in df.columns:
                    y_columns = [col_value]

                # 4. Plot
                if y_columns:
                    fig = px.line(
                        filtered_df,
                        x=col_year,
                        y=y_columns,
                        markers=True,
                        title=f"Zero-Age Population Estimates: {selected_province}",
                        labels={col_year: "Year", "value": "Population", "variable": "Group"}
                    )
                    fig.update_layout(hovermode="x unified", legend_title_text="Sex")
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.error("Could not find data columns (TOTAL, MALE, FEMALE) to plot.")
            else:
                st.error(f"Column mismatch! Needed 'YEAR' and 'LEVEL/PROVINCE'. Found: {list(df.columns)}")

    else:
        st.warning(f"⚠️ File '{file_name}' not found. Please ensure it is in the same folder.")