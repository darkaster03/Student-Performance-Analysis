import streamlit as st
import pandas as pd
from io import StringIO
import matplotlib.pyplot as plt
import seaborn as sns

# ---------- Function to process uploaded CSV data ----------
def process_csv_data(csv_str):
    df = pd.read_csv(StringIO(csv_str))

    # Detect numeric columns (assumed to be marks)
    mark_columns = df.select_dtypes(include='number').columns

    # Add Total and Average marks
    df['Total'] = df[mark_columns].sum(axis=1)
    df['Average'] = df[mark_columns].mean(axis=1)

    return df

# ---------- Main app ----------
def main():
    st.set_page_config(page_title="Student Marks Analyzer", layout="wide")
    st.title("Student Marks Analyzer ")

    uploaded_file = st.file_uploader("Upload your student marks table (CSV or Excel)", type=["csv", "xlsx"])

    if uploaded_file is not None:
        # Read uploaded file
        if uploaded_file.name.endswith('.csv'):
            df = pd.read_csv(uploaded_file)
        else:
            df = pd.read_excel(uploaded_file)

        st.subheader("Uploaded Data")
        st.dataframe(df)

        # Convert DataFrame to CSV string and process
        csv_data = df.to_csv(index=False)
        processed_df = process_csv_data(csv_data)

        st.subheader("Processed Data (Total & Average)")
        st.dataframe(processed_df)

        # ---------- Analyze individual student ----------
        st.subheader(" Analyze Individual Student")
        student_column = processed_df.columns[0]  # Assuming first column is student name or ID
        student_list = processed_df[student_column].tolist()
        selected_student = st.selectbox("Select a student", student_list)

        student_data = processed_df[processed_df[student_column] == selected_student]
        st.write(f"Details for *{selected_student}*")
        st.dataframe(student_data)

        # ---------- Low-performing students ----------
        st.subheader(" Students with Low Average (Avg < 40)")
        low_students = processed_df[processed_df['Average'] < 40]
        st.dataframe(low_students)

        # ---------- Lagging students (fail in any subject) ----------
        st.subheader("🐢 Lagging Students (Any subject mark < 35)")
        mark_columns = processed_df.select_dtypes(include='number').drop(columns=['Total', 'Average'])
        lagging_mask = (mark_columns < 35).any(axis=1)
        lagging_students = processed_df[lagging_mask]
        st.dataframe(lagging_students)

        # ---------- Data visualizations ----------
        st.subheader(" Overall Data Visualizations")
        col1, col2 = st.columns(2)

        with col1:
            st.markdown("###  Total Marks Distribution")
            fig1, ax1 = plt.subplots()
            sns.histplot(processed_df['Total'], bins=10, kde=True, ax=ax1)
            ax1.set_xlabel("Total Marks")
            st.pyplot(fig1)

        with col2:
            st.markdown("###  Average Marks per Student")
            fig2, ax2 = plt.subplots(figsize=(10, 5))
            sns.barplot(x=processed_df[student_column], y=processed_df['Average'], ax=ax2)
            ax2.set_xlabel("Student")
            ax2.set_ylabel("Average Marks")
            ax2.set_xticklabels(ax2.get_xticklabels(), rotation=45, ha='right')
            st.pyplot(fig2)

        # ---------- Scatter plot ----------
        st.subheader(" Scatter Plot: Total vs Average")
        fig3, ax3 = plt.subplots()
        sns.scatterplot(data=processed_df, x='Total', y='Average', hue=student_column, ax=ax3)
        ax3.set_title("Total vs Average Marks")
        st.pyplot(fig3)

        # ---------- Box plot ----------
        st.subheader(" Box Plot of Marks (Subject-wise Spread)")
        numeric_columns = processed_df.select_dtypes(include='number').drop(columns=['Total', 'Average'])
        df_box = pd.melt(processed_df, id_vars=[student_column], value_vars=numeric_columns.columns,
                         var_name="Subject", value_name="Marks")
        fig4, ax4 = plt.subplots()
        sns.boxplot(x="Subject", y="Marks", data=df_box, ax=ax4)
        ax4.set_title("Subject-wise Marks Distribution")
        st.pyplot(fig4)

if __name__ == "__main__":
    main()