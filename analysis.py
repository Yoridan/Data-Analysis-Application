import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from io import BytesIO


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

if uploaded_file and df is not None:
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
    chart_type = st.selectbox("Выберите тип графика", [
        "Гистограмма", "Линейный график", "Круговая диаграмма",
        "Ящик с усами (Boxplot)", "Точечная диаграмма (Scatter Plot)",
        "Тепловая карта плотности", "Тепловая карта корреляции"
    ])

    numeric_columns = df.select_dtypes(include=['number']).columns.tolist()

    if chart_type in ["Гистограмма", "Линейный график", "Круговая диаграмма", "Ящик с усами (Boxplot)"]:
        column = st.selectbox("Выберите колонку", numeric_columns)

    elif chart_type in ["Точечная диаграмма (Scatter Plot)", "Тепловая карта плотности"]:
        x_col = st.selectbox("Выберите параметр для X", numeric_columns)
        y_col = st.selectbox("Выберите параметр для Y", numeric_columns)

    plt.figure(figsize=(8, 5))

    if chart_type == "Гистограмма":
        sns.histplot(df[column], bins=20, kde=True)
        plt.xlabel(column)
        plt.ylabel("Частота")
        plt.title(f"Гистограмма: {column}")

    elif chart_type == "Линейный график":
        plt.plot(df[column])
        plt.xlabel("Индекс")
        plt.ylabel(column)
        plt.title(f"Линейный график: {column}")

    elif chart_type == "Круговая диаграмма":
        value_counts = df[column].value_counts()
        if len(value_counts) <= 10:  # Ограничение по количеству значений
            value_counts.plot.pie(autopct='%1.1f%%')
            plt.title(f"Круговая диаграмма: {column}")
        else:
            st.warning("Слишком много уникальных значений для круговой диаграммы!")

    elif chart_type == "Ящик с усами (Boxplot)":
        sns.boxplot(y=df[column])
        plt.ylabel(column)
        plt.title(f"Ящик с усами: {column}")

    elif chart_type == "Точечная диаграмма (Scatter Plot)":
        sns.scatterplot(x=df[x_col], y=df[y_col])
        plt.xlabel(x_col)
        plt.ylabel(y_col)
        plt.title(f"Точечная диаграмма: {x_col} vs {y_col}")

    elif chart_type == "Тепловая карта плотности":
        sns.kdeplot(x=df[x_col], y=df[y_col], cmap="Blues", fill=True)
        plt.xlabel(x_col)
        plt.ylabel(y_col)
        plt.title(f"Тепловая карта плотности: {x_col} vs {y_col}")

    elif chart_type == "Тепловая карта корреляции":
        plt.figure(figsize=(10, 6))
        sns.heatmap(df.corr(), annot=True, cmap="coolwarm", fmt=".2f")
        plt.title("Тепловая карта корреляции")

    st.pyplot(plt)

    buf = BytesIO()
    plt.savefig(buf, format="png")
    buf.seek(0)
    st.download_button(label="💾 Скачать график", data=buf, file_name="chart.png", mime="image/png")
