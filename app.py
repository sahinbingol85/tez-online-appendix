import streamlit as st
import pandas as pd
import plotly.express as px
import os

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="Thesis Online Appendix",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- MAIN TITLE ---
st.title("📄 Online Appendix: Demographic Data Harmonization in Türkiye")
st.markdown("""
This web application presents the **Supplementary Materials** for the study titled **"Aligning Historical Data: Harmonization of the Historical Under-5 Mortality Data in Türkiye"**.
""")

# --- SIDEBAR NAVIGATION ---
st.sidebar.title("Navigation")
selection = st.sidebar.radio("Go to:",
                             ["Home",
                              "Appendix E: Harmonized Mortality Data",
                              "Appendix F: Derivation Process & Thresholds",
                              "Appendix G: Supplementary Tables & Graphs"])


# --- DATA LOADING FUNCTION (UPDATED) ---
# header parametresi eklendi: Bazı dosyalar (Appx F gibi) çok satırlı başlığa sahip olabilir.
@st.cache_data
def load_data(file_name, header_arg=0):
    file_path = f"data/{file_name}"
    if not os.path.exists(file_path):
        return None
    try:
        # header_arg varsayılan olarak 0 (ilk satır), ama Appendix F için [0,1] göndereceğiz.
        df = pd.read_excel(file_path, header=header_arg)
        return df
    except Exception as e:
        st.error(f"Error reading file: {e}")
        return None


# --- 1. HOME PAGE ---
if selection == "Home":
    st.info("👈 Please use the sidebar menu to navigate through the datasets.")

    st.header("About the Study")

    st.markdown("""
    ### **Objective**
    This study reconstructs Türkiye’s historical demographic trends by harmonizing fragmented archival records into a coherent longitudinal dataset. It addresses a critical gap in historical demography: the inconsistency between **mortality records** (often limited to administrative centers) and **census data** (covering the total population).

    ### **Key Methodological Contributions**
    1.  **Digitization & Standardization:** Fragmented historical mortality records from 1931 to 2008 were digitized and reclassified into a standardized **22-age category system**, enabling consistent comparison across decades.

    2.  **Addressing the "Coverage Mismatch":**
        Historical mortality statistics in Türkiye were predominantly **urban-centric (Province and District Centers - PDC)**, while censuses covered the entire population. Using unadjusted census counts as denominators produces biased mortality rates. 

    3.  **Ratio-Based PDC Reconstruction:**
        To resolve this, the study introduces a novel **"Ratio-Based PDC Reconstruction Method"**. This approach isolates the true urban risk pools from census data and harmonizes them with mortality registries, ensuring that the **numerator (deaths)** and **denominator (population)** are structurally consistent.

    ### **Data Availability**
    The datasets provided here serve as the empirical foundation for this reconstruction, offering transparency and reproducibility for future research.
    """)

# --- 2. APPENDIX E ---
elif selection == "Appendix E: Harmonized Mortality Data":
    st.header("📂 Appendix E: Harmonized Mortality Data")
    st.markdown("""
    This dataset contains the fully harmonized mortality statistics, standardized into comparable age groups.

    **Coverage:**
    * **National Level:** 1950–2008
    * **Provincial Level:** 1931–2008
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
        st.warning(f"⚠️ File '{file_name}' not found. Please ensure it is located in the 'data' folder.")

# --- 3. APPENDIX F (UPDATED FOR MULTI-ROW HEADER) ---
elif selection == "Appendix F: Derivation Process & Thresholds":
    st.header("📂 Appendix F: Derivation Process and Threshold Choices")
    st.markdown(
        "This section details the population threshold choices applied for each province during census years to isolate the urban (PDC) population.")
    st.markdown("*Note: The table below reflects the hierarchical structure of the census data calculation.*")

    file_name = "derivation_threshold.xlsx"

    # header=[0, 1] kullanarak ilk iki satırı başlık olarak okuyoruz.
    # Böylece "TOTAL POPULATION" altındaki "TOTAL | MALE | FEMALE" yapısı bozulmaz.
    df = load_data(file_name, header_arg=[0, 1])

    if df is not None:
        st.dataframe(df, use_container_width=True)

        csv = df.to_csv(index=True).encode('utf-8')  # MultiIndex olduğu için index yapısını koruyoruz
        st.download_button(
            label="💾 Download Data (CSV)",
            data=csv,
            file_name="thresholds_appendix_f.csv",
            mime="text/csv"
        )
    else:
        st.warning(f"⚠️ File '{file_name}' not found. Please ensure it is located in the 'data' folder.")

# --- 4. APPENDIX G (PREVIOUSLY UPDATED) ---
elif selection == "Appendix G: Supplementary Tables & Graphs":
    st.header("📂 Appendix G: Supplementary Tables & Estimates")
    st.markdown(
        "This section presents the final **zero-age population estimates** derived using the Ratio-Based PDC Reconstruction Method.")

    file_name = "final_zero_age_estimates.xlsx"
    df = load_data(file_name)

    if df is not None:
        # --- PART 1: DATA TABLE ---
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

        # --- PART 2: INTERACTIVE GRAPH ---
        with st.expander("📈 Visualize Data (Click to Open Interactive Graphs)", expanded=False):
            st.subheader("Population Trends by Level")
            st.markdown(
                "Select a level (province or national) below to visualize the zero-age population estimates over time.")

            # --- COLUMN SETTINGS ---
            col_province = 'LEVEL'  # Appendix G dosyasındaki başlık
            col_year = 'YEAR'
            col_value = 'TOTAL'

            # Sütun başlıklarını standardize et (Büyük harf)
            df.columns = [str(c).upper() for c in df.columns]

            if col_province in df.columns and col_year in df.columns:

                provinces_list = df[col_province].unique()
                selected_province = st.selectbox("Select Level / Province:", provinces_list)

                filtered_df = df[df[col_province] == selected_province]

                # Çizilecek sütunları belirle
                y_columns = []
                if 'TOTAL' in df.columns: y_columns.append('TOTAL')
                if 'MALE' in df.columns: y_columns.append('MALE')
                if 'FEMALE' in df.columns: y_columns.append('FEMALE')

                if not y_columns and col_value in df.columns:
                    y_columns = [col_value]

                if y_columns:
                    fig = px.line(
                        filtered_df,
                        x=col_year,
                        y=y_columns,
                        markers=True,
                        title=f"Zero-Age Population Estimates: {selected_province}",
                        labels={col_year: "Year", "value": "Population", "variable": "Group"}
                    )
                    fig.update_layout(
                        hovermode="x unified",
                        legend_title_text="Demographic Group"
                    )
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.error("Could not find data columns (TOTAL, MALE, FEMALE) to plot.")
            else:
                st.error(
                    f"Column mismatch! Expected '{col_province}' and '{col_year}'. Found in file: {list(df.columns)}")

    else:
        st.warning(f"⚠️ File '{file_name}' not found. Please ensure it is located in the 'data' folder.")