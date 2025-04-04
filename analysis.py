import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from io import BytesIO
import io
import plotly.express as px


def load_data(file):
    if file is None:
        return None
    try:
        if file.name.endswith(".csv"):
            return pd.read_csv(file)
        elif file.name.endswith(".xlsx"):
            return pd.read_excel(file, engine='openpyxl')
        elif file.name.endswith(".json"):
            return pd.read_json(file)
        else:
            st.error("Неподдерживаемый формат файла. Пожалуйста, загрузите CSV, Excel или JSON.")
            return None
    except Exception as e:
        st.error(f"Ошибка при загрузке данных: {str(e)}")
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

    try:
        if chart_type == "Гистограмма":
            fig, ax = plt.subplots()
            sns.histplot(df[column], bins=20, kde=True, ax=ax)
            ax.set_xlabel(column)
            ax.set_ylabel("Частота")
            ax.set_title(f"Гистограмма: {column}")
            st.pyplot(fig)

        elif chart_type == "Линейный график":
            fig, ax = plt.subplots()
            ax.plot(df[column])
            ax.set_xlabel("Индекс")
            ax.set_ylabel(column)
            ax.set_title(f"Линейный график: {column}")
            st.pyplot(fig)

        elif chart_type == "Круговая диаграмма":
            value_counts = df[column].value_counts()
            if len(value_counts) <= 10:
                fig, ax = plt.subplots()
                value_counts.plot.pie(autopct='%1.1f%%', ax=ax)
                ax.set_title(f"Круговая диаграмма: {column}")
                st.pyplot(fig)
            else:
                st.warning("Слишком много уникальных значений для круговой диаграммы!")

        elif chart_type == "Ящик с усами (Boxplot)":
            fig = px.box(df, y=column, points="all", hover_data=df.columns)
            st.plotly_chart(fig)

            q1 = df[column].quantile(0.25)
            q3 = df[column].quantile(0.75)
            iqr = q3 - q1
            outliers = df[(df[column] < (q1 - 1.5 * iqr)) | (df[column] > (q3 + 1.5 * iqr))]

            if not outliers.empty:
                st.write("**Выбросы в данных:**")
                st.dataframe(outliers)

        elif chart_type == "Точечная диаграмма (Scatter Plot)":
            fig, ax = plt.subplots()
            sns.scatterplot(x=df[x_col], y=df[y_col], ax=ax)
            ax.set_xlabel(x_col)
            ax.set_ylabel(y_col)
            ax.set_title(f"Точечная диаграмма: {x_col} vs {y_col}")
            st.pyplot(fig)

        elif chart_type == "Тепловая карта плотности":
            fig, ax = plt.subplots()
            sns.kdeplot(x=df[x_col], y=df[y_col], cmap="Blues", fill=True, ax=ax)
            ax.set_xlabel(x_col)
            ax.set_ylabel(y_col)
            ax.set_title(f"Тепловая карта плотности: {x_col} vs {y_col}")
            st.pyplot(fig)

        elif chart_type == "Тепловая карта корреляции":
            fig, ax = plt.subplots(figsize=(10, 6))
            sns.heatmap(df.corr(), annot=True, cmap="coolwarm", fmt=".2f", ax=ax)
            ax.set_title("Тепловая карта корреляции")
            st.pyplot(fig)

        # Сохранение графика в буфер и добавление кнопки скачивания
        buf = BytesIO()
        if chart_type == "Ящик с усами (Boxplot)":
            fig.write_image(buf, format="png")
        else:
            fig.savefig("graph.png")  # Сохранение для matplotlib
        buf.seek(0)
        st.download_button(label="💾 Скачать график", data=buf, file_name="chart.png", mime="image/png")

    except Exception as e:
        st.error(f"Ошибка при построении графика: {str(e)}")
