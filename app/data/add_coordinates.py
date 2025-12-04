import pandas as pd
from geopy.geocoders import Nominatim
from geopy.extra.rate_limiter import RateLimiter
import time
import os

# Путь к вашему файлу
CSV_FILE = "/Users/mikhailsuvaev/Documents/GitHub/ucheba/app/data/moscow_places.csv"
OUTPUT_FILE = CSV_FILE.replace(".csv", "_with_coords.csv")

# Загрузка данных
df = pd.read_csv(CSV_FILE)

# Инициализация геокодера (с ограничением — 1 запрос в секунду)
geolocator = Nominatim(user_agent="moscow_places_geocoder")
geocode = RateLimiter(geolocator.geocode, min_delay_seconds=1)

# Добавим колонки, если их нет
if 'lat' not in df.columns:
    df['lat'] = None
if 'lng' not in df.columns:
    df['lng'] = None

# Функция для получения координат по адресу
def get_coords(address):
    if pd.isna(address) or address.strip() == "":
        return None, None
    try:
        location = geocode(f"{address}, Москва, Россия")
        if location:
            return location.latitude, location.longitude
    except Exception as e:
        print(f"Ошибка при обработке адреса '{address}': {e}")
    return None, None

# Заполняем только пустые координаты
total = len(df)
filled = 0

for idx, row in df.iterrows():
    if pd.isna(row.get('lat')) or pd.isna(row.get('lng')):
        lat, lng = get_coords(row['address'])
        df.at[idx, 'lat'] = lat
        df.at[idx, 'lng'] = lng
        if lat is not None and lng is not None:
            filled += 1
        print(f"[{idx+1}/{total}] Обработан: {row['name']} → ({lat}, {lng})")
        time.sleep(1)  # уважаем API

# Сохраняем результат
df.to_csv(OUTPUT_FILE, index=False, encoding='utf-8')
print(f"\n✅ Готово! Файл сохранён: {OUTPUT_FILE}")
print(f"Добавлено координат: {filled} из {total}")