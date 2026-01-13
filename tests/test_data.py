"""
Тесты для модуля справочных данных.
"""
import pytest
from src.data import (
    GAMMA_E_DATA,
    GAMMA_T_NORMAL_STRENGTH,
    GAMMA_T_INCREASED_STRENGTH,
    GAMMA_T_HIGH_STRENGTH,
    RYN_TABLE,
    get_gamma_t_table,
    interpolate,
    get_critical_temp,
    get_ryn
)


class TestGammaData:
    """Тесты для проверки структуры данных температурных коэффициентов."""

    def test_gamma_e_data_structure(self):
        """Проверка структуры GAMMA_E_DATA."""
        assert isinstance(GAMMA_E_DATA, dict)
        assert 20 in GAMMA_E_DATA
        assert 800 in GAMMA_E_DATA
        assert GAMMA_E_DATA[20] == 1.0

    def test_gamma_t_normal_strength_structure(self):
        """Проверка структуры GAMMA_T_NORMAL_STRENGTH."""
        assert isinstance(GAMMA_T_NORMAL_STRENGTH, dict)
        assert 20 in GAMMA_T_NORMAL_STRENGTH
        assert 800 in GAMMA_T_NORMAL_STRENGTH
        assert GAMMA_T_NORMAL_STRENGTH[20] == 1.0

    def test_gamma_t_increased_strength_structure(self):
        """Проверка структуры GAMMA_T_INCREASED_STRENGTH."""
        assert isinstance(GAMMA_T_INCREASED_STRENGTH, dict)
        assert 20 in GAMMA_T_INCREASED_STRENGTH
        assert GAMMA_T_INCREASED_STRENGTH[20] == 1.0

    def test_gamma_t_high_strength_structure(self):
        """Проверка структуры GAMMA_T_HIGH_STRENGTH."""
        assert isinstance(GAMMA_T_HIGH_STRENGTH, dict)
        assert 20 in GAMMA_T_HIGH_STRENGTH
        assert GAMMA_T_HIGH_STRENGTH[20] == 1.0

    def test_gamma_values_decreasing(self):
        """Проверка, что коэффициенты убывают с температурой."""
        temps = sorted(GAMMA_T_NORMAL_STRENGTH.keys())
        for i in range(len(temps) - 1):
            t1, t2 = temps[i], temps[i + 1]
            g1, g2 = GAMMA_T_NORMAL_STRENGTH[t1], GAMMA_T_NORMAL_STRENGTH[t2]
            assert g1 >= g2, f"Gamma должен убывать: T={t1}°C -> {t2}°C, но {g1} < {g2}"


class TestGetGammaTTable:
    """Тесты для функции get_gamma_t_table."""

    def test_normal_strength_steel(self):
        """Проверка выбора таблицы для стали обычной прочности."""
        table = get_gamma_t_table("C235")
        assert table == GAMMA_T_NORMAL_STRENGTH

        table = get_gamma_t_table("C245")
        assert table == GAMMA_T_NORMAL_STRENGTH

        table = get_gamma_t_table("C255")
        assert table == GAMMA_T_NORMAL_STRENGTH

    def test_increased_strength_steel(self):
        """Проверка выбора таблицы для стали повышенной прочности."""
        table = get_gamma_t_table("C345")
        assert table == GAMMA_T_INCREASED_STRENGTH

        table = get_gamma_t_table("C345K")
        assert table == GAMMA_T_INCREASED_STRENGTH

        table = get_gamma_t_table("C355")
        assert table == GAMMA_T_INCREASED_STRENGTH

    def test_high_strength_steel(self):
        """Проверка выбора таблицы для стали высокой прочности."""
        table = get_gamma_t_table("C390")
        assert table == GAMMA_T_HIGH_STRENGTH

        table = get_gamma_t_table("C440")
        assert table == GAMMA_T_HIGH_STRENGTH

    def test_cyrillic_steel_grades(self):
        """Проверка работы с кириллическими обозначениями."""
        table = get_gamma_t_table("С235")  # Кириллица
        assert table == GAMMA_T_NORMAL_STRENGTH

        table = get_gamma_t_table("С345")  # Кириллица
        assert table == GAMMA_T_INCREASED_STRENGTH


class TestInterpolate:
    """Тесты для функции линейной интерполяции."""

    def test_linear_interpolation(self):
        """Проверка линейной интерполяции."""
        result = interpolate(25, 20, 1.0, 30, 0.8)
        expected = 1.0 + (25 - 20) * (0.8 - 1.0) / (30 - 20)
        assert abs(result - expected) < 0.001

    def test_interpolation_at_bounds(self):
        """Проверка интерполяции на границах."""
        result = interpolate(20, 20, 1.0, 30, 0.8)
        assert result == 1.0

        result = interpolate(30, 20, 1.0, 30, 0.8)
        assert result == 0.8

    def test_interpolation_equal_x(self):
        """Проверка при равных x1 и x2."""
        result = interpolate(25, 20, 1.0, 20, 0.8)
        assert result == 1.0  # Должна вернуть y1


class TestGetCriticalTemp:
    """Тесты для функции определения критической температуры."""

    def test_gamma_t_one(self):
        """Проверка при gamma_t = 1.0."""
        result = get_critical_temp(1.0, "C245")
        assert result["value"] == 20.0

    def test_gamma_t_greater_than_one(self):
        """Проверка при gamma_t > 1.0."""
        result = get_critical_temp(1.5, "C245")
        assert result["value"] == 20.0

    def test_gamma_t_zero(self):
        """Проверка при gamma_t = 0."""
        result = get_critical_temp(0.0, "C245")
        assert result["value"] == 800  # Максимальная температура в таблице

    def test_gamma_t_interpolation(self):
        """Проверка интерполяции критической температуры."""
        # Для C245 при gamma_t = 0.84 (точное значение при 300°C)
        result = get_critical_temp(0.84, "C245")
        assert abs(result["value"] - 300.0) < 1.0

    def test_gamma_t_between_values(self):
        """Проверка интерполяции между табличными значениями."""
        # Для C245 gamma_t при 300°C = 0.84, при 350°C = 0.78
        # Среднее = 0.81 должно дать температуру ~325°C
        result = get_critical_temp(0.81, "C245")
        assert 300 < result["value"] < 350
        assert result["trace"] is not None

    def test_different_steel_grades(self):
        """Проверка для разных марок стали."""
        result_normal = get_critical_temp(0.7, "C245")
        result_increased = get_critical_temp(0.7, "C345")
        result_high = get_critical_temp(0.7, "C390")

        # Температуры должны отличаться для разных марок
        assert result_normal["value"] != result_high["value"]


class TestRynTable:
    """Тесты для таблицы нормативных сопротивлений."""

    def test_ryn_table_structure(self):
        """Проверка структуры RYN_TABLE."""
        assert isinstance(RYN_TABLE, dict)
        assert "C245" in RYN_TABLE
        assert "C345" in RYN_TABLE
        assert "C390" in RYN_TABLE

    def test_ryn_values_format(self):
        """Проверка формата значений в таблице."""
        for grade, data in RYN_TABLE.items():
            assert isinstance(data, list)
            for thickness, value in data:
                assert isinstance(thickness, (int, float))
                assert isinstance(value, (int, float))
                assert value > 0


class TestGetRyn:
    """Тесты для функции получения нормативного сопротивления."""

    def test_c245_thin(self):
        """Проверка Ryn для C245 при малой толщине."""
        ryn = get_ryn("C245", 15)
        assert ryn == 245

    def test_c245_medium(self):
        """Проверка Ryn для C245 при средней толщине."""
        ryn = get_ryn("C245", 30)
        assert ryn == 235

    def test_c345_thin(self):
        """Проверка Ryn для C345 при малой толщине."""
        ryn = get_ryn("C345", 8)
        assert ryn == 345

    def test_c345_thick(self):
        """Проверка Ryn для C345 при большой толщине."""
        ryn = get_ryn("C345", 35)
        assert ryn == 305

    def test_thickness_exceeds_table(self):
        """Проверка при толщине, превышающей табличные значения."""
        # Должно вернуть последнее значение из таблицы
        ryn = get_ryn("C345", 100)
        assert ryn == 305  # Последнее значение для C345

    def test_unknown_grade(self):
        """Проверка для неизвестной марки стали."""
        ryn = get_ryn("C999", 10)
        # Должно вернуть fallback значение
        assert isinstance(ryn, float)
        assert ryn > 0

    def test_cyrillic_grade(self):
        """Проверка с кириллическим обозначением."""
        ryn = get_ryn("С245", 15)  # Кириллица
        assert ryn == 245
