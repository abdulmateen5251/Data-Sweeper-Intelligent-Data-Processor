import streamlit as st
import pandas as pd
import os
from io import StringIO, BytesIO
import seaborn as sns
import matplotlib.pyplot as plt

# Configure Streamlit app
st.set_page_config(page_title="Data Sweeper", layout="wide")

# =========================
# CUSTOM STYLING (DARK MODE UI)
# =========================
st.markdown(
    """
    <style>
        .main { background-color: #121212; }
        .block-container {
            padding: 3rem 2rem;
            border-radius: 12px;
            background-color: #1e1e1e;
            box-shadow: 0 4px 15px rgba(0, 0, 0, 0.3);
        }
        h1, h2, h3, h4, h5, h6 { color: #66c2ff; }
        .stButton>button {
            border-radius: 8px;
            background-color: #0078D7;
            color: white;
            font-size: 1rem;
        }
        .stButton>button:hover { background-color: #005a9e; }
        .stDownloadButton>button {
            background-color: #28a745;
            color: white;
        }
        .stDownloadButton>button:hover { background-color: #218838; }
    </style>
    """,
    unsafe_allow_html=True
)

# =========================
# HEADER & FILE UPLOAD SECTION
# =========================
st.title("📊 Data Sweeper - Intelligent Data Processor")
st.write("Easily clean, analyze, and transform your data files with automated features.")

# File uploader to accept CSV and Excel files
uploaded_file = st.file_uploader("📂 Upload your dataset (CSV or Excel):", type=["csv", "xlsx"])

# Proceed only if a file is uploaded
if uploaded_file:
    file_extension = os.path.splitext(uploaded_file.name)[-1].lower()

    # Read file into Pandas DataFrame
    if file_extension == ".csv":
        df = pd.read_csv(uploaded_file)
    elif file_extension == ".xlsx":
        df = pd.read_excel(uploaded_file)
    else:
        st.error(f"❌ Unsupported file type: {file_extension}")
        st.stop()

    # Display file metadata
    st.write(f"**📄 File Name:** {uploaded_file.name}")
    st.write(f"**📏 File Size:** {uploaded_file.size / 1024:.2f} KB")

    # =========================
    # DYNAMIC COLUMN SELECTION (NEW FEATURE)
    # =========================
    st.subheader("📌 Dynamic Column Selection")
    selected_columns = st.multiselect("📊 Select columns to analyze:", df.columns, default=df.columns)

    # Apply selection to DataFrame
    df = df[selected_columns]
    st.write("🔍 **Updated Data Preview:**")
    st.dataframe(df.head())

    # =========================
    # DATA CLEANING SECTION
    # =========================
    st.subheader("🛠️ Data Cleaning Options")

    if st.checkbox("Enable Data Cleaning"):
        col1, col2 = st.columns(2)

        # Remove duplicate rows
        with col1:
            if st.button("🗑 Remove Duplicate Rows"):
                df.drop_duplicates(inplace=True)
                st.success("✔ Duplicates removed successfully!")

        # Fill missing values with mean (for numeric columns)
        with col2:
            if st.button("🔄 Fill Missing Values (Mean)"):
                numeric_cols = df.select_dtypes(include=["number"]).columns
                df[numeric_cols] = df[numeric_cols].fillna(df[numeric_cols].mean())
                st.success("✔ Missing values filled with column means!")

    # =========================
    # DATA EXPLORATION
    # =========================
    st.subheader("🔎 Data Exploration")

    if st.checkbox("📌 Show Summary Statistics"):
        st.write("**📊 Dataset Information:**")

        buffer_info = StringIO()
        df.info(buf=buffer_info)
        st.text(buffer_info.getvalue())  # Display DataFrame info()

        st.write("**📈 Summary Statistics:**")
        st.dataframe(df.describe())

    # Correlation Heatmap
    if st.checkbox("📉 Show Correlation Heatmap"):
        numeric_data = df.select_dtypes(include=["number"])
        if numeric_data.empty:
            st.warning("⚠ No numeric columns available for correlation heatmap.")
        else:
            fig, ax = plt.subplots(figsize=(8, 6))
            sns.heatmap(numeric_data.corr(), annot=True, cmap="coolwarm", ax=ax)
            st.pyplot(fig)

    # Histograms
    if st.checkbox("📊 Show Histograms"):
        numeric_data = df.select_dtypes(include=["number"])
        if numeric_data.empty:
            st.warning("⚠ No numeric columns available for histogram plotting.")
        else:
            for col in numeric_data.columns:
                fig, ax = plt.subplots()
                ax.hist(numeric_data[col].dropna(), bins=20, color="skyblue")
                ax.set_title(f"Distribution of {col}")
                st.pyplot(fig)

    # =========================
    # DATA EXPORT & CONVERSION
    # =========================
    st.subheader("🔄 Export & Convert Data")

    conversion_type = st.radio("Choose export format:", ["CSV", "Excel"])

    if st.button("📥 Convert & Download"):
        buffer = BytesIO() if conversion_type == "Excel" else StringIO()

        # Convert DataFrame to chosen format
        if conversion_type == "CSV":
            df.to_csv(buffer, index=False)
            mime_type = "text/csv"
        else:  # Excel format
            df.to_excel(buffer, index=False, engine='openpyxl')
            mime_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"

        buffer.seek(0)  # Reset buffer position
        st.download_button(
            label=f"📥 Download as {conversion_type}",
            data=buffer,
            file_name=f"processed_data.{conversion_type.lower()}",
            mime=mime_type
        )

    st.success("✅ All operations completed successfully!")

else:
    st.info("📂 Please upload a CSV or Excel file to begin.")
