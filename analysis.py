import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns


def load_data(file):
    if file is None:
        return None
    if file.name.endswith(".csv"):
        return pd.read_csv(file)
    elif file.name.endswith(".xlsx"):
        return pd.read_excel(file, engine='openpyxl')
    elif file.name.endswith(".json"):
        return pd.read_json(file)
    else:
        st.error("Неподдерживаемый формат файла. Пожалуйста, загрузите CSV, Excel или JSON.")
        return None


st.title("📊 Интерактивный анализ данных")
uploaded_file = st.file_uploader("Загрузите файл", type=["csv", "xlsx", "json"])

df = load_data(uploaded_file)

if df is not None:
    numeric_columns = df.select_dtypes(include=['number']).columns.tolist()
    selected_columns = st.multiselect("Выберите столбцы для анализа", numeric_columns, default=numeric_columns)

    if not selected_columns:
        st.warning("Выберите хотя бы один столбец!")
    else:
        df = df[selected_columns]


if uploaded_file:
    if df is not None:
        st.write("### Просмотр данных:")
        st.dataframe(df.head())

        st.write("### Базовая статистика:")
        st.write(df.describe())

        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button(label="💾 Скачать обработанные данные",
                           data=csv,
                           file_name="processed_data.csv",
                           mime="text/csv")

        st.write("### Выбор графика:")
        chart_type = st.selectbox("Выберите тип графика", ["Гистограмма", "Линейный график", "Круговая диаграмма"])
        column = st.selectbox("Выберите колонку", df.select_dtypes(include=['number']).columns)

        plt.figure(figsize=(8, 5))
        if chart_type == "Гистограмма":
            sns.histplot(df[column], bins=20, kde=True)
        elif chart_type == "Линейный график":
            plt.plot(df[column])
        elif chart_type == "Круговая диаграмма":
            df[column].value_counts().plot.pie(autopct='%1.1f%%')

        st.pyplot(plt)
