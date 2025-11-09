# app.py
import streamlit as st
import pandas as pd
import os

# Константы
CSV_FILE = "/Users/mikhailsuvaev/Documents/GitHub/ucheba/app/data/moscow_places.csv"
COL_DISTRICT = 'district'
COL_CATEGORY = 'category'
COL_SEATS = 'seats'
COL_RATING = 'rating'
COL_NAME = 'name'

DISPLAY_COLUMNS = {
    COL_NAME: "Название",
    COL_CATEGORY: "Тип заведения",
    COL_DISTRICT: "Район",
    COL_SEATS: "Места",
    COL_RATING: "Рейтинг",
}

# --- ЛОГИКА ФИЛЬТРАЦИИ И СОРТИРОВКИ ---
def filter_and_sort_places(df, type_input="", district_input="", seats_input=""):
    """
    Фильтрует и сортирует DataFrame с заведениями.
    Возвращает отфильтрованный и отсортированный по рейтингу DataFrame.
    """
    filtered_df = df.copy()

    if type_input.strip():
        filtered_df = filtered_df[
            filtered_df[COL_CATEGORY].astype(str).str.contains(type_input.strip(), case=False, na=False)
        ]

    if district_input.strip():
        filtered_df = filtered_df[
            filtered_df[COL_DISTRICT].astype(str).str.contains(district_input.strip(), case=False, na=False)
        ]

    if seats_input.strip():
        try:
            seats_value = int(seats_input.strip())
            filtered_df = filtered_df[filtered_df[COL_SEATS] == seats_value]
        except ValueError:
            # Возвращаем пустой DataFrame при ошибке
            return filtered_df.iloc[0:0]

    # Сортировка по рейтингу (лучшие — сверху)
    filtered_df = filtered_df.sort_values(by=COL_RATING, ascending=False, na_position='last')
    return filtered_df


# --- STREAMLIT ИНТЕРФЕЙС ---
def main():
    st.title("Поиск заведений в Москве")

    if not os.path.exists(CSV_FILE):
        st.error(f"Файл не найден: {CSV_FILE}")
        st.stop()

    try:
        df = pd.read_csv(CSV_FILE)
    except Exception as e:
        st.error(f"Ошибка при чтении файла: {e}")
        st.stop()

    required_cols = [COL_DISTRICT, COL_CATEGORY, COL_SEATS, COL_RATING]
    if not all(col in df.columns for col in required_cols):
        st.error(f"В файле должны быть колонки: {', '.join(required_cols)}")
        st.stop()

    df[COL_SEATS] = pd.to_numeric(df[COL_SEATS], errors="coerce")
    df[COL_RATING] = pd.to_numeric(df[COL_RATING], errors="coerce")

    with st.form(key="search_form"):
        col1, col2 = st.columns(2)
        with col1:
            type_input = st.text_input("Тип заведения")
            district_input = st.text_input("Район")
        with col2:
            seats_input = st.text_input("Количество мест")
        submit_button = st.form_submit_button("Показать")

    if submit_button:
        result_df = filter_and_sort_places(df, type_input, district_input, seats_input)

        # Выбор колонок для отображения
        available_cols = [col for col in DISPLAY_COLUMNS.keys() if col in result_df.columns]
        if available_cols:
            result_df = result_df[available_cols].rename(columns=DISPLAY_COLUMNS)

        if not result_df.empty:
            st.write(f"Найдено заведений: {len(result_df)}")
            st.dataframe(result_df.reset_index(drop=True))
        else:
            st.write("Ничего не найдено по вашему запросу.")


if __name__ == "__main__":
    main()