# test_app.py
import unittest
import pandas as pd
from app import filter_and_sort_places

class TestFilterAndSortPlaces(unittest.TestCase):

    def setUp(self):
        """Создаём тестовый DataFrame"""
        self.df = pd.DataFrame({
            'category': ['Кафе', 'Ресторан', 'Бар', 'Кафе', 'Пекарня'],
            'district': ['Центр', 'Арбат', 'Центр', 'Тверской', 'Арбат'],
            'seats': [30, 80, 50, 40, 20],
            'rating': [4.2, 4.8, 3.9, 4.5, None],
            'name': ['Кофемания', 'Гастрономика', 'Пинта', 'Уголёк', 'Хлебница']
        })

    def test_no_filters_returns_all_sorted(self):
        result = filter_and_sort_places(self.df)
        self.assertEqual(len(result), 5)
        # Проверяем, что сортировка по рейтингу убывающая
        ratings = result['rating'].dropna().tolist()
        self.assertEqual(ratings, sorted(ratings, reverse=True))

    def test_filter_by_category(self):
        result = filter_and_sort_places(self.df, type_input="Кафе")
        self.assertEqual(len(result), 2)
        self.assertTrue(all(result['category'] == 'Кафе'))

    def test_filter_by_district(self):
        result = filter_and_sort_places(self.df, district_input="Арбат")
        self.assertEqual(len(result), 2)
        self.assertTrue(all(result['district'] == 'Арбат'))

    def test_filter_by_seats(self):
        result = filter_and_sort_places(self.df, seats_input="80")
        self.assertEqual(len(result), 1)
        self.assertEqual(result.iloc[0]['seats'], 80)

    def test_invalid_seats_returns_empty(self):
        result = filter_and_sort_places(self.df, seats_input="abc")
        self.assertTrue(result.empty)

    def test_combined_filters(self):
        result = filter_and_sort_places(self.df, type_input="Кафе", district_input="Центр")
        self.assertEqual(len(result), 1)
        self.assertEqual(result.iloc[0]['name'], 'Кофемания')

    def test_sorting_with_nan_rating(self):
        result = filter_and_sort_places(self.df)
        # Убеждаемся, что заведение без рейтинга — последнее
        self.assertTrue(pd.isna(result.iloc[-1]['rating']))


if __name__ == '__main__':
    unittest.main()
    