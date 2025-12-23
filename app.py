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


# --- DATA LOADING FUNCTION ---
@st.cache_data
def load_data(file_name, header_arg=0):
    file_path = file_name
    if not os.path.exists(file_path):
        return None
    try:
        # Excel okurken header parametresini esnek tutuyoruz
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
    2.  **Addressing the "Coverage Mismatch":** Historical mortality statistics in Türkiye were predominantly **urban-centric (Province and District Centers - PDC)**, while censuses covered the entire population. 
    3.  **Ratio-Based PDC Reconstruction:** The study introduces a novel **"Ratio-Based PDC Reconstruction Method"** to isolate true urban risk pools from census data.
    """)

# --- 2. APPENDIX E ---
elif selection == "Appendix E: Harmonized Mortality Data":
    st.header("📂 Appendix E: Harmonized Mortality Data")
    st.markdown(
        "This dataset contains the fully harmonized mortality statistics (National & Provincial) from 1931 to 2008.")

    file_name = "all_deaths-by_age_province.xlsx"
    df = load_data(file_name)

    if df is not None:
        st.dataframe(df, use_container_width=True)
        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button("💾 Download CSV", csv, "harmonized_mortality.csv", "text/csv")
    else:
        st.warning(f"File '{file_name}' not found.")

# --- 3. APPENDIX F (YENİLENEN KISIM: DETAYLI TABLO GÖRÜNÜMÜ) ---
elif selection == "Appendix F: Derivation Process & Thresholds":
    st.header("📂 Appendix F: Derivation Process and Threshold Choices")
    st.markdown("""
    This section provides the **step-by-step calculation logic** used to align census populations with mortality records.
    Since the calculation involves isolating specific population groups (threshold-based subtraction), the table below details every component of the equation.
    """)

    # 1. Veriyi Yükle (2 satırlı başlık olduğu için header=[0,1])
    file_name = "derivation_threshold.xlsx"
    df = load_data(file_name, header_arg=[0, 1])

    if df is not None:
        # 2. İndirme Butonunu En Üste Koy (Araştırmacılar için ham veri önemlidir)
        csv = df.to_csv(index=True).encode('utf-8')
        st.download_button(
            label="💾 Download Full Dataset (All Provinces & Years)",
            data=csv,
            file_name="derivation_thresholds_appendix_f.csv",
            mime="text/csv"
        )

        st.divider()

        # 3. İNTERAKTİF FİLTRELEME (Karmaşıklığı Yönetmek İçin)
        st.subheader("🔍 Explore Derivation Details by Province")

        # Excel'deki sütun isimlerini temizlemek gerekebilir ama MultiIndex olduğu için
        # ilk seviyedeki (üst satırdaki) isimleri alalım.
        # Genellikle PROVINCE sütunu ilk seviyede bellidir.

        # Sütunları düzleştiriyoruz (Handling Multi-Level Headers)
        # Örn: ('Total Population', 'Male') -> 'Total Population - Male'
        df_display = df.copy()
        df_display.columns = [' '.join(col).strip() if isinstance(col, tuple) else col for col in df_display.columns]

        # İli bulmaya çalışalım (Genellikle içinde 'Province' veya 'Il' geçen sütun)
        province_col = next((col for col in df_display.columns if "PROVINCE" in col.upper() or "İL" in col.upper()),
                            None)

        if province_col:
            provinces = df_display[province_col].unique()
            selected_province = st.selectbox("Select a Province to View Calculation Steps:", provinces)

            # Seçilen ile göre filtrele
            filtered_df = df_display[df_display[province_col] == selected_province]

            st.markdown(f"**Showing derivation steps for: {selected_province}**")
            st.dataframe(filtered_df, use_container_width=True)

            st.info("""
            **Guide to Columns:**
            * **Total Population:** Raw Census Count.
            * **Areas < 10,000:** Population excluded to match urban definition.
            * **Remaining Population:** The reconstructed urban base (Denominator).
            * **PDC Population:** Reference population from Mortality Statistics.
            * **Coverage Rate:** Alignment score (Ideal is ~100%).
            * **ZeroShare:** Derived ratio applied to estimate zero-age population.
            """)
        else:
            # Eğer otomatik sütun bulamazsa ham halini göster
            st.warning("Could not automatically detect 'Province' column for filtering. Showing full table.")
            st.dataframe(df, use_container_width=True)

    else:
        st.warning(f"File '{file_name}' not found.")

# --- 4. APPENDIX G ---
elif selection == "Appendix G: Supplementary Tables & Graphs":
    st.header("📂 Appendix G: Province-Specific Estimates of Zero-Age Populations and Time-Series Trends")
    st.markdown("This section presents the final **zero-age population estimates**.")

    file_name = "final_zero_age_estimates.xlsx"
    df = load_data(file_name)

    if df is not None:
        st.subheader("📊 Data Table")
        st.dataframe(df, use_container_width=True)
        col1, col2 = st.columns([1, 5])
        with col1:
            csv = df.to_csv(index=False).encode('utf-8')
            st.download_button("💾 Download CSV", csv, "zero_age_estimates_appendix_g.csv", "text/csv")

        st.divider()

        with st.expander("📈 Visualize Data (Click to Open Interactive Graphs)", expanded=False):
            st.subheader("Population Trends")
            col_province, col_year, col_value = 'LEVEL', 'YEAR', 'TOTAL'
            df.columns = [str(c).upper() for c in df.columns]

            if col_province in df.columns and col_year in df.columns:
                provinces_list = df[col_province].unique()
                selected_province = st.selectbox("Select Level / Province:", provinces_list)
                filtered_df = df[df[col_province] == selected_province]

                y_columns = [c for c in ['TOTAL', 'MALE', 'FEMALE'] if c in df.columns] or (
                    [col_value] if col_value in df.columns else [])

                if y_columns:
                    fig = px.line(filtered_df, x=col_year, y=y_columns, markers=True,
                                  title=f"Trends: {selected_province}")
                    fig.update_layout(hovermode="x unified")
                    st.plotly_chart(fig, use_container_width=True)
            else:
                st.error("Column mismatch regarding LEVEL/YEAR.")
    else:
        st.warning(f"File '{file_name}' not found.")