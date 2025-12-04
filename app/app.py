import streamlit as st
import pandas as pd
import os

# Путь к CSV-файлу — относительно файла test_app.py
CSV_FILE  = os.path.join(os.path.dirname(__file__), "..", "data", "moscow_places.csv")

# Колонки в вашем CSV
COL_NAME = 'name'
COL_CATEGORY = 'category'
COL_ADDRESS = 'address'
COL_DISTRICT = 'district'
COL_HOURS = 'hours'
COL_LAT = 'lat'      # Широта
COL_LNG = 'lng'      # Долгота
COL_RATING = 'rating'
COL_SEATS = 'seats'

# --- Настройка страницы ---
st.set_page_config(
    page_title="🍽️ Поиск заведений в Москве",
    page_icon="🗺️",
    layout="wide"
)

# Кастомный CSS
st.markdown("""
<style>
    .main { background-color: #f9f9fb; }
    .stButton>button {
        background-color: #4CAF50;
        color: white;
        border: none;
        padding: 10px 20px;
        font-size: 16px;
        border-radius: 8px;
        width: 100%;
    }
    .map-section {
        margin-top: 20px;
        padding-top: 15px;
        border-top: 1px solid #eee;
    }
    .result-card {
        background: white;
        padding: 16px;
        border-radius: 12px;
        margin-bottom: 12px;
        box-shadow: 0 2px 6px rgba(0,0,0,0.1);
        border-left: 4px solid #4CAF50;
    }
    .result-title {
        font-size: 20px;
        font-weight: bold;
        color: #2c3e50;
        margin-bottom: 6px;
    }
    .result-row {
        display: flex;
        justify-content: space-between;
        font-size: 14px;
        color: #555;
    }
    .map-badge {
        font-size: 12px;
        padding: 2px 8px;
        border-radius: 10px;
        color: white;
    }
    .map-badge--yes {
        background-color: #4CAF50;
    }
    .map-badge--no {
        background-color: #ff9800;
    }
</style>
""", unsafe_allow_html=True)

# --- Функция фильтрации ---
def filter_and_sort_places(df, categories_list, districts_list, seats_min=None, rating_min=0.0):
    filtered_df = df.copy()

    # Фильтр по типу заведения (несколько значений)
    if categories_list and len(categories_list) > 0:
        filtered_df = filtered_df[
            filtered_df[COL_CATEGORY].isin(categories_list)
        ]

    # Фильтр по округу (несколько значений)
    if districts_list and len(districts_list) > 0:
        filtered_df = filtered_df[
            filtered_df[COL_DISTRICT].isin(districts_list)
        ]

    # Минимум мест
    if seats_min is not None and seats_min > 0:
        filtered_df = filtered_df[filtered_df[COL_SEATS] >= seats_min]

    # Минимальный рейтинг
    if rating_min > 0:
        filtered_df = filtered_df[filtered_df[COL_RATING] >= rating_min]

    # Сортировка: рейтинг (↓) → название (↑)
    filtered_df = filtered_df.sort_values(
        by=[COL_RATING, COL_NAME],
        ascending=[False, True],
        na_position='last'
    )
    return filtered_df

# --- Основная функция ---
def main():
    st.title("🍽️ Поиск заведений в Москве")
    st.markdown("Выберите фильтры — карта и результаты появятся ниже.")

    # Проверка файла
    if not os.path.exists(CSV_FILE):
        st.error(f"Файл не найден: `{CSV_FILE}`")
        st.stop()

    try:
        df = pd.read_csv(CSV_FILE)
    except Exception as e:
        st.error(f"Ошибка при чтении файла: {e}")
        st.stop()

    # Проверка обязательных колонок
    required_cols = [COL_NAME, COL_CATEGORY, COL_DISTRICT, COL_SEATS, COL_RATING, COL_LAT, COL_LNG]
    if not all(col in df.columns for col in required_cols):
        st.error(f"В файле должны быть колонки: {', '.join(required_cols)}")
        st.stop()

    # Приведение типов
    df[COL_SEATS] = pd.to_numeric(df[COL_SEATS], errors="coerce").fillna(0).astype(int)
    df[COL_RATING] = pd.to_numeric(df[COL_RATING], errors="coerce")

    # Уникальные значения
    all_categories = sorted(df[COL_CATEGORY].dropna().unique())
    all_districts = sorted(df[COL_DISTRICT].dropna().unique())

    # --- ФОРМА ПОИСКА ---
    with st.form(key="search_form"):
        col1, col2 = st.columns(2)

        with col1:
            selected_categories = st.multiselect(
                "Тип заведения",
                options=all_categories,
                default=[]
            )
            selected_districts = st.multiselect(
                "Округ",
                options=all_districts,
                default=[]
            )

        with col2:
            min_seats = st.number_input("Минимум мест", min_value=0, value=0, step=1)
            rating_min = st.slider("Минимальный рейтинг", 0.0, 5.0, 3.0, 0.1)

        submit_button = st.form_submit_button("🔍 Найти заведения")

    # --- ОБРАБОТКА ЗАПРОСА ---
    if submit_button:
        result_df = filter_and_sort_places(
            df,
            categories_list=selected_categories,
            districts_list=selected_districts,
            seats_min=min_seats if min_seats > 0 else None,
            rating_min=rating_min
        )

        if result_df.empty:
            st.warning("📭 Ничего не найдено. Попробуйте ослабить фильтры.")
        else:
            st.success(f"✅ Найдено {len(result_df)} заведений")

            # --- КАРТА СВЕРХУ (только для объектов с координатами) ---
            map_data = result_df.dropna(subset=[COL_LAT, COL_LNG]).copy()
            if not map_data.empty:
                st.markdown('<div class="map-section"><h3>📍 Карта найденных заведений</h3></div>', unsafe_allow_html=True)
                st.map(map_data[[COL_LAT, COL_LNG]].rename(columns={COL_LAT: 'lat', COL_LNG: 'lon'}))
            else:
                st.info("📌 У найденных заведений нет координат для отображения на карте.")

            # --- РЕЗУЛЬТАТЫ В КАРТОЧКАХ ---
            st.markdown("### Результаты поиска")
            for _, row in result_df.iterrows():
                name = row.get(COL_NAME, "Без названия")
                category = row.get(COL_CATEGORY, "—")
                district = row.get(COL_DISTRICT, "—")
                seats = row.get(COL_SEATS, "—")
                rating = row.get(COL_RATING, None)
                rating_display = f"⭐ {rating:.1f}" if pd.notna(rating) else "—"

                # Проверка координат
                lat = row.get(COL_LAT)
                lng = row.get(COL_LNG)
                has_location = pd.notna(lat) and pd.notna(lng)

                map_badge = (
                    '<span class="map-badge map-badge--yes">📍 На карте</span>'
                    if has_location else
                    '<span class="map-badge map-badge--no">— Нет метки на карте</span>'
                )

                st.markdown(f"""
                <div class="result-card">
                    <div class="result-title">{name}</div>
                    <div class="result-row">
                        <span><b>Тип:</b> {category}</span>
                        <span><b>Округ:</b> {district}</span>
                    </div>
                    <div class="result-row">
                        <span><b>Места:</b> {seats}</span>
                        <span><b>Рейтинг:</b> {rating_display}</span>
                    </div>
                    <div style="margin-top: 8px;">{map_badge}</div>
                </div>
                """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()