"""
Тесты для модуля теплотехнического расчета.
"""
import pytest
import math
from src.thermal import (
    standard_fire_curve,
    calc_section_factor,
    calc_heated_perimeter_ibeam,
    calc_heated_perimeter_rect_tube,
    calc_heated_perimeter_channel,
    calc_heated_perimeter_circ_tube,
    calc_steel_temperature_step_custom,
    calculate_fire_resistance
)


class TestStandardFireCurve:
    """Тесты для стандартной температурной кривой пожара."""

    def test_initial_temperature(self):
        """Проверка начальной температуры (t=0)."""
        temp = standard_fire_curve(0)
        # При t=0: 345*log10(1) + 293 = 345*0 + 293 = 293 K
        assert abs(temp - 293.0) < 0.1

    def test_temperature_at_60_sec(self):
        """Проверка температуры через 1 минуту."""
        temp = standard_fire_curve(60)
        # 345*log10((8*60/60) + 1) + 293 = 345*log10(9) + 293
        expected = 345.0 * math.log10(9) + 293.0
        assert abs(temp - expected) < 0.1

    def test_temperature_increasing(self):
        """Проверка, что температура возрастает со временем."""
        temp_0 = standard_fire_curve(0)
        temp_60 = standard_fire_curve(60)
        temp_300 = standard_fire_curve(300)

        assert temp_60 > temp_0
        assert temp_300 > temp_60

    def test_temperature_at_30_min(self):
        """Проверка температуры через 30 минут."""
        temp = standard_fire_curve(30 * 60)
        # Должна быть > 800°C (>1073 K)
        assert temp > 1073


class TestSectionFactor:
    """Тесты для расчета приведенной толщины металла."""

    def test_section_factor_normal(self):
        """Проверка расчета приведенной толщины."""
        area = 5000  # мм²
        perimeter = 500  # мм
        factor = calc_section_factor(perimeter, area)
        expected = area / perimeter  # = 10 мм
        assert abs(factor - expected) < 0.01

    def test_section_factor_zero_perimeter(self):
        """Проверка при нулевом периметре."""
        factor = calc_section_factor(0, 5000)
        assert factor == 0


class TestHeatedPerimeterIbeam:
    """Тесты для расчета обогреваемого периметра двутавра."""

    def test_ibeam_4_sides(self, sample_ibeam_params):
        """Проверка расчета для обогрева с 4 сторон."""
        h = sample_ibeam_params["h_mm"]
        b = sample_ibeam_params["b_mm"]
        tw = sample_ibeam_params["tw_mm"]

        perimeter = calc_heated_perimeter_ibeam(h, b, tw, 10, exposure="4_sides")
        expected = 2 * h + 4 * b - 2 * tw
        assert abs(perimeter - expected) < 0.1

    def test_ibeam_3_sides(self, sample_ibeam_params):
        """Проверка расчета для обогрева с 3 сторон."""
        h = sample_ibeam_params["h_mm"]
        b = sample_ibeam_params["b_mm"]
        tw = sample_ibeam_params["tw_mm"]

        perimeter = calc_heated_perimeter_ibeam(h, b, tw, 10, exposure="3_sides")
        expected = 2 * h + 3 * b - 2 * tw
        assert abs(perimeter - expected) < 0.1

    def test_ibeam_3_sides_less_than_4_sides(self, sample_ibeam_params):
        """Проверка, что периметр для 3 сторон меньше, чем для 4."""
        h = sample_ibeam_params["h_mm"]
        b = sample_ibeam_params["b_mm"]
        tw = sample_ibeam_params["tw_mm"]

        p4 = calc_heated_perimeter_ibeam(h, b, tw, 10, exposure="4_sides")
        p3 = calc_heated_perimeter_ibeam(h, b, tw, 10, exposure="3_sides")

        assert p3 < p4


class TestHeatedPerimeterRectTube:
    """Тесты для расчета обогреваемого периметра прямоугольной трубы."""

    def test_rect_tube_4_sides(self, sample_rect_tube_params):
        """Проверка расчета для обогрева с 4 сторон."""
        h = sample_rect_tube_params["h_mm"]
        b = sample_rect_tube_params["b_mm"]

        perimeter = calc_heated_perimeter_rect_tube(h, b, exposure="4_sides")
        expected = 2 * (h + b)
        assert abs(perimeter - expected) < 0.1

    def test_rect_tube_3_sides(self, sample_rect_tube_params):
        """Проверка расчета для обогрева с 3 сторон."""
        h = sample_rect_tube_params["h_mm"]
        b = sample_rect_tube_params["b_mm"]

        perimeter = calc_heated_perimeter_rect_tube(h, b, exposure="3_sides")
        expected = 2 * h + b
        assert abs(perimeter - expected) < 0.1


class TestHeatedPerimeterChannel:
    """Тесты для расчета обогреваемого периметра швеллера."""

    def test_channel_4_sides(self, sample_ibeam_params):
        """Проверка расчета для обогрева с 4 сторон."""
        h = sample_ibeam_params["h_mm"]
        b = sample_ibeam_params["b_mm"]
        tw = sample_ibeam_params["tw_mm"]
        tf = sample_ibeam_params["tf_mm"]

        perimeter = calc_heated_perimeter_channel(h, b, tw, tf, exposure="4_sides")
        expected = 2 * h + 4 * b - 2 * tw
        assert abs(perimeter - expected) < 0.1

    def test_channel_3_sides(self, sample_ibeam_params):
        """Проверка расчета для обогрева с 3 сторон."""
        h = sample_ibeam_params["h_mm"]
        b = sample_ibeam_params["b_mm"]
        tw = sample_ibeam_params["tw_mm"]
        tf = sample_ibeam_params["tf_mm"]

        perimeter = calc_heated_perimeter_channel(h, b, tw, tf, exposure="3_sides")
        expected = 2 * h + 3 * b - 2 * tw
        assert abs(perimeter - expected) < 0.1


class TestHeatedPerimeterCircTube:
    """Тесты для расчета обогреваемого периметра круглой трубы."""

    def test_circ_tube_perimeter(self, sample_circ_tube_params):
        """Проверка расчета периметра круглой трубы."""
        d = sample_circ_tube_params["d_mm"]
        perimeter = calc_heated_perimeter_circ_tube(d)
        expected = math.pi * d
        assert abs(perimeter - expected) < 0.1


class TestSteelTemperatureStep:
    """Тесты для пошагового расчета температуры стали."""

    def test_temperature_step_no_heating(self):
        """Проверка при равных температурах газа и стали."""
        t_steel_prev = 500.0  # K
        t_gas = 500.0  # K
        dt = 1.0  # сек
        am_v = 100  # 1/м

        t_new, alpha = calc_steel_temperature_step_custom(t_steel_prev, t_gas, dt, am_v)

        # При одинаковых температурах изменение должно быть минимальным
        assert abs(t_new - t_steel_prev) < 1.0

    def test_temperature_step_heating(self):
        """Проверка нагрева стали."""
        t_steel_prev = 293.0  # K
        t_gas = 600.0  # K
        dt = 1.0  # сек
        am_v = 100  # 1/м

        t_new, alpha = calc_steel_temperature_step_custom(t_steel_prev, t_gas, dt, am_v)

        # Температура стали должна увеличиться
        assert t_new > t_steel_prev
        # Но не достичь температуры газа за 1 секунду
        assert t_new < t_gas
        # Альфа должен быть положительным
        assert alpha > 0

    def test_temperature_step_zero_am_v(self):
        """Проверка при нулевом коэффициенте сечения."""
        t_steel_prev = 293.0
        t_gas = 600.0
        dt = 1.0
        am_v = 0

        result = calc_steel_temperature_step_custom(t_steel_prev, t_gas, dt, am_v)

        # Функция возвращает кортеж (t_new, alpha)
        if isinstance(result, tuple):
            t_new, alpha = result
        else:
            t_new = result

        # При нулевом Am_V температура не должна измениться
        assert t_new == t_steel_prev

    def test_temperature_increases_with_larger_am_v(self):
        """Проверка, что при большем Am_V нагрев быстрее."""
        t_steel_prev = 293.0
        t_gas = 800.0
        dt = 1.0

        t_new_small_am_v, _ = calc_steel_temperature_step_custom(t_steel_prev, t_gas, dt, 50)
        t_new_large_am_v, _ = calc_steel_temperature_step_custom(t_steel_prev, t_gas, dt, 200)

        # При большем Am_V (меньшее сечение) нагрев должен быть быстрее
        assert t_new_large_am_v > t_new_small_am_v


class TestCalculateFireResistance:
    """Тесты для расчета предела огнестойкости."""

    def test_fire_resistance_basic(self):
        """Базовая проверка расчета предела огнестойкости."""
        am_v = 150  # 1/м
        crit_temp = 500  # °C
        max_time_min = 60

        result = calculate_fire_resistance(
            Am_V=am_v,
            crit_temp=crit_temp,
            protection_type="unprotected",
            max_time_min=max_time_min
        )

        assert "R_min" in result
        assert "raw_time" in result
        assert "history" in result

        # Проверка истории расчета
        history = result["history"]
        assert "Time_min" in history.columns
        assert "T_gas" in history.columns
        assert "T_steel" in history.columns
        assert "Alpha" in history.columns

        # Проверка, что температура стали возрастает
        assert history["T_steel"].iloc[-1] > history["T_steel"].iloc[0]

    def test_fire_resistance_reaches_critical(self):
        """Проверка достижения критической температуры."""
        am_v = 200  # 1/м (большое значение - быстрый нагрев)
        crit_temp = 400  # °C (низкая критическая температура)
        max_time_min = 60

        result = calculate_fire_resistance(
            Am_V=am_v,
            crit_temp=crit_temp,
            protection_type="unprotected",
            max_time_min=max_time_min
        )

        # Должен достичь критической температуры
        assert isinstance(result["R_min"], (int, float))
        assert result["R_min"] < max_time_min

    def test_fire_resistance_not_reached(self):
        """Проверка, когда критическая температура не достигнута."""
        am_v = 50  # 1/м (малое значение - медленный нагрев)
        crit_temp = 900  # °C (очень высокая критическая температура)
        max_time_min = 10  # Короткое время расчета

        result = calculate_fire_resistance(
            Am_V=am_v,
            crit_temp=crit_temp,
            protection_type="unprotected",
            max_time_min=max_time_min
        )

        # Критическая температура не должна быть достигнута
        assert isinstance(result["R_min"], str)
        assert ">" in result["R_min"]

    def test_fire_resistance_history_length(self):
        """Проверка длины истории расчета."""
        am_v = 150
        crit_temp = 500
        max_time_min = 30

        result = calculate_fire_resistance(
            Am_V=am_v,
            crit_temp=crit_temp,
            protection_type="unprotected",
            max_time_min=max_time_min
        )

        history = result["history"]
        # Количество записей = max_time_min * 60 + 1 (начальная точка)
        expected_length = max_time_min * 60 + 1
        assert len(history) == expected_length

    def test_fire_resistance_temperature_monotonic(self):
        """Проверка монотонности роста температуры стали."""
        am_v = 150
        crit_temp = 500
        max_time_min = 30

        result = calculate_fire_resistance(
            Am_V=am_v,
            crit_temp=crit_temp,
            protection_type="unprotected",
            max_time_min=max_time_min
        )

        history = result["history"]
        t_steel = history["T_steel"].values

        # Проверка, что температура не убывает
        for i in range(len(t_steel) - 1):
            assert t_steel[i+1] >= t_steel[i], f"Температура убывает на шаге {i}"

    def test_fire_resistance_gas_temp_follows_standard_curve(self):
        """Проверка, что температура газа следует стандартной кривой."""
        am_v = 150
        crit_temp = 500
        max_time_min = 10

        result = calculate_fire_resistance(
            Am_V=am_v,
            crit_temp=crit_temp,
            protection_type="unprotected",
            max_time_min=max_time_min
        )

        history = result["history"]

        # Проверим температуру газа в нескольких точках
        for i in range(0, len(history), 60):  # Каждую минуту
            time_sec = history["Time_sec"].iloc[i]
            t_gas_expected_k = standard_fire_curve(time_sec)
            t_gas_expected_c = t_gas_expected_k - 273.15
            t_gas_actual_c = history["T_gas"].iloc[i]

            assert abs(t_gas_actual_c - t_gas_expected_c) < 1.0
